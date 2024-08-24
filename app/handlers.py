from aiogram import types, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.custom_filter import ContainsCallbackData
import math

from app.scripts import (
    count_tokens, 
    get_total_price,
    extract_text_from_docx,
    extract_text_from_txt,
    send_feedback_via_email
)

from app.api import fetch_chatgpt_response, fetch_dalle_response, create_invoice, transcribe_voice_to_text
import app.keyboards as kb
import app.keyboards as kb

from data.database.query import (
    create_user,
    increment_referral_count,
    get_referral_data,
    set_first_promt,
    set_second_promt,
    get_promts,
    set_default_promts,
    get_dialogue_names,
    create_new_chat,
    set_current_dialog_index,
    get_dialog_data_by_index,
    set_dialog_name,
    get_current_dialog_index,
    set_model,
    del_current_dialogue,
    get_data_for_request,
    # get_balance,
    # set_balance,
    get_referral_balance,
    get_last_invoice,
    set_last_invoice,
    decrement_free_requests,
    add_message_to_history,
    get_dialogue_history,
    get_referral_user,
    get_subscription_end_date,
    user_has_subscription,
    activate_subscription,
    referral_replenishment,
    is_ther_a_user
)

from data.outputs import answer_texts, default_answer_texts
import config
import os

import io
from jinja2 import Environment, FileSystemLoader
import tempfile


router = Router()
env = Environment(loader=FileSystemLoader('templates'))


class States(StatesGroup):
    first_promt = State()
    second_promt = State()
    feedback = State()
    chat = State()
    change_name = State()
    amount = State()
    crypto_amount = State()
    last_message = State()
    s_type = State()
    

# COMMANDS
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    # https://t.me/chatgpt_kaba_bot?start=test
    args = message.text.split()[1:]
    args = message.text.split()[1:]
    if args:
        referrer_id = int(args[0])
        not_new_user = await is_ther_a_user(int(message.from_user.id))

        if not not_new_user:
            await increment_referral_count(id=referrer_id)

    else:
        referrer_id = 0

    await create_user(
        id=int(message.from_user.id),
        firstname=str(message.from_user.first_name), 
        lastname=str(message.from_user.last_name),
        referral_user=referrer_id
    )
            
    await message.answer(
        text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('main'), 
        parse_mode='html',
        reply_markup=await kb.main(str(message.from_user.language_code))
    )


@router.message(Command('wallet'))
async def wallet(message: types.Message, state: FSMContext):
    await state.clear()
    has_subscription = await user_has_subscription(id=int(message.from_user.id))
    if has_subscription:
        subscription_end_date = await get_subscription_end_date(id=int(message.from_user.id))
        await message.answer(
            text=answer_texts.get(str(message.from_user.language_code), default_answer_texts)
                .get('yes_subcribe')
                .format(subscription_end_date),
            parse_mode='html',
            reply_markup=await kb.wallet(laungage_code=str(message.from_user.language_code), has_subscription=has_subscription)
        )

    else:
        await message.answer(
            text=answer_texts.get(str(message.from_user.language_code), default_answer_texts)
                .get('not_subcribe'),
            parse_mode='html',
            reply_markup=await kb.wallet(laungage_code=str(message.from_user.language_code), has_subscription=has_subscription)
        )


@router.message(Command('benefit'))
async def wallet(message: types.Message, state: FSMContext):
    await state.clear()
    has_subscription = await user_has_subscription(id=int(message.from_user.id))
    if has_subscription:
        subscription_end_date = await get_subscription_end_date(id=int(message.from_user.id))
        await message.answer(
            text=answer_texts.get(str(message.from_user.language_code), default_answer_texts)
                .get('yes_subcribe')
                .format(subscription_end_date),
            parse_mode='html',
            reply_markup=await kb.wallet(laungage_code=str(message.from_user.language_code), has_subscription=has_subscription)
        )

    else:
        await message.answer(
            text=answer_texts.get(str(message.from_user.language_code), default_answer_texts)
                .get('not_subcribe'),
            parse_mode='html',
            reply_markup=await kb.wallet(laungage_code=str(message.from_user.language_code), has_subscription=has_subscription)
        )



