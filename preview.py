import os
import subprocess
import sys
import threading
from flask import Flask, Response
import webbrowser
from config import OUTPUT_DIR, PREVIEW_PORT

_flask_app = Flask(__name__)
_html_content = ""
_server_thread = None


@_flask_app.route("/")
def serve_preview():
    return Response(_html_content, mimetype="text/html")


def _build_html(blog: dict, image_urls: list) -> str:
    title = blog.get("title", "Blog Preview")
    intro = blog.get("intro", "")
    sections = blog.get("sections", [])
    conclusion = blog.get("conclusion", "")
    tags = blog.get("tags", [])

    word_count = len(intro.split()) + len(conclusion.split())
    for sec in sections:
        word_count += len(sec.get("content", "").split())
    read_time = max(1, word_count // 200)

    tags_html = "".join(
        f'<span style="display:inline-block;background:#f0f0f0;color:#555;'
        f'padding:4px 12px;border-radius:20px;margin:4px 4px 0 0;font-size:13px;">'
        f'#{t}</span>'
        for t in tags
    )

    sections_html = ""
    for i, sec in enumerate(sections):
        heading = sec.get("heading", "")
        content = sec.get("content", "")
        url = image_urls[i] if i < len(image_urls) else None

        img_html = ""
        if url:
            img_html = (
                f'<figure style="margin:32px 0 24px;text-align:center;">'
                f'<img src="{url}" alt="{heading}" '
                f'style="max-width:100%;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.12);">'
                f"</figure>"
            )

        content_paragraphs = "".join(
            f"<p>{p.strip()}</p>"
            for p in content.split("\n\n")
            if p.strip()
        ) or f"<p>{content}</p>"

        sections_html += f"""
        <section style="margin-bottom:48px;">
            <h2 style="font-size:26px;font-weight:700;margin:0 0 16px;color:#1a1a1a;">{heading}</h2>
            {img_html}
            <div style="font-size:18px;line-height:1.8;color:#292929;">
                {content_paragraphs}
            </div>
        </section>
        """

    conclusion_paragraphs = "".join(
        f"<p>{p.strip()}</p>"
        for p in conclusion.split("\n\n")
        if p.strip()
    ) or f"<p>{conclusion}</p>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Preview</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            background: #fafafa;
            color: #292929;
        }}
        .preview-banner {{
            background: #1a1a1a;
            color: #fff;
            text-align: center;
            padding: 10px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 13px;
            letter-spacing: 0.5px;
        }}
        .preview-banner kbd {{
            background: #444;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 12px;
        }}
        article {{
            max-width: 740px;
            margin: 0 auto;
            padding: 60px 24px 100px;
        }}
        header {{
            margin-bottom: 48px;
        }}
        h1 {{
            font-size: 40px;
            font-weight: 800;
            line-height: 1.2;
            color: #1a1a1a;
            margin-bottom: 16px;
        }}
        .meta {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 14px;
            color: #757575;
        }}
        .intro {{
            font-size: 20px;
            line-height: 1.7;
            color: #292929;
            margin-bottom: 48px;
            border-left: 4px solid #e8e8e8;
            padding-left: 20px;
        }}
        .conclusion {{
            margin-top: 48px;
            padding: 32px;
            background: #f5f5f5;
            border-radius: 8px;
        }}
        .conclusion h2 {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 16px;
            color: #1a1a1a;
        }}
        .conclusion p {{
            font-size: 17px;
            line-height: 1.8;
        }}
        .tags {{
            margin-top: 48px;
            padding-top: 32px;
            border-top: 1px solid #e8e8e8;
        }}
        .tags h3 {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #757575;
            margin-bottom: 12px;
        }}
    </style>
</head>
<body>
    <div class="preview-banner">
        📝 BLOG PREVIEW &nbsp;|&nbsp;
        Go to your terminal and press <kbd>P</kbd> to publish &nbsp;·&nbsp;
        <kbd>E</kbd> to edit &nbsp;·&nbsp; <kbd>Q</kbd> to quit
    </div>
    <article>
        <header>
            <h1>{title}</h1>
            <div class="meta">{read_time} min read &nbsp;·&nbsp; {word_count} words</div>
        </header>

        <div class="intro">
            {''.join(f'<p style="margin-bottom:12px;">{p.strip()}</p>' for p in intro.split(chr(10)+chr(10)) if p.strip()) or f'<p>{intro}</p>'}
        </div>

        {sections_html}

        <div class="conclusion">
            <h2>Conclusion</h2>
            <div style="font-size:17px;line-height:1.8;">
                {conclusion_paragraphs}
            </div>
        </div>

        <div class="tags">
            <h3>Tags</h3>
            {tags_html}
        </div>
    </article>
</body>
</html>"""


def _start_flask(html: str, port: int):
    global _html_content
    _html_content = html
    import logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    _flask_app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def serve_preview(blog: dict, image_urls: list, port: int = PREVIEW_PORT,
                  auto_open_browser: bool = False) -> str:
    global _server_thread

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html = _build_html(blog, image_urls)

    preview_path = os.path.join(OUTPUT_DIR, "preview.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html)

    _server_thread = threading.Thread(target=_start_flask, args=(html, port), daemon=True)
    _server_thread.start()

    url = f"http://localhost:{port}"
    print(f"\n  ✅  Preview ready → {url}")

    if auto_open_browser:
        webbrowser.open(url)
        print("  Browser opened automatically.")
    else:
        print("  Open the URL above in your browser, then return here.")

    print()
    print("  ┌──────────────────────────────────────┐")
    print("  │  [P] Publish                         │")
    print("  │  [E] Open HTML in editor to edit     │")
    print("  │  [Q] Quit without publishing         │")
    print("  └──────────────────────────────────────┘")

    while True:
        try:
            choice = input("  Your choice (P / E / Q): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\n  Aborted.")
            sys.exit(0)

        if choice == "P":
            return "publish"

        elif choice == "E":
            print(f"\n  Opening {preview_path} in your default editor...")
            _open_in_editor(preview_path)
            input("  Press Enter when you're done editing to continue...")
            print("  Reloading preview with your edits...")
            try:
                with open(preview_path, "r", encoding="utf-8") as f:
                    updated_html = f.read()
                global _html_content
                _html_content = updated_html
                print(f"  ✅  Preview updated → http://localhost:{port} (refresh browser)")
            except Exception as exc:
                print(f"  Warning: could not reload preview: {exc}")
            print()
            print("  ┌──────────────────────────────────────┐")
            print("  │  [P] Publish                         │")
            print("  │  [E] Open HTML in editor again       │")
            print("  │  [Q] Quit without publishing         │")
            print("  └──────────────────────────────────────┘")

        elif choice == "Q":
            print("  Quitting. Your blog draft is saved at:", preview_path)
            sys.exit(0)

        else:
            print("  Please type P, E, or Q.")


def _open_in_editor(path: str):
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif sys.platform.startswith("linux"):
            editors = ["xdg-open", "gedit", "nano"]
            for editor in editors:
                try:
                    subprocess.Popen([editor, path])
                    break
                except FileNotFoundError:
                    continue
        elif sys.platform == "win32":
            os.startfile(path)
    except Exception as exc:
        print(f"  Could not open editor automatically: {exc}")
        print(f"  Please open manually: {path}")
