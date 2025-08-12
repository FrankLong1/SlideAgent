# SlideAgent

You are an expert presentation generator using SlideAgent. This unified system combines professional slide generation with integrated chart creation for high-quality business presentations.

## Environment Initialization

**CRITICAL - Always perform these setup steps first:**

1. **Setup Python Dependencies with uv**:
```bash
# Install all Python dependencies (creates .venv automatically)
uv sync
# No need to activate venv - use 'uv run' prefix for commands
```

2. **Install Node.js Dependencies**:
```bash
npm install  # Required for PDF generation and live viewer
```

3. **Setup MCP Servers**:

**SlideAgent MCP Helper** (automatically configured):
- The `.mcp.json` file in this project already configures the SlideAgent MCP helper server
- Provides project management tools specific to SlideAgent
- Automatically available when you open this project in Claude Code

**Puppeteer MCP** (needs one-time global setup):
```bash
# Install Puppeteer MCP server globally (only needed once per machine)
npm install -g @modelcontextprotocol/server-puppeteer

# Add to Claude globally (only needed once)
claude mcp add puppeteer
```

4. **Verify MCP Tools are Available**:
- Test SlideAgent tools: Try calling `list_projects()` or `list_themes()`
- Test Puppeteer tools: Check for `mcp__puppeteer__puppeteer_navigate` availability
- If tools are missing, restart Claude Code or check MCP server logs
 
5. **Initialize user directory structure**:
```bash
mkdir -p user_projects \
         user_resources/themes \
         user_resources/templates/slides \
         user_resources/templates/charts \
         user_resources/templates/outlines
```

Anytime that the user is making themes or asking to save templates for slides / charts / outlines, do it all in here. By default we should treat slideagent_mcp as system space so it should not be touched unless you are extremely explicitly asked.

## Project Management via MCP

SlideAgent provides all project operations through MCP (Model Context Protocol) tools. The MCP server is configured in `.mcp.json` and provides automatic tool discovery.

**Available MCP Servers:**
- **slideagent**: Project management, templates, themes (local to this project)
- **puppeteer**: Browser automation for validation (mcp__puppeteer_* tools)

## Directory Structure

```
SlideAgent/
├── slideagent_mcp/              # SlideAgent MCP helper server
│   ├── server.py                # FastMCP server implementation
│   ├── pdf_generator.js         # PDF generation utility
│   └── live_viewer_server.js    # Live preview server
├── src/
│   ├── charts/
│   │   ├── chart_templates/     # Self-documenting chart templates
│   │   └── utils/
│   │       └── plot_buddy.py    # Main chart generation class
│   └── slides/
│       ├── base.css             # Core slide styling & PDF optimization
│       └── slide_templates/     # Self-documenting slide templates
├── themes/
│   ├── examples/                # Example themes for reference
│   │   └── acme_corp/           # Default professional theme
│   └── private/                  # Custom/client-specific themes
├── user_projects/               # All user projects
│   └── [project-name]/
│       ├── theme/               # Project-local theme files (self-contained)
│       │   ├── base.css         # Copy of core CSS
│       │   ├── [theme]_theme.css# Theme-specific CSS
│       │   ├── [theme]_icon_logo.png  # Icon logo
│       │   └── [theme]_text_logo.png  # Text logo
│       ├── slides/              # Individual standalone HTML slide files
│       ├── validation/          # Screenshots for quality control
│       ├── plots/               # Chart files (_clean.png for slides)
│       ├── input/               # Source materials
│       ├── outline.md           # Section-based outline
│       └── [project-name].pdf   # Generated PDF
├── .mcp.json                    # MCP server configuration
├── package.json                 # Node.js dependencies
└── requirements.txt             # Python dependencies
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
4. **Run the script**: `cd user_projects/[project] && python plots/[chart_name].py`
5. **Get both versions**: Automatically generates `_branded.png` and `_clean.png`

### Clean vs Branded Chart Usage
**CRITICAL**: Understanding when to use each chart version:

#### Clean Versions (`_clean.png`)
- **ALWAYS use for slides** - slides already have headers/titles
- No chart titles or subtitles (removed by PlotBuddy)
- No logos or branding elements
- No source citations at bottom
- Preserves only essential data elements (axes, labels, data)

#### Branded Versions (`_branded.png`)
- Use for standalone documents or reports
- Includes full titles and subtitles
- Has logo placement
- Shows source citations
- Complete self-contained chart

#### Why This Matters
- Slides have their own header structure with titles
- Using branded charts in slides creates **redundant titles**
- Clean versions integrate seamlessly into slide layouts
- Prevents overflow and maintains professional appearance

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
 - For private/corporate themes, store in `user_resources/themes/[theme]/`

### CSS Path Management
**IMPORTANT**: Projects are self-contained with their own theme folder.

**CSS paths in all slides** (from `slides/` folder):
```html
<link rel="stylesheet" href="../theme/base.css">
<link rel="stylesheet" href="../theme/[theme]_theme.css">
```

When you use `init_slide` MCP tool, these paths are automatically set correctly. The theme files are copied to each project during `create_project`.

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

# Complete Workflow

## Core Principles
1. **Ensure environment is ready** - venv activated, MCPs available
2. **Discover templates first** - Always call `list_slide_templates` and `list_chart_templates`
3. **Use exact template paths** - Use paths returned by list tools, don't construct them
4. **Analyze input/ folder comprehensively** before generating outlines
5. **Use PlotBuddy.from_project_config()** for automatic theme loading
6. **Match templates to content** - Review template metadata for best fit

## CSS Architecture

**Two-Layer Structure:**
1. **`src/slides/base.css`** - Foundation (layout, typography, dimensions)
2. **`themes/`** - Brand Identity (colors, fonts, logos)

**Design Philosophy:**
- Fixed 16:9 dimensions (1920x1080px)
- PDF-safe CSS only (no shadows, gradients, opacity<1)
- Static design (no animations)
- Professional appearance (no emojis)

## Workflow Steps

### 1. Project Setup
Use the `create_project` MCP tool to create a new project. This automatically:
- Creates directory structure (slides/, plots/, input/, validation/, theme/)
- Copies base.css and all theme files to project's theme/ folder
- Makes project self-contained with all necessary CSS and assets
- Copies theme files to project-local theme/ folder
- Creates outline.md template

### 2. Content Analysis & Input Preparation

**CRITICAL**: Before generating any outline, you MUST:
1. **Copy/Move source materials** to `user_projects/[project-name]/input/` folder
   - For HTML files (like S1 filings): Copy to input folder, and it probably makes sense to write a quick and dirty script within the project folder to strip out the html and have a cleaner version that goes into the outline.
   - For PDFs, docs, spreadsheets: Copy to input folder
   - For web content: Save as HTML or text in input folder
2. **Verify files are in input folder** using LS tool
3. **Read and analyze ALL files** in input folder comprehensively
4. **Extract specific data points** (numbers, dates, quotes, facts) for the outline


### 3. Template Discovery & Outline Generation

**CRITICAL OUTLINE FORMAT** (Required for live viewer to work):
```markdown
# Project Title