@router.message(Command('dialogues'))
async def func(message: types.Message, state: FSMContext):
    await state.clear()
    dialogue_names = await get_dialogue_names(id=int(message.from_user.id))

    await message.answer(
        text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('dialogue'), 
        parse_mode='html', 
        reply_markup=await kb.dialogue(laungage_code=str(message.from_user.language_code), dialogue_names=dialogue_names)
    )


@router.message(Command('info'))
async def func(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('info'), 
        parse_mode='html', 
        reply_markup=await kb.info(str(message.from_user.language_code))
    )


@router.message(Command('feedback'))
async def func(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(States.feedback)
    await message.answer(
        text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('feedback_1'), 
        parse_mode='html', 
    )


@router.message(Command('referral'))
async def func(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=answer_texts.get(
            str(message.from_user.language_code), default_answer_texts)
                .get('referral')
                .format(
                    *await get_referral_data(id=int(message.from_user.id)
                )
        ), 
        parse_mode='Markdown', 
        reply_markup=await kb.referral(str(message.from_user.language_code))
    )


@router.message(Command('settings'))
async def func(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('settings'), 
        parse_mode='html', 
        reply_markup=await kb.settings(str(message.from_user.language_code))
    )


# ------------------------------ PAYMENT ------------------------------ #
@router.callback_query(F.data == 'payment_1')
async def wallet(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(s_type='m')

    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('payment_type'),
        parse_mode='html',
        reply_markup=await kb.payment_type(str(callback.from_user.language_code))
    )

    await callback.answer()


@router.callback_query(F.data == 'payment_2')
async def wallet(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(s_type='y')

    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('payment_type'),
        parse_mode='html',
        reply_markup=await kb.payment_type(str(callback.from_user.language_code))
    )

    await callback.answer()


@router.callback_query(F.data == 'payment_type_1')
async def send_invoice_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    s_type = data.get('s_type', None)
    if s_type is not None:
        amount = math.ceil(800 if s_type == 'm' else 2388 ) * 100
        await callback.message.delete()
        await callback.message.answer_invoice(        
            title="Пополнение баланса.",
            description="Пополнение кошелька для использования ИИ.\n Конечная сумма будет переведена в USD",
            payload="Payment",
            provider_token=config.YOUKASSA_TEST_TOKEN if config.DEBUG else config.YOUKASSA_TOKEN,
            currency="rub",
            prices=[
                types.LabeledPrice(
                    label='Общая сумма',
                    amount=amount
                )
            ],
            disable_notification=False,
            protect_content=True
        )
    callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def success_payment_handler(message: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    s_type = data.get('s_type', None)
    if s_type is not None:
        if s_type == 'm':
            await activate_subscription(id=int(message.from_user.id), is_monthly=True)
            await message.answer(text="✅ Ежемесячная подписка успешно оформленна")
            payment_amount = 800
            ...
        if s_type == 'y':
            await activate_subscription(id=int(message.from_user.id), is_monthly=False)
            await message.answer(text="✅ Годовая подписка успешно оформленна")
            payment_amount = 2388 
            ...

        referral_user = await get_referral_user(id=int(message.from_user.id))

        if int(referral_user) != 0: 
            price = payment_amount * 0.1
            await referral_replenishment(id=int(referral_user), price=price)

        await state.clear()


@router.callback_query(F.data == 'payment_type_2')
async def func(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    s_type = data.get('s_type', None)
    if s_type is not None:
        amount = 3.49 if s_type == 'm' else 29.99
        link = await create_invoice(amount=amount)
        await callback.message.edit_text(text=f'Для оплаты перейдите по ссылке:\n\n{link}')
        
    await state.clear()

    await callback.answer()


    


# ------------------------------ PAYMENT ------------------------------ #


@router.callback_query(F.data == 'wallet')
@router.callback_query(F.data == 'to_wallet')
async def wallet(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    has_subscription = await user_has_subscription(id=int(callback.from_user.id))

    if has_subscription:
        subscription_end_date = await get_subscription_end_date(id=int(callback.from_user.id))
        await callback.message.edit_text(
            text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts)
                .get('yes_subcribe')
                .format(subscription_end_date),
            parse_mode='html',
            reply_markup=await kb.wallet(laungage_code=str(callback.from_user.language_code), has_subscription=has_subscription)
        )

    else:
        await callback.message.edit_text(
            text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts)
                .get('not_subcribe'),
            parse_mode='html',
            reply_markup=await kb.wallet(laungage_code=str(callback.from_user.language_code), has_subscription=has_subscription)
        )


@router.callback_query(F.data == 'dialogue')
@router.callback_query(F.data == 'to_dialogue')
async def func(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    dialogue_names = await get_dialogue_names(id=int(callback.from_user.id))

    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('dialogue'), 
        parse_mode='html', 
        reply_markup=await kb.dialogue(laungage_code=str(callback.from_user.language_code), dialogue_names=dialogue_names)
    )


@router.callback_query(F.data == 'create_new_chat')
async def func(callback: types.CallbackQuery, state: FSMContext):
    chat_name, chat_model, dialog_index = await create_new_chat(id=int(callback.from_user.id))

    await state.set_state(States.chat)

    await set_current_dialog_index(
        id=int(callback.from_user.id), 
        current_dialog_index=dialog_index
    )
    
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts)
            .get('create_new_chat')
            .format(chat_model), 
        parse_mode='html', 
        reply_markup= await kb.inner_dialogue(laungage_code=str(callback.from_user.language_code))
    )
    

