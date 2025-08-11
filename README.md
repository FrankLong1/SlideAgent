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

 `CLAUDE.md` is the system prompt and authoritative source of process and written to maximally depend on the decision making of the model, and keep actual programming logic minimal. Read `CLAUDE.md` for detailed guidance when you need more than the quick start, as the system prompt gives much more detail about how all this works.

The MCP layer exposes a small set of tools that let models operate SlideAgent safely and consistently. Think of it as a context management and orchestration layer, not an application: it lists templates and themes, initializes slides/charts, swaps themes, starts the live preview, and exports PDFs. It contains almost no business logic—the model provides the content; MCP ensures correct file structure, paths, and repeatable operations.

Typical capabilities provided by the MCP server(s):
- Discover and read context: list projects, themes, slide/chart templates
- Initialize from templates: create slides and charts with correct paths and CSS
- Manage preview/export: start live viewer, generate PDF (simple utility logic only)
- Optional browsing/validation: navigate and screenshot via a Puppeteer MCP

