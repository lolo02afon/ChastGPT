import openai
import asyncio
import config
import requests
import assemblyai as aai
from data.database.query import get_messages_with_assistant


openai.api_key = config.OPAENAI_TOKEN
aai.settings.api_key = config.AAI_TOKEN


async def fetch_chatgpt_response(
        id: int,
        model: str, 
        prompt: str, 
        instructions: str, 
        max_tokens: int = config.MAX_OUTPUT_TOKENS, 
        image_url: str = None) -> str:
    try:

        messages = await get_messages_with_assistant(id=id, prompt=prompt, instructions=instructions, image_url=image_url)
        
        request_params = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens
        }

        response = await openai.ChatCompletion.acreate(**request_params)

        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Ошибка при получении ответа от OpenAI: {e if config.DEBUG else ''}"


async def fetch_dalle_response(prompt: str, num_images: int = 1) -> str:
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=num_images,
            size="1024x1024",
            response_format="url"
        )
        
        return response['data'][0]['url']
    except Exception as e:
        return f"Ошибка при получении ответа от OpenAI {e if config.DEBUG else ''}"
                                                        

async def create_invoice(amount: int) -> str:
    url = "https://api.cryptocloud.plus/v2/invoice/create"
    headers = {
        "Authorization": f"Token {config.CRYPTOCLOUD_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "amount": amount,
        "shop_id": f"{config.CRYPTOCLOUD_SHOP_ID}",
        "currency": "USD"
    }

    response = requests.post(url, headers=headers, json=data)
    response = response.json()
    uuid = response['result']['uuid']

    return response['result']['link']


async def transcribe_voice_to_text(file_url: str) -> str:
    config = aai.TranscriptionConfig(language_code="ru")

    transcriber = aai.Transcriber()

    transcript = await asyncio.to_thread(transcriber.transcribe, file_url, config=config)

    if transcript.status == aai.TranscriptStatus.error:
        ...

    else:
        return str(transcript.text)
    

if __name__ == "__main__":
    asyncio.run(
        fetch_chatgpt_response(
            model='gpt-4o-mini',
            instructions='Ответь как можно лучше на этот вопрос',
            prompt='Ты знаешь Python?'
        )
    )