@router.callback_query(F.data == 'change_name')
async def func(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.change_name)

    await callback.message.answer(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('change_name_1'), 
        parse_mode='html', 
    )
    await callback.answer()


@router.message(States.change_name)
async def func(message: types.Message, state: FSMContext):
    if len(str(message.text)) <= 40:
        await set_dialog_name(
            id=int(message.from_user.id), 
            dialog_name=str(message.text),
        )
        await message.answer(
            text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('change_name_2'), 
            parse_mode='html', 
        )
        await state.set_state(States.chat)
    else: 
        await message.answer(
            text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('change_name_1'), 
            parse_mode='html', 
        )


@router.callback_query(F.data == 'change_model')
async def func(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('change_model'), 
        parse_mode='html', 
        reply_markup=await kb.change_model(laungage_code=str(callback.from_user.language_code))
    )


@router.callback_query(F.data == 'show_history')
async def func(callback: types.CallbackQuery, state: FSMContext):
    message_history, current_dialog_index = await get_dialogue_history(id=int(callback.from_user.id), need_parse=False)
    
    if str(current_dialog_index) in message_history:
        history = message_history[str(current_dialog_index)]

        template = env.get_template('template.html')
        rendered_html = template.render(messages=history)
        
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as temp_file:
            temp_file.write(rendered_html)
            temp_file_path = temp_file.name

        try:
            await callback.message.answer_document(
                document=types.FSInputFile(temp_file_path, filename=f"history_{callback.from_user.id}.html"),
                caption="Ваша история сообщений"
            )
        finally:
            os.remove(temp_file_path)
    else:
        await callback.message.answer(
            text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('empty_history'), 
            parse_mode='html', 
        )
    
    await callback.answer()


