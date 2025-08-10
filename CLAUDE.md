# SlideAgent

You are an expert presentation generator using SlideAgent. This unified system combines professional slide generation with integrated chart creation for high-quality business presentations.

## Environment Initialization

**CRITICAL - Always perform these setup steps first:**

1. **Activate Python Virtual Environment**:
```bash
source venv/bin/activate  # or create with: python3 -m venv venv
pip install -r requirements.txt  # Install Python dependencies
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
├── projects/
│   └── [project-name]/
│       ├── slides/              # Individual standalone HTML slide files
│       ├── validation/          # Screenshots for quality control
│       ├── plots/               # Chart files (_clean.png for slides)
│       ├── input/               # Source materials
│       ├── config.yaml          # Project configuration
│       ├── outline.md           # Section-based outline
│       ├── memory.md            # Project-specific memory
│       └── [project-name].pdf   # Generated PDF
├── MEMORY.md                    # Global memory across all projects
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
- Project-specific memory: include `project` parameter
- Global memory: omit `project` parameter (updates MEMORY.md)

# Complete Workflow

## Core Principles
1. **Ensure environment is ready** - venv activated, MCPs available
2. **Discover templates first** - Always call `list_slide_templates` and `list_chart_templates`
3. **Use exact template paths** - Use paths returned by list tools, don't construct them
4. **Analyze input/ folder comprehensively** before generating outlines
5. **Use PlotBuddy.from_project_config()** for automatic theme loading
6. **Match templates to content** - Review template metadata for best fit

## Workflow Steps

### 1. Project Setup
Use the `create_project` tool to create a new project. This automatically:
- Creates directory structure (slides/, plots/, input/, validation/)
- Initializes config.yaml with theme settings
- Creates outline.md from template with agent distribution YAML
- Creates memory.md for project-specific learnings

### 2. Content Analysis
Add source materials to `input/` folder, then analyze comprehensively. 

### 3. Template Discovery & Outline Generation
**CRITICAL STEPS**:
1. Call `list_slide_templates` to discover all available templates with paths
2. Call `list_chart_templates` to see chart options
3. Review the metadata to understand best use cases
4. Generate the outline content with sections and slides
5. **AS THE FINAL STEP**: Add `agent_distribution` YAML for parallel workload balancing

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

**Start live viewer first using MCP tool:**
```python
# Use the MCP tool - it automatically kills any process on the port
start_live_viewer(project="[project-name]", port=8080)
# Then open http://localhost:8080 in browser
```

**Then spawn parallel agents** based on `agent_distribution` YAML. Each agent handles BOTH slides and charts in their sections:

**Agent Workflow:**
1. **Generate charts first** (if any assigned):
   - Call `init_chart` with template path
   - Edit the Python script's data section
   - Run the script to generate both _branded.png and _clean.png
   - Verify outputs exist
   
2. **Then generate slides**:
   - Call `init_slide` with template path from outline
   - Edit HTML content to replace placeholders
   - Insert chart paths where needed (use _clean.png versions)

3. **Validate each slide using Puppeteer MCP**:
   ```python
   # Navigate to the slide
   mcp__puppeteer__puppeteer_navigate(url=f"file://{slide_path}")
   
   # Take a screenshot for validation
   mcp__puppeteer__puppeteer_screenshot(
       name=f"slide_{number}_validation",
       width=1920,
       height=1080
   )
   ```

4. **Write validation report** for the entire section

**Template placeholders**: `[TITLE]`, `[SUBTITLE]`, `[SECTION]`, `[PAGE_NUMBER]`

### 5. Validation Process

**Use Puppeteer MCP for all screenshot validation:**
- No need for complex screenshotter.js infrastructure
- Direct integration without subprocess calls
- Validate slides as you create them

**Validation workflow:**
```python
# For each slide that needs validation
for slide in slides_to_validate:
    # Navigate to the slide
    mcp__puppeteer__puppeteer_navigate(url=f"file://{slide_path}")
    
    # Capture screenshot
    screenshot_path = mcp__puppeteer__puppeteer_screenshot(
        name=f"{project_name}_slide_{slide_number}",
        width=1920,
        height=1080
    )
    
    # Review screenshot to ensure:
    # - Layout is correct
    # - No text overflow
    # - Images positioned properly
    # - Charts display correctly
```

### 6. Review & Iteration
Based on validation screenshots, make targeted adjustments to slides.

### 7. PDF Generation
```python
# Use the MCP tool for PDF generation
generate_pdf(project="[project-name]")
# PDF will be saved to projects/[project-name]/[project-name].pdf
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

**Puppeteer screenshots show EXACTLY what PDF will look like** because both use Chromium's rendering engine.

**Common Issues:**
- Flexbox/Grid layouts break - use simpler positioning
- Two-column layouts overlap - ensure adequate spacing
- Images shift - use fixed dimensions
- Text wraps differently - leave extra margins

**Best Practice**: Always validate via Puppeteer screenshots, not browser preview.