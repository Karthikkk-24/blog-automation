import json
import os
from dotenv import load_dotenv

load_dotenv()

PLATFORMS_FILE = "platforms.json"

_ALWAYS_REQUIRED = ["GEMINI_API_KEY", "HF_TOKEN", "IMGBB_API_KEY"]

_PLATFORM_KEYS = {
    "publish_to": {
        "devto":   ["DEVTO_API_KEY"],
        "medium":  ["MEDIUM_TOKEN", "MEDIUM_AUTHOR_ID"],
    },
    "share_on": {
        "twitter":  ["TWITTER_API_KEY", "TWITTER_API_SECRET",
                     "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"],
        "linkedin": ["LINKEDIN_ACCESS_TOKEN", "LINKEDIN_PERSON_URN"],
    },
}


def load_platforms() -> dict:
    defaults = {
        "publish_to": {"devto": True, "medium": False},
        "share_on":   {"twitter": False, "linkedin": False},
    }
    try:
        with open(PLATFORMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  Warning: {PLATFORMS_FILE} not found — using defaults (Dev.to only).")
        return defaults
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {PLATFORMS_FILE}: {exc}")


def validate_config():
    platforms = load_platforms()
    required = list(_ALWAYS_REQUIRED)

    for section, platform_map in _PLATFORM_KEYS.items():
        for platform, keys in platform_map.items():
            if platforms.get(section, {}).get(platform):
                required.extend(keys)

    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(missing)}\n"
            "Check your .env file and ensure all keys for enabled platforms are set.\n"
            f"Enabled platforms are controlled by {PLATFORMS_FILE}."
        )


# ── Core keys ────────────────────────────────────────────────────────────────
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
HF_TOKEN        = os.getenv("HF_TOKEN", "")
IMGBB_API_KEY   = os.getenv("IMGBB_API_KEY", "")

# ── Publishing platforms ──────────────────────────────────────────────────────
DEVTO_API_KEY    = os.getenv("DEVTO_API_KEY", "")
MEDIUM_TOKEN     = os.getenv("MEDIUM_TOKEN", "")
MEDIUM_AUTHOR_ID = os.getenv("MEDIUM_AUTHOR_ID", "")

# ── Social platforms ──────────────────────────────────────────────────────────
TWITTER_API_KEY             = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET          = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN        = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
LINKEDIN_ACCESS_TOKEN       = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_PERSON_URN         = os.getenv("LINKEDIN_PERSON_URN", "")

# ── Model / API constants ─────────────────────────────────────────────────────
GEMINI_MODEL_PRIMARY = "gemini-2.5-flash"
GEMINI_MODEL_FALLBACK = "gemini-1.5-flash"

HF_IMAGE_MODEL   = "black-forest-labs/FLUX.1-schnell"
HF_INFERENCE_URL = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"

DEVTO_API_URL    = "https://dev.to/api/articles"
MEDIUM_API_BASE  = "https://api.medium.com/v1"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"
LINKEDIN_UGC_URL = "https://api.linkedin.com/v2/ugcPosts"

OUTPUT_DIR   = "output"
PREVIEW_PORT = 5050