@router.callback_query(F.data == 'set_gpt-4o')
@router.callback_query(F.data == 'set_gpt-4o-mini')
@router.callback_query(F.data == 'set_dall-e-3')
async def func(callback: types.CallbackQuery, state: FSMContext):
    if 'gpt-4o-mini' in str(callback.data):
        await set_model(id=int(callback.from_user.id), model='gpt-4o-mini')

    elif 'gpt-4o' in str(callback.data):
        await set_model(id=int(callback.from_user.id), model='gpt-4o')

    elif 'dall-e-3' in str(callback.data):
        await set_model(id=int(callback.from_user.id), model='dall-e-3')

    current_dialog_index = await get_current_dialog_index(id=int(callback.from_user.id))

    dialogue_model, dialog_title = await get_dialog_data_by_index(
        id=int(callback.from_user.id), 
        dialog_index=current_dialog_index
    )

    await state.set_state(States.chat)

    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts)
            .get('inner_dialogue')
            .format(dialog_title), 
        parse_mode='html', 
        reply_markup= await kb.inner_dialogue(laungage_code=str(callback.from_user.language_code))
    )


@router.callback_query(F.data == 'to_current_d')
async def func(callback: types.CallbackQuery, state: FSMContext):
    current_dialog_index = await get_current_dialog_index(id=int(callback.from_user.id))

    dialogue_model, dialog_title = await get_dialog_data_by_index(
        id=int(callback.from_user.id), 
        dialog_index=current_dialog_index
    )

    await state.set_state(States.chat)

    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts)
            .get('inner_dialogue')
            .format(dialog_title), 
        parse_mode='html', 
        reply_markup= await kb.inner_dialogue(laungage_code=str(callback.from_user.language_code))
    )


@router.callback_query(F.data == 'del_d')
async def func(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await del_current_dialogue(id=int(callback.from_user.id))

    dialogue_names = await get_dialogue_names(id=int(callback.from_user.id))

    await callback.message.answer(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('del_d'),
        parse_mode='html'
    )

    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('dialogue'), 
        parse_mode='html', 
        reply_markup=await kb.dialogue(laungage_code=str(callback.from_user.language_code), dialogue_names=dialogue_names)
    )


# @router.callback_query('c_' in F.data)
@router.callback_query(ContainsCallbackData(substring='c_'))
async def func(callback: types.CallbackQuery, state: FSMContext):
    sent_message = await callback.message.edit_text(
        text="Обработка запроса...", 
        parse_mode='html', 
    )

    await set_current_dialog_index(
        id=int(callback.from_user.id), 
        current_dialog_index=int(str(callback.data)[-1])
    )

    previous_message = await state.get_data()
    last_message = previous_message.get('last_message', None)

    if 'state_last_message_image_url' in last_message:
        last_message, image_url = last_message.split('state_last_message_image_url=')
    else:
        image_url = None

    if last_message is not None or image_url is not None:
        data_for_request = first_promt, second_promt, dialogue_model, free_requests = await get_data_for_request(id=int(callback.from_user.id))

        token_count = await count_tokens(
            prompt=str(last_message),
            instructions=f"{first_promt} {second_promt}",
        )

        has_subscription = await user_has_subscription(int(callback.from_user.id))

        if not has_subscription:
            if int(free_requests) == 0:
                await callback.message.edit_text(
                    text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('not_money_not_limit'), 
                    parse_mode='html', 
                    reply_markup=await kb.to_wallet(str(callback.from_user.language_code))
                )

            elif int(free_requests) != 0 and dialogue_model != 'gpt-4o-mini':
                await callback.message.edit_text(
                    text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts)
                        .get('not_money')
                        .format(free_requests), 
                    parse_mode='html', 
                    reply_markup=await kb.to_wallet(str(callback.from_user.language_code))
                )

            elif int(free_requests) != 0 and dialogue_model == 'gpt-4o-mini':
                

                response = await fetch_chatgpt_response(
                    id=int(callback.from_user.id),
                    model=str(dialogue_model),
                    prompt=str(last_message),
                    instructions='',
                    image_url=image_url

                )

                await callback.message.answer(
                    text=f"{response}",
                    parse_mode='Markdown', 
                )

                await decrement_free_requests(id=int(callback.from_user.id))

                # await callback.message.answer(
                #     text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts)
                #         .get('not_money')
                #         .format(int(free_requests) - 1), 
                #     parse_mode='html', 
                #     reply_markup=await kb.to_wallet(str(callback.from_user.language_code))
                # )

                await add_message_to_history(
                    id=str(callback.from_user.id),
                    new_message=last_message,
                    sender=str(callback.from_user.first_name)
                )
                await add_message_to_history(
                    id=str(callback.from_user.id),
                    new_message=response,
                    sender=dialogue_model
                )

        else:
            try:

                response = await fetch_chatgpt_response(
                    id=int(callback.from_user.id),
                    model=str(dialogue_model),
                    prompt=str(last_message),
                    instructions=f"{first_promt} {second_promt}",
                    image_url=image_url
                )

                await callback.message.answer(
                    text=f"{response}", 
                    parse_mode='Markdown', 
                )

                await add_message_to_history(
                    id=str(callback.from_user.id),
                    new_message=last_message,
                    sender=str(callback.from_user.first_name)
                )
                await add_message_to_history(
                    id=str(callback.from_user.id),
                    new_message=response,
                    sender=dialogue_model
                )

            except Exception as ex:
                print(f'Ошибка в обработке запроса к OpenAI, {ex}')

    await sent_message.delete()
    


