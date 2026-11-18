from features.gamba_house.data.repository.gino_winners_log_repository import GinoWinnersLogRepository
from features.user.data.repository.gino_user_repository import GinoUserRepository
from core.providers.random_provider import IRandomProvider
from features.user.data.dtos.user_dto import User
from core.consts.dictionary import Dictionary
import random



class TrashLotoManager:
    user_repo:GinoUserRepository = GinoUserRepository()
    winners_log_repo:GinoWinnersLogRepository = GinoWinnersLogRepository()
    
    def __init__(self, dictionary:Dictionary):
        self.dict = dictionary

    async def play(self, user:User, chat_id:int, bet:int, provider: IRandomProvider) -> dict:
        if user.money < bet: return {"error": "not_enough_money"}
        value, slot_msg = await provider.spin_slot(chat_id)
        
        # Индексы: 0=BAR, 1=🍒, 2=🍋, 3=777
        value -= 1
        left, middle, right = value % 4, (value // 4) % 4, value // 16

        is_minor_win = (left == middle or middle == right)
        is_major_win = (left == middle == right)
        is_consolation = (left == right)
        is_jackpot = value == 63

        award = 0
        length = 0
        energy = 0

        slot_result_msg:str = None
        error:str = None

        # 777
        if is_jackpot:
            award =  random.randrange(4*bet, 6*bet)
            energy = random.randrange(3, 6)
            length = 10

            slot_result_msg = self.dict.trash_loto_jackpot_money_award(user.tg_name, user.tg_id, award, length, energy)
            await self.winners_log_repo.add_win_log(user.id, event_type=0, money=award, bet=bet, energy=energy)
        # тройная комбинаций
        elif is_major_win:
            multiplier:int = bet // 5 + 1
            action = random.choices([1, 2, 3])
            if (action[0] == 1):
                length = random.randrange(1 * multiplier, 2 * multiplier)
                slot_result_msg = self.dict.trash_loto_major_length_award(user.tg_name, user.tg_id, length)
                await self.winners_log_repo.add_win_log(user.id, event_type=2, length=length, bet=bet, energy=energy)
            elif (action[0] == 1):
                award = random.randrange(2 * bet, 3 * bet)
                slot_result_msg = self.dict.trash_loto_major_money_award(user.tg_name, user.tg_id, award)
                await self.winners_log_repo.add_win_log(user.id, event_type=2, money=award, bet=bet, energy=energy)
            else:
                energy = 1 * bet
                slot_result_msg = self.dict.trash_loto_major_energy_award(user.tg_name, user.tg_id, energy)
                await self.winners_log_repo.add_win_log(user.id, event_type=2, money=award, bet=bet, energy=energy)
                
        # Проверка на одинаковые крайние
        elif is_consolation:
            multiplier:int = bet // 5 + 1
            award = random.randrange(1*multiplier, 5*multiplier)
            slot_result_msg = self.dict.trash_loto_consolation_money_award(user.tg_name, user.tg_id, award)
            await self.winners_log_repo.add_win_log(user.id, event_type=3, money=award, bet=bet, energy=energy)

        # Проверка на любые две одинаковые подряд
        elif is_minor_win:
            action = random.choices([1, 2, 3])
            multiplier:int = bet // 5 + 1
            if (action[0] == 1):
                length = 1 * multiplier
                slot_result_msg = self.dict.trash_loto_minor_length_award(user.tg_name, user.tg_id, length)
                await self.winners_log_repo.add_win_log(user.id, event_type=1, length=length, bet=bet, energy=energy)
            elif (action[0] == 1):
                award =  random.randrange(bet + 1, bet * 2)
                slot_result_msg = self.dict.trash_loto_minor_money_award(user.tg_name, user.tg_id, award)
                await self.winners_log_repo.add_win_log(user.id, event_type=1, money=award, bet=bet, energy=energy)
            else:
                energy = 2
                slot_result_msg = self.dict.trash_loto_minor_energy_award(user.tg_name, user.tg_id, energy)
                await self.winners_log_repo.add_win_log(user.id, event_type=2, money=award, bet=bet, energy=energy)
            
        else:
            slot_result_msg = self.dict.trash_loto_lose(user.tg_name, user.tg_id)
            # Проигрыш тоже пишем в лог — только ставку, без выигрыша (event_type=6)
            await self.winners_log_repo.add_win_log(user.id, event_type=6, bet=bet, energy=energy)
        
        await self.user_repo.update(user,
                                length=user.length + length,
                                money=user.money + award - bet,
                                energy = user.energy + energy,
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