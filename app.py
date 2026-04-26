import gradio as gr
import requests
import re
from urllib.parse import urlparse

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TaptwiceAEOBot/1.0)"}


def validate_llms(url):
    if not url.startswith("http"):
        url = "https://" + url

    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    llms_url = base.rstrip("/") + "/llms.txt"

    results = [f"## llms.txt Validator\n**Checked:** `{llms_url}`\n"]

    try:
        r = requests.get(llms_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            results.append(f"❌ **Not found** — `{llms_url}` returned HTTP {r.status_code}")
            results.append("\n### What to do")
            results.append("Create a `llms.txt` file at your domain root. Minimum structure:")
            results.append("```")
            results.append("# Your Brand Name")
            results.append("")
            results.append("> One-sentence description of what you do.")
            results.append("")
            results.append("## Key Pages")
            results.append("- [Home](https://yourdomain.com)")
            results.append("- [About](https://yourdomain.com/about)")
            results.append("```")
            results.append('\nUse our <a href="https://huggingface.co/spaces/taptwicemedia/llms-txt-generator" target="_blank">llms.txt Generator</a> to build yours in minutes.')
            return "\n".join(results)

        text = r.text
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        results.append(f"✅ **Found** — {len(lines)} non-empty lines ({len(text)} bytes)\n")
        results.append("---")
        results.append("### Structure Analysis\n")

        score = 0
        max_score = 0

        max_score += 20
        h1_lines = [l for l in lines if l.startswith("# ") and not l.startswith("## ")]
        if h1_lines:
            results.append(f"✅ **Brand heading (# H1)**: `{h1_lines[0]}`")
            score += 20
        else:
            results.append("❌ **Brand heading**: Missing — add `# YourBrandName` as the first line")

        max_score += 20
        desc_lines = [l for l in lines if l.startswith("> ")]
        if desc_lines:
            results.append(f"✅ **Description block (>)**: `{desc_lines[0][:80]}`")
            score += 20
        else:
            results.append("❌ **Description block**: Missing — add `> One sentence about your brand`")

        max_score += 20
        h2_lines = [l for l in lines if l.startswith("## ")]
        if len(h2_lines) >= 2:
            results.append(f"✅ **Sections (## H2)**: {len(h2_lines)} found — {', '.join(l[3:] for l in h2_lines[:4])}")
            score += 20
        elif len(h2_lines) == 1:
            results.append(f"⚠️ **Sections**: Only 1 section — add more (Services, Blog, Contact, etc.)")
            score += 10
        else:
            results.append("❌ **Sections**: No ## sections — add categorized sections with links")

        max_score += 20
        link_lines = [l for l in lines if re.search(r'\[.+\]\(.+\)', l)]
        if len(link_lines) >= 5:
            results.append(f"✅ **Links**: {len(link_lines)} linked items — good coverage")
            score += 20
        elif len(link_lines) >= 2:
            results.append(f"⚠️ **Links**: {len(link_lines)} links — add more page links so AI knows where to find content")
            score += 10
        else:
            results.append("❌ **Links**: Too few links — add `- [Page Name](https://url)` items under each section")

        max_score += 20
        size = len(text)
        if 200 <= size <= 5000:
            results.append(f"✅ **File size**: {size} bytes — concise and complete")
            score += 20
        elif size < 200:
            results.append(f"⚠️ **File size**: {size} bytes — too sparse, add more content")
            score += 10
        else:
            results.append(f"⚠️ **File size**: {size} bytes — very large, keep llms.txt under 5KB")
            score += 10

        pct = int((score / max_score) * 100)
        filled = pct // 5
        bar = "█" * filled + "░" * (20 - filled)
        grade = "🟢 Strong" if pct >= 80 else "🟡 Good" if pct >= 60 else "🟠 Needs work" if pct >= 40 else "🔴 Poor"

        results.append("\n---")
        results.append("### llms.txt Quality Score\n")
        results.append(f"**{grade}** [{bar}] {pct}%")
        results.append(f"\nScore: **{score}/{max_score}**")

        if score < max_score:
            results.append('\nUse our <a href="https://huggingface.co/spaces/taptwicemedia/llms-txt-generator" target="_blank">llms.txt Generator</a> to improve your file.')

    except Exception as e:
        results.append(f"❌ **Error**: {e}")

    results.append("\n---")
    results.append('*Validator by <a href="https://taptwicemedia.com" target="_blank">Taptwice Media</a> — AEO &amp; GEO specialists*')
    return "\n".join(results)


demo = gr.Interface(
    fn=validate_llms,
    inputs=gr.Textbox(label="Enter website URL", placeholder="https://yourwebsite.com", scale=4),
    outputs=gr.Markdown(label="llms.txt Validation Report"),
    title="llms.txt Validator by Taptwice Media",
    description=(
        "Check if your website has a valid llms.txt file and grade its quality. "
        "llms.txt tells AI engines (ChatGPT, Claude, Perplexity, Gemini) what your brand is about. "
        'Built by <a href="https://taptwicemedia.com" target="_blank">Taptwice Media</a> — the AEO &amp; GEO specialists.'
    ),
    examples=[["https://taptwicemedia.com"], ["https://perplexity.ai"], ["https://anthropic.com"]],
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
