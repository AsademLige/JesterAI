from features.bots import bots_behaviors
from features.gamba_house.domain.trash_loto_manager import TrashLotoManager
from features.user.data.repository.user_repository import IUserRepository
from features.user.domain.user_manager import UserManager
from py_trees.composites import Selector, Sequence
from features.user.data.dtos.user_dto import User
from core.utils.app_herald import AppHerald
from py_trees.common import Access, Status
from py_trees.behaviour import Behaviour
from py_trees.trees import BehaviourTree
from dataclasses import dataclass, field
from typing import Dict, Optional
import threading
import logging
import asyncio
import random
import json

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

class PencilCheck(Behaviour):
    def __init__(self, user: User, user_repo: IUserRepository, profile: BotProfile, on_data_callback=None):
        super().__init__(name=f"pencil_check_{user.id}")

        self.background_loop = asyncio.new_event_loop()
        threading.Thread(target=self.background_loop.run_forever, daemon=True).start()
        self.log: AppHerald = AppHerald()

        self.profile = profile
        self.user_mr = UserManager(repo=user_repo)
        self.on_data_callback = on_data_callback
        self.user_repo = user_repo
        self.user = user
        self._task = None
        self._skipped_due_to_laziness = False

        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key=f"pencil_check_node_{user.id}", access=Access.WRITE)

    def initialise(self):
        action_chance = self.profile.calculate_action_chance("pencil")
        self.future = None

        if (not UserManager.check_pencil_ready(self.user.last_length_check)):
            self._skipped_due_to_laziness = True
            return

        if random.random() > action_chance:
            if self.on_data_callback:
                    self.on_data_callback({
                        "actor": self.user,
                        "action": "pencil_check",
                        "result": {
                            "msg" : f"skip action (chance {action_chance:.2f})"
                        }
                    })
            self._skipped_due_to_laziness = True
            return

        self._skipped_due_to_laziness = False
        self.future = asyncio.run_coroutine_threadsafe(self.action(), self.background_loop)

    async def action(self):
        result = await self.user_mr.pencil_change(self.user)
        self.user = await self.user_repo.get_user(id=self.user.id)
        return result

    def update(self):
        if self._skipped_due_to_laziness:
            return Status.FAILURE

        if self.future.done():
            try:
                result = self.future.result()
                setattr(self.blackboard, f"pencil_check_node_{self.user.id}", result)
                if self.on_data_callback:
                    self.on_data_callback({
                        "actor": self.user,
                        "action": "pencil_check",
                        "result": result
                    })
                return Status.SUCCESS
            except Exception as e:
                self.log.send_log("bot_engine", logging.ERROR, f"pencil_check_node_{self.user.id} exit with error: {e}")
                return Status.FAILURE
        return Status.RUNNING

    def terminate(self, new_status: Status):
        if new_status == Status.INVALID and self.future and not self.future.done():
            self.log.send_log(f"bot_engine", logging.WARNING, f"[{self.name} - {self.user.id}] cancel")
            self.future.cancel()
    
class TrashLoto(Behaviour):
    def __init__(self, user: User, user_repo: IUserRepository):
        super().__init__(name="Проверка {{pencil}}")
        # self.trash_loto_mr = TrashLotoManager()
        self.user_repo = user_repo
        self.user = user

    def update(self) -> Status:
        loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.repo.update_bot_memory(memory))
        
        return Status.SUCCESS

class BotEngine:
    def __init__(self, user: User, profile: BotProfile, user_repo: IUserRepository, on_data_callback=None):
        super().__init__()
        self.user_repo = user_repo
        self.user = user
        self.profile = profile
        self.root = Selector(name=f"ai_selector_{user.id}", memory=False)
    
        actions = {
            "pencil" : PencilCheck(self.user, self.user_repo, self.profile, on_data_callback),
            # "trash_loto": TrashLoto(self.user, self.user_repo, self.profile, on_data_callback)
        }

        sorted_actions = sorted(
            actions.items(), 
            key=lambda item: self.profile.get_interest(item[0]), 
            reverse=True
        )

        for action_name, action_node in sorted_actions:
            seq = Sequence(name=f"seq_{action_name}", memory=False)
            seq.add_children([action_node])
            self.root.add_children([seq])

    def get_tree(self):
        return BehaviourTree(self.root)
    
    async def tick_async(self):
        self.get_tree().tick()
        await asyncio.sleep(0.001)
        return self.root.status
