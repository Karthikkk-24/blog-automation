import json
import re
import requests
import google.generativeai as genai
from config import (
    GEMINI_API_KEY, GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACK,
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET,
    LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN, LINKEDIN_UGC_URL,
)

genai.configure(api_key=GEMINI_API_KEY)


def _generate_social_content(blog: dict, blog_url: str) -> dict:
    title = blog.get("title", "")
    intro_snippet = blog.get("intro", "")[:200]
    tags = blog.get("tags", [])

    prompt = f"""You are a social media expert helping promote a blog post.

Blog title : "{title}"
Blog intro : {intro_snippet}...
Tags       : {', '.join(tags)}

Generate two social media posts:

1. TWEET (max 240 chars — URL will be appended separately):
   - Open with a hook: surprising stat, bold question, or counterintuitive statement
   - Make someone STOP scrolling and want to click
   - Include 1-2 relevant hashtags
   - Never start with "Just published", "New blog", or "Excited to share"

2. LINKEDIN_POST (120-180 words):
   - Open with a sharp insight or question — no fluff opener
   - 3-4 short paragraphs, each punchy and valuable on its own
   - End with "Read the full post:" (URL appended automatically)
   - 3-5 relevant hashtags on the last line
   - Tone: warm professional — smart but not stiff

Return ONLY raw JSON, no markdown fences:
{{
  "tweet": "...",
  "linkedin_post": "..."
}}"""

    for model_name in [GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACK]:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,
                    max_output_tokens=1024,
                ),
            )
            raw = response.text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            return json.loads(raw)
        except Exception as exc:
            print(f"  Warning: social content generation failed ({model_name}): {exc}")
            continue

    return {
        "tweet": f"Have you thought about this? → {title}",
        "linkedin_post": f"{title}\n\nRead the full post:",
    }


def _review_in_terminal(platform: str, content: str) -> bool:
    width = 54
    print(f"\n  ┌─── {platform} Preview {'─' * max(0, width - len(platform) - 10)}┐")
    for line in content.split("\n"):
        while len(line) > width:
            print(f"  │  {line[:width]}")
            line = line[width:]
        print(f"  │  {line}")
    print(f"  └{'─' * (width + 4)}┘\n")

    while True:
        try:
            choice = input(f"  Post to {platform}?  [Y] Yes   [N] Skip: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            return False
        if choice == "Y":
            return True
        if choice == "N":
            return False
        print("  Please type Y or N.")


def post_to_twitter(tweet_text: str, blog_url: str) -> str:
    try:
        import tweepy
    except ImportError:
        raise RuntimeError("tweepy is not installed. Run: pip install tweepy>=4.14.0")

    full_tweet = f"{tweet_text}\n\n{blog_url}"
    if len(full_tweet) > 280:
        allowed = 280 - len(blog_url) - 3
        tweet_text = tweet_text[:allowed].rstrip() + "…"
        full_tweet = f"{tweet_text}\n\n{blog_url}"

    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
    )
    try:
        response = client.create_tweet(text=full_tweet)
        tweet_id = response.data["id"]
        return f"https://twitter.com/i/web/status/{tweet_id}"
    except Exception as exc:
        raise RuntimeError(f"Twitter API error: {exc}")


def post_to_linkedin(post_text: str, blog_url: str, blog_title: str) -> str:
    full_post = f"{post_text}\n\n{blog_url}"

    payload = {
        "author": f"urn:li:person:{LINKEDIN_PERSON_URN}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": full_post},
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "originalUrl": blog_url,
                        "title": {"text": blog_title},
                    }
                ],
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        response = requests.post(LINKEDIN_UGC_URL, json=payload, headers=headers, timeout=30)
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network error posting to LinkedIn: {exc}")

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"LinkedIn API error {response.status_code}: {response.text[:400]}"
        )

    post_id = response.headers.get("x-restli-id", "")
    return f"https://www.linkedin.com/feed/ (post ID: {post_id})" if post_id else "https://www.linkedin.com/feed/"


def run_social_sharing(blog: dict, published_urls: dict, platforms: dict) -> None:
    share_config = platforms.get("share_on", {})

    if not any(share_config.values()):
        return

    primary_url = next(
        (url for url in published_urls.values() if url and not url.startswith("(")),
        None,
    )
    if not primary_url:
        print("  ⚠️  No valid blog URL for social sharing — skipping.")
        return

    print("\n━━━ [6] Generating social media posts with Gemini ...")
    social = _generate_social_content(blog, primary_url)
    print("  Social posts ready for review.\n")

    if share_config.get("twitter"):
        print("  ── Twitter ──────────────────────────────────────────")
        tweet = social.get("tweet", "")
        preview = f"{tweet}\n\n{primary_url}"
        if _review_in_terminal("Twitter", preview):
            try:
                url = post_to_twitter(tweet, primary_url)
                print(f"  ✅  Tweet posted! → {url}")
            except Exception as exc:
                print(f"  ❌  Tweet failed: {exc}")
        else:
            print("  Skipped Twitter.")

    if share_config.get("linkedin"):
        print("\n  ── LinkedIn ─────────────────────────────────────────")
        li_post = social.get("linkedin_post", "")
        preview = f"{li_post}\n\nRead the full post: {primary_url}"
        if _review_in_terminal("LinkedIn", preview):
            try:
                url = post_to_linkedin(li_post, primary_url, blog.get("title", ""))
                print(f"  ✅  LinkedIn post shared! → {url}")
            except Exception as exc:
                print(f"  ❌  LinkedIn post failed: {exc}")
        else:
            print("  Skipped LinkedIn.")