# @router.callback_query('d_' in F.data)
@router.callback_query(ContainsCallbackData(substring='d_'))
async def func(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.chat)

    await set_current_dialog_index(
        id=int(callback.from_user.id), 
        current_dialog_index=int(str(callback.data)[-1])
    )

    dialogue_model, dialog_title = await get_dialog_data_by_index(
        id=int(callback.from_user.id), 
        dialog_index=int(str(callback.data)[-1])
    )

    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts)
            .get('inner_dialogue')
            .format(dialog_title), 
        parse_mode='html', 
        reply_markup= await kb.inner_dialogue(laungage_code=str(callback.from_user.language_code))
    )


@router.message(States.chat)
# @router.message(States.chat, content_types=[types.ContentType.TEXT, types.ContentType.DOCUMENT])
async def func(message: types.Message, state: FSMContext):
    sent_message = await message.answer(
        text="Обработка запроса...", 
        parse_mode='html', 
    )

    text = message.caption if message.caption else message.text if message.text else ""
    
    if message.document:
        document = message.document
        if document.mime_type in ['text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            file_info = await message.bot.get_file(document.file_id)
            downloaded_file = await message.bot.download_file(file_info.file_path)

            file_path = document.file_name
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())

            if document.mime_type == 'text/plain':
                file_text = await extract_text_from_txt(file_path)
            elif document.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                file_text = await extract_text_from_docx(file_path)
            os.remove(file_path)

            text = f"{text}\n\n{file_text}" if text else file_text
        else:
            await message.answer("Поддерживаются только файлы .txt и .docx")
            return
        
    elif message.voice:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        voice_url = f'https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}'
        text = await transcribe_voice_to_text(file_url=voice_url)

    if message.photo:
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        image_url = f'https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}'
    else:
        image_url = None

    data_for_request = first_promt, second_promt, dialogue_model, free_requests = await get_data_for_request(id=int(message.from_user.id))

    has_subscription = await user_has_subscription(int(message.from_user.id))
    if not has_subscription:
        if int(free_requests) == 0:
            await message.answer(
                text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('not_money_not_limit'), 
                parse_mode='html', 
                reply_markup=await kb.to_wallet(str(message.from_user.language_code))
            )

        elif int(free_requests) != 0 and dialogue_model != 'gpt-4o-mini':
            await message.answer(
                text=answer_texts.get(str(message.from_user.language_code), default_answer_texts)
                    .get('not_money')
                    .format(free_requests), 
                parse_mode='html', 
                reply_markup=await kb.to_wallet(str(message.from_user.language_code))
            )

        elif int(free_requests) != 0 and dialogue_model == 'gpt-4o-mini':
            
            response = await fetch_chatgpt_response(
                id=int(message.from_user.id),
                model=str(dialogue_model),
                prompt=str(text),
                instructions='',
                image_url=image_url

            )

            await message.answer(
                text=f"{response}",
                parse_mode='Markdown', 
            )
            await decrement_free_requests(id=int(message.from_user.id))

            # await message.answer(
            #     text=answer_texts.get(str(message.from_user.language_code), default_answer_texts)
            #         .get('not_money')
            #         .format(int(free_requests) - 1), 
            #     parse_mode='html', 
            #     reply_markup=await kb.to_wallet(str(message.from_user.language_code))

            # )

            await add_message_to_history(
                id=str(message.from_user.id),
                new_message=str(message.text),
                sender=str(message.from_user.first_name)
            )
            await add_message_to_history(
                id=str(message.from_user.id),
                new_message=response,
                sender=dialogue_model
            )

    else:
        try:
            response = await fetch_chatgpt_response(
                id=int(message.from_user.id),
                model=str(dialogue_model),
                prompt=str(text),
                instructions=f"{first_promt} {second_promt}",
                image_url=image_url
            )

            await message.answer(
                text=f"{response}", 
                parse_mode='Markdown', 
            )

            await add_message_to_history(
                id=str(message.from_user.id),
                new_message=str(text),
                sender=str(message.from_user.first_name)
            )
            await add_message_to_history(
                id=str(message.from_user.id),
                new_message=response,
                sender=dialogue_model
            )

        except Exception as ex:
            print(f'Ошибка в обработке запроса к OpenAI, {ex}')

    await sent_message.delete()
    


