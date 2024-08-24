from dotenv import load_dotenv
import os
import pytz

load_dotenv()

DEBUG = os.getenv('DEBUG') == 'True'

TIME_ZONE = pytz.timezone('Europe/Moscow')

BOT_TOKEN = os.getenv('BOT_TOKEN')

OPAENAI_TOKEN = os.getenv('OPAENAI_TOKEN')

YOUKASSA_TEST_TOKEN = os.getenv('YOUKASSA_TEST_TOKEN')

YOUKASSA_TOKEN = os.getenv('YOUKASSA_TOKEN')

CRYPTOCLOUD_TOKEN = os.getenv('CRYPTOCLOUD_TOKEN')

CRYPTOCLOUD_SHOP_ID = os.getenv('CRYPTOCLOUD_SHOP_ID')

EMAIL_SENDER = os.getenv('EMAIL_SENDER')

EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

EMAIL_RECEIVERS = os.getenv('EMAIL_RECEIVERS')

AAI_TOKEN = os.getenv('AAI_TOKEN')

MAX_OUTPUT_TOKENS = 2048

PRICE_MULTIPLIER = 5

DEFAULT_LAUNGAGE = 'ru'

OPENAI_MODEL = {
    'gpt-4o': {
        'Context window': '128,000 tokens',
        'Max output tokens': '4,096 tokens',
        'input': '0.000005',
        'output': '0.000015'
    },
    'gpt-4o-mini': {
        'Context window': '128,000 tokens',
        'Max output tokens': '16,384 tokens',
        'input': f'{0.15 / 1_000_000}',
        'output': f'{0.6 / 1_000_000}'
    },
    'dall-e-3': {
        'Standard': {
            '1024×1024': '0.040',
            '1024×1792': '0.080',
            '1792×1024': '0.080'
        },
        'HD': {
            '1024×1024': '0.080',
            '1024×1792': '0.120',
            '1792×1024': '0.120'
        }
    }
}

ADMIN_CHAT_IDS=[
    '5243937469',
    '978640309'
]

DEFAULT_VALUES = {
    'first_promt': """Инструкции по ответу не заданы
""",
    'second_promt': """Описание желаемого ответа не задано
"""
}

# DEFAULT_VALUES = {
#     'first_promt': """Follow in the strict order:

# 1. USE the language of my message.
# 2. **ONCE PER CHAT** assign a real-world expert role to yourself before answering, e.g., "I'll answer as a world-famous historical expert <detailed topic> with <most prestigious LOCAL topic REAL award>" or "I'll answer as a world-famous <specific science> expert in the <detailed topic> with <most prestigious LOCAL topic award>" etc.
# 3. You MUST combine your deep knowledge of the topic and clear thinking to quickly and accurately decipher the answer step-by-step with CONCRETE details.
# 4. I'm going to tip $1,000,000 for the best reply. 
# 5. Your answer is critical for my career.
# 6. Answer the question in a natural, human-like manner.
# 7. ALWAYS use an answering example for a first message structure.

# ##Answering in English example##

# I'll answer as the world-famous <specific field> scientists with <most prestigious LOCAL award>

# <Deep knowledge step-by-step answer, with CONCRETE details>""",
#     'second_promt': """You MUST follow the instructions for answering:

# - ALWAYS answer in the language of my message.
# - Read the entire convo history line by line before answering.
# - I have no fingers and the placeholders trauma. Return the entire code template for an answer when needed. NEVER use placeholders.
# - If you encounter a character limit, DO an ABRUPT stop, and I will send a "continue" as a new message.
# - You ALWAYS will be PENALIZED for wrong and low-effort answers. 
# - ALWAYS follow "Answering rules."
# """
# }

