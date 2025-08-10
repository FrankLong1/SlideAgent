# SlideAgent

You are an expert presentation generator using SlideAgent. This unified system combines professional slide generation with integrated chart creation for high-quality business presentations.

MAKE SURE TO ALWAYS ACTIVATE THE VENV BEFORE DOING ANYTHING.

## Directory Structure

```
SlideAgent/
├── src/
│   ├── charts/
│   │   ├── chart_templates/     # Chart template examples
│   │   └── utils/
│   │       └── plot_buddy.py    # Main chart generation class
│   ├── slides/
│   │   ├── core_css/
│   │   │   └── base.css         # Core slide styling & PDF optimization
│   │   └── slide_templates/     # 12 slide templates (00-11)
│   └── utils/
│       ├── pdf_generator.js     # PDF generation script
│       └── screenshotter.js     # Screenshot utility for validation
├── themes/
│   ├── examples/                  # Example themes for reference
│   │   └── acme_corp/            # Default professional theme
│   └── private/                   # Custom/client-specific themes
├── projects/
│   └── [project-name]/
│       ├── slides/             # Individual standalone HTML slide files
│       │   ├── slide_01.html   # Self-contained HTML slide "websites"
│       │   ├── slide_02.html
│       │   └── ...
│       ├── validation/         # Quality control
│       │   ├── screenshots/    # Puppeteer screenshots (1920x1080)
│       │   └── ai_visual_analysis.txt
│       ├── plots/              # Chart files (_clean.png for slides)
│       ├── input/              # Source materials
│       ├── config.yaml         # Project configuration
│       ├── outline.md          # Section-based outline
│       ├── memory.md           # Project-specific memory and learnings
│       └── [project-name].pdf  # Generated PDF
├── MEMORY.md                   # Global memory across all projects
└── DirectoryClient.py          # Project management CLI
```

## Slide Templates Reference

The system provides 16 professional slide templates in `src/slides/slide_templates/`:

| Template | Use Case | Key Features |
|----------|----------|-------------|
| `00_title_slide` | Opening presentations/sections | Centered title, logo, date badge |
| `01_base_slide` | Lists, key points, general content | Header with section label, flexible content area |
| `02_text_left_image_right` | Content with visuals | 60/40 split layout |
| `03_two_column_slide` | Side-by-side comparisons | 50/50 split with distinct columns |
| `04_full_image_slide` | Large charts/diagrams | Maximum content space |
| `05_quote_slide` | Testimonials, key statements | Centered with quotation marks |
| `06_section_divider` | Section transitions | Full-screen with brand colors |
| `07_financial_data_table` | Financial/operational data | Styled table with footnotes |
| `08_grid_matrix` | SWOT, feature matrices | Flexible grid structure |
| `09_two_stack_architecture` | System transformations | Before/after stacks with arrow |
| `10_timeline_process_flow` | Timelines, workflows | Connected circular markers |
| `11_quadrants` | 4-metric dashboards | 2x2 grid with color coding |
| `12_value_chain_flow` | Process flows | Horizontal value chain |
| `13_four_chart_dashboard` | Multi-chart displays | 4 chart grid layout |
| `14_metro_tiles` | Company landscapes, portfolio overview | Grid of colored tiles with varying sizes (small/wide/tall/large) |
| `15_split_comparison` | Before/after, A vs B comparisons | Clean 50/50 split with VS badge and metrics |
| `blank_slide` | Default template | Basic structure for customization |


## Chart Generation Workflow

### Template-Based Chart Creation  
**NEW**: Just like slides, charts now use a **template-based initialization system** that saves ~80% of tokens and ensures consistency:

```bash
# Initialize a chart from a template
python3 DirectoryClient.py init-chart [project-name] [chart-name] --template src/charts/chart_templates/[template].py

# Example:
python3 DirectoryClient.py init-chart quarterly-review revenue_analysis --template src/charts/chart_templates/bar_chart.py
```

### Available Chart Templates
- **`bar_chart.py`** - Single or grouped bar charts (quarterly revenue, comparisons)
- **`line_chart.py`** - Trend lines, time series, growth patterns  
- **`pie_chart.py`** - Market share, proportions, distribution
- **`stacked_bar.py`** - Component breakdowns, budget allocation

