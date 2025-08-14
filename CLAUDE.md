# SlideAgent

You are an expert presentation generator using SlideAgent - a unified system for professional slides with integrated charts.

## Quick Setup

1. **Install dependencies**: `uv sync && npm install`
2. **Verify MCP tools**: The SlideAgent MCP tools should be available automatically via `.mcp.json`
3. **One-time Puppeteer setup** (if needed):
   ```bash
   npm install -g @modelcontextprotocol/server-puppeteer
   claude mcp add puppeteer
   ```
   
## Core Concepts

### Project Structure
- **Projects are self-contained** with their own `theme/` folder containing all CSS and assets
- **User space**: `user_projects/` and `user_resources/` for custom content  
- **System space**: `slideagent_mcp/` - don't modify unless explicitly asked

### Path Rules
From slides folder:
- CSS: `../theme/slide_base.css` and `../theme/{theme}_theme.css`
- Charts: Use `_clean.png` for slides (no titles), `_branded.png` for reports

### Theme System
Each theme needs 4 files:
- `{theme}_theme.css` - Slide styling
- `{theme}_style.mplstyle` - Chart styling  
- `{theme}_icon_logo.png` - Header logo
- `{theme}_text_logo.png` - Title slide logo

**Important**: Use PNG logos only (no custom SVGs - trademark issues)

## Workflow

### 1. Prepare Input
- Copy source materials to `user_projects/{project}/input/`
- Read and analyze ALL input files before outlining

### 2. Generate Outline

**Format Requirements**:
```markdown
# Project Title

# Section Name (slides X-Y)     ← Single # for sections
## Slide X: Title               ← Double ## for slides
- Template: template_name.html  ← Just filename
- Content: [ACTUAL DETAILED DATA - not placeholders]

agent_distribution:
  agent_1:
    sections: ["Section 1"]
    slides: [1-5]
```

**Content must be specific**: Include real numbers, quotes, data points from source materials.

### 3. Generate Content

**Start live viewer first before spawning agents** (use `start_live_viewer()`)

**Then spawn parallel agents** based on `agent_distribution`:
- Each agent handles assigned slides/charts using `init_from_template()`
- Agents validate visually with Puppeteer screenshots
- Fix issues immediately if detected
- To stop viewer when done: `pkill -f "node.*live_viewer"`

### 4. Generate PDF
Use `generate_pdf()` with format="slides" (horizontal) or "report" (vertical)

## Chart Guidelines

### For Slides
- **16:9 aspect ratio**: `figsize=(14, 7.875)`
- **Use _clean.png** versions (no titles - slide provides them)
- **Legends on right**: `bbox_to_anchor=(1.05, 0.5)`

### Clean vs Branded
- **Clean** (`_clean.png`): For slides - no titles/logos
- **Branded** (`_branded.png`): For reports - full titles/logos/sources

## Header Structure
```html
<div class="header">
    <div class="header-left">
        <div class="slide-title">Main Title</div>
        <div class="slide-subtitle">Subtitle</div>
    </div>
    <div class="header-right">
        <div class="section-label">Section</div>
        <div class="logo"></div>
    </div>
</div>
```

## Remember
- Discover templates first with `get_templates()` before creating content
- Be specific in outlines - no placeholders  
- Validate visually with Puppeteer
- PlotBuddy.from_project_config() loads theme automatically
- All discovery functions (`get_*`) accept flexible arguments