# Section 1: Section Name (slides X-Y)    ← Use single # for sections
## Slide X: Slide Title                   ← Use double ## for slides
- Template: src/slides/slide_templates/00_title_slide.html
- Content: [DETAILED CONTENT - see below for requirements]
```

**IMPORTANT FORMAT RULES**:
- Use `#` (single hash) for section headers, NOT `##` 
- Use `##` (double hash) for slide headers, NOT `###`
- Include `(slides X-Y)` in section headers

**CRITICAL CONTENT REQUIREMENTS**:
The outline should contain **ACTUAL DETAILED CONTENT** for each slide, not placeholders. Since the outline has direct access to the raw source context, it should include:

- **Bias toward verbosity and specificity in the outline**: It's closest to source ingestion, so include exact numbers, quotes, labels, and chart references. Richer outlines produce better slides.

- **For text slides**: Complete bullet points, full sentences, specific data points
- **For data tables**: Actual numbers, percentages, dollar amounts with proper formatting
- **For comparison slides**: Specific comparison points, metrics, advantages/disadvantages
- **For quote slides**: The exact quote text and attribution
- **For timeline slides**: Specific dates, milestones, and descriptions
- **For chart slides**: Exact data values, axis labels, legend items
- **For architecture slides**: Component names, relationships, descriptions

**TEMPLATE SELECTION FLEXIBILITY**:
- **Use templates that match your content**, generally variety is nice, but please make sure it's actually the right format for the content
- **Repeat templates as needed** - it's fine to have 10 consecutive base slides
- **Use ANY slide templates in ANY order and Skip templates that don't fit** - don't force content into inappropriate templates

**Example of GOOD detailed content**:
```markdown
## Slide 2: Financial Performance
- Template: src/slides/slide_templates/07_financial_data_table.html
- Content:
  - Revenue FY2024: $1.9B (737% YoY growth)
  - Revenue FY2023: $229M (1,346% YoY growth)  
  - Revenue FY2022: $16M
  - Gross Margin: 42% (up from 38% in FY2023)
  - Operating Loss: ($863M) in FY2024
  - Adjusted EBITDA: ($65M) vs ($45M) in FY2023
  - Cash & Equivalents: $450M
  - Total Debt: $8.0B
  - RPO (Remaining Performance Obligations): $15.1B
```

**Example of BAD placeholder content**:
```markdown
## Slide 2: Financial Performance
- Template: src/slides/slide_templates/07_financial_data_table.html
- Content: Financial metrics and performance data
```

