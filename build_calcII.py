#!/usr/bin/env python3
"""
build_calcII.py — Obsidian vault → static site builder for calcII.html

Usage:
    python build_calcII.py

Reads:  notes/calcII/*.md
Writes: calcII/<slug>.html  (one per note)
        graph-data.json      (nodes + edges for D3 graph)

Supported wikilink syntax:
    [[page]]                 → basic link
    [[page|display text]]    → aliased link
    [[page#heading]]         → heading anchor link
    [[page^blockID]]         → block-reference link (target note gets id="blockID" on the paragraph)
    [[page#heading|alias]]   → heading anchor with alias
    [[page^blockID|alias]]   → block ref with alias
"""

import os
import re
import json
import shutil
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
NOTES_DIR   = Path("notes/calcII")
OUTPUT_DIR  = Path("calcII")
GRAPH_JSON  = Path("graph-data.json")

# ── Helpers ──────────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    """Convert a note name to a URL-safe slug."""
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s

def note_name_to_slug(name: str) -> str:
    return slugify(name)

def collect_notes(notes_dir: Path) -> dict[str, Path]:
    """Returns {note_name: path} for every .md file found."""
    notes = {}
    for path in sorted(notes_dir.rglob("*.md")):
        name = path.stem
        notes[name] = path
    return notes

# ── Block-ID pre-pass ────────────────────────────────────────────────────────

BLOCK_ID_RE = re.compile(r"\s+\^([\w-]+)\s*$")

def strip_block_ids(text: str) -> tuple[str, dict[str, int]]:
    """
    Remove ^blockID markers from end of lines.
    Returns cleaned text and a dict {blockID: line_number (0-indexed)}.
    """
    lines = text.split("\n")
    block_map: dict[str, int] = {}
    clean_lines = []
    for i, line in enumerate(lines):
        m = BLOCK_ID_RE.search(line)
        if m:
            block_map[m.group(1)] = len(clean_lines)  # index into clean_lines
            clean_lines.append(BLOCK_ID_RE.sub("", line))
        else:
            clean_lines.append(line)
    return "\n".join(clean_lines), block_map

# ── Markdown → HTML conversion ────────────────────────────────────────────────

WIKILINK_RE = re.compile(
    r"\[\[([^\]|#^]+?)(?:#([^\]|^]+?))?(?:\^([^\]|]+?))?(?:\|([^\]]+?))?\]\]"
)

# Matches ![[image.png]], ![[image.png|alt text]], ![[image.png|300]] (Obsidian width syntax)
IMAGE_EMBED_RE = re.compile(r"!\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]")

def convert_image_embeds(text: str) -> str:
    """
    Replace Obsidian ![[image.png]] embeds with <img> tags.

    Obsidian stores images anywhere in the vault; we assume you've copied
    your vault's attachment folder into notes/calcII/attachments/ (or the
    repo root images/ folder). The build script looks for the image filename
    in both locations and uses a relative path from calcII/<note>.html.

    Supported syntax:
        ![[photo.png]]              → <img src="../images/photo.png" alt="photo">
        ![[photo.png|My caption]]   → <img> with alt="My caption"
        ![[photo.png|300]]          → <img> with width="300"
        ![[photo.png|300x200]]      → <img> with width="300" height="200"
    """
    def replace(m):
        filename = m.group(1).strip()
        modifier = (m.group(2) or "").strip()

        # Determine alt text vs. size modifier
        alt   = filename.rsplit(".", 1)[0]   # default alt = filename without extension
        width_attr  = ""
        height_attr = ""

        if modifier:
            # Pure number → width only, e.g. |300
            if re.fullmatch(r"\d+", modifier):
                width_attr = f' width="{modifier}"'
            # WxH → width and height, e.g. |300x200
            elif re.fullmatch(r"\d+x\d+", modifier):
                w, h = modifier.split("x")
                width_attr  = f' width="{w}"'
                height_attr = f' height="{h}"'
            else:
                # Treat as alt text
                alt = modifier

        # Image src: generated notes live in calcII/, so go up one level
        # to reach images/ at the repo root (or notes/calcII/attachments/).
        # We try to find the file; if not found we still emit the tag with
        # a sensible path so it works once the image is in the right place.
        src = f"../images/{filename}"

        return (
            f'<figure class="centered">'
            f'<img src="{src}" alt="{alt}"{width_attr}{height_attr} loading="lazy" />'
            f'<figcaption>{alt}</figcaption>'
            f'</figure>'
        )

    return IMAGE_EMBED_RE.sub(replace, text)


