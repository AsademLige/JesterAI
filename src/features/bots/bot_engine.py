from features.game_engine.data.repository.bot_settings_repository import IBotSettingsRepository
from features.user.data.repository.user_repository import IUserRepository
from features.user.domain.user_manager import UserManager
from py_trees.composites import Selector, Sequence
from features.user.data.dtos.user_dto import User
from core.utils.app_herald import AppHerald
from py_trees.common import Access, Status
from py_trees.behaviour import Behaviour
from py_trees.trees import BehaviourTree
from dataclasses import dataclass, field
from features.bots import bots_behaviors
from typing import Dict, Optional
import threading
import logging
import asyncio
import random

@dataclass
class BotProfile:
    """Модель личности бота"""
    laziness: float = 0.5
    interests: Dict[str, float] = field(default_factory=dict)
    personality: Dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def from_type(cls, behavior: Optional[str]) -> 'BotProfile':
        if (behavior):
            data = bots_behaviors.bot_behaviors[behavior]
        else:
            data = bots_behaviors.bot_behaviors["normal"]

        return cls(
            laziness=data.get("personality", data).get("laziness", 0.5),
            interests=data.get("interests", {}),
            personality=data.get("personality", {})
        )

    def get_interest(self, action_name: str) -> float:
        return self.interests.get(action_name, 0.5)

    def calculate_action_chance(self, action_name: str) -> float:
        base_activity = 1.0 - self.laziness
        interest_modifier = self.get_interest(action_name) * self.laziness
        return min(1.0, base_activity + interest_modifier)
    
class AsyncLoopManager:
    _loop: asyncio.AbstractEventLoop = None
    _lock = threading.Lock()
    
    @classmethod
    def get_loop(cls) -> asyncio.AbstractEventLoop:
        with cls._lock:
            if cls._loop is None or cls._loop.is_closed():
                cls._loop = asyncio.new_event_loop()
                threading.Thread(target=cls._loop.run_forever, daemon=True, name="BotAsyncLoop").start()
                asyncio.run_coroutine_threadsafe(asyncio.sleep(0), cls._loop).result(timeout=2.0)
            return cls._loop

    @classmethod
    def run_coroutine(cls, coro):
        return asyncio.run_coroutine_threadsafe(coro, cls.get_loop())


class AsyncPencilCheck(Behaviour):
    def __init__(self, user:User, user_repo:IUserRepository, 
                 settings_repo:IBotSettingsRepository, 
                 profile:BotProfile, callback=None):
        super().__init__(name=f"pencil_check_{user.id}")
        
        self.user = user
        self.profile = profile
        self.user_repo = user_repo
        self.settings_repo = settings_repo
        self.callback = callback
        
        self.user_mr = UserManager(user_repo, settings_repo)
        self.log = AppHerald()
        
        self._future = None
        self._skipped = False
        
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key=f"pencil_check_node_{user.id}", access=Access.WRITE)

    def initialise(self):
        self._future = None
        self._skipped = False
        
        action_chance = self.profile.calculate_action_chance("pencil")

        if not UserManager.check_pencil_ready(self.user.last_length_check):
            self._skipped = True
            return

        if random.random() > action_chance:
            self._skipped = True
            if self.callback:
                self.callback({
                    "actor": self.user,
                    "action": "pencil_check",
                    "result": {"msg": f"skip action (chance {action_chance:.2f})"}
                })
            return

        self._future = AsyncLoopManager.run_coroutine(self._action())

    async def _action(self):
        self.user = await self.user_repo.get_user(id=self.user.id)
        result = await self.user_mr.pencil_change(self.user)
        return {"result": result, "user": self.user}

    def update(self):
        if self._skipped:
            return Status.FAILURE

        if self._future is None:
            return Status.RUNNING

        if self._future.done():
            try:
                data = self._future.result()
                setattr(self.blackboard, f"pencil_check_node_{self.user.id}", data["result"])
                
                if self.callback:
                    self.callback({
                        "actor": data["user"],
                        "action": "pencil_check",
                        "result": data["result"]
                    })
                return Status.SUCCESS
                
            except asyncio.CancelledError:
                self.log.send_log("bot_engine", logging.WARNING, f"[{self.name} - {self.user.id}] cancel")
                return Status.FAILURE
                
            except Exception as e:
                self.log.send_log("bot_engine", logging.ERROR, f"pencil_check_node_{self.user.id} exit with error: {e}")
                
                if self.callback:
                    self.callback({
                        "actor": self.user,
                        "action": "pencil_check",
                        "result": {"error": str(e)}
                    })
                return Status.FAILURE
                
        return Status.RUNNING

    def terminate(self, new_status):
        if new_status == Status.INVALID and self._future and not self._future.done():
            self.log.send_log("bot_engine", logging.WARNING, f"[{self.name} - {self.user.id}] cancel")
            self._future.cancel()

class BotEngine:
    def __init__(self, user, profile, user_repo, settings_repo, callback=None):
        self.user = user
        self.profile = profile
        self.user_repo = user_repo
        self.settings_repo = settings_repo
    
        pencil_node = AsyncPencilCheck(
            user=user,
            user_repo=user_repo,
            settings_repo=settings_repo,
            profile=profile,
            callback=callback
        )
        
        self.root = Selector(
            name=f"ai_selector_{user.id}", 
            memory=False
        )
        self.root.add_child(pencil_node)

    def get_tree(self):
        return BehaviourTree(self.root)