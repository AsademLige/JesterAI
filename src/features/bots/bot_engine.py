from features.gamba_house.domain.trash_loto_manager import TrashLotoManager
from features.user.data.repository.user_repository import IUserRepository
from features.user.domain.user_manager import UserManager
from py_trees.composites import Selector, Sequence
from features.user.data.dtos.user_dto import User
from core.utils.app_herald import AppHerald
from py_trees.common import Access, Status
from py_trees.behaviour import Behaviour
from py_trees.trees import BehaviourTree
import threading
import logging
import asyncio

class PencilCheck(Behaviour):
    def __init__(self, user: User, user_repo: IUserRepository, on_data_callback=None):
        super().__init__(name="{{pencil}}_check")

        self.background_loop = asyncio.new_event_loop()
        threading.Thread(target=self.background_loop.run_forever, daemon=True).start()
        self.log:AppHerald = AppHerald()

        self.user_mr = UserManager(repo=user_repo)
        self.on_data_callback = on_data_callback
        self.user_repo = user_repo
        self.user = user
        self._task = None

        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key(key=f"pencil_check_node_{user.id}", access=Access.WRITE)

    async def action(self):
        result = await self.user_mr.pencil_change(self.user)
        self.user = await self.user_repo.get_user(id=self.user.id)
        return result

    def initialise(self):
        self.future = asyncio.run_coroutine_threadsafe(
            self.action(), 
            self.background_loop
        )

    def update(self):
        if self.future.done():
            try:
                result = self.future.result()
                setattr(self.blackboard, f"pencil_check_node_{self.user.id}", result)
                if self.on_data_callback:
                    self.on_data_callback({
                        "actor" : self.user,
                        "action" : "pencil_check",
                        "result": result
                    })
            
                return Status.SUCCESS
            except Exception as e:
                self.log.send_log(f"bot_engine", logging.ERROR, f"pencil_check_node_{self.user.id} exit with error: {e}")
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
    def __init__(self, user: User, user_repo: IUserRepository, on_data_callback=None):
        super().__init__()
        self.user_repo = user_repo
        self.user = user
        self.root = Selector(name=f"ai_{user.id}", memory=False)

        pencil_seq = Sequence(name="Проверка {{pencil}}", memory=False)
        pencil_seq.add_children([PencilCheck(self.user, self.user_repo, on_data_callback)])
        self.root.add_children([pencil_seq])

    def get_tree(self):
        return BehaviourTree(self.root)
    
    async def tick_async(self):
        self.get_tree().tick()
        await asyncio.sleep(0.001)

        return self.root.status
