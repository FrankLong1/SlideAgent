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

**Important**: Use PNG logos only (no custom SVGs)

## Workflow

### 0. Project Setup & Discovery
**CRITICAL: Always check if project exists first before creating**

1. **Check for existing project**: Use `get_projects(project_name)` to see if project already exists
2. **If project exists**: 
   - Examine existing content in `user_projects/{project}/`
   - Check `slides/` folder for completed slides
   - Check `input/` folder for source materials
   - Check `outline.md` if it exists
   - Resume workflow from appropriate step based on what's already completed
3. **If project doesn't exist**: Create new project with `create_project(name, theme="acme_corp")`
4. **Always inspect project structure** before proceeding to understand current state

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

**Slide Template Variety**: Use diverse slide templates throughout presentations:
- **00_title_slide.html**: Opening slides and section dividers
- **01_base_slide.html**: Standard content with bullet points
- **02_text_left_image_right.html**: Key insights with supporting visuals
- **03_two_column_slide.html**: Side-by-side comparisons 
- **04_full_image_slide.html**: Charts, diagrams, and data visualizations
- **07_financial_data_table.html**: Financial metrics and KPI tables
- **08_grid_matrix.html**: Framework analysis and categorizations
- **10_timeline_process_flow.html**: Strategic roadmaps and processes
- **11_quadrants.html**: Risk/return analysis and portfolio views
- **13_split_comparison.html**: Before/after transformations
- **15_percentage_circles.html**: KPI dashboards and performance metrics

**Template Selection Strategy**: Vary slide types every 2-3 slides to maintain visual interest. Match template to content purpose - use full_image for charts, two_column for comparisons, grid_matrix for frameworks, etc.

### 3. Generate Content

**Start live viewer first before spawning agents** (use `start_live_viewer(project, markdown_file_path)` - markdown file path is REQUIRED, no defaults)

**Then spawn ALL parallel agents simultaneously** based on `agent_distribution`:
- **MINIMUM 3 agents required** - spawning fewer than 3 agents doesn't justify the overhead, just do the work directly
- **ALWAYS spawn ALL agents at once in a single message** - never spawn one agent at a time or sequentially
- **Use multiple Task tool calls in one message** - this enables true parallelism and maximizes efficiency
- **Chart generation is handled by sub-agents** - each agent creates their own required charts for maximum parallelism
- Several agents should be working simultaneously to speed up slide generation
- To stop viewer when done: `pkill -f "node.*live_viewer"`

## Sub-Agents (Task Tool)

**Using the Task Tool for Parallel Slide Generation:**

### Task Tool Requirements
- **MINIMUM 3 Task tool calls required** - if you have fewer than 3 tasks, just do the work directly
- **ALWAYS spawn ALL Task agents in a single message** - never spawn sequentially 
- **Use multiple Task tool calls in one message** for true parallelism
- Each Task agent automatically inherits CLAUDE.md context (theme settings, uv usage, etc.)

### Task Distribution Best Practices
- **Balanced workload**: Distribute slides evenly across Task agents
- **Section coherence**: Keep related slides within same Task agent when possible
- **Chart ownership**: If a slide needs charts/plots, assign that entire slide (including chart generation) to ONE specific Task agent
- **Clear assignments**: Each Task should have specific slide numbers and content requirements
- **Chart responsibility**: The Task agent assigned to a slide with charts is 100% responsible for creating those charts

### Task Agent System Prompt Instructions
---

**TASK AGENT WORKFLOW - PROCESS ONE SLIDE AT A TIME**

**CRITICAL**: You must process each assigned slide individually in sequence - do NOT batch process multiple slides.

**For Each Assigned Slide (one at a time):**

**STEP 1: Check if Slide Requires Charts/Plots**
1. Review the outline to see if your assigned slide needs any charts, graphs, or data visualizations
2. If slide requires charts, YOU are responsible for creating them - do not expect them to exist already
3. Chart creation is part of your slide assignment and must be completed by you

**STEP 2: Create Required Charts First (if needed)**
4. Use `init_from_template()` to create chart files in the `plots/` directory
5. Choose appropriate chart templates: `pie_chart.py`, `bar_chart.py`, `line_chart.py`, `stacked_bar.py`, `boilerplate.py`
6. Edit the chart Python files with real data from the dataroom materials
7. Run the chart Python scripts using `Bash` to generate both `_clean.png` and `_branded.png` versions
8. Verify charts are generated successfully before proceeding to slide creation