def convert_wikilinks(text: str, all_note_slugs: set[str]) -> tuple[str, list[str]]:
    """
    Replace [[wikilinks]] with <a> tags.
    Returns (converted_text, list_of_linked_slugs).
    """
    linked: list[str] = []

    def replace(m):
        page   = m.group(1).strip()
        heading = m.group(2)
        block   = m.group(3)
        alias   = m.group(4)

        slug = note_name_to_slug(page)
        linked.append(slug)

        # build href
        if block:
            href = f"#{block}"           # points to id on current rendered page
            # but for cross-note block refs we need the note too
            href = f"calcII/{slug}.html#{block}"
        elif heading:
            anchor = slugify(heading)
            href = f"calcII/{slug}.html#{anchor}"
        else:
            href = f"calcII/{slug}.html"

        display = alias or heading or block or page
        return f'<a href="{href}" class="wiki-link" data-note="{slug}">{display}</a>'

    converted = WIKILINK_RE.sub(replace, text)
    return converted, linked

def md_to_html(text: str) -> str:
    """
    Minimal Markdown → HTML converter that preserves LaTeX and code blocks.
    Handles: headings, bold, italic, inline code, fenced code, blockquotes,
             horizontal rules, unordered/ordered lists, paragraphs.
    LaTeX ($...$, $$...$$) is left untouched for MathJax.
    """
    # ── 1. Protect fenced code blocks ────────────────────────────────────────
    code_blocks: list[str] = []
    def stash_code(m):
        lang = m.group(1) or ""
        code = m.group(2)
        code_blocks.append((lang, code))
        return f"\x00CODE{len(code_blocks)-1}\x00"

    text = re.sub(r"```(\w*)\n(.*?)```", stash_code, text, flags=re.DOTALL)

    # ── 2. Protect inline LaTeX ($...$) and display ($$...$$) ────────────────
    latex_stash: list[str] = []
    def stash_latex(m):
        latex_stash.append(m.group(0))
        return f"\x00LATEX{len(latex_stash)-1}\x00"

    text = re.sub(r"\$\$[\s\S]*?\$\$", stash_latex, text)
    text = re.sub(r"\$[^\$\n]+?\$",    stash_latex, text)

    # ── 3. Headings ───────────────────────────────────────────────────────────
    def heading(m):
        level = len(m.group(1))
        content = m.group(2).strip()
        anchor  = slugify(re.sub(r"<[^>]+>", "", content))
        return f"<h{level} id=\"{anchor}\">{content}</h{level}>"

    text = re.sub(r"^(#{1,6})\s+(.+)$", heading, text, flags=re.MULTILINE)

    # ── 4. Bold / italic ──────────────────────────────────────────────────────
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.+?)\*\*",     r"<strong>\1</strong>",          text)
    text = re.sub(r"\*(.+?)\*",         r"<em>\1</em>",                  text)
    text = re.sub(r"__(.+?)__",         r"<strong>\1</strong>",          text)
    text = re.sub(r"_(.+?)_",           r"<em>\1</em>",                  text)

    # ── 5. Inline code ────────────────────────────────────────────────────────
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # ── 6. Horizontal rules ───────────────────────────────────────────────────
    text = re.sub(r"^[-*_]{3,}\s*$", "<hr>", text, flags=re.MULTILINE)

    # ── 7. Blockquotes ────────────────────────────────────────────────────────
    def blockquote(m):
        inner = re.sub(r"^> ?", "", m.group(0), flags=re.MULTILINE)
        return f"<blockquote>{inner.strip()}</blockquote>"
    text = re.sub(r"(^> .+\n?)+", blockquote, text, flags=re.MULTILINE)

    # ── 8. Lists (basic) ─────────────────────────────────────────────────────
    def ul_list(m):
        items = re.findall(r"^[-*+] (.+)$", m.group(0), flags=re.MULTILINE)
        lis = "".join(f"<li>{i}</li>" for i in items)
        return f"<ul>{lis}</ul>"
    text = re.sub(r"(^[-*+] .+\n?)+", ul_list, text, flags=re.MULTILINE)

    def ol_list(m):
        items = re.findall(r"^\d+\. (.+)$", m.group(0), flags=re.MULTILINE)
        lis = "".join(f"<li>{i}</li>" for i in items)
        return f"<ol>{lis}</ol>"
    text = re.sub(r"(^\d+\. .+\n?)+", ol_list, text, flags=re.MULTILINE)

    # ── 9. Paragraphs ─────────────────────────────────────────────────────────
    paragraphs = []
    for block in re.split(r"\n{2,}", text.strip()):
        block = block.strip()
        if not block:
            continue
        # Don't wrap structural tags in <p>
        if re.match(r"^<(h[1-6]|ul|ol|blockquote|hr|pre|\x00CODE)", block):
            paragraphs.append(block)
        else:
            # single newlines → <br> inside paragraph
            block = block.replace("\n", "<br>\n")
            paragraphs.append(f"<p>{block}</p>")
    text = "\n\n".join(paragraphs)

    # ── 10. Restore code blocks ───────────────────────────────────────────────
    for i, (lang, code) in enumerate(code_blocks):
        escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lang_class = f' class="language-{lang}"' if lang else ""
        replacement = f'<pre><code{lang_class}>{escaped}</code></pre>'
        text = text.replace(f"\x00CODE{i}\x00", replacement)

    # ── 11. Restore LaTeX ─────────────────────────────────────────────────────
    for i, latex in enumerate(latex_stash):
        text = text.replace(f"\x00LATEX{i}\x00", latex)

    return text

