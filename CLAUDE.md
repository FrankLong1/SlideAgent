# SlideAgent

You are an expert presentation generator using SlideAgent. This unified system combines professional slide generation with integrated chart creation for high-quality business presentations.

MAKE SURE TO ALWAYS ACTIVATE THE VENV BEFORE DOING ANYTHING.

## Project Management via MCP

SlideAgent provides all project operations through MCP (Model Context Protocol) tools. The MCP server is configured in `.mcp.json` and provides automatic tool discovery. You can also use slideagent.py directly for CLI operations if needed.

**Key MCP Tools Available:**
- `create_project` - Create new projects with proper structure
- `list_projects` - View all projects
- `list_themes` - See available themes  
- `init_slide` - Initialize slides from templates
- `init_chart` - Initialize charts from templates
- `list_slide_templates` - Discover slide templates with paths and metadata
- `list_chart_templates` - Discover chart templates with paths and metadata
- `get_outline` - Read project outlines
- `update_memory` - Track learnings and improvements
- `swap_theme` - Change project theme

## Directory Structure

```
SlideAgent/
├── src/
│   ├── charts/
│   │   ├── chart_templates/     # Self-documenting chart templates
│   │   └── utils/
│   │       └── plot_buddy.py    # Main chart generation class
│   ├── slides/
│   │   ├── base.css             # Core slide styling & PDF optimization
│   │   └── slide_templates/     # Self-documenting slide templates (17 total)
│   └── utils/
│       ├── pdf_generator.js     # PDF generation script
│       └── screenshotter.js     # Screenshot utility for validation
├── themes/
│   ├── examples/                # Example themes for reference
│   │   └── acme_corp/           # Default professional theme
│   └── private/                  # Custom/client-specific themes
├── projects/
│   └── [project-name]/
│       ├── slides/              # Individual standalone HTML slide files
│       ├── validation/          # Quality control
│       ├── plots/               # Chart files (_clean.png for slides)
│       ├── input/               # Source materials
│       ├── config.yaml          # Project configuration
│       ├── outline.md           # Section-based outline
│       ├── memory.md            # Project-specific memory
│       └── [project-name].pdf   # Generated PDF
├── MEMORY.md                    # Global memory across all projects
├── slideagent.py                # CLI & MCP server implementation
└── .mcp.json                    # MCP server configuration
```

## Template Discovery

**CRITICAL**: Always call these tools before creating outlines or content:
- Use `list_slide_templates` to discover all available slide templates with their paths
- Use `list_chart_templates` to discover all chart templates with their paths
- Templates are self-documenting with metadata about use cases and best practices
- Use the EXACT paths returned by these tools in your outline and when calling init tools

## Chart Generation

### Slide-Optimized Chart Guidelines
When generating charts for slides:

#### Chart Dimensions & Aspect Ratio
- **Use 16:9 aspect ratio** for slide charts: `figsize=(14, 7.875)`
- **Never use square charts** for slides - they waste horizontal space
- **Full-image slides**: Use even wider ratios to maximize coverage

#### Clean Version Requirements (for slides)
- **NO TITLES in clean versions** - the slide header provides the title
- **Include ONLY descriptive subtitles** if needed
- **Keep axis labels and legends** but position them efficiently
- **Position legends on the RIGHT**: Use `bbox_to_anchor=(1.05, 0.5)`

### Chart Generation Process
1. **Discover templates**: Call `list_chart_templates` to see available options
2. **Initialize from template**: Use `init_chart` with the template path
3. **Edit the EDIT SECTION**: Modify only the data and configuration
4. **Run the script**: `cd projects/[project] && python plots/[chart_name].py`
5. **Get both versions**: Automatically generates `_branded.png` and `_clean.png`

## Theme System

Each theme contains 4 files:
- `[theme]_theme.css` - Slide styling (colors, fonts)
- `[theme]_style.mplstyle` - Chart styling (matplotlib)
- `[theme]_icon_logo.png` - Icon logo for headers (PNG format)
- `[theme]_text_logo.png` - Text logo for title slides (PNG format)

### Logo Requirements
**IMPORTANT**: Always use authentic logos in PNG format:
- **DO NOT create custom SVG logos** - trademark violations
- **USE PNG format** for logos
- **RESPECT brand guidelines**
- For private/corporate themes, store in `themes/private/`

