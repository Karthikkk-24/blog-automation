#!/usr/bin/env python3
"""
blog-automation — entry point

Usage:
    python main.py "Your Blog Title"
    python main.py "Your Blog Title" --tone simple
    python main.py "Your Blog Title" --words 2000 --draft
    python main.py "Your Blog Title" --no-images
"""

import argparse
import os
import sys


def _parse_args():
    parser = argparse.ArgumentParser(
        prog="blog-automation",
        description="Generate and publish a blog post. Configure platforms in config.json.",
    )
    parser.add_argument("title", help="The blog post title.")
    parser.add_argument(
        "--tone",
        choices=["simple", "storytelling", "casual", "professional", "technical"],
        default="simple",
        help="Writing tone (default: simple — plain English, easy to read).",
    )
    parser.add_argument(
        "--words",
        type=int,
        default=1800,
        help="Target word count (default: 1800).",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Publish as draft on all platforms (not public).",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        dest="no_images",
        help="Skip image generation (much faster).",
    )
    return parser.parse_args()


def _show_config_summary(config: dict):
    publish    = config.get("publish_to", {})
    share      = config.get("share_on", {})
    share_text = config.get("share_text", {})
    preview    = config.get("preview", {})

    def tick(val):
        return "✅" if val else "○ "

    print("  Platforms:")
    print(f"    {tick(publish.get('devto'))}  Dev.to publish")
    print(f"    {tick(publish.get('medium'))}  Medium publish")
    print(f"    {tick(share.get('twitter'))}  Twitter auto-share")
    print(f"    {tick(share.get('linkedin'))}  LinkedIn auto-share")
    print(f"    {tick(share_text.get('enabled', True))}  Share text (clipboard copy)")
    print(f"    Port   : {preview.get('port', 5050)}  |  Auto-open browser: {preview.get('auto_open_browser', False)}")
    print()


def main():
    args = _parse_args()

    print("\n╔══════════════════════════════════════════════════╗")
    print("║           BLOG AUTOMATION — Starting             ║")
    print("╚══════════════════════════════════════════════════╝\n")
    print(f"  Title  : {args.title}")
    print(f"  Tone   : {args.tone}")
    print(f"  Words  : ~{args.words}")
    print(f"  Mode   : {'DRAFT' if args.draft else 'PUBLIC'}")
    print(f"  Images : {'off' if args.no_images else 'on'}")
    print()

    os.makedirs("output", exist_ok=True)

    print("━━━ [1/5] Loading config & validating API keys ...")
    try:
        from config import load_config, validate_config
        config = load_config()
        _show_config_summary(config)
        validate_config()
        print("  All required API keys present.\n")
    except (EnvironmentError, RuntimeError) as exc:
        print(f"\n  ❌  Config error:\n  {exc}\n")
        sys.exit(1)

    publish_config   = config.get("publish_to", {})
    share_config     = config.get("share_on", {})
    share_text_cfg   = config.get("share_text", {})
    preview_cfg      = config.get("preview", {})

    if not any(publish_config.values()):
        print("  ⚠️  No publish platforms are enabled in config.json.")
        print("  Set at least one of devto or medium to true and re-run.\n")
        sys.exit(1)

    print("━━━ [2/5] Generating blog with Gemini ...")
    try:
        from writer import generate_blog
        blog = generate_blog(title=args.title, tone=args.tone, word_count=args.words)
        print()
    except Exception as exc:
        print(f"\n  ❌  Blog generation failed:\n  {exc}\n")
        sys.exit(1)

    if args.no_images:
        print("━━━ [3/5] Image generation skipped (--no-images).\n")
        image_urls = [None] * len(blog.get("sections", []))
    else:
        print("━━━ [3/5] Generating and uploading images ...")
        try:
            from image_gen import generate_and_upload_images
            prompts = [sec["image_prompt"] for sec in blog.get("sections", [])]
            image_urls = generate_and_upload_images(prompts)
            print()
        except Exception as exc:
            print(f"\n  ⚠️  Image generation error: {exc}")
            print("  Continuing without images...\n")
            image_urls = [None] * len(blog.get("sections", []))

    print("━━━ [4/5] Launching preview server ...")
    try:
        from preview import serve_preview
        decision = serve_preview(
            blog,
            image_urls,
            port=preview_cfg.get("port", 5050),
            auto_open_browser=preview_cfg.get("auto_open_browser", False),
        )
    except Exception as exc:
        print(f"\n  ❌  Preview failed:\n  {exc}\n")
        sys.exit(1)

    if decision != "publish":
        print("\n  Aborted — blog was not published.\n")
        sys.exit(0)

    print("\n━━━ [5/5] Publishing ...")
    published_urls = {}

    if publish_config.get("devto"):
        print("\n  ── Dev.to ───────────────────────────────────────────")
        try:
            from publisher import publish_to_devto
            url = publish_to_devto(blog, image_urls, draft=args.draft)
            published_urls["Dev.to"] = url
            label = "draft saved" if args.draft else "published"
            print(f"  ✅  Dev.to {label}!")
            print(f"  🔗  {url}")
        except Exception as exc:
            print(f"  ❌  Dev.to failed: {exc}")

    if publish_config.get("medium"):
        print("\n  ── Medium ───────────────────────────────────────────")
        try:
            from publisher import publish_to_medium
            url = publish_to_medium(blog, image_urls, draft=args.draft)
            published_urls["Medium"] = url
            label = "draft saved" if args.draft else "published"
            print(f"  ✅  Medium {label}!")
            print(f"  🔗  {url}")
        except Exception as exc:
            print(f"  ❌  Medium failed: {exc}")

    needs_social = any(share_config.values()) or share_text_cfg.get("enabled", False)
    if published_urls and needs_social:
        try:
            from social import run_social_sharing
            run_social_sharing(blog, published_urls, config)
        except Exception as exc:
            print(f"\n  ⚠️  Social sharing error: {exc}")

    print()
    if published_urls:
        print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  All done! Published to:")
        for platform, url in published_urls.items():
            print(f"    • {platform}: {url}")
        print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    else:
        print("  No platforms published successfully.\n")


if __name__ == "__main__":
    main()