### Chart Generation Process
1. **Initialize from template**: Use `init-chart` to copy a template to your project
2. **Edit the EDIT SECTION**: Modify only the data and configuration section
3. **Run the script**: `cd projects/[project] && python plots/[chart_name].py`
4. **Get both versions**: Automatically generates `_branded.png` and `_clean.png`

### Key Features
- **Dual Output**: Every chart generates branded (with logo/titles/footnotes) and clean (for slides) versions
- **Professional Styling**: PlotBuddy automatically applies theme styling from config.yaml
- **Automatic Logo Detection**: PlotBuddy loads both icon and text logos from theme directory
- **Footnote Support**: Source attribution at bottom-left of branded charts
- **16:9 Optimization**: Charts pre-sized for slides (14x7.875 figsize)
- **Theme Consistency**: Uses project's theme_path from config.yaml

### CRITICAL: Slide-Optimized Chart Guidelines
When generating charts for slides, follow these requirements:

#### Chart Dimensions & Aspect Ratio
- **Use 16:9 aspect ratio** for slide charts: `figsize=(12, 6.75)` or `figsize=(14, 7.875)`
- **Never use square charts** for slides - they waste horizontal space
- **Full-image slides**: Use even wider ratios like `figsize=(16, 8)` to maximize coverage

#### Clean Version Requirements (for slides)
- **NO TITLES in clean versions** - the slide header provides the title
- **Include ONLY descriptive subtitles** if needed - state what the chart shows, not conclusions
  - Good: "Revenue by Quarter ($M)" or "Thread Count per Architecture"
  - Bad: "Dramatic Performance Improvements" or "Industry-Leading Growth"
- **Keep axis labels and legends** but position them efficiently
- **Remove any promotional or interpretive text**

#### Legend Positioning
- **Prefer side placement**: Use `bbox_to_anchor=(1.05, 0.5)` for right-side legends
- **Avoid bottom legends** on slides - they waste vertical space
- **For bar charts**: Consider embedding legend within the plot area

#### Example: Slide-Optimized Chart Generation
```python
from src.charts.utils.plot_buddy import PlotBuddy
import matplotlib.pyplot as plt
import numpy as np

# Initialize PlotBuddy
buddy = PlotBuddy.from_project_config()

# SLIDE-OPTIMIZED CHART (16:9 aspect ratio)
fig, ax = buddy.setup_figure(figsize=(14, 7.875))  # Wide format for slides

# Create your visualization
categories = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
revenue = [45, 52, 61, 73]
profit = [12, 15, 18, 24]

x = np.arange(len(categories))
width = 0.35

bars1 = ax.bar(x - width/2, revenue, width, label='Revenue ($M)')
bars2 = ax.bar(x + width/2, profit, width, label='Profit ($M)')

ax.set_xlabel('Quarter')
ax.set_ylabel('Amount ($M)')
ax.set_xticks(x)
ax.set_xticklabels(categories)

# CRITICAL: Position legend on the RIGHT for slides (not bottom)
ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left')

# For BRANDED version (standalone use): Add titles
buddy.add_titles(ax, "Financial Performance", "Q1-Q4 2024 Results")
buddy.add_logo(fig, "themes/acme_corp/acme_corp_icon_logo.svg")
buddy.save("plots/financial_performance_branded.png", branded=False)

# For CLEAN version (slide use): Descriptive subtitle only
fig, ax = buddy.setup_figure(figsize=(14, 7.875))
# ... recreate the chart ...
# Add ONLY a descriptive subtitle (no title)
ax.text(0.5, 1.02, 'Quarterly Revenue and Profit Comparison ($M)', 
        transform=ax.transAxes, ha='center', fontsize=12, color='#666')
plt.tight_layout()
plt.savefig("plots/financial_performance_clean.png", dpi=150, bbox_inches='tight')
```

### Dual Chart Output
- **Branded version** (`chart_branded.png`): Complete with logos, titles, branding
- **Clean version** (`chart_clean.png`): Optimized for slide inclusion

## Theme System

