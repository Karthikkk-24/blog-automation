# Blog Automation

A Python CLI tool that automatically writes, previews, and publishes full blog posts based on a single title. It uses Google Gemini for writing the content, Hugging Face (FLUX.1-schnell) for generating custom images, and supports publishing to Dev.to and Medium, as well as social sharing to Twitter and LinkedIn.

## Features

- Generates a fully structured blog post (1,500-2,000 words by default).
- Generates custom AI images for each section of the blog.
- Supports configuring publishing platforms (Dev.to, Medium).
- Auto-shares on Twitter and LinkedIn.
- Includes a local Flask server to preview the styled post before publishing.

## Prerequisites & Setup

### 1. API Keys
You need the following required API keys:
- `GEMINI_API_KEY`: Google Gemini (AI writer)
- `HF_TOKEN`: Hugging Face (AI images)
- `IMGBB_API_KEY`: imgbb (Image hosting)

Depending on where you want to publish/share, you will also need:
- `DEVTO_API_KEY`: For Dev.to publishing.
- `MEDIUM_TOKEN` & `MEDIUM_AUTHOR_ID`: For Medium publishing.
- `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`: For Twitter sharing.
- `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_URN`: For LinkedIn sharing.

### 2. Installation
```bash
# Clone the repository and enter the directory (if you haven't already)
cd blog-automation

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy the sample environment file and fill in your keys:
```bash
cp .env.example .env
```

Configure your enabled platforms in `config.json`. By default, Dev.to publishing and preview auto-open are enabled.
```json
{
  "publish_to": {
    "devto": true,
    "medium": false
  },
  "share_on": {
    "twitter": false,
    "linkedin": false
  },
  "share_text": {
    "enabled": true,
    "copy_to_clipboard": true
  },
  "preview": {
    "port": 5050,
    "auto_open_browser": true
  }
}
```

## How to Run (Modes)

Run the application using `main.py` with your blog post title. The application provides several modes and options:

### 1. Standard / Public Mode
Generates the blog post, generates images, launches a preview server, and waits for your confirmation to publish publicly to your configured platforms.
```bash
python main.py "The Future of Artificial Intelligence"
```

### 2. Draft Mode (`--draft`)
Publishes the post as a draft (not visible to the public) on all configured platforms.
```bash
python main.py "The Future of Artificial Intelligence" --draft
```

### 3. No-Images Mode (`--no-images`)
Skips the image generation phase. This makes the generation much faster (~30 seconds instead of ~2 minutes).
```bash
python main.py "The Future of Artificial Intelligence" --no-images
```

### 4. Custom Tone and Word Count
You can customize the writing style and the target length of the post.
- **Tones available**: `simple` (default), `storytelling`, `casual`, `professional`, `technical`
- **Words**: Integer value (default is 1800)

```bash
python main.py "Understanding Microservices" --tone technical --words 2500
```

## Previewing and Publishing

Once generation is complete, a local Flask server will start (default: `http://localhost:5050`). If enabled in `config.json`, your browser will open automatically.

In the terminal running the preview server, you can:
- Press **P**: Publish the post immediately to the configured platforms.
- Press **E**: Open `output/preview.html` in your system editor to make manual changes, then press Enter to reload the preview.
- Press **Q**: Quit the process without publishing.

## Output

All generated files and backups are stored in the `output/` directory:
- Locally saved images for each section (`section_N_image.png`)
- The generated HTML preview (`preview.html`)
- A plain text backup of the published blog (`YYYY-MM-DD_slug.txt`)
