from core.providers.random_provider import IRandomProvider
from typing import Any, List, Tuple
import random


class LocalRandomProvider(IRandomProvider):
    async def roll_dice(self, chat_id: int) -> Tuple[List[int], List[Any]]:
        return [random.randint(1, 6), random.randint(1, 6)], []

    async def spin_slot(self, chat_id: int) -> Tuple[int, Any]:
        return random.randint(1, 64), None