from features.user.data.repository.gino_user_repository import GinoUserRepository
from core.providers.random_provider import IRandomProvider
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
from core.data.data_base import DataBase
import random



class TrashLotoManager:
    user_repo:GinoUserRepository = GinoUserRepository()
    
    def __init__(self, db:DataBase, dictionary:Dictionary):
        self.db = db
        self.dict = dictionary

    async def play(self, user:User, bet:int, provider: IRandomProvider) -> dict:
        if user.money < bet: return {"error": "not_enough_money"}
        value, slot_msg = await provider.spin_slot(user.chat_id)
        
        # Индексы: 0=BAR, 1=🍒, 2=🍋, 3=777
        value -= 1
        left, middle, right = value % 4, (value // 4) % 4, value // 16

        is_minor_win = (left == middle or middle == right)
        is_major_win = (left == middle == right)
        is_consolation = (left == right)
        is_jackpot = value == 63

        award = 0
        length = 0

        slot_result_msg:str = None
        error:str = None

        # 777
        if is_jackpot:
            award =  random.randrange(4*bet, 6*bet)
            slot_result_msg = self.dict.trash_loto_jackpot_money_award(user.tg_name, user.tg_id, award)
            await self.db.add_win_log(user.id, event_type=0, money=award)
        #тройная комбинаций
        elif is_major_win:
            multiplier:int = bet // 5 + 1
            action = random.choices([1, 2])
            if (action[0] == 1):
                length = random.randrange(1 * multiplier, 2 * multiplier)
                slot_result_msg = self.dict.trash_loto_major_length_award(user.tg_name, user.tg_id, length)
                await self.db.add_win_log(user.id, event_type=2, length=length)
            else:
                award =  random.randrange(2 * bet, 3 * bet)
                slot_result_msg = self.dict.trash_loto_major_money_award(user.tg_name, user.tg_id, award)
                await self.db.add_win_log(user.id, event_type=2, money=award)

        # Проверка на одинаковые крайние
        elif is_consolation:
            multiplier:int = bet // 5 + 1
            award = random.randrange(1*multiplier, 5*multiplier)
            slot_result_msg = self.dict.trash_loto_consolation_money_award(user.tg_name, user.tg_id, award)
            await self.db.add_win_log(user.id, event_type=3, money=award)

        # Проверка на любые две одинаковые подряд
        elif is_minor_win:
            action = random.choices([1, 2])
            multiplier:int = bet // 5 + 1
            if (action[0] == 1):
                length = 1 * multiplier
                slot_result_msg = self.dict.trash_loto_minor_length_award(user.tg_name, user.tg_id, length)
                await self.db.add_win_log(user.id, event_type=1, length=length)
            else:
                award =  random.randrange(bet + 1, bet * 2)
                slot_result_msg = self.dict.trash_loto_minor_money_award(user.tg_name, user.tg_id, award)
                await self.db.add_win_log(user.id, event_type=1, money=award)
        else:
            slot_result_msg = self.dict.trash_loto_lose(user.tg_name, user.tg_id)
        
        await self.user_repo.update(user,
                                length=user.length + length,
                                money=user.money + award - bet,
                                trash_loto_spins= user.trash_loto_spins + 1,
                                trash_loto_money_wins=user.trash_loto_money_wins + award,
                                trash_loto_length_wins=user.trash_loto_length_wins + length,
                                trash_loto_jackpots=user.trash_loto_jackpots + (1 if is_jackpot else 0))
        
        return {
            "is_jackpot": is_jackpot, "is_major_win": is_major_win,
            "is_consolation": is_consolation, "slot_result_msg" : slot_result_msg,
            "award": award, "length": length, "slot_msg": slot_msg,
            "error": error,
        }