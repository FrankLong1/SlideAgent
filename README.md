# SlideAgent

Minimal presentation framework for AI agents. This README is intentionally short: two sections (System Prompt, MCP) and a Quick Start you can copy-paste into Claude Code. 

## Quick Start

Honestly Claude Code should be able to do just about all of the environment setup, just ask it to "get my environment setup and make sure the mcp is working". After that is taken care of you can put in things like..

```text
Create a new project called "demo" using the "acme_corp" theme. Start the live viewer. Then scan everything in projects/demo/input/ and draft a crisp, section-based outline that maps each section to a specific slide template. Call out which template you plan to use per section and why.
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
Create a new theme called xyz_corp based on this input and color palette <INSERT SOME DIRECTION ON COLORS AND VIBE>
```

## All the Logic: CLAUDE.md + slideagent_mcp folder

 `CLAUDE.md` is the system prompt and authoritative source of process and is written to maximally depend on the decision making of the model, keeping actual programming logic minimal in alignment with [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html). Read `CLAUDE.md` for detailed guidance when you need more than the quick start, as the system prompt gives much more detail about how all this works.

The MCP layer exposes a small set of tools that let models operate SlideAgent safely and consistently. Think of it as a context management and orchestration layer, not an application: it lists templates and themes, initializes slides/charts, swaps themes, starts the live preview, and exports PDFs. It contains almost no business logic—the model provides the content; MCP ensures correct file structure, paths, and repeatable operations.

Typical capabilities provided by the MCP server(s):
- Discover and read context: list projects, themes, slide/chart templates
- Initialize from templates: create slides and charts with correct paths and CSS
- Manage preview/export: start live viewer, generate PDF (simple utility logic only)
- Optional browsing/validation: navigate and screenshot via a Puppeteer MCP

## What does the system struggle with?

### Dynamic Layout Adaptation
The system faces challenges with responsive content placement, particularly:

- **Chart aspect ratios**: Charts need different dimensions depending on context:
  - Single-chart slides: 16:9 aspect ratio (14x7.875 figsize)
  - 4-chart dashboards: 2:1 aspect ratio (7x3.5 figsize) 
  - 6-chart grids: Even more square ratios needed
  - The same chart can't work well in both contexts without regeneration

- **Overflow management**: Content frequently overflows slide boundaries because:
  - Fixed 1920x1080px dimensions don't account for headers/footers
  - Chart images don't automatically resize to fit containers
  - CSS `object-fit: contain` helps but isn't perfect
  - Multi-chart layouts compound the spacing challenges
- **Container sizing**: The interplay between padding, margins, and actual content area

There are things that could be implemented that would improve these things, but if you believe the bitter lesson you would do none of these things and ride the curve of model improvement, rather than building point-in-time optimizations that will become legacy.

## Dependency Management with uv

SlideAgent uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python dependency management. Here's everything you (or Claude) need to get started:

### Initial Setup (One-time)
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repo
git clone https://github.com/yourusername/SlideAgent.git
cd SlideAgent

# Install all dependencies (creates .venv automatically)
uv sync

# Install Node dependencies for PDF generation
npm install
```

### Daily Usage
```bash
# Run any Python command in the virtual environment
uv run python slideagent_mcp/server.py

# Run tests
uv run pytest tests/

# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade
```

### For Claude Code
When working with this project:
1. First run: `uv sync` to ensure all dependencies are installed
2. Then run: `npm install` for Node.js dependencies  
3. Use `uv run` prefix for any Python commands
4. The virtual environment is managed automatically in `.venv/`

### Why uv?
- **Fast**: 10-100x faster than pip
- **Reliable**: Lock file ensures reproducible installs
- **Simple**: No manual venv activation needed
- **Modern**: Replaces pip, pip-tools, pipenv, poetry, virtualenv
