#!/usr/bin/env python3
"""
blog-automation — entry point

Usage:
    python main.py "Your Blog Title"
    python main.py "Your Blog Title" --tone professional
    python main.py "Your Blog Title" --words 2000 --draft
    python main.py "Your Blog Title" --no-images
"""

import argparse
import os
import sys


def _parse_args():
    parser = argparse.ArgumentParser(
        prog="blog-automation",
        description="Generate and publish a full Medium blog post from a title.",
    )
    parser.add_argument("title", help="The blog post title.")
    parser.add_argument(
        "--tone",
        choices=["storytelling", "casual", "professional", "technical"],
        default="storytelling",
        help="Writing tone (default: storytelling).",
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
        help="Publish to Medium as a draft instead of public.",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        dest="no_images",
        help="Skip image generation (much faster).",
    )
    return parser.parse_args()


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

    # ── Step 1: Validate config ──────────────────────────────────────────────
    print("━━━ [1/4] Validating config ...")
    try:
        from config import validate_config
        validate_config()
        print("  All API keys present.\n")
    except EnvironmentError as exc:
        print(f"\n  ❌  Config error:\n  {exc}\n")
        sys.exit(1)

    # ── Step 2: Generate blog ────────────────────────────────────────────────
    print("━━━ [2/4] Generating blog with Gemini ...")
    try:
        from writer import generate_blog
        blog = generate_blog(
            title=args.title,
            tone=args.tone,
            word_count=args.words,
        )
        print()
    except Exception as exc:
        print(f"\n  ❌  Blog generation failed:\n  {exc}\n")
        sys.exit(1)

    # ── Step 3: Generate images ──────────────────────────────────────────────
    if args.no_images:
        print("━━━ [3/4] Image generation skipped (--no-images).\n")
        image_urls = [None] * len(blog.get("sections", []))
    else:
        print("━━━ [3/4] Generating and uploading images ...")
        try:
            from image_gen import generate_and_upload_images
            prompts = [sec["image_prompt"] for sec in blog.get("sections", [])]
            image_urls = generate_and_upload_images(prompts)
            print()
        except Exception as exc:
            print(f"\n  ⚠️  Image generation error: {exc}")
            print("  Continuing without images...\n")
            image_urls = [None] * len(blog.get("sections", []))

    # ── Step 4: Preview ──────────────────────────────────────────────────────
    print("━━━ [4/4] Launching preview server ...")
    try:
        from preview import serve_preview
        decision = serve_preview(blog, image_urls)
    except Exception as exc:
        print(f"\n  ❌  Preview failed:\n  {exc}\n")
        sys.exit(1)

    # ── Step 5: Publish ──────────────────────────────────────────────────────
    if decision == "publish":
        print("\n━━━ Publishing to Medium ...")
        try:
            from publisher import publish_to_medium
            post_url = publish_to_medium(blog, image_urls, draft=args.draft)
            status_label = "draft" if args.draft else "live"
            print(f"\n  ✅  Published ({status_label})!")
            print(f"  🔗  {post_url}\n")
        except Exception as exc:
            print(f"\n  ❌  Publishing failed:\n  {exc}\n")
            sys.exit(1)
    else:
        print("\n  Aborted — blog was not published.\n")


if __name__ == "__main__":
    main()