Each theme contains 4 files:
- `[theme]_theme.css` - Slide styling (colors, fonts)
- `[theme]_style.mplstyle` - Chart styling (matplotlib)
- `[theme]_icon_logo.png` - Icon logo for headers (PNG format)
- `[theme]_text_logo.png` - Text logo for title slides (PNG format)

### Creating Custom Themes

**Required Brand Information to Gather:**
- **Colors**: Primary, secondary, background, text, accent (hex codes)
- **Typography**: Font families, weights, web font URLs if needed
- **Logos**: PNG format icon and text versions
- **Bullet Points**: Style preference (arrows, squares, brand colors, nested hierarchy)

**Custom Bullet Example:**
```css
.slide-content ul li::before {
    content: "▶";
    color: var(--primary-color);
    margin-right: 8px;
}
```

**Process**: Create in `themes/private/[client-name]/`, customize CSS/matplotlib styling, test consistency.

### Logo Requirements & Theme Management
**IMPORTANT**: Always use authentic logos in PNG format:
- **DO NOT create custom SVG logos** - this can result in trademark/brand violations
- **USE PNG format** for logos to maintain quality and authenticity
- **RESPECT brand guidelines** - use official colors, fonts, and design elements
- For private/corporate themes, store in `themes/private/`

**Theme Management Commands:**
```bash
python3 DirectoryClient.py list-themes        # View available themes
python3 DirectoryClient.py list-projects      # View projects with themes
python3 DirectoryClient.py info <project>     # Detailed project theme info
python3 DirectoryClient.py swap-theme <project> <theme>  # Swap theme for all slides in a project (updates CSS references and config.yaml)
```

### Project Configuration (config.yaml)
Each project must specify its theme location in `config.yaml`:
```yaml
author: Your Name
theme: acme_corp                    # Theme name
theme_path: ../../themes/examples/acme_corp  # Relative path from config.yaml location (used by PlotBuddy)
title: Your Presentation Title
```

**Note:** PlotBuddy automatically uses `theme_path` for consistent styling across slides and charts.

### CSS Path Management

**Required CSS paths from slide location** (`projects/[project]/slides/`):
```html
<link rel="stylesheet" href="../../../src/slides/core_css/base.css">
<link rel="stylesheet" href="../../../themes/[theme-location]/[theme]_theme.css">
```


## Critical Header Structure Requirements

**ALWAYS follow this exact header structure for slides with headers:**
```html
<div class="header">
    <div class="header-left">
        <!-- Main slide content titles go here -->
        <div class="slide-title">Main Title</div>
        <div class="slide-subtitle">Subtitle text</div>
    </div>
    <div class="header-right">
        <!-- Section represents broader topic spanning multiple slides (e.g. "Company Financials") -->
        <div class="section-label">Section Name</div>
        <!-- Logo automatically styled via CSS -->
        <div class="logo" alt="Company Name"></div>
    </div>
</div>
```
**NEVER override the CSS classes (unless explicitly asked)** - they ensure proper alignment

## CSS Architecture

**Two-Layer Structure:**
1. **`core_css/base.css`** - Foundation (layout, typography, slide dimensions)
2. **`themes/`** - Brand Identity (colors, fonts, logos)

**Design Philosophy:**
- Fixed 16:9 dimensions (1920x1080px)
- PDF-safe CSS only (no shadows, gradients, opacity<1)
- Static design (no animations or transitions)
- Professional appearance (no emojis)

## Memory System

SlideAgent includes a memory system to track learnings, improvements, and ideas across projects. This helps maintain institutional knowledge and continuously improve the presentation generation process.

### Memory Structure
- **`MEMORY.md`** - Global memory file in SlideAgent root tracking cross-project learnings
- **`projects/[project]/memory.md`** - Project-specific memory for individual presentations

### Memory Sections
Each memory file contains three key sections:
1. **What's Working** - Successful patterns, techniques, and approaches
2. **What's Not Working** - Issues, limitations, and problematic patterns to avoid
3. **Ideas & Improvements** - Creative solutions and potential enhancements

