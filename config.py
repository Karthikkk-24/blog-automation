import os
from dotenv import load_dotenv

load_dotenv()

_REQUIRED_KEYS = [
    "GEMINI_API_KEY",
    "HF_TOKEN",
    "MEDIUM_TOKEN",
    "MEDIUM_AUTHOR_ID",
    "IMGBB_API_KEY",
]


def validate_config():
    missing = [k for k in _REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in all values."
        )


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
MEDIUM_TOKEN = os.getenv("MEDIUM_TOKEN", "")
MEDIUM_AUTHOR_ID = os.getenv("MEDIUM_AUTHOR_ID", "")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")

GEMINI_MODEL_PRIMARY = "gemini-2.5-flash"
GEMINI_MODEL_FALLBACK = "gemini-1.5-flash"

HF_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
HF_INFERENCE_URL = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"

MEDIUM_API_BASE = "https://api.medium.com/v1"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

OUTPUT_DIR = "output"
PREVIEW_PORT = 5050