**Chart Creation Guidelines for Task Agents:**
- **Available chart templates**: `pie_chart.py`, `bar_chart.py`, `line_chart.py`, `stacked_bar.py`, `boilerplate.py`
- **Naming convention**: Use descriptive names like `revenue_by_channel`, `financial_trends`, `profitability_comparison`
- **Data requirements**: Always use real financial data from the dataroom materials, never placeholder data
- **Chart sizing**: Charts auto-generate at 16:9 aspect ratio (14, 7.875) - perfect for slides
- **File outputs**: Each chart generates both `_clean.png` (for slides) and `_branded.png` (for reports)
- **Slide integration**: Reference `_clean.png` versions in slides using `../plots/chartname_clean.png`

**Chart Creation Steps:**
1. `init_from_template(project, "chart", "chart_name", "chart_template.py")`
2. `Edit` the Python file with real data and appropriate titles/labels
3. `Bash` command: `cd /path/to/project && uv run plots/chart_name.py`
4. Verify both PNG files are created before using in slides

**Performance Benefit:**
- By having each Task agent handle their own chart creation, we achieve true parallelism
- No bottlenecks waiting for central chart generation
- Each agent can optimize their charts specifically for their assigned slides

**STEP 3: Initialize Single Slide Template**
9. Use `init_from_template()` to create ONE slide file with correct template
10. Use only the standard placeholders: TITLE, SUBTITLE, SECTION, PAGE_NUMBER
11. This creates the HTML structure but leaves placeholder content

**STEP 4: Edit That Single Slide with Real Content (CRITICAL)**
12. Immediately use Edit/MultiEdit tools to replace ALL template content in that ONE slide with real data from the outline
13. Replace generic placeholder text with specific content from dataroom materials
14. Add actual bullet points, financial metrics, company data, and detailed information
15. If slide has charts, reference the `_clean.png` versions you created (e.g., `../plots/revenue_by_channel_clean.png`)
16. Populate tables with real numbers, percentages, and financial data
17. Add specific company details, market data, and strategic information
18. Ensure this slide tells the complete story with real content, not placeholders

**STEP 5: Repeat for Next Slide**
19. Only after completing one slide fully (charts + template + content), move to the next assigned slide
20. Repeat the process: check for charts, create charts if needed, initialize template, then edit with real content
21. Continue until all assigned slides are completed

**Example of Real Content Replacement:**
- Template placeholder: "Add your bullet points here"
- Real content: "• #2-3 market position in U.S. cabinet industry with 11% share • Serves 17 of top 20 U.S. builders • 20+ year relationships with Home Depot and Lowe's"

**IMPORTANT**: Slide generation is NOT complete until real content replaces ALL template placeholders!

---

## Alternative Slide Creation

When users request alternative versions of existing slides, use this naming convention:

### **Alternative Slide Naming**
- **Base slide**: `slide_04.html` (optional - doesn't need to exist)
- **Alternatives**: `slide_04b.html`, `slide_04c.html`, `slide_04d.html`, etc.

### **Examples of Alternative Creation Requests:**
- "Make slide 4 more visual" → Create `slide_04b.html`
- "Create 3 different versions of slide 18" → Create `slide_18b.html`, `slide_18c.html`, `slide_18d.html`
- "Try a chart version of slide 10" → Create `slide_10b.html`

### **Benefits:**
- ✅ **Natural sorting**: Alphabetical order works perfectly
- ✅ **Readable**: Clear which slide and which alternative  
- ✅ **Flexible**: Base slides not required
- ✅ **PDF friendly**: Simple alphabetical sorting in PDF generator
- ✅ **26 alternatives**: Supports a-z suffixes per slide

### **Implementation:**
- Use `init_from_template()` with the new alternative filename
- Follow same two-step process: initialize template, then edit content
- Alternatives can use different templates for varied visual approaches

### 4. Generate PDF
Use `generate_pdf()` with format="slides" (horizontal) or "report" (vertical)

**Quality Check:**
- Run `generate_pdf()` with the desired format.
- Review the Chromium-rendered PNG previews saved in `validation/slide_previews/` or `validation/report_previews/`.
- Use the Puppeteer MCP (`puppeteer_navigate` + `puppeteer_screenshot`) on those PNGs to verify padding, margins, and that no text is clipped.
- Make any HTML fixes, regenerate, and confirm the updated preview before the final PDF sign-off.
- Keep the compiled PDF review as a last pass once previews look correct.

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
