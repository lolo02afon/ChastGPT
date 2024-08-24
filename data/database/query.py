from data.database.models import async_session
from data.database.models import User
from sqlalchemy import select, update, delete
from config import DEFAULT_VALUES
from app.scripts import delete_and_renumber
from datetime import datetime, timedelta
import json


async def create_user(id: int, firstname: str, lastname: str, referral_user: str) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == id).limit(1))

        if not user:
            session.add(User(
                id=id,
                firstname=firstname,
                lastname=lastname,

                balance=0,
                referral_balance=0,

                first_promt=DEFAULT_VALUES.get('first_promt'),
                second_promt=DEFAULT_VALUES.get('second_promt'),

                referral_user=referral_user
            ))

            await session.commit()


async def get_dialogue_names(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            dialog_titles = str(user.dialog_titles).split(', ')[0:-1]
            dialogue_models = str(user.dialogue_models).split(', ')[0:-1]
            titles = [
                f"{dialog_titles[i]}" for i in range(len(dialog_titles))
            ]
            
            return titles
        

async def user_has_subscription(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            has_subscription = bool(user.has_subscription)
            
            return has_subscription
        

async def get_subscription_end_date(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            date = str(user.subscription_end_date).split('-')
            mouths = {
                '1': 'Января',
                '2': 'Февраля',
                '3': 'Марта',
                '4': 'Апреля',
                '5': 'Мая',
                '6': 'Июня',
                '7': 'Июля',
                '8': 'Августа',
                '9': 'Сентября',
                '10': 'Октября',
                '11': 'Ноября',
                '12': 'Декабря',
            }
            if date[1] != '10':
                mouth = mouths[date[1].replace('0', '')]
            else:
                mouth = mouths[date[1]]

            subscription_end_date = f"{date[2]} {mouth} {date[0]}"
            return subscription_end_date
        

async def activate_subscription(id: int, is_monthly: bool) -> tuple[str]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            now = datetime.now()

            # Рассчитываем дату окончания подписки
            if is_monthly:
                end_date = now + timedelta(days=30)
            else:
                end_date = now + timedelta(days=365)
            

            await session.execute(update(User).where(User.id == id).values(
                has_subscription=True,
                subscription_end_date=end_date.strftime('%Y-%m-%d')
            ))

            await session.commit()


async def get_balance(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            balance = str(user.balance)
            return balance
        

async def get_last_invoice(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            last_invoice = str(user.last_invoice)
            return last_invoice


async def set_last_invoice(id: int, last_invoice: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            await session.execute(update(User).where(User.id == id).values(
                last_invoice=last_invoice,
            ))

            await session.commit()


async def get_referral_balance(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            referral_balance = str(user.referral_balance)
            return referral_balance
        

async def get_referral_user(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            referral_user = int(user.referral_user)
            return referral_user
        

async def referral_replenishment(id: int, price: float) -> tuple[str]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            referral_balance = float(user.referral_balance) + price
            balance = float(user.balance) + price
            
            await session.execute(update(User).where(User.id == id).values(
                balance=balance,
                referral_balance=referral_balance
            ))

            await session.commit()
        

async def is_ther_a_user(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            return True
        return False



async def set_balance(id: int, balance: str) -> tuple[str]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            await session.execute(update(User).where(User.id == id).values(
                balance=balance,
            ))

            await session.commit()
        

async def create_new_chat(id: int) -> tuple[str]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            dialog_titles = str(user.dialog_titles)
            dialog_titles += f"Диалог {int(len(dialog_titles.split(', ')[0:-1])) + 1}, "
            dialogue_models = str(user.dialogue_models) + 'gpt-4o, '
            new_dialog_index = len(dialog_titles.split(', ')[0:-1]) - 1

            await session.execute(update(User).where(User.id == id).values(
                dialog_titles=dialog_titles,
                dialogue_models=dialogue_models
            ))
            await session.commit()

            return dialogue_models.split(', ')[-2], dialog_titles.split(', ')[-2], new_dialog_index


async def add_message_to_history(id: int, new_message: str, sender: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            history = json.loads(user.message_history or "{}")
            current_dialog_index = str(user.current_dialog_index)

            if str(current_dialog_index) not in history:
                history[str(current_dialog_index)] = []

            history[str(current_dialog_index)].append({
                "sender": sender,
                "message": new_message
            })
            # if len(history[str(current_dialog_index)]) > 10:
            #     history[str(current_dialog_index)] = history[str(current_dialog_index)][2:]
            
            history = json.dumps(history, ensure_ascii=False)

            await session.execute(update(User).where(User.id == id).values(
                message_history=history
            ))
            await session.commit()


async def get_dialogue_history(id: int, need_parse: bool = True) -> str | tuple[str]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            message_history = json.loads(user.message_history or "{}")
            current_dialog_index = str(user.current_dialog_index)
            
            if need_parse:
                if str(current_dialog_index) not in message_history:
                    return None

                message_history = message_history[str(current_dialog_index)]
                history = ''
                for message in message_history:
                    history += f"- {message.get('sender')}\n➖➖➖➖➖➖➖➖➖➖➖\n{message.get('message')}\n\n\n"

                if len(history) > 4000:
                    return history[len(history) - 4000::]
                return history
            else:
                return message_history, current_dialog_index


async def increment_referral_count(id: int) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            referral_count = int(user.referral_count) + 1

            await session.execute(update(User).where(User.id == id).values(
                referral_count=referral_count
            ))
            await session.commit()


async def decrement_free_requests(id: int) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            free_requests = int(user.free_requests) - 1

            await session.execute(update(User).where(User.id == id).values(
                free_requests=free_requests
            ))
            await session.commit()


async def get_referral_data(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            referral_balance = str(user.referral_balance)
            referral_count = str(user.referral_count)
            referral_link = rf'https://t.me/chastgpt_bot?start={id}'

            return referral_count, referral_balance, referral_link
        

async def get_promts(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            first_promt = str(user.first_promt)
            second_promt = str(user.second_promt)

            return first_promt, second_promt
        

async def get_data_for_request(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            current_dialog_index = int(user.current_dialog_index)
            free_requests = int(user.free_requests)
            first_promt = str(user.first_promt)
            second_promt = str(user.second_promt)
            dialogue_model = str(user.dialogue_models).split(', ')[0:-1][current_dialog_index]

            return first_promt, second_promt, dialogue_model, free_requests
        

async def get_current_dialog_index(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            current_dialog_index = int(user.current_dialog_index)

            return current_dialog_index


async def get_dialog_data_by_index(id: int, dialog_index: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()

        if user:
            dialog_title = str(user.dialog_titles).split(', ')[0:-1][dialog_index]
            dialogue_model = str(user.dialogue_models).split(', ')[0:-1][dialog_index]

            return dialogue_model, dialog_title
        

async def set_model(id: int, model: str) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            current_dialog_index = int(user.current_dialog_index)
            dialogue_models = str(user.dialogue_models).split(', ')[0:-1]
            dialogue_models[current_dialog_index] = model
            dialogue_models = ', '.join(dialogue_models) + ', '

            await session.execute(update(User).where(User.id == id).values(
                dialogue_models=dialogue_models 
            ))
            await session.commit()


async def del_current_dialogue(id: int) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            current_dialog_index = int(user.current_dialog_index)
            dialogue_models = str(user.dialogue_models).split(', ')[0:-1]
            dialog_titles = str(user.dialog_titles).split(', ')[0:-1]
            history = json.loads(user.message_history or "{}")

            del dialogue_models[current_dialog_index]
            del dialog_titles[current_dialog_index]
            history = await delete_and_renumber(dialogues=history, n=current_dialog_index)
            history = json.dumps(history, ensure_ascii=False)

            if dialogue_models == [] and dialog_titles == []:
                dialogue_models = ''
                dialog_titles = ''

            else:
                dialogue_models = ', '.join(dialogue_models) + ', '
                dialog_titles = ', '.join(dialog_titles) + ', '

            await session.execute(update(User).where(User.id == id).values(
                dialogue_models=dialogue_models,
                dialog_titles=dialog_titles,
                message_history=history
            ))
            await session.commit()


async def set_first_promt(id: int, first_promt: str) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            await session.execute(update(User).where(User.id == id).values(
                first_promt=first_promt 
            ))
            await session.commit()


async def set_dialog_name(id: int, dialog_name: str) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            current_dialog_index = int(user.current_dialog_index)
            dialog_titles = str(user.dialog_titles).split(', ')[0:-1]
            dialog_titles[current_dialog_index] = dialog_name
            dialog_titles = ', '.join(dialog_titles) + ', '

            await session.execute(update(User).where(User.id == id).values(
                dialog_titles=dialog_titles 
            ))
            await session.commit()


async def set_current_dialog_index(id: int, current_dialog_index: int) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            await session.execute(update(User).where(User.id == id).values(
                current_dialog_index=current_dialog_index 
            ))
            await session.commit()


async def set_second_promt(id: int, second_promt: str) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            await session.execute(update(User).where(User.id == id).values(
                second_promt=second_promt 
            ))
            await session.commit()


async def set_default_promts(id: int) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        
        if user:
            await session.execute(update(User).where(User.id == id).values(
                first_promt=DEFAULT_VALUES.get('first_promt'), 
                second_promt=DEFAULT_VALUES.get('second_promt'),
            ))
            await session.commit()




async def get_messages_with_assistant(id: int, prompt: str, instructions: str, image_url: str | None = None) -> dict | None:
    message_history, current_dialog_index = await get_dialogue_history(id=id, need_parse=False)

    if str(current_dialog_index) not in message_history:
        if image_url is not None:
            messages = [
                {"role": "system", "content": instructions},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ] 
        else:
            messages = [
                {"role": "system", "content": instructions},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                ]}
            ] 
            
        return messages

    message_history = message_history[str(current_dialog_index)]
    messages = [
        {"role": "system", "content": instructions}
    ]

    models = ['gpt-4o', 'gpt-4o-mini', 'dall-e-3']
    first_user_is_added = False
    last_is_user = None

    for message in message_history:
        if first_user_is_added:
            if message.get('sender') in models and last_is_user:
                messages.append({
                    "role": "assistant",
                    "content": message.get('message')
                })
                last_is_user = False

            elif not (message.get('sender') in models) and not last_is_user:
                messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": message.get('message')},]
                })
                last_is_user = True

        else:
            if not (message.get('sender') in models):
                messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": message.get('message')},]
                })

                first_user_is_added = True
                last_is_user = True

    if image_url is not None:
        messages.append({
            "role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        })

    elif image_url is None:
        messages.append({
            "role": "user", "content": [
                {"type": "text", "text": prompt},
            ]
        })

    return messages
