from aiogram.filters import Filter
from aiogram.types import CallbackQuery


class ContainsCallbackData(Filter):
    key = 'contains_callback_data'
    
    def __init__(self, substring: str):
        self.substring = substring

    async def __call__(self, callback_query: CallbackQuery) -> bool:
        return self.substring in callback_query.data and len(str(callback_query.data)) == 3
    