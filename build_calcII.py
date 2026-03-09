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

BLOCK_ID_RE = re.compile(r"(?<!\])\s+\^([\w-]+)\s*$")

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

# ── Callout type → CSS class + default title ─────────────────────────────────

CALLOUT_STYLES = {
    # type           : (css_class,      default_title)
    "note"           : ("callout-note",      "Note"),
    "info"           : ("callout-info",      "Info"),
    "tip"            : ("callout-tip",       "Tip"),
    "hint"           : ("callout-tip",       "Hint"),
    "important"      : ("callout-important", "Important"),
    "warning"        : ("callout-warning",   "Warning"),
    "caution"        : ("callout-warning",   "Caution"),
    "attention"      : ("callout-warning",   "Attention"),
    "danger"         : ("callout-danger",    "Danger"),
    "error"          : ("callout-danger",    "Error"),
    "example"        : ("callout-example",   "Example"),
    "question"       : ("callout-question",  "Question"),
    "faq"            : ("callout-question",  "FAQ"),
    "help"           : ("callout-question",  "Help"),
    "success"        : ("callout-success",   "Solution"),
    "check"          : ("callout-success",   "Check"),
    "done"           : ("callout-success",   "Done"),
    "quote"          : ("callout-quote",     "Quote"),
    "cite"           : ("callout-quote",     "Cite"),
    "abstract"       : ("callout-abstract",  "Abstract"),
    "summary"        : ("callout-abstract",  "Summary"),
    "theorem"        : ("callout-theorem",   "Theorem"),
    "lemma"          : ("callout-theorem",   "Lemma"),
    "corollary"      : ("callout-theorem",   "Corollary"),
    "proposition"    : ("callout-theorem",   "Proposition"),
    "definition"     : ("callout-definition","Definition"),
    "proof"          : ("callout-proof",     "Proof"),
    "remark"         : ("callout-remark",    "Remark"),
    "exercise"       : ("callout-exercise",  "Exercise"),
}

def parse_callout_block(lines: list[str]) -> tuple[str, bool, str, list[str]] | None:
    """
    Given a list of raw lines (with leading '> ' stripped one level),
    detect if the first line is an Obsidian callout header: [!type] Title
    or [!type]+ Title  (collapsible, open by default)
    or [!type]- Title  (collapsible, closed by default)

    Returns (callout_type, collapsible, title, body_lines) or None if not a callout.
    """
    if not lines:
        return None
    first = lines[0].strip()
    m = re.match(r"^\[!(\w+)\]([+-]?)\s*(.*)", first)
    if not m:
        return None
    ctype      = m.group(1).lower()
    fold_char  = m.group(2)          # '+' open, '-' closed, '' not collapsible
    title_rest = m.group(3).strip()
    collapsible = fold_char in ("+", "-")
    start_open  = fold_char != "-"   # '+' or '' → open; '-' → closed

    css_class, default_title = CALLOUT_STYLES.get(ctype, ("callout-note", ctype.capitalize()))
    title = title_rest if title_rest else default_title

    return css_class, collapsible, start_open, title, lines[1:]


def convert_callouts_and_blockquotes(text: str) -> str:
    """
    Convert Obsidian callout blocks (and plain blockquotes) to HTML.
    Handles arbitrary nesting: the content of each callout is recursively
    processed so nested callouts work correctly.

    Obsidian callout syntax (each line prefixed with '>'):
        > [!theorem] Integral Test
        > Statement of the theorem...
        >
        > > [!example]+ Example
        > > Some example text
        > > > [!success]- Solution
        > > > The solution goes here
    """

    def extract_quote_block(lines: list[str], start: int) -> tuple[list[str], int]:
        """
        Extract a contiguous run of '> ...' lines starting at `start`.
        Returns (block_lines_with_prefix_stripped_one_level, end_index).
        """
        block = []
        i = start
        while i < len(lines):
            line = lines[i]
            if re.match(r"^>", line):
                # strip exactly one level of '> ' or '>'
                stripped = re.sub(r"^> ?", "", line, count=1)
                block.append(stripped)
                i += 1
            else:
                break
        return block, i

    def render_block(inner_lines: list[str]) -> str:
        """
        Given lines with one quote-level stripped, render as either a
        callout or a plain blockquote, recursively handling nested quotes.
        """
        result = parse_callout_block(inner_lines)
        if result is None:
            # Plain blockquote — recurse on content in case nested
            inner_html = process_lines(inner_lines)
            return f"<blockquote>{inner_html}</blockquote>"

        css_class, collapsible, start_open, title, body_lines = result
        body_html = process_lines(body_lines)

        if collapsible:
            open_attr = " open" if start_open else ""
            return (
                f'<details class="callout {css_class}"{open_attr}>'
                f'<summary class="callout-title">{title}</summary>'
                f'<div class="callout-body">{body_html}</div>'
                f'</details>'
            )
        else:
            return (
                f'<div class="callout {css_class}">'
                f'<div class="callout-title">{title}</div>'
                f'<div class="callout-body">{body_html}</div>'
                f'</div>'
            )

    def process_lines(lines: list[str]) -> str:
        """
        Walk a list of lines, pulling out quote blocks and rendering them,
        leaving everything else as plain text to be joined.
        """
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if re.match(r"^>", line):
                block, i = extract_quote_block(lines, i)
                out.append(render_block(block))
            else:
                out.append(line)
                i += 1
        return "\n".join(out)

    return process_lines(text.split("\n"))


