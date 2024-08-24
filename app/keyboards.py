from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from data.outputs import btn_texts, default_btn_texts
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def main(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('dialogue'), callback_data='dialogue')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('wallet'), callback_data='wallet')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('more'), callback_data='more')],
        ]
    )
    return markup


async def wallet(laungage_code: str, has_subscription: bool):
    inline_keyboard = [
        [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_main')],
    ] if has_subscription else [
        [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('payment_1'), callback_data='payment_1')],
        # [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('payment_2'), callback_data='payment_2')],
        [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_main')],
    ]
    markup = InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )
    return markup


async def payment_type(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('payment_type_1'), callback_data='payment_type_1')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('payment_type_2'), callback_data='payment_type_2')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_wallet')],
        ]
    )
    return markup


async def more(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('referral'), callback_data='referral')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('settings'), callback_data='settings')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('info'), callback_data='info')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('feedback'), callback_data='feedback')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_main')],
        ]
    )
    return markup


async def referral(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_more')],
        ]
    )
    return markup


async def settings(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('first_promt'), callback_data='first_promt')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('second_promt'), callback_data='second_promt')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('see_promts'), callback_data='see_promts')],
            # [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('set_default_promt'), callback_data='set_default_promt')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_more')],
        ]
    )
    return markup


async def see_promts(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_settings')],
        ]
    )
    return markup


async def info(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('settings_ai'), callback_data='settings_ai')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('actual_ai'), callback_data='actual_ai')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('token'), callback_data='token')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('usage_ai'), callback_data='usage_ai')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_more')],
        ]
    )
    return markup


async def to_info(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_info')],
        ]
    )
    return markup


async def inner_dialogue(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('change_name'), callback_data='change_name')],
            # [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('change_model'), callback_data='change_model')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('show_history'), callback_data='show_history')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('del_d'), callback_data='del_d')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_dialogue')],
        ]
    )
    return markup


async def change_model(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('gpt-4o'), callback_data='set_gpt-4o')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('gpt-4o-mini'), callback_data='set_gpt-4o-mini')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('dall-e-3'), callback_data='set_dall-e-3')],
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data='to_current_d')],
        ]
    )
    return markup


async def dialogue(laungage_code: str, dialogue_names: list[str], need_continue: bool = False):
    builder = InlineKeyboardBuilder()
    for d_index, name in enumerate(dialogue_names):
        builder.row(InlineKeyboardButton(text=name, callback_data=f"c_{d_index}" if need_continue else f"d_{d_index}"))

    builder.row(InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('create_new_chat'), callback_data=f"create_new_chat"))
    builder.row(InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('back'), callback_data=f"to_main"))
    
    return builder.as_markup()


async def to_wallet(laungage_code: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn_texts.get(laungage_code, default_btn_texts).get('to_wallet'), callback_data='to_wallet')],
        ]
    )
    return markup