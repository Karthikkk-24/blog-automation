# blog-automation

A Python CLI tool that writes, previews, and publishes a full Medium blog post from a single title — completely free, no monthly fees, runs on your own machine.

**Time to publish:** ~2 minutes after setup.

---

## What it does

1. You type one blog title
2. Gemini AI writes a full 1,500–2,000 word structured blog
3. Flux.1-schnell generates one custom image per section
4. A local Flask server shows you a styled browser preview
5. Press **P** to publish live to your Medium profile

---

## Prerequisites — Get these first

You need 5 free API keys before running anything.

| Key | Service | URL | Urgency |
|-----|---------|-----|---------|
| `GEMINI_API_KEY` | Google Gemini (AI writer) | https://aistudio.google.com | Normal |
| `HF_TOKEN` | Hugging Face (AI images) | https://huggingface.co → Settings → Access Tokens | Normal |
| `MEDIUM_TOKEN` | Medium integration token | medium.com → Settings → Security & apps | **⚠️ Get first — limited availability** |
| `MEDIUM_AUTHOR_ID` | Your Medium user ID | See below | After Medium token |
| `IMGBB_API_KEY` | imgbb image hosting | https://api.imgbb.com | Normal |

### Getting your Medium Author ID

After you have your Medium token, run:

```bash
curl -H "Authorization: Bearer YOUR_MEDIUM_TOKEN" https://api.medium.com/v1/me
```

Copy the `data.id` value from the JSON response.

---

## Setup

```bash
# 1. Clone / enter the project folder
cd blog-automation

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API keys
cp .env.example .env
# Open .env and fill in all 5 values
```

Your `.env` file:

```
GEMINI_API_KEY=AIza...
HF_TOKEN=hf_...
MEDIUM_TOKEN=...
MEDIUM_AUTHOR_ID=...
IMGBB_API_KEY=...
```

> **Never commit `.env` to git.** It is already in `.gitignore`.

---

## Usage

```bash
python main.py "Your Blog Title"
```

### All flags

| Flag | Default | Description |
|------|---------|-------------|
| `--tone` | `storytelling` | Writing style: `storytelling`, `casual`, `professional`, `technical` |
| `--words` | `1800` | Target word count |
| `--draft` | off | Publish to Medium as a **draft** (not public) |
| `--no-images` | off | Skip image generation (~30 sec total instead of ~2 min) |

### Examples

```bash
# Default: storytelling tone, ~1800 words, public post
python main.py "The Hidden Cost of Convenience"

# Professional tone, longer post
python main.py "Why Microservices Fail at Scale" --tone professional --words 2000

# Quick draft, no images
python main.py "My Travel Notes from Tokyo" --draft --no-images
```

---

## Preview controls

Once the browser preview loads at `http://localhost:5050`:

| Key | Action |
|-----|--------|
| `P` | Publish to Medium immediately |
| `E` | Open `output/preview.html` in your system editor, then press Enter to reload |
| `Q` | Quit without publishing |

---

## Output files

All generated files are saved in the `output/` folder:

| File | Description |
|------|-------------|
| `section_N_image.png` | Locally saved AI-generated images |
| `preview.html` | Styled HTML preview of your blog |
| `YYYY-MM-DD_slug.txt` | Plain-text backup of every published blog |

---

## Architecture

```
.env / config.py
     │
     ▼
  main.py ──► writer.py      (Gemini → blog dict)
     │
     ├──────► image_gen.py   (HF → PNG files → imgbb → public URLs)
     │
     ├──────► preview.py     (Flask server at localhost:5050)
     │
     └──────► publisher.py   (Medium API → live post URL)
```

---

## Free services used

| Service | Purpose | Cost |
|---------|---------|------|
| Google Gemini API | AI blog writing | Free (1,500 req/day) |
| Hugging Face API | AI image generation | Free |
| imgbb.com | Public image hosting | Free forever |
| Medium API | Blog publishing | Free |

**Total: ₹0 / month**