### CSS Path Management
**Required CSS paths from slide location** (`projects/[project]/slides/`):
```html
<link rel="stylesheet" href="../../../src/slides/base.css">
<link rel="stylesheet" href="../../../themes/[theme-location]/[theme]_theme.css">
```

## Critical Header Structure

**ALWAYS follow this exact header structure for slides with headers:**
```html
<div class="header">
    <div class="header-left">
        <!-- Main slide content titles go here -->
        <div class="slide-title">Main Title</div>
        <div class="slide-subtitle">Subtitle text</div>
    </div>
    <div class="header-right">
        <!-- Section represents broader topic spanning multiple slides -->
        <div class="section-label">Section Name</div>
        <!-- Logo automatically styled via CSS -->
        <div class="logo" alt="Company Name"></div>
    </div>
</div>
```

**Note**: Title slides use a different structure - they display `[TITLE]` and `[SUBTITLE]` prominently in the center, not in the header.

## Memory System

SlideAgent tracks learnings and improvements:
- **`MEMORY.md`** - Global memory across all projects
- **`projects/[project]/memory.md`** - Project-specific discoveries

Use the `update_memory` tool to track:
- What's working (section: "working")
- What's not working (section: "not_working")  
- Ideas & improvements (section: "ideas")

# Complete Workflow

## Core Principles
1. **Use MCP tools for all operations** - Don't manually create files or structure
2. **Discover templates first** - Always call `list_slide_templates` and `list_chart_templates`
3. **Use exact template paths** - Use paths returned by list tools, don't construct them
4. **Activate venv first** for chart generation: `source venv/bin/activate`
5. **Analyze input/ folder comprehensively** before generating outlines
6. **Use PlotBuddy.from_project_config()** for automatic theme loading
7. **Match templates to content** - Review template metadata for best fit

## Workflow Steps

### 1. Project Setup
Use the `create_project` tool to create a new project with proper structure.

### 2. Content Analysis
Add source materials to `input/` folder, then analyze comprehensively.

### 3. Template Discovery & Outline Generation
**CRITICAL STEPS**:
1. Call `list_slide_templates` to discover all available templates with paths
2. Call `list_chart_templates` to see chart options
3. Review the metadata to understand best use cases
4. Generate `outline.md` using the EXACT template paths returned:

```yaml
agent_distribution:
  agent_1:
    sections: ["Introduction", "Main Analysis"]
    slides: [1-5]
```

```markdown
# Section 1: Introduction (slides 1-2)
## Slide 1: Title Slide
- Template: src/slides/slide_templates/00_title_slide.html  # Use exact path from list_templates
- Content: Project Title, Author, Date
```

### 4. Chart Generation
Use `init_chart` with template paths from `list_chart_templates`.

### 5. Parallel Slide Generation

**Start live viewer first:**
```bash
pkill -f "node.*live_viewer_server"  # Stop existing
node src/utils/live_viewer_server.js [project-name]
open http://localhost:8080
```

**Then spawn parallel agents** based on `agent_distribution` YAML. Each agent:
1. Calls `init_slide` with template path from outline
2. Edits HTML content to replace placeholders
3. Runs screenshotter for validation
4. Writes validation report

**Template placeholders**: `[TITLE]`, `[SUBTITLE]`, `[SECTION]`, `[PAGE_NUMBER]`

### 6. Review & Iteration
Based on validation reports, make targeted adjustments.

### 7. PDF Generation
```bash
node src/utils/pdf_generator.js projects/[project-name]/slides/
open projects/[project-name]/[project-name].pdf
```

## CSS Architecture

**Two-Layer Structure:**
1. **`src/slides/base.css`** - Foundation (layout, typography, dimensions)
2. **`themes/`** - Brand Identity (colors, fonts, logos)

**Design Philosophy:**
- Fixed 16:9 dimensions (1920x1080px)
- PDF-safe CSS only (no shadows, gradients, opacity<1)
- Static design (no animations)
- Professional appearance (no emojis)

## Critical HTML vs PDF Rendering

**WARNING**: Browser rendering ≠ PDF rendering. Screenshots show EXACTLY what PDF will look like.

**Common Issues:**
- Flexbox/Grid layouts break - use simpler positioning
- Two-column layouts overlap - ensure adequate spacing
- Images shift - use fixed dimensions
- Text wraps differently - leave extra margins

**Best Practice**: Always validate via screenshots, not browser preview.