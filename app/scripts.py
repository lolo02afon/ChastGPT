import tiktoken
import asyncio
import config
from docx import Document
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from data.database.query import get_dialogue_history


async def count_tokens(prompt: str, instructions: str) -> int:
    """Мерзость для токенизации текста"""
    # cl100k_base - все остальное
    # o200k_base - gpt-4o

    try:
        tokenizer = tiktoken.get_encoding("o200k_base")  

        prompt_tokens = tokenizer.encode(prompt)
        instructions_tokens = tokenizer.encode(instructions)

        total_tokens = len(prompt_tokens) + len(instructions_tokens) + 3  # Добавляем 3 для учета токенов системы и пользователя

        return total_tokens
    except Exception as e:
        return -1 


async def get_total_price(dialogue_model: str, token_count: int) -> float:
    model_1_input_token_price = float(config.OPENAI_MODEL['gpt-4o-mini']['input'])
    model_1_output_token_price = float(config.OPENAI_MODEL['gpt-4o-mini']['output'])

    model_2_input_token_price = float(config.OPENAI_MODEL['gpt-4o']['input'])
    model_2_output_token_price = float(config.OPENAI_MODEL['gpt-4o']['output'])

    model_3_generate_price = float(config.OPENAI_MODEL['dall-e-3']['Standard']['1024×1024'])

    if dialogue_model == 'gpt-4o-mini':
        total_price = model_1_input_token_price * token_count + model_1_output_token_price * config.MAX_OUTPUT_TOKENS
        
    elif dialogue_model == 'gpt-4o':
        total_price = model_2_input_token_price * token_count + model_2_output_token_price * config.MAX_OUTPUT_TOKENS
        
    elif dialogue_model == 'dall-e-3':
        total_price = model_3_generate_price
    
    else: return

    total_price = total_price * config.PRICE_MULTIPLIER

    return total_price


async def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)


async def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    

async def delete_and_renumber(dialogues, n):
    if str(n) in dialogues:
        del dialogues[str(n)]
    
    renumbered_dialogues = {}
    for i, (key, value) in enumerate(dialogues.items()):
        renumbered_dialogues[str(i)] = value
    
    return renumbered_dialogues


async def send_feedback_via_email(feedback, user_id):
    email_sender = config.EMAIL_SENDER
    email_password = config.EMAIL_PASSWORD
    email_receivers = config.EMAIL_RECEIVERS.split(',')

    subject = f"ChastGPT. Обратная связь от пользователя {user_id}."
    body = feedback

    for email_receiver in email_receivers:
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        async with aiosmtplib.SMTP(hostname="smtp.gmail.com", port=465, use_tls=True) as server:
            await server.login(email_sender, email_password)
            await server.send_message(msg)