import os
import re
from datetime import date
import requests
from config import MEDIUM_TOKEN, MEDIUM_AUTHOR_ID, MEDIUM_API_BASE, OUTPUT_DIR


def _blog_to_html(blog: dict, image_urls: list) -> str:
    parts = []

    parts.append(f"<h1>{blog['title']}</h1>")

    intro = blog.get("intro", "")
    for para in intro.split("\n\n"):
        para = para.strip()
        if para:
            parts.append(f"<p>{para}</p>")

    sections = blog.get("sections", [])
    for i, sec in enumerate(sections):
        heading = sec.get("heading", "")
        content = sec.get("content", "")
        url = image_urls[i] if i < len(image_urls) else None

        parts.append(f"<h2>{heading}</h2>")

        if url:
            parts.append(
                f'<figure>'
                f'<img src="{url}" alt="{heading}">'
                f"</figure>"
            )

        for para in content.split("\n\n"):
            para = para.strip()
            if para:
                parts.append(f"<p>{para}</p>")

    parts.append("<h2>Conclusion</h2>")
    conclusion = blog.get("conclusion", "")
    for para in conclusion.split("\n\n"):
        para = para.strip()
        if para:
            parts.append(f"<p>{para}</p>")

    return "\n".join(parts)


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


def publish_to_medium(blog: dict, image_urls: list, draft: bool = False) -> str:
    html_content = _blog_to_html(blog, image_urls)
    publish_status = "draft" if draft else "public"

    tags = blog.get("tags", [])[:5]

    payload = {
        "title": blog["title"],
        "contentFormat": "html",
        "content": html_content,
        "tags": tags,
        "publishStatus": publish_status,
    }

    headers = {
        "Authorization": f"Bearer {MEDIUM_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    url = f"{MEDIUM_API_BASE}/users/{MEDIUM_AUTHOR_ID}/posts"

    print(f"  Publishing to Medium as '{publish_status}'...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network error while publishing to Medium: {exc}")

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Medium API error {response.status_code}: {response.text[:400]}"
        )

    data = response.json()
    post_url = data.get("data", {}).get("url", "(URL not returned by API)")

    _save_backup(blog)

    return post_url