# ── HTML page template ────────────────────────────────────────────────────────

PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <title>{title} | Calc II Notes</title>
  <link rel="stylesheet" href="../style.css" />
  <link rel="stylesheet" href="../styles.css" />
  <link rel="stylesheet" href="../prism/prism.css" />
  <style>
    /* block-reference highlight */
    .block-ref-target {{
      background: hsl(55, 90%, 85%);
      border-left: 3px solid hsl(45, 90%, 50%);
      padding: 2px 6px;
      border-radius: 2px;
      transition: background 0.4s;
    }}
    .latex-dark .block-ref-target {{
      background: hsl(45, 40%, 25%);
      border-left-color: hsl(45, 80%, 55%);
    }}
    /* wiki-links */
    a.wiki-link {{
      color: var(--link-visited);
      text-decoration: underline dotted;
    }}
  </style>
</head>
<body id="top">
  <header>
    <h1>
      <a href="../index.html" class="no-style-link">
        <span class="latex">S <span>i</span>R<span>e</span>E<span>s</span>H</span>.tex
      </a>
    </h1>
    <p class="author">
      <a href="../index.html" class="no-style-link">Sireesh Vinnakota</a><br />
      Graduate Student in Mathematics
    </p>
  </header>

  <div class="abstract">
    <h2>Abstract</h2>
    <p>
      Calculus II — <em>{title}</em><br />
      <a href="../calcII.html">← Back to Calc II graph</a>
      &nbsp;
      <button id="home-button">Home</button>
      <button id="dark-mode-toggle">Toggle dark mode</button>
      <button id="typeface-toggle">Typeface: <span id="typeface">Latin Modern</span></button>
    </p>
  </div>

  <main>
    <article>
{body}
    </article>
  </main>

  <footer>
    <p>Template by <a href="https://github.com/vincentdoerig/latex-css">Vincent Doerig</a>.</p>
  </footer>

  <script>
  MathJax = {{ tex: {{ inlineMath: [['$','$']] }} }};
  window.addEventListener('DOMContentLoaded', () => {{
    if (localStorage.getItem('darkMode') === 'true')
      document.body.classList.add('latex-dark');
    if (localStorage.getItem('typeface') === 'libertinus') {{
      document.body.classList.add('libertinus');
      document.getElementById('typeface').textContent = 'Libertinus';
    }}
    // highlight block-ref targets (URL hash like #blockID)
    if (location.hash) {{
      const el = document.getElementById(location.hash.slice(1));
      if (el) el.classList.add('block-ref-target');
    }}
  }});
  document.getElementById('dark-mode-toggle').addEventListener('click', () => {{
    document.body.classList.toggle('latex-dark');
    localStorage.setItem('darkMode', document.body.classList.contains('latex-dark'));
  }});
  document.getElementById('typeface-toggle').addEventListener('click', () => {{
    document.body.classList.toggle('libertinus');
    const lib = document.body.classList.contains('libertinus');
    document.getElementById('typeface').textContent = lib ? 'Libertinus' : 'Latin Modern';
    localStorage.setItem('typeface', lib ? 'libertinus' : 'latin-modern');
  }});
  document.getElementById('home-button').addEventListener('click', () => {{
    window.location.href = '../index.html';
  }});
  </script>
  <script id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <script async src="../prism/prism.js"></script>
