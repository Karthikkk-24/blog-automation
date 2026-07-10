import sys
import os
from social import _generate_social_content

blogs = [
    {
        "title": "The Death of the 9-to-5 Workday",
        "intro": "The standard 9-to-5 workday is a relic of the industrial revolution, designed for factories, not laptops. As remote work becomes the norm, companies forcing employees back to rigid schedules are bleeding their best talent. It's time to admit that the 40-hour office week is dead, and asynchronous work is the future.",
        "tags": ["remotework", "productivity"]
    },
    {
        "title": "Why You Should Stop Using React for Everything",
        "intro": "React has dominated web development for a decade, but it's time to face the truth: we are over-engineering simple websites. Shipping megabytes of JavaScript for a static landing page is terrible for performance and user experience. With the rise of HTMX and vanilla web components, building simple, fast web apps has never been easier.",
        "tags": ["webdev", "javascript"]
    }
]

url = "https://medium.com/@yourprofile/blog-url"

print("Generating tweets...\n")
for idx, b in enumerate(blogs):
    res = _generate_social_content(b, url)
    print(f"--- Example {idx+1}: {b['title']} ---")
    print(res.get("tweet"))
    print()