@router.callback_query(F.data == 'more')
@router.callback_query(F.data == 'to_more')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('more'), 
        parse_mode='html', 
        reply_markup=await kb.more(str(callback.from_user.language_code))
    )


@router.callback_query(F.data == 'info')
@router.callback_query(F.data == 'to_info')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('info'), 
        parse_mode='html', 
        reply_markup=await kb.info(str(callback.from_user.language_code))
    )


@router.callback_query(F.data == 'feedback')
async def func(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.feedback)
    await callback.message.answer(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('feedback_1'), 
        parse_mode='html', 
    )
    await callback.answer()


@router.message(States.feedback)
async def func(message: types.Message, state: FSMContext):
    await state.clear()
    # for admin_id in config.ADMIN_CHAT_IDS:
    #     try:
    #         await message.forward(chat_id=int(admin_id))
    #     except Exception as e:
    #         print(f"Failed to forward message to admin {admin_id}: {e}")
    await send_feedback_via_email(feedback=str(message.text), user_id=int(message.from_user.id))
    await message.answer(
        text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('feedback_2'), 
        parse_mode='html', 
    )


@router.callback_query(F.data == 'token')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('token'), 
        parse_mode='html',
        reply_markup=await kb.to_info(str(callback.from_user.language_code)) 
    )
    await callback.answer()


@router.callback_query(F.data == 'settings_ai')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('settings_ai'), 
        parse_mode='html', 
        reply_markup=await kb.to_info(str(callback.from_user.language_code))
    )
    await callback.answer()


@router.callback_query(F.data == 'usage_ai')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('usage_ai'), 
        parse_mode='html', 
        reply_markup=await kb.to_info(str(callback.from_user.language_code))
    )
    await callback.answer()


@router.callback_query(F.data == 'actual_ai')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('actual_ai'), 
        parse_mode='html', 
        reply_markup=await kb.to_info(str(callback.from_user.language_code))
    )
    await callback.answer()


@router.callback_query(F.data == 'bot_benefit')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('bot_benefit'), 
        parse_mode='html', 
        reply_markup=await kb.to_info(str(callback.from_user.language_code))
    )
    await callback.answer()