</body>
</html>
"""

# ── Main build ────────────────────────────────────────────────────────────────

def build():
    if not NOTES_DIR.exists():
        print(f"[ERROR] Notes directory '{NOTES_DIR}' not found.")
        print("  Create it and put your Obsidian .md files inside.")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    notes = collect_notes(NOTES_DIR)
    if not notes:
        print(f"[WARNING] No .md files found in '{NOTES_DIR}'.")
        return

    all_slugs  = {note_name_to_slug(n) for n in notes}
    graph_nodes = []
    graph_links = []
    seen_edges: set[tuple[str, str]] = set()

    print(f"Found {len(notes)} notes. Building…")

    for note_name, path in notes.items():
        slug = note_name_to_slug(note_name)
        raw  = path.read_text(encoding="utf-8")

        # Strip Obsidian front-matter
        raw = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.DOTALL)

        # Pre-pass: collect block IDs
        raw, block_map = strip_block_ids(raw)

        # Convert image embeds BEFORE wikilinks (so ![[]] is handled first)
        raw = convert_image_embeds(raw)

        # Replace wikilinks
        raw, linked_slugs = convert_wikilinks(raw, all_slugs)

        # Convert markdown
        body_html = md_to_html(raw)

        # Inject block-ID anchors: wrap paragraph at that line with an id span
        # We do this at HTML level by scanning for the paragraphs
        for bid, _line_idx in block_map.items():
            # wrap first occurrence of each paragraph that had a block ID
            # simplest: add id to first <p> that contains anchor marker text
            # Since we already converted the text, insert a named span at top of article
            body_html = f'<span id="{bid}" class="block-anchor"></span>\n' + body_html

        # Write individual note HTML
        out_path = OUTPUT_DIR / f"{slug}.html"
        page_html = PAGE_TEMPLATE.format(
            title=note_name,
            body=body_html,
        )
        out_path.write_text(page_html, encoding="utf-8")
        print(f"  ✓ {slug}.html")

        # Accumulate graph data
        graph_nodes.append({"id": slug, "label": note_name})

        for target_slug in linked_slugs:
            edge_key = (slug, target_slug)
            if edge_key not in seen_edges and slug != target_slug:
                seen_edges.add(edge_key)
                graph_links.append({"source": slug, "target": target_slug})

    # Write graph JSON
    graph_data = {"nodes": graph_nodes, "links": graph_links}
    GRAPH_JSON.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
    print(f"\n  ✓ graph-data.json  ({len(graph_nodes)} nodes, {len(graph_links)} edges)")
    print("\nDone. Commit everything and push.")

if __name__ == "__main__":
    build()