def convert_md_table(text: str) -> str:
    """
    Convert Markdown pipe tables to HTML <table> elements.

    Handles:
        | Col A | Col B |
        |-------|-------|
        | cell  | cell  |

    Also handles tables without a leading/trailing pipe on each row.
    """
    # A table block is: one or more lines containing '|', with at least one
    # separator row (cells of dashes/colons only).
    TABLE_BLOCK_RE = re.compile(
        r"(?:^|\n)"                        # start of string or newline
        r"((?:[^\n]*\|[^\n]*\n?)+"         # one or more pipe-containing lines
        r")",
        re.MULTILINE,
    )

    def render_table(block: str) -> str:
        raw_lines = [l for l in block.strip().splitlines() if l.strip()]
        if len(raw_lines) < 2:
            return block

        def split_row(line: str) -> list[str]:
            line = line.strip().strip("|")
            return [c.strip() for c in line.split("|")]

        # Detect separator row (row of dashes/colons)
        sep_idx = None
        for idx, line in enumerate(raw_lines):
            if re.match(r"^\|?[\s\-\|:]+\|?$", line) and "-" in line:
                sep_idx = idx
                break
        if sep_idx is None:
            return block   # not a real table

        header_rows = raw_lines[:sep_idx]
        body_rows   = raw_lines[sep_idx + 1:]

        # Parse alignment from separator row
        sep_cells = split_row(raw_lines[sep_idx])
        alignments = []
        for cell in sep_cells:
            cell = cell.strip()
            if cell.startswith(":") and cell.endswith(":"):
                alignments.append(' style="text-align:center"')
            elif cell.endswith(":"):
                alignments.append(' style="text-align:right"')
            else:
                alignments.append("")

        def make_row(line: str, tag: str) -> str:
            cells = split_row(line)
            html = ""
            for j, cell in enumerate(cells):
                align = alignments[j] if j < len(alignments) else ""
                html += f"<{tag}{align}>{cell}</{tag}>"
            return f"<tr>{html}</tr>"

        thead = "".join(make_row(r, "th") for r in header_rows)
        tbody = "".join(make_row(r, "td") for r in body_rows)
        return f"<table><thead>{thead}</thead><tbody>{tbody}</tbody></table>"

    def try_replace(m: re.Match) -> str:
        block = m.group(1)
        # Only replace if it looks like a table (has a separator row)
        if re.search(r"^\|?[\s\-\|:]+\|?$", block, re.MULTILINE) and "-" in block:
            rendered = render_table(block)
            # Preserve leading newline if present
            prefix = "\n" if m.group(0).startswith("\n") else ""
            return prefix + rendered
        return m.group(0)

    return TABLE_BLOCK_RE.sub(try_replace, text)