@router.callback_query(F.data == 'referral')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(
            str(callback.from_user.language_code), default_answer_texts)
                .get('referral')
                .format(
                    *await get_referral_data(id=int(callback.from_user.id)
                )
        ), 
        parse_mode='Markdown', 
        reply_markup=await kb.referral(str(callback.from_user.language_code))
    )


@router.callback_query(F.data == 'settings')
@router.callback_query(F.data == 'to_settings')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('settings'), 
        parse_mode='html', 
        reply_markup=await kb.settings(str(callback.from_user.language_code))
    )


@router.callback_query(F.data == 'to_main')
async def func(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('main'), 
        parse_mode='html',
        reply_markup=await kb.main(str(callback.from_user.language_code))
    )


@router.callback_query(F.data == 'first_promt')
async def func(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.first_promt)
    
    await callback.message.answer(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('first_promt'), 
        parse_mode='html',
    )
    await callback.answer()


@router.message(States.first_promt)
async def func(message: types.Message, state: FSMContext):
    await set_first_promt(id=int(message.from_user.id), first_promt=str(message.text))
    await state.clear()
    await message.answer(
        text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('first_promt_ok'), 
        parse_mode='html',
    )


@router.callback_query(F.data == 'second_promt')
async def func(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.second_promt)
    
    await callback.message.answer(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('second_promt'), 
        parse_mode='html',
    )
    await callback.answer()


@router.message(States.second_promt)
async def func(message: types.Message, state: FSMContext):
    await set_second_promt(id=int(message.from_user.id), second_promt=str(message.text))
    await state.clear()
    await message.answer(
        text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('second_promt_ok'), 
        parse_mode='html',
    )


@router.callback_query(F.data == 'see_promts')
async def func(callback: types.CallbackQuery):
    
    await callback.message.edit_text(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts)
            .get('see_promts')
            .format(*await get_promts(id=int(callback.from_user.id))
        ),
        reply_markup=await kb.see_promts(str(callback.from_user.language_code)),
        parse_mode='html'
    )
    await callback.answer()


@router.callback_query(F.data == 'set_default_promt')
async def func(callback: types.CallbackQuery):
    await set_default_promts(id=int(callback.from_user.id))
    await callback.message.answer(
        text=answer_texts.get(str(callback.from_user.language_code), default_answer_texts).get('set_default_promt'),
        parse_mode='html',
    )
    await callback.answer()


@router.message()
async def func(message: types.Message, state: FSMContext):
    sent_message = await message.answer(
        text="Обработка...", 
        parse_mode='html', 
    )
    await state.clear()

    dialogue_names = await get_dialogue_names(id=int(message.from_user.id))

    text = message.caption if message.caption else message.text if message.text else ""
    
    if message.document:
        document = message.document
        if document.mime_type in ['text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            file_info = await message.bot.get_file(document.file_id)
            downloaded_file = await message.bot.download_file(file_info.file_path)

            file_path = document.file_name
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())

            if document.mime_type == 'text/plain':
                file_text = await extract_text_from_txt(file_path)
            elif document.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                file_text = await extract_text_from_docx(file_path)
            os.remove(file_path)

            text = f"{text}\n\n{file_text}" if text else file_text
        else:
            await message.answer("Поддерживаются только файлы .txt и .docx")
            return
        
    elif message.voice:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        voice_url = f'https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}'
        text = await transcribe_voice_to_text(file_url=voice_url)

    if message.photo:
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        image_url = f'https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}'
        text += f"state_last_message_image_url={image_url}"

    await state.update_data(last_message=text)

    await message.answer(
        text=answer_texts.get(str(message.from_user.language_code), default_answer_texts).get('continue'), 
        parse_mode='html', 
        reply_markup=await kb.dialogue(laungage_code=str(message.from_user.language_code), dialogue_names=dialogue_names, need_continue=True)
    )

    await sent_message.delete()

    