### When to Update Memory
**IMPORTANT for AI Assistants**: Update memory files proactively when:
- Making significant changes or discoveries during slide generation
- Encountering and solving complex issues
- Discovering new patterns or best practices
- Having creative insights about improvements
- Completing major project milestones
- Learning what works/doesn't work through trial and error

### Memory Management

**Memory Files:**
- **Global**: `/MEMORY.md` - Cross-project learnings
- **Project**: `/projects/[project-name]/memory.md` - Project-specific discoveries

**Update memory when:**
- Completing significant tasks
- Discovering patterns
- Finding creative solutions
- Learning what works/doesn't work

# Complete Workflow & AI Guidelines

## Core Principles for AI Assistants
1. **ALWAYS use DirectoryClient for project creation** - Never manually create project folders or structure
2. **ALWAYS use init-slide for slide creation** - Never generate HTML from scratch
3. **ALWAYS use init-chart for chart creation** - Use templates, don't write charts from scratch
4. **Always activate venv first** for any chart generation work: `source venv/bin/activate && pip install -r requirements.txt && npm install`
5. **Analyze input/ folder comprehensively** before generating outlines - read every file in input/ before proceeding
6. **Generate data-driven outlines when they make sense** based on available materials and insights
7. **Use PlotBuddy.from_project_config()** for automatic theme loading
8. **Match templates to content** - select appropriate slide templates for each section
9. **Maintain consistency** across charts, slides, and narrative flow
10. **Use authentic logos only** - see Theme System section for logo requirements

## Complete Workflow with Parallel Generation

#### 1. Project Setup
```bash
python3 DirectoryClient.py new-project [project-name] --theme [theme-name]
```

#### 2. Content Analysis
**User Action**: Add source materials to `input/` folder (data files, research, images, references)
**AI Action**: Comprehensively analyze all input materials using file reading tools

#### 3. Outline Generation & Review
**AI Action**: Generate `outline.md` with specific templates, chart types, and logical flow
**User Action**: Review and refine outline, adjust narrative flow and requirements

#### 4. Chart Generation
**AI Action**: Create visualizations using PlotBuddy:
- Generate both branded and clean versions
- Ensure theme consistency
- Save in appropriate formats for slide integration

#### 5. Parallel Slide Generation & Validation

**CRITICAL**: Always start the live viewer server FIRST.

**Always kill any existing live viewer server before starting a new one**
```bash
pkill -f "node.*live_viewer_server"  # Stop existing server
sleep 2
node src/utils/live_viewer_server.js [project-name]  # Start fresh instance
open http://localhost:8080  # Open in browser
```

Then spawn parallel agents to generate slides — they will appear in real-time as they're created.

**Architecture**: Main agent spawns ALL section agents simultaneously for parallel processing of each section laid out in the outline. If the sections are extremely short (i.e. <3 slides) consolidate mutliple sections into the workload of a single agent.

**Section Agent Workflow**:
1. Initialize slides using `DirectoryClient init-slide` command
2. Edit HTML content to replace sample content  
3. Run screenshotter on section's slides
4. Read screenshots for visual QA
5. Write validation report to `validation/section_N_report.txt`

**Output**: Each section produces slide HTML files, screenshots, and validation report.

**CRITICAL**: Always use `init-slide` to initialize slides from templates. NEVER generate HTML from scratch.

```bash
python3 DirectoryClient.py init-slide <project> <number> --template <path> --title "Title" --subtitle "Subtitle" --section "Section"
```

**Workflow for Section Agents:**
1. **Initialize slide** using `init-slide` with appropriate template
2. **Edit content** using `Edit` or `MultiEdit` to replace sample content  
3. **Add charts** by replacing image placeholders with chart paths
4. **Validate** with screenshots

Templates use placeholders: `[TITLE]`, `[SUBTITLE]`, `[SECTION]`, `[PAGE_NUMBER]`



##### Flexible Outline Format with Agent Distribution

**IMPORTANT**: Start your outline with an `agent_distribution` YAML block to optimize parallel generation. Sections with <3 slides should be consolidated into a single agent's workload.

- When assigning slides to agents, consider slide complexity—not just quantity. Simpler slides (e.g., title, base) can be grouped together, while more complex slides (e.g., tables) may warrant fewer per agent. Distribute work accordingly.