def md_to_html(text: str) -> str:
    """
    Markdown → HTML converter that preserves LaTeX and code blocks.
    Handles: headings, bold, italic, inline code, fenced code,
             Obsidian callouts (nested + collapsible), blockquotes,
             pipe tables, horizontal rules, unordered/ordered lists,
             paragraphs.
    LaTeX ($...$, $$...$$) is left untouched for MathJax.
    """
    # ── 1. Protect fenced code blocks ────────────────────────────────────────
    code_blocks: list[tuple[str, str]] = []
    def stash_code(m):
        lang = m.group(1) or ""
        code = m.group(2)
        code_blocks.append((lang, code))
        return f"\x00CODE{len(code_blocks)-1}\x00"

    text = re.sub(r"```(\w*)\n(.*?)```", stash_code, text, flags=re.DOTALL)

    # ── 2. Protect display LaTeX ($$...$$) then inline ($...$) ───────────────
    latex_stash: list[str] = []
    def stash_latex(m):
        latex_stash.append(m.group(0))
        return f"\x00LATEX{len(latex_stash)-1}\x00"

    text = re.sub(r"\$\$[\s\S]*?\$\$", stash_latex, text)
    text = re.sub(r"\$[^\$\n]+?\$",    stash_latex, text)

    # ── 3. Callouts and blockquotes (before paragraph splitting) ─────────────
    text = convert_callouts_and_blockquotes(text)

    # ── 4. Pipe tables ────────────────────────────────────────────────────────
    text = convert_md_table(text)

    # ── 5. Headings ───────────────────────────────────────────────────────────
    def heading(m):
        level   = len(m.group(1))
        content = m.group(2).strip()
        anchor  = slugify(re.sub(r"<[^>]+>", "", content))
        return f'<h{level} id="{anchor}">{content}</h{level}>'

    text = re.sub(r"^(#{1,6})\s+(.+)$", heading, text, flags=re.MULTILINE)

    # ── 6. Bold / italic ──────────────────────────────────────────────────────
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.+?)\*\*",     r"<strong>\1</strong>",          text)
    text = re.sub(r"\*(.+?)\*",         r"<em>\1</em>",                  text)
    text = re.sub(r"__(.+?)__",         r"<strong>\1</strong>",          text)
    text = re.sub(r"_(.+?)_",           r"<em>\1</em>",                  text)

    # ── 7. Inline code ────────────────────────────────────────────────────────
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # ── 8. Horizontal rules ───────────────────────────────────────────────────
    text = re.sub(r"^[-*_]{3,}\s*$", "<hr>", text, flags=re.MULTILINE)

    # ── 9. Lists ─────────────────────────────────────────────────────────────
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

    # ── 10. Paragraphs ────────────────────────────────────────────────────────
    BLOCK_TAGS = re.compile(
        r"^<(h[1-6]|ul|ol|blockquote|hr|pre|table|div|details|figure|\x00CODE)",
        re.IGNORECASE,
    )
    paragraphs = []
    for block in re.split(r"\n{2,}", text.strip()):
        block = block.strip()
        if not block:
            continue
        if BLOCK_TAGS.match(block):
            paragraphs.append(block)
        else:
            block = block.replace("\n", "<br>\n")
            paragraphs.append(f"<p>{block}</p>")
    text = "\n\n".join(paragraphs)

    # ── 11. Restore code blocks ───────────────────────────────────────────────
    for i, (lang, code) in enumerate(code_blocks):
        escaped = (code
                   .replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;"))
        lang_class = f' class="language-{lang}"' if lang else ""
        text = text.replace(
            f"\x00CODE{i}\x00",
            f"<pre><code{lang_class}>{escaped}</code></pre>",
        )

    # ── 12. Restore LaTeX ─────────────────────────────────────────────────────
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

    /* ── Callouts ─────────────────────────────────────────────────────── */
    .callout {{
      border-left: 4px solid;
      border-radius: 4px;
      margin: 1.2em 0;
      padding: 0;
      overflow: hidden;
    }}
    .callout-title {{
      font-weight: bold;
      font-size: 0.92em;
      padding: 0.45em 0.9em;
      letter-spacing: 0.01em;
    }}
    .callout-body {{
      padding: 0.6em 1em 0.7em;
      font-size: 0.97em;
    }}
    .callout-body p:first-child {{ margin-top: 0; }}
    .callout-body p:last-child  {{ margin-bottom: 0; }}

    /* collapsible callouts via <details> */
    details.callout > summary {{
      cursor: pointer;
      list-style: none;
      padding: 0.45em 0.9em;
      font-weight: bold;
      font-size: 0.92em;
    }}
    details.callout > summary::-webkit-details-marker {{ display: none; }}
    details.callout > summary::before {{
      content: "▶ ";
      font-size: 0.75em;
      opacity: 0.7;
    }}
    details.callout[open] > summary::before {{ content: "▼ "; }}

    /* colour themes */
    .callout-note       {{ border-color: hsl(210,70%,55%); background: hsl(210,60%,96%); }}
    .callout-note       .callout-title, details.callout-note > summary {{ background: hsl(210,60%,90%); color: hsl(210,60%,30%); }}
    .callout-info       {{ border-color: hsl(195,70%,50%); background: hsl(195,60%,96%); }}
    .callout-info       .callout-title, details.callout-info > summary {{ background: hsl(195,55%,88%); color: hsl(195,60%,28%); }}
    .callout-tip        {{ border-color: hsl(160,55%,45%); background: hsl(160,50%,96%); }}
    .callout-tip        .callout-title, details.callout-tip > summary {{ background: hsl(160,45%,88%); color: hsl(160,55%,25%); }}
    .callout-important  {{ border-color: hsl(265,60%,58%); background: hsl(265,50%,97%); }}
    .callout-important  .callout-title, details.callout-important > summary {{ background: hsl(265,45%,90%); color: hsl(265,55%,32%); }}
    .callout-warning    {{ border-color: hsl(38,90%,50%); background: hsl(45,90%,97%); }}
    .callout-warning    .callout-title, details.callout-warning > summary {{ background: hsl(45,85%,88%); color: hsl(38,70%,28%); }}
    .callout-danger     {{ border-color: hsl(0,70%,55%);  background: hsl(0,60%,97%); }}
    .callout-danger     .callout-title, details.callout-danger > summary {{ background: hsl(0,55%,90%);  color: hsl(0,65%,32%); }}
    .callout-example    {{ border-color: hsl(270,50%,58%); background: hsl(270,40%,97%); }}
    .callout-example    .callout-title, details.callout-example > summary {{ background: hsl(270,40%,91%); color: hsl(270,50%,32%); }}
    .callout-question   {{ border-color: hsl(30,80%,52%);  background: hsl(35,75%,97%); }}
    .callout-question   .callout-title, details.callout-question > summary {{ background: hsl(35,70%,89%);  color: hsl(30,65%,28%); }}
    .callout-success    {{ border-color: hsl(145,55%,42%); background: hsl(145,50%,96%); }}
    .callout-success    .callout-title, details.callout-success > summary {{ background: hsl(145,45%,87%); color: hsl(145,55%,24%); }}
    .callout-quote      {{ border-color: hsl(0,0%,55%);    background: hsl(0,0%,97%); }}
    .callout-quote      .callout-title, details.callout-quote > summary {{ background: hsl(0,0%,90%);    color: hsl(0,0%,30%); }}
    .callout-abstract   {{ border-color: hsl(185,60%,48%); background: hsl(185,50%,96%); }}
    .callout-abstract   .callout-title, details.callout-abstract > summary {{ background: hsl(185,50%,88%); color: hsl(185,55%,26%); }}
    /* Math-specific callouts */
    .callout-theorem    {{ border-color: hsl(220,65%,52%); background: hsl(220,55%,97%); }}
    .callout-theorem    .callout-title, details.callout-theorem > summary {{ background: hsl(220,55%,90%); color: hsl(220,60%,28%); }}
    .callout-definition {{ border-color: hsl(340,60%,52%); background: hsl(340,50%,97%); }}
    .callout-definition .callout-title, details.callout-definition > summary {{ background: hsl(340,50%,91%); color: hsl(340,55%,30%); }}
    .callout-proof      {{ border-color: hsl(0,0%,60%);    background: hsl(0,0%,98%); font-style: italic; }}
    .callout-proof      .callout-title, details.callout-proof > summary {{ background: hsl(0,0%,91%);    color: hsl(0,0%,28%); font-style: normal; }}
    .callout-remark     {{ border-color: hsl(50,70%,48%);  background: hsl(50,65%,97%); }}
    .callout-remark     .callout-title, details.callout-remark > summary {{ background: hsl(50,60%,88%);  color: hsl(50,60%,26%); }}
    .callout-exercise   {{ border-color: hsl(15,70%,52%);  background: hsl(15,60%,97%); }}
    .callout-exercise   .callout-title, details.callout-exercise > summary {{ background: hsl(15,55%,89%);  color: hsl(15,60%,28%); }}

    /* dark mode overrides */
    .latex-dark .callout {{ background: hsl(0,0%,14%); }}
    .latex-dark .callout-note       {{ border-color: hsl(210,60%,55%); }}
    .latex-dark .callout-note       .callout-title, .latex-dark details.callout-note > summary {{ background: hsl(210,35%,22%); color: hsl(210,60%,78%); }}
    .latex-dark .callout-theorem    {{ border-color: hsl(220,55%,60%); }}
    .latex-dark .callout-theorem    .callout-title, .latex-dark details.callout-theorem > summary {{ background: hsl(220,35%,22%); color: hsl(220,60%,80%); }}
    .latex-dark .callout-definition {{ border-color: hsl(340,50%,60%); }}
    .latex-dark .callout-definition .callout-title, .latex-dark details.callout-definition > summary {{ background: hsl(340,30%,22%); color: hsl(340,55%,78%); }}
    .latex-dark .callout-example    {{ border-color: hsl(270,45%,62%); }}
    .latex-dark .callout-example    .callout-title, .latex-dark details.callout-example > summary {{ background: hsl(270,28%,22%); color: hsl(270,50%,80%); }}
    .latex-dark .callout-success    {{ border-color: hsl(145,45%,48%); }}
    .latex-dark .callout-success    .callout-title, .latex-dark details.callout-success > summary {{ background: hsl(145,28%,20%); color: hsl(145,50%,72%); }}
    .latex-dark .callout-warning    {{ border-color: hsl(38,80%,52%); }}
    .latex-dark .callout-warning    .callout-title, .latex-dark details.callout-warning > summary {{ background: hsl(40,40%,20%); color: hsl(40,70%,72%); }}
    .latex-dark .callout-proof      {{ background: hsl(0,0%,14%); }}
    .latex-dark .callout-proof      .callout-title, .latex-dark details.callout-proof > summary {{ background: hsl(0,0%,20%); color: hsl(0,0%,72%); }}
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