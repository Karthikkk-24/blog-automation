import os
import re
from datetime import date
import requests
from config import DEVTO_API_KEY, DEVTO_API_URL, OUTPUT_DIR


def _blog_to_markdown(blog: dict, image_urls: list) -> str:
    lines = []

    intro = blog.get("intro", "")
    lines.append(intro)
    lines.append("")

    sections = blog.get("sections", [])
    for i, sec in enumerate(sections):
        heading = sec.get("heading", "")
        content = sec.get("content", "")
        url = image_urls[i] if i < len(image_urls) else None

        lines.append(f"## {heading}")
        lines.append("")

        if url:
            lines.append(f"![{heading}]({url})")
            lines.append("")

        lines.append(content)
        lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    lines.append(blog.get("conclusion", ""))
    lines.append("")

    return "\n".join(lines)


def _blog_to_text(blog: dict) -> str:
    lines = []
    lines.append(blog.get("title", "").upper())
    lines.append("=" * len(blog.get("title", "")))
    lines.append("")
    lines.append(blog.get("intro", ""))
    lines.append("")

    for sec in blog.get("sections", []):
        lines.append(f"--- {sec.get('heading', '')} ---")
        lines.append("")
        lines.append(sec.get("content", ""))
        lines.append("")

    lines.append("--- Conclusion ---")
    lines.append("")
    lines.append(blog.get("conclusion", ""))
    lines.append("")
    lines.append("Tags: " + ", ".join(blog.get("tags", [])))

    return "\n".join(lines)


def _slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:60]


def _clean_devto_tags(tags: list) -> list:
    cleaned = []
    for tag in tags:
        tag = tag.lower()
        tag = re.sub(r"[^a-z0-9]", "", tag)
        if tag and tag not in cleaned:
            cleaned.append(tag)
    return cleaned[:4]


def _save_backup(blog: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().isoformat()
    slug = _slugify(blog.get("title", "blog"))
    filename = os.path.join(OUTPUT_DIR, f"{today}_{slug}.txt")
    text = _blog_to_text(blog)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  Backup saved → {filename}")
    return filename


def publish_to_devto(blog: dict, image_urls: list, draft: bool = False) -> str:
    body_markdown = _blog_to_markdown(blog, image_urls)
    tags = _clean_devto_tags(blog.get("tags", []))

    payload = {
        "article": {
            "title": blog["title"],
            "body_markdown": body_markdown,
            "published": not draft,
            "tags": tags,
        }
    }

    headers = {
        "api-key": DEVTO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/vnd.forem.api-v1+json",
    }

    status_label = "draft" if draft else "public"
    print(f"  Publishing to Dev.to as '{status_label}'...")
    try:
        response = requests.post(DEVTO_API_URL, json=payload, headers=headers, timeout=30)
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network error while publishing to Dev.to: {exc}")

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Dev.to API error {response.status_code}: {response.text[:400]}"
        )

    data = response.json()
    post_url = data.get("url", "(URL not returned by API)")

    _save_backup(blog)

    return post_url
