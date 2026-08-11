from features.game_engine.data.repository.local_bot_settings_repository import LocalBotSettingsRepository
from features.store.data.repository.local_store_repository import LocalStoreRepository
from features.user.data.repository.local_user_repository import LocalUserRepository
from core.services.apscheduler.global_jobs import TestJobTracker
from core.services.apscheduler.scheduler_main import Scheduler
from features.bots.bot_engine import BotEngine, BotProfile
from datetime import datetime, timedelta, timezone
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from core.utils.app_herald import AppHerald
from typing import Any, Dict, List
from freezegun import freeze_time
from pathlib import Path
from tqdm import tqdm
import logging
import asyncio
import random
import time
import json

##PYTHONPATH=../src python3 bots_test.py   

async def main():
    async def test_handle_event(chat_id: int, event_type: str, data: Dict):
        try:
            if event_type == "day_salary":
                if (data.get("money")):
                    if not int(time.time()) in simulation_data["timeline"]:
                        simulation_data["timeline"][int(time.time())] = []
                    simulation_data["timeline"][int(time.time())].append({
                        "data":{
                            "action": "day_salary",
                            "result": data,
                        },
                    })

            elif event_type == "day_draw":
                if (data.get("winner")):
                    if not int(time.time()) in simulation_data["timeline"]:
                        simulation_data["timeline"][int(time.time())] = []
                        simulation_data["timeline"][int(time.time())].append({
                            "data":{
                                "action": "day_draw",
                                "result": {
                                    "winner":data["winner"].id,
                                    "length_change":data["length_change"]
                                },
                            },
                        })
                
            elif event_type == "warehouse_update":
                # text = self.dict.warehouse_update(data["discounts"])
                print(data)

        except Exception as e:
            logger.send_log("test_scheduler", logging.ERROR, f"Failed to send {event_type}: {e}")
    
    user_repo = LocalUserRepository(snapshot_dir="snapshots/users")
    store_repo = LocalStoreRepository("snapshots/store")
    settings_repo = LocalBotSettingsRepository("snapshots/settings")
    scheduler = await Scheduler.local(test_handle_event, 
                                           user_repo,
                                           store_repo,
                                           settings_repo)
    
    logging.getLogger('apscheduler').setLevel(logging.ERROR)
    logging.getLogger('apscheduler.executors.default').setLevel(logging.ERROR)

    logger:AppHerald = AppHerald()
    dict = Dictionary()

    simulation_data:Dict[Any, Any] = {
        "started_at": int(time.time()),
        "template": {
            "actors_num": 3,
            "simulation_length": timedelta(days=3),
            "simulation_tick": timedelta(hours=6)
        },
        "actors": [],
        "timeline" : {}
    }

    def on_data_received(data:Dict):
        user:User = data["actor"]
        result = data["result"]
        action = data["action"]
        
        log:str = None
        str_time:str = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        if (action == "pencil_check" and result.get("msg")):
            log = f"simulation time: {str_time}\n"
            log += f"[{action}] - ({user.id}):{user.tg_name} {user.custom_title} - {result['msg']}"

        if (result.get("length_change")):
            log += f": {user.length - result['length_change']} -> {user.length}"

        if not int(time.time()) in simulation_data["timeline"]:
            simulation_data["timeline"][int(time.time())] = []

        if (log):
            simulation_data["timeline"][int(time.time())].append({
                "actor":user.id,
                "action":action,
                "data":result,
            })

    def save_simulation_result(path: str = "", result:Dict[str, Any] = {}):
        snapshot_dir = Path(path)
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        result["template"]["simulation_length"] = str(result["template"]["simulation_length"])
        result["template"]["simulation_tick"] = str(result["template"]["simulation_tick"])
        
        actors_map:List = []
        actors:List[User] = result["actors"]
        for actor in actors:
            actors_map.append(actor.model_dump_json(indent=4))
        result["actors"] = actors_map
        
        file_path = snapshot_dir / f"{result['started_at']}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, indent=2))

    async def simulation(users: List[User], start_date: datetime, duration: timedelta, tick: timedelta = timedelta(hours=1)):
        users_ai: Dict[int, BotEngine] = {}
        
        for user in users:
            profile: BotProfile = BotProfile.from_type(user.behavior)
            users_ai[user.id] = BotEngine(user, profile, user_repo, settings_repo, on_data_received)

        end_date = start_date + duration
        total_ticks = int(duration.total_seconds() / tick.total_seconds())
        sim_start_date = datetime.now() 

        job_tracker = TestJobTracker()
        all_jobs = scheduler.core.get_jobs()
        
        with tqdm(total=total_ticks, desc="Симуляция", unit="тик", ncols=100) as pbar:
            
            while datetime.now() < end_date:
                current_sim_time = datetime.now()
                current_day = (current_sim_time.date() - sim_start_date.date()).days + 1
                current_date_str = current_sim_time.strftime("%Y-%m-%d")
            
                pbar.set_description(f"День {current_day:03d} ({current_sim_time.strftime('%d.%m')})")
                
                for job in all_jobs:
                    if job_tracker.should_fire(job.id, current_date_str):
                        await job.func(*job.args, **job.kwargs)

                for user in users: 
                    try:
                        users_ai[user.id].get_tree().tick()
                    except KeyboardInterrupt:
                        for u in users:
                            users_ai[u.id].get_tree().shutdown()
                        raise
                
                frozen_time.tick(tick)
                pbar.update(1)
                time.sleep(0.01) 

        print("\n✅ Симуляция завершена! Сохранение результатов...")
        save_simulation_result("snapshots/simulation", simulation_data)
        user_repo.save_cache()
        scheduler.core.shutdown()
    
    with freeze_time(datetime.now(), tick=True) as frozen_time:
        max_id:int = user_repo.get_max_id()
        for i in range(simulation_data["template"]["actors_num"]):
            id:int = max_id+1
            while await user_repo.get_user(tg_id=id, chat_id=999) != None:
                id+=1

            bot = await user_repo.add(tg_id=id, tg_name=random.choice(dict.bot_names), 
                                length=random.Random().randint(10, 15), 
                                custom_title=random.choice(dict.bot_custom_titles), 
                                chat_id=999)
            simulation_data["actors"].append(bot)

        await simulation(simulation_data["actors"], datetime.now(), 
                   simulation_data["template"]["simulation_length"], 
                   simulation_data["template"]["simulation_tick"])

if __name__ == "__main__":
    asyncio.run(main())