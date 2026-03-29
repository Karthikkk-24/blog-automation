import base64
import os
import time
import requests
from config import HF_TOKEN, IMGBB_API_KEY, HF_INFERENCE_URL, IMGBB_UPLOAD_URL, OUTPUT_DIR

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
RETRY_WAIT = 5
BETWEEN_CALLS = 3


def _generate_image_bytes(prompt: str, attempt: int = 1) -> bytes | None:
    try:
        response = requests.post(
            HF_INFERENCE_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=120,
        )
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type or len(response.content) > 1000:
                return response.content
            print(f"    HF returned non-image content: {response.text[:200]}")
            return None
        if response.status_code == 503 and attempt == 1:
            print(f"    HF model loading (503), waiting {RETRY_WAIT}s and retrying...")
            time.sleep(RETRY_WAIT)
            return _generate_image_bytes(prompt, attempt=2)
        print(f"    HF API error {response.status_code}: {response.text[:200]}")
        return None
    except requests.exceptions.Timeout:
        print("    HF request timed out.")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"    HF request failed: {exc}")
        return None


def _save_image(image_bytes: bytes, index: int) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"section_{index + 1}_image.png")
    with open(path, "wb") as f:
        f.write(image_bytes)
    return path


def _upload_to_imgbb(image_path: str) -> str | None:
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        response = requests.post(
            IMGBB_UPLOAD_URL,
            data={"key": IMGBB_API_KEY, "image": encoded},
            timeout=60,
        )
        if response.status_code == 200:
            data = response.json()
            url = data.get("data", {}).get("url")
            if url:
                return url
        print(f"    imgbb upload error {response.status_code}: {response.text[:200]}")
        return None
    except Exception as exc:
        print(f"    imgbb upload failed: {exc}")
        return None


def generate_and_upload_images(image_prompts: list) -> list:
    urls = []
    total = len(image_prompts)

    for i, prompt in enumerate(image_prompts):
        print(f"  Generating image {i + 1}/{total}...")
        print(f"    Prompt: {prompt[:80]}...")

        image_bytes = _generate_image_bytes(prompt)

        if image_bytes is None:
            print(f"    Image {i + 1} generation failed — will use placeholder.")
            urls.append(None)
            if i < total - 1:
                time.sleep(BETWEEN_CALLS)
            continue

        image_path = _save_image(image_bytes, i)
        print(f"    Saved to {image_path}. Uploading to imgbb...")

        public_url = _upload_to_imgbb(image_path)
        if public_url:
            print(f"    Uploaded: {public_url}")
        else:
            print(f"    imgbb upload failed — image saved locally but no public URL.")

        urls.append(public_url)

        if i < total - 1:
            time.sleep(BETWEEN_CALLS)

    successful = sum(1 for u in urls if u is not None)
    print(f"  Images done: {successful}/{total} uploaded successfully.")
    return urls
