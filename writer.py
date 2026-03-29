import json
import re
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACK

genai.configure(api_key=GEMINI_API_KEY)

TONE_INSTRUCTIONS = {
    "storytelling": (
        "Write in a narrative, story-driven style. Open with a vivid anecdote or scene. "
        "Use human stories, real-life examples, and emotional hooks throughout. "
        "The reader should feel like they are on a journey, not reading a manual."
    ),
    "casual": (
        "Write in a friendly, conversational tone. Use simple language, contractions, "
        "and occasional humour. Imagine you're explaining this to a smart friend over coffee."
    ),
    "professional": (
        "Write in a formal, authoritative tone. Use data, statistics, and citations where "
        "relevant. Avoid colloquialisms. Target audience: business professionals and decision-makers."
    ),
    "technical": (
        "Write in a precise, expert-level tone. Include technical details, code concepts, "
        "system design considerations, and industry terminology. Target audience: senior engineers "
        "and technical architects."
    ),
}


def _build_prompt(title: str, tone: str, word_count: int, feedback: str = "") -> str:
    tone_guide = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["storytelling"])
    feedback_block = (
        f"\n\nUser feedback on the previous draft — incorporate this:\n{feedback}\n"
        if feedback
        else ""
    )

    return f"""You are an expert blog writer for Medium.com.{feedback_block}

Write a complete, publication-ready blog post on the topic: "{title}"

TONE INSTRUCTIONS:
{tone_guide}

STRUCTURE REQUIREMENTS:
- Introduction: 150-200 words. Start with a compelling hook — a question, story, or surprising fact.
- 5 main sections, each with:
    * A clear, engaging subheading
    * 250-320 words of rich content
    * At least one concrete example, data point, or real-world scenario
    * A natural transition sentence leading to the next section
- Conclusion: 150-180 words. Summarise key takeaways and end with a call to action or forward-looking statement.
- 5 SEO-friendly Medium tags (single words or short hyphenated phrases, lowercase)
- One vivid image_prompt per section: a single English sentence describing a photorealistic or illustrative scene for an AI image generator. Be specific about colours, setting, and mood.

TARGET WORD COUNT: approximately {word_count} words for the full post body.

OUTPUT FORMAT:
Return ONLY raw JSON — no markdown code fences, no backticks, no extra commentary.
The JSON must exactly match this schema:

{{
  "title": "string",
  "intro": "string",
  "sections": [
    {{
      "heading": "string",
      "content": "string",
      "image_prompt": "string"
    }}
  ],
  "conclusion": "string",
  "tags": ["string", "string", "string", "string", "string"]
}}

Ensure all string values use proper English punctuation. Do not truncate any section."""


def generate_blog(
    title: str,
    tone: str = "storytelling",
    word_count: int = 1800,
    feedback: str = "",
) -> dict:
    prompt = _build_prompt(title, tone, word_count, feedback)

    for model_name in [GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACK]:
        try:
            print(f"  Calling Gemini ({model_name})...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.85,
                    max_output_tokens=8192,
                ),
            )
            raw = response.text.strip()

            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

            blog = json.loads(raw)
            _validate_blog_dict(blog)
            print(f"  Blog generated successfully ({_count_words(blog)} words).")
            return blog

        except json.JSONDecodeError as exc:
            print(f"  JSON parse error with {model_name}: {exc}. Retrying with fallback...")
            continue
        except Exception as exc:
            print(f"  Error with {model_name}: {exc}. Trying fallback...")
            continue

    raise RuntimeError(
        "Both Gemini models failed to generate a valid blog. "
        "Check your GEMINI_API_KEY and network connection."
    )


def _validate_blog_dict(blog: dict):
    required_top = {"title", "intro", "sections", "conclusion", "tags"}
    missing = required_top - blog.keys()
    if missing:
        raise ValueError(f"Blog JSON missing keys: {missing}")
    if not isinstance(blog["sections"], list) or len(blog["sections"]) < 3:
        raise ValueError("Blog must have at least 3 sections.")
    for i, sec in enumerate(blog["sections"]):
        for field in ("heading", "content", "image_prompt"):
            if field not in sec:
                raise ValueError(f"Section {i} missing field: {field}")
    if not isinstance(blog["tags"], list) or len(blog["tags"]) < 1:
        raise ValueError("Blog must have at least one tag.")


def _count_words(blog: dict) -> int:
    text = blog.get("intro", "") + " " + blog.get("conclusion", "")
    for sec in blog.get("sections", []):
        text += " " + sec.get("content", "")
    return len(text.split())
