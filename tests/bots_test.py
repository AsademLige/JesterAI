from features.user.data.repository.local_user_repository import LocalUserRepository
from core.services.apscheduler.scheduler_main import Scheduler
from features.bots.bot_engine import BotEngine, BotProfile
from features.user.data.dtos.user_dto import User
from core.utils.app_herald import AppHerald
from datetime import datetime, timedelta
from freezegun import freeze_time
from typing import Dict, List
import logging
import asyncio
import time

async def main():
    scheduler = await Scheduler.background(test_handle_event)
    
    user_repo = LocalUserRepository(snapshot_dir="snapshots")
    logger:AppHerald = AppHerald()

    def on_data_received(data:Dict):
        user:User = data["actor"]
        result = data["result"]
        action = data["action"]
        
        msg:str = None

        if (action == "pencil_check" and result.get("msg")):
            msg = f"simulation time: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            msg += f"[{action}] - ({user.id}):{user.tg_name} {user.custom_title} - {result['msg']}"

        if (result.get("length_change")):
            msg += f": {user.length - result['length_change']} -> {user.length}"

        if (msg):
            logger.send_log(f"simulation", logging.INFO, msg, show_time=False)

    def simulation(users:List[User], start_date:datetime, duration:timedelta, tick:timedelta = timedelta(hours=1)):
        logger.send_log("simulation", logging.INFO, f"\n------------ simulation started! Day: 1", show_time=False)
        user_repo = LocalUserRepository(snapshot_dir="snapshots")
        users_ai:Dict[int, BotEngine] = {}
        
        for user in users:
            profile:BotProfile = BotProfile.from_type(user.behavior)

            users_ai[user.id] = BotEngine(user, profile, user_repo, on_data_received)
            

        end_date = start_date + duration
        last_logged_day = datetime.now().day
        while datetime.now() < end_date:
            if datetime.now().day != last_logged_day:
                day_number = (datetime.now().date() - start_date.date()).days + 1
                logger.send_log("simulation", logging.INFO, f"\n------------ simulation day: {day_number}", show_time=False)
                last_logged_day = datetime.now().day
            
            with scheduler.core._jobstores_lock:
                scheduler.core._process_jobs()

            for user in users:
                try:
                    users_ai[user.id].get_tree().tick()    
                except KeyboardInterrupt as e:
                    users_ai[user.id].get_tree().shutdown()

            frozen_time.tick(tick)
            time.sleep(0.1)

        scheduler.core.shutdown()
    
    with freeze_time(datetime.now()) as frozen_time:
        bot1 = await user_repo.get_user(tg_id=111)
        if (not bot1):
            await user_repo.add(tg_id=111, tg_name="Егор", length=15, custom_title="Black hole", chat_id=999)
            bot1 = await user_repo.get_user(tg_id=111)
        
        bot2 = await user_repo.get_user(tg_id=222)
        if (not bot2):
            await user_repo.add(tg_id=222, tg_name="Сеня", length=12, custom_title="SVO", chat_id=999)
            bot2 = await user_repo.get_user(tg_id=222)

        simulation([bot1, bot2], datetime.now(), timedelta(days=7), tick=timedelta(hours=6))

async def test_handle_event(self, chat_id: int, event_type: str, data: dict):
    try:
        if event_type == "weekly_winners":
            # text = self.dict.weekly_winners(data["sorted_users"], data["rewards"])
            print(data)

        elif event_type == "day_salary":
            # text = self.dict.day_salary(data["money"])
            print(data)

        elif event_type == "tech_work_compensation":
            # text = self.dict.tech_work_compensation(data["money"])
            print(data)

        elif event_type == "day_draw":
            # text = self.dict.draw(data["winner"], data["length_change"])
            print(data)
            
        elif event_type == "warehouse_update":
            # text = self.dict.warehouse_update(data["discounts"])
            print(data)

    except Exception as e:
        self.logger.send_log("telegram_scheduler", logging.ERROR, f"Failed to send {event_type}: {e}")

if __name__ == "__main__":
    asyncio.run(main())