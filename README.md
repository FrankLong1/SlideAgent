# SlideAgent

Minimal, purposefully thin presentation framework for AI agents. SlideAgent focuses on great defaults, a clean template/theme system, and a tiny MCP surface so models can do the work without heavy app logic.

## TL;DR Quick Start

```bash
# 1) Install deps (Python managed by uv, Node for PDF/live viewer)
curl -LsSf https://astral.sh/uv/install.sh | sh   # if uv not installed
uv sync
npm install

# 2) Run the MCP server
uv run python ./slideagent_mcp/server.py

# 3) In Claude Code (or Goose), connect to the MCP and issue prompts like:
#    - create a project, start the live viewer, list templates, etc.
```

Example prompts you can paste into Claude Code:

```text
Create a new project called "demo" using the "acme_corp" theme. Start the live viewer. Then scan everything in user_projects/demo/input/ and draft a crisp, section-based outline that maps each section to a specific slide template. Call out which template you plan to use per section and why.
```

```text
Read these links and build a slide deck with the acme_corp theme.
- https://www.example.com/industry-trends-2025
- https://news.example.org/company-q2-results
- https://analyst.example.net/sector-outlook
Also include one risks/mitigations slide and a next-steps slide.
```

```text
Make me a presentation based on the content I paste here, use the pokemon theme
<<< BEGIN CONTENT >>>
[ Paste long-form notes, meeting transcript, PDF text, or bullets here ]
<<< END CONTENT >>>
```

```text
Make a pie chart based on <INSERT CSV> using <INSERT THEME>
```

```text
Create a new theme called xyz_corp based on this input and color palette <INSERT COLORS + VIBE>
```

## How SlideAgent Works

`CLAUDE.md` is the system prompt and the authoritative process guide. The MCP layer exposes a small, safe toolset: list templates/themes, initialize slides/charts from templates with correct CSS/paths, start the live preview, and export PDFs. The model provides the content; MCP keeps structure, paths, and repeatability.

Typical capabilities provided by the MCP server(s):
- Discover context: list projects, themes, slide/chart templates
- Initialize from templates: slides and charts with correct paths/CSS
- Manage preview/export: start live viewer, generate PDF
- Optional validation: navigate and screenshot via a Puppeteer MCP

## Install and Run

### Using uv (recommended)
```bash
# One-time setup
curl -LsSf https://astral.sh/uv/install.sh | sh   # if uv not installed
uv sync
npm install

# Run MCP server
uv run python ./slideagent_mcp/server.py

# Run tests
uv run pytest tests/

# Add a dependency
uv add <package>
```

Notes:
- Use `uv sync` and `uv run`; no manual venv activation is needed.
- The virtual environment is managed automatically in `.venv/`.

### Alternative: plain venv + pip (if you really need it)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
uv pip sync pyproject.toml  # or: pip install -e .
npm install
python ./slideagent_mcp/server.py
```

## Core Workflows (via MCP prompts)

- **Create a project**: ask to "create a project named X with theme Y". This creates `user_projects/X/` with `slides/`, `plots/`, `input/`, `validation/`, and a project-local `theme/` folder containing the CSS and logos.
- **Discover templates**: ask to "list slide templates" and "list chart templates". Use exact paths returned when initializing.
- **Charts first**: ask to initialize a chart from a chosen template, then run the generated script inside the project (it outputs `_branded.png` and `_clean.png`).
- **Slides next**: initialize slides from templates and insert content and chart image paths (prefer `_clean.png` for slides).
- **Preview while building**: start the live viewer and navigate to the slide paths (the live viewer uses Chromium; what you see matches the PDF exporter).
- **Export PDF**: ask to generate the PDF for the project; it will save to `user_projects/<project>/<project>.pdf`.

## Troubleshooting

- **CSS not loading**: Always initialize slides via MCP. Slides should reference `../theme/base.css` and `../theme/<theme>_theme.css` relative to the `slides/` folder.
- **Live viewer issues**: Restart the live viewer; ensure the server is running. Preview URLs follow the per-project paths (e.g., `http://localhost:8080/slide_01.html`).
- **PDF generation**: If slides look correct in the live viewer, PDFs should match (Chromium-based exporter).
- **Puppeteer MCP**: Install globally if you want browsing/screenshot validation:
  - `npm install -g @modelcontextprotocol/server-puppeteer`
  - Add it to your client (Claude/Goose) if not auto-detected.
- **uv basics**: `uv sync` (install/update), `uv run <cmd>`, `uv add <pkg>`, `uv run pytest tests/`.

## Use with Goose

You can also drive SlideAgent from Goose: [`https://block.github.io/goose/`](https://block.github.io/goose/).

Connect Goose to SlideAgent MCP:
- If not auto-detected, add an MCP server in Goose "Extensions" with:
  - `uv run python ./slideagent_mcp/server.py`
- If you installed the Puppeteer MCP globally, add it too for browsing/screenshots.
- Optionally copy `CLAUDE.md` to `.goosehints` (Goose's system prompt management).

## Why uv?

- **Fast**: significantly faster than pip
- **Reliable**: lock file for reproducible installs
- **Simple**: no manual venv activation
- **Modern**: a cleaner replacement for pip/pip-tools/pipenv/poetry/virtualenv

---

# Musings about AI Agents
This project is my contribution to the world of open model benchmarks. It is a living qualitative benchmark of what today’s AI agents can and can’t do. Slide generation is an interesting stress test — it demands structured reasoning, precise layouts, and adaptation to tight visual constraints, all within long-horizon tasks that span multiple files, coordinate sub-agents, and require fine-grained visual and spatial reasoning.

Right now, the weak spots are clear:
Pixel-level multimodal understanding is still shaky. Models struggle to place and size elements with exactness, which leads to overlapping content or overflowing slides.

Vertical report generation often fails because page length and spacing aren’t dynamically managed easily by the models.

Complex slide layouts can break when multiple charts, text blocks, or images compete for limited real estate.

The model is not very smart about checking its work and iterating, often losing track of the goal or ignoring obvious fixes.

All of these will improve as base models improve. Yes, there are “engineering fixes” I could add today to paper over these issues. But the point of SlideAgent is not to make a quality product that addresses the weaknesses of the current generation of models. The point is to ride the curve of model improvement — to keep the system minimal so it reflects exactly what the raw model can do, without product-specific scaffolding that will turn into legacy baggage.

If you believe in The Bitter Lesson, you expect that the most successful slide generators of the future won’t be the ones with the most elaborate domain-specific code; they’ll be the ones that let the model do the work. If you really believe the Bitter Lesson you will ponder whether this is true for every piece of application software in the world. Right now, there are highly capable, well-funded products that outperform this project because they’ve built a lot of specialized tooling around today’s limitations. But eventually, much of that tooling will be obsolete — just extra weight when the base models are strong enough to handle the task directly.

So SlideAgent is a benchmark in two senses:

Performance tracking — seeing how raw models measure up against highly engineered systems over time.

Philosophical testing — measuring how close we are to the point where “pure model” approaches beat “great product work with guardrails.”

The day a minimal agent like SlideAgent consistently beats a purpose-built, feature-rich slide generator… that will be a sign that the AI models have crossed a major threshold.