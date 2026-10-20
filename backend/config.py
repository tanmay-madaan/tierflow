import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
MODEL_DIR = BASE_DIR / 'trained_models'
DB_PATH = BASE_DIR / 'database' / 'experiments.db'
BENCHMARK_DIR = BASE_DIR / 'benchmarks'
BENCHMARK_DATA_DIR = BENCHMARK_DIR / 'data'
BENCHMARK_RESULTS_DIR = BENCHMARK_DIR / 'results'

# Load environment variables from .env in backend/ or root workspace
load_dotenv(BASE_DIR / '.env')
load_dotenv(BASE_DIR.parent / '.env')

def get_active_api_key() -> str:
    """Return currently active API key, checking GEMINI_API_KEY, LLM_API_KEY, or OPENAI_API_KEY."""
    # Re-read environment dynamically
    return os.getenv('GEMINI_API_KEY', os.getenv('LLM_API_KEY', os.getenv('OPENAI_API_KEY', ''))).strip()

API_KEY = get_active_api_key()

# Provider Base URL:
# If GEMINI_API_KEY is provided and no custom LLM_BASE_URL is specified, default to
# Google AI Studio's OpenAI-compatible endpoint.
def get_base_url() -> str:
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    custom_url = os.getenv('LLM_BASE_URL', os.getenv('OPENAI_BASE_URL', ''))
    if custom_url:
        return custom_url.rstrip('/')
    if gemini_key:
        return 'https://generativelanguage.googleapis.com/v1beta/openai'
    return 'https://api.openai.com/v1'

LLM_BASE_URL = get_base_url()
LLM_TIMEOUT = float(os.getenv('LLM_TIMEOUT', '30.0'))
LLM_MAX_RETRIES = int(os.getenv('LLM_MAX_RETRIES', '2'))

# Default mode: Demo mode if no API key is provided
DEMO_MODE = not bool(API_KEY)

# Provider detection
IS_GEMINI = "generativelanguage.googleapis.com" in LLM_BASE_URL or bool(os.getenv('GEMINI_API_KEY'))

# Model identifiers per tier (configurable via environment variables)
# Google Gemini defaults:
#   SMALL:  gemini-1.5-flash-8b (ultra-fast, low cost)
#   MEDIUM: gemini-1.5-flash    (balanced reasoning)
#   LARGE:  gemini-1.5-pro      (complex reasoning & analysis)
# OpenAI defaults:
#   SMALL:  gpt-4o-mini
#   MEDIUM: gpt-4o
#   LARGE:  gpt-4-turbo
if IS_GEMINI:
    DEFAULT_SMALL = 'gemini-3.5-flash-lite'
    DEFAULT_MEDIUM = 'gemini-flash-latest'
    DEFAULT_LARGE = 'gemini-3.8-flash'
else:
    DEFAULT_SMALL = 'gpt-4o-mini'
    DEFAULT_MEDIUM = 'gpt-4o'
    DEFAULT_LARGE = 'gpt-4-turbo'

LLM_MODEL_SMALL = os.getenv('LLM_MODEL_SMALL', DEFAULT_SMALL)
LLM_MODEL_MEDIUM = os.getenv('LLM_MODEL_MEDIUM', DEFAULT_MEDIUM)
LLM_MODEL_LARGE = os.getenv('LLM_MODEL_LARGE', DEFAULT_LARGE)

# Model tiers with transparent token pricing
if IS_GEMINI:
    MODEL_TIERS = {
        'SMALL': {
            'name': 'Small LLM (Gemini 3.5 Flash-Lite)',
            'model_id': LLM_MODEL_SMALL,
            'latency_range': (0.1, 0.4),
            'cost_per_token': 0.000000075,
            'input_cost_per_token': 0.0000000375,  # $0.0375 / 1M input
            'output_cost_per_token': 0.000000150,  # $0.15 / 1M output
        },
        'MEDIUM': {
            'name': 'Medium LLM (Gemini Flash Latest)',
            'model_id': LLM_MODEL_MEDIUM,
            'latency_range': (0.3, 0.8),
            'cost_per_token': 0.000000150,
            'input_cost_per_token': 0.000000075,  # $0.075 / 1M input
            'output_cost_per_token': 0.000000300,  # $0.30 / 1M output
        },
        'LARGE': {
            'name': 'Large LLM (Gemini 3.8 Flash)',
            'model_id': LLM_MODEL_LARGE,
            'latency_range': (0.8, 2.5),
            'cost_per_token': 0.000002500,
            'input_cost_per_token': 0.000001250,  # $1.25 / 1M input
            'output_cost_per_token': 0.000005000,  # $5.00 / 1M output
        },
    }
else:
    MODEL_TIERS = {
        'SMALL': {
            'name': 'Small LLM',
            'model_id': LLM_MODEL_SMALL,
            'latency_range': (0.1, 0.3),
            'cost_per_token': 0.00000030,
            'input_cost_per_token': 0.00000015,
            'output_cost_per_token': 0.00000060,
        },
        'MEDIUM': {
            'name': 'Medium LLM',
            'model_id': LLM_MODEL_MEDIUM,
            'latency_range': (0.5, 1.2),
            'cost_per_token': 0.00000500,
            'input_cost_per_token': 0.00000250,
            'output_cost_per_token': 0.00001000,
        },
        'LARGE': {
            'name': 'Large LLM',
            'model_id': LLM_MODEL_LARGE,
            'latency_range': (1.5, 3.5),
            'cost_per_token': 0.00002000,
            'input_cost_per_token': 0.00001000,
            'output_cost_per_token': 0.00003000,
        },
    }

# Router config
CONFIDENCE_THRESHOLD = 0.5