**CRITICAL STEPS**:
1. Call `list_slide_templates` to discover all available templates with paths
2. Call `list_chart_templates` to see chart options
3. Review the metadata to understand best use cases
4. **EXTRACT DETAILED CONTENT** from source materials (input files, S1 filings, etc.)
5. Generate the outline with **COMPLETE, SPECIFIC CONTENT** for each slide
6. **AS THE FINAL STEP**: Add `agent_distribution` YAML for parallel workload balancing

**Agent Distribution (Workload Balancing):**
The `agent_distribution` YAML defines how work is divided among parallel agents. Add this **AFTER** creating your full outline, considering:
- **Slide complexity weighting** - Complex templates (tables, matrices, dashboards) count more than simple ones
- **Balanced workload** - Aim for even distribution, not just equal slide counts

**Complexity Weights for Load Balancing:**
- Simple slides (title, base, quote): 1x weight
- Medium slides (two-column, text+image): 1.5x weight  
- Complex slides (tables, matrices, dashboards): 2x weight

```yaml
# Add this AFTER outline is complete, based on complexity analysis
agent_distribution:
  agent_1:
    sections: ["Introduction", "Market Analysis"]
    slides: [1-5]  # 2 simple + 3 medium = ~6 weight units
  agent_2:
    sections: ["Financial Data"]
    slides: [6-9]  # 2 complex tables + 2 charts = ~8 weight units
  agent_3:
    sections: ["Implementation", "Conclusion"]
    slides: [10-15]  # 4 simple + 2 medium = ~7 weight units
```

```markdown
# Section 1: Introduction (slides 1-2)
## Slide 1: Title Slide
- Template: src/slides/slide_templates/00_title_slide.html  # Use exact path from list_templates
- Content: Project Title, Author, Date
```

### 4. Parallel Slide & Chart Generation

**IMPORTANT: You MUST start the live viewer using the MCP tool BEFORE spawning any agents. This is a required prerequisite so the user can watch progress.**

**Then spawn parallel agents** based on `agent_distribution` YAML using Claude Code's Task tool. Each agent handles BOTH slides and charts in their assigned sections:

**Example spawning parallel agents:**
```python
# After reading the outline's agent_distribution YAML, spawn agents in parallel:
# Each agent works on their assigned sections/slides independently

# Example for a project with 3 agents defined in agent_distribution:
Task(
    subagent_type="general-purpose",
    description="Generate and review slides 1-5",
    prompt="[Agent prompt]"
)

Task(
    subagent_type="general-purpose", 
    description="Generate and review slides 6-9",
    prompt="[Agent prompt]"
)

Task(
    subagent_type="general-purpose",
    description="Generate and review slides 10-15",
    prompt="[Agent prompt]"
)

# All three agents run simultaneously, drastically reducing generation time
```

#### **Agent Workflow**
1. **Charts first**
   - Use `init_chart` MCP tool with the exact template path from `list_chart_templates`
   - Edit data/config only (EDIT SECTION)
   - Run → outputs `_branded.png` and `_clean.png`
   - Verify files exist

2. **Slides next**
   - Use `init_slide` MCP tool with the exact template path from `list_slide_templates`
   - The MCP tool automatically sets correct CSS paths to ../theme/
   - Replace placeholders with detailed content from outline
   - Insert chart paths (use `_clean.png` versions)

3. **Visual validation by agents**
   - Use Puppeteer MCP (navigate + screenshot) after creating each slide
   - Visually inspect screenshots for quality issues:
     * Professional appearance and layout
     * No text overflow or cutoff
     * Proper spacing and alignment
     * No redundant titles (especially in chart slides)
   - Trust AI visual judgment rather than complex programmatic checks
   - Fix issues immediately if something looks wrong

### 5. PDF Generation
Use the PDF tool from the SlideAgent MCP to generate the project PDF (saved to `user_projects/[project-name]/[project-name].pdf`).


## Troubleshooting

### CSS Not Loading in Slides
- **Always use MCP tools** (`init_slide`) which set paths automatically
- CSS paths should be: `../theme/base.css` and `../theme/[theme]_theme.css`
- Each project has its own `theme/` folder with all necessary files
- Never use paths like `../../../src/slides/` or `../../../themes/`

### Live Viewer Issues
- Restart live viewer if CSS changes: `stop_live_viewer` then `start_live_viewer`
- Live viewer serves from project root, so paths are relative to that
- Check http://localhost:8080/slide_01.html for preview

### PDF Generation
- PDF generator uses Chromium, same as live viewer
- If slides look correct in live viewer, PDF will be correct
- Always generate PDF after all slides are complete

## General Notes
- Projects are self-contained - all CSS and assets are copied to project/theme/
- Always use MCP tools for consistency
- Path issues usually mean not using MCP tools correctly