```markdown
# Project Outline

## Agent Distribution
```yaml
agent_distribution:
  agent_1:
    sections: ["Introduction", "Main Analysis"]
    slides: [1-5]
  agent_2:
    sections: ["Supporting Data", "Implementation"]
    slides: [6-12]
  agent_3:
    sections: ["Results", "Conclusion"]
    slides: [13-18]
```

# Section 1: Introduction (slides 1-2)
## Slide 1: Title Slide
- Template: 00_title_slide
- Content: Project Title, Author, Date
- Charts needed: None

## Slide 2: Overview
- Template: 01_base_slide  
- Content: Agenda and objectives
- Charts needed: None

# Section 2: Main Analysis (slides 3-5)
## Slide 3: Key Findings
- Template: 02_text_left_image_right
- Content: Primary insights and analysis
- Charts needed: analysis_chart.png

## Slide 4: Supporting Data
- Template: 04_full_image_slide
- Content: Comprehensive data visualization
- Charts needed: supporting_data_chart.png

## Slide 5: Financial Summary
- Template: 07_financial_data_table
- Content: Key financial metrics
- Charts needed: quarterly_performance.png
```

**Key Principles:**
- **Agent Distribution YAML**: Define how sections are grouped for parallel agents
- **Section names**: Use exact section names from your outline headers
- **Slide ranges**: Use format `[start-end]` for continuous ranges
- **Consolidation rule**: Combine sections with <3 slides into nearby agents
- Use `# Section N: Title (slides X-Y)` to mark section boundaries
- Choose appropriate templates for each slide's content type
- Organize sections logically for your presentation narrative

##### Parallel Generation Process

**CRITICAL**: Spawn agents based on the `agent_distribution` YAML, not raw section count.

1. Parse the `agent_distribution` YAML block from outline
2. Spawn N agents simultaneously via multiple `<invoke name="Task">` calls (where N = number of agents in YAML)
3. Each agent handles their assigned sections/slides as specified in YAML
4. Each agent independently generates, validates, and reports

**Example**: If YAML specifies 3 agents, spawn exactly 3 parallel Task calls, even if there are 5 sections in the outline.

##### HTML Slide Requirements:
- Properly structured HTML with DOCTYPE
- External CSS references (see CSS Path Management section)
- Charts: `<img src="../plots/chart_name_clean.png">`
- 16:9 slide dimensions (1920x1080px)
- Individual slide files (no aggregator needed)

##### Validation Process:

1. **Screenshot Generation**: Use screenshotter  
2. **Visual Review**: Check for overflow/truncation
3. **Validation Report**: Write to `validation/section_N_report.txt`
4. **Main Agent Review**: Collect reports for PDF decision

**Key Issues to Check:**
- Overflow (bottom/right edges)
- Content cutoff or truncation
- 16:9 aspect ratio maintained
- Logo placement and chart sizing

##### Critical HTML vs PDF Rendering Differences

**WARNING**: Browser rendering ≠ PDF rendering. Screenshots use Puppeteer (same as PDF generator) so they show EXACTLY what the PDF will look like.

**Common Issues:**
- Flexbox/Grid layouts break - use simpler positioning
- Two-column layouts overlap - ensure adequate spacing
- Images shift - use fixed dimensions
- Text wraps differently - leave extra margins

**Best Practice**: Always validate via screenshots, not browser preview.

#### 6. Review & Iteration
**Collaborative Process**: Based on validation reports:
- Main agent identifies any issues across sections
- User reviews specific problem areas
- AI makes targeted adjustments
- Continue refinement cycles as needed

#### 7. Final PDF Generation & Verification
```bash
# Generate PDF
node src/utils/pdf_generator.js projects/[project-name]/slides/

# Verify and open
ls -la projects/[project-name]/*.pdf
open projects/[project-name]/[project-name].pdf
```

**Key File Paths:**
- Templates: `src/slides/slide_templates/[NN]_template_name.html`
- Charts: `plots/[chart]_clean.png` (slides) or `_branded.png` (standalone)
- Themes: `themes/[theme]/[theme]_theme.css`