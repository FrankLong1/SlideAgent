# BMPS - BitterMax Presentation Services

You are an expert presentation generator using the BMPS (BitterMax Presentation Services) framework. This unified system combines professional slide generation with integrated chart creation for high-quality business presentations.

## Core Architecture

BMPS integrates two main components:
- **Slide Generation**: HTML/CSS templates with professional corporate themes
- **Chart Generation**: Python matplotlib charts with consistent branding via PlotBuddy



## Directory Structure

```
BMPS/
├── src/
│   ├── charts/
│   │   ├── chart_templates/     # Chart template examples
│   │   └── utils/
│   │       └── plot_buddy.py    # Main chart generation class
│   └── slides/
│       ├── core_css/
│       │   ├── base.css         # Core slide styling
│       │   └── print.css        # PDF optimization
│       ├── slide_templates/     # 12 slide templates (00-11)
│       └── pdf_generator.js     # PDF generation script
├── themes/
│   ├── examples/                  # Example themes for reference
│   │   └── acme_corp/            # Default professional theme
│   └── private/                   # Custom/client-specific themes
├── projects/
│   └── [project-name]/
│       ├── config.yaml         # Project configuration
│       ├── input/              # Source materials
│       ├── plots/              # Generated charts
│       ├── outline.md          # Content outline
│       ├── presentation.html   # Final presentation
│       └── [project-name].pdf  # Generated PDF
└── DirectoryClient.py          # Project management CLI
```

## Slide Templates Overview

The system provides a set of professional slide templates, each optimized for specific content types:

### **00_title_slide.html** - Opening Slide
**Use Case**: Opening a presentation or section  
**Layout**: Centered layout with company logo at top right, main title/subtitle in center, date and department info at bottom
**Key Elements**: Large centered title (48-60px), subtitle, date badge, department/division info

### **01_base_slide.html** - General Content  
**Use Case**: Lists, key points, structured information
**Layout**: Standard header → main content area → optional highlight box → footer
**Key Elements**: Section label and slide title in header, flexible content area, optional yellow highlight box

### **02_text_left_image_right.html** - Content + Visual
**Use Case**: Explaining concepts with supporting visuals
**Layout**: 60/40 split with text content on left, image/chart/visual on right
**Key Elements**: Left side bullets/paragraphs, right side image/chart container

### **03_two_column_slide.html** - Side-by-Side Comparison  
**Use Case**: Comparing two options or states (before/after, option A vs. B, pros/cons)
**Layout**: 50/50 split with distinct visual separation
**Key Elements**: Two equal columns with different background colors, column headers

### **04_full_image_slide.html** - Full-Screen Display
**Use Case**: Large charts, diagrams, or images that need maximum space
**Layout**: Full-screen content with minimal header/footer

### **05_quote_slide.html** - Emphasis Slide
**Use Case**: Highlighting important statements (testimonials, CEO quotes, key insights)
**Layout**: Centered content with dramatic typography
**Key Elements**: Large quotation marks, centered quote text, attribution line

### **06_section_divider.html** - Section Breaks
**Use Case**: Transitioning between major topics
**Layout**: Full-screen with brand colors and large centered text
**Key Elements**: Full blue background, large white text, no header/footer

### **07_financial_data_table.html** - Financial Data
**Use Case**: Structured financial or operational data (income statements, KPI tables)
**Layout**: Professional table with structured data presentation
**Key Elements**: Styled table headers, row striping, footnotes section

### **08_grid_matrix.html** - Flexible Grid/Matrix
**Use Case**: Multi-dimensional comparisons (SWOT analysis, feature matrices, vendor evaluation)
**Layout**: Flexible table/grid structure adaptable to various configurations
**Key Elements**: Customizable rows/columns, colored headers, analysis box

### **09_two_stack_architecture.html** - Architecture Transformation
**Use Case**: Showing system transformation (technology migration, process improvement)
**Layout**: Two vertical stacks side-by-side with transformation arrow
**Key Elements**: Left stack (old state), right stack (new state), center transformation arrow

### **10_timeline_process_flow.html** - Timeline/Process Flow
**Use Case**: Sequential steps or progression over time (project timelines, workflows)
**Layout**: Horizontal flow with connected circular markers
**Key Elements**: Numbered circular markers, connecting lines, status indicators

### **11_quadrants.html** - 4-Metric Dashboard
**Use Case**: Key metrics or KPIs in dashboard format
**Layout**: 2x2 grid of metric cards with central comparison element
**Key Elements**: Four color-coded quadrants, large numeric displays, central summary

## Chart Generation with PlotBuddy

### Key Features
- **Dual Output**: Automatically generates both branded and clean versions
- **Professional Styling**: Consistent corporate appearance
- **Theme Integration and Local Style Loading**: Uses local `.mplstyle` files without system installation to match matplotlib styles with CSS themes

### Usage Example
```python
from src.charts.utils.plot_buddy import PlotBuddy
import matplotlib.pyplot as plt

# Simple initialization - reads theme from project config.yaml
buddy = PlotBuddy.from_project_config()

# Alternative: specify theme directly  
# buddy = PlotBuddy.from_theme("acme_corp")

# Create chart
fig, ax = buddy.setup_figure()
# ... add your data plotting code ...
buddy.add_titles(ax, "Revenue Growth", "Q1-Q4 2024 Performance")
buddy.add_logo(fig, "themes/acme_corp/acme_corp_icon_logo.svg")

# Save both versions automatically
branded_path, clean_path = buddy.save("plots/revenue_analysis.png", branded=True)
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

### Logo File Requirements
**IMPORTANT**: Always use authentic logos in PNG format:
- **DO NOT create custom SVG logos** - this can result in trademark/brand violations
- **USE PNG format** for logos to maintain quality and authenticity
- **RESPECT brand guidelines** - use official colors, fonts, and design elements
- For private/corporate themes, store in `themes/private/`

### Use the DirectoryClient to check for available themes:
```bash
python3 DirectoryClient.py list-themes
```

### Project Configuration (config.yaml)
Each project must specify its theme location in `config.yaml`:
```yaml
author: Your Name
theme: acme_corp                    # Theme name
theme_path: ../../themes/examples/acme_corp  # Relative path from config.yaml location
title: Your Presentation Title
```

**Note:** PlotBuddy automatically uses `theme_path` for consistent styling across slides and charts.


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

### Three-Layer Structure
Core CSS
1. **`core_css/base.css`** - Foundation (layout, typography, slide dimensions)
2. **`core_css/print.css`** - PDF Export optimization

### theme specific stuff
3.**`themes/`** - Brand Identity (colors, fonts, brand elements)

### Static Slide Design Philosophy
- **No animations or CSS transitions** - Designed for static presentation and PDF export
- **Fixed 16:9 presentation dimensions** - Optimized for projector display
- **Print-focused styling** - No visual effects just static stuff for printed/PDF format
- **No emojis** - Professional and institutional appearance

## AI-Assisted Workflow Process

### 1. Project Setup
```bash
python3 DirectoryClient.py new-project [project-name] --theme acme_corp
```
Configure `config.yaml` with theme path:
```yaml
author: Your Name
theme: acme_corp
theme_path: ../../themes/examples/acme_corp
title: Your Presentation Title
```

## DirectoryClient CLI Commands

The DirectoryClient provides comprehensive project management for BMPS:

### Core Commands

**Create New Project:**
```bash
python3 DirectoryClient.py new-project <project-name> [--theme <theme>]
```
- Creates project directory structure
- Generates initial config.yaml and outline.md
- Sets up input/ and plots/ folders

**List Projects:**
```bash
python3 DirectoryClient.py list-projects [--detailed]
```
- Basic: Shows project name, theme, and title
- Detailed: Shows paths, file status, content counts, theme configuration

**List Available Themes:**
```bash
python3 DirectoryClient.py list-themes
```
- Shows all available themes with status indicators
- Checks for both CSS and matplotlib style files
- Identifies private themes in themes/private/

**Project Information:**
```bash
python3 DirectoryClient.py info <project-name>
```
- Detailed project status
- File existence checks (outline, HTML, PDF)
- Plot count and configuration details

**Generate PDF:**
```bash
python3 DirectoryClient.py generate-pdf <project-name>
```
- Converts presentation.html to PDF
- Requires Node.js and presentation.html to exist

### Programmatic Access

The DirectoryClient can also be used programmatically:
```python
from DirectoryClient import BMPSClient

client = BMPSClient()
projects_data = client.get_all_projects_data()
# Returns structured data for all projects including paths, configs, file status
```

### 2. Content Gathering Phase
**User Action**: Dump all source materials into `input/` folder:
- Data files (CSV, Excel, JSON)
- Research documents (PDF, Word, text)
- Images, charts, diagrams
- Reference materials
- Any other relevant content

### 3. AI Outline Generation
**Model Action**: Analyze input materials and generate comprehensive `outline.md`:
- Review all files in `input/` folder
- Identify key themes, data insights, and narrative flow
- Propose slide structure with specific templates
- Suggest chart types and data visualizations needed
- Create logical presentation flow

### 4. User Outline Review
**User Action**: Review and refine the generated outline:
- Approve/modify slide sequence
- Adjust narrative flow
- Add/remove sections as needed
- Specify any particular emphasis or messaging
- Confirm chart and visualization requirements

### 5. AI Chart Generation
**Model Action**: Generate data visualizations based on approved outline:
- Create data visualizations using PlotBuddy
- Generate both branded and clean chart versions
- Ensure theme consistency across all chart elements
- Save charts in appropriate formats for slide integration

### 6. AI Slide Generation
**Model Action**: Build slide content using approved outline and generated charts:
- Build slide content using appropriate templates
- Make sure to build it slide by slide, so create an individual task for each slide.
- Before making a slide ensure you have read the template it is based on. Every slide should be based on a template.
- If you have a creative idea for what a slide should look like feel free to generate that as an alternative following the standard templated one.
- Integrate generated charts into relevant slides
- Ensure theme consistency across all slide elements
- Produce complete `presentation.html`

### 7. User Review & Iteration
**User Action**: Review generated presentation:
- Check slide content and flow
- Verify chart accuracy and clarity
- Assess overall messaging and impact
- Request specific changes or refinements

### 7. Iteration Cycles
**Collaborative Process**: Refine until perfect:
- Model makes requested adjustments
- User reviews changes
- Continue iterations as needed
- Focus on specific slides, charts, or content sections

### 8. Final PDF Generation
```bash
python3 DirectoryClient.py generate-pdf [project-name]
```

**Key Principle**: The model does the heavy lifting of content analysis, outline creation, and presentation generation, while the user provides direction, feedback, and refinement through iterative collaboration.

## Power Plant Analysis Project

### Overview
Comprehensive analysis of power plant generation data for datacenter deployment scenarios. Analyzes 8 power plants across the US using slack capacity, solar generation, battery storage, and backup generators.

### Key Files
- `src/active_projects/power_plant_curtailment/main_analysis.py` - Main analysis orchestration
- `utils.py` - Solar modeling, battery simulation, chart creation
- `constants.yaml` - Configuration constants
- `plant_*/outputs/` - Generated charts (7 charts per plant)

### Chart Types Generated
1. Daily Peaks - Annual generation patterns
2. Daily Cycle - 24-hour generation profile
3. Slack Capacity - Available unused generation capacity
4. Solar Potential - Location-specific solar generation modeling
5. Combined Capacity - Plant slack + solar generation
6. Battery Storage - Integrated battery storage system analysis
7. Backup Generators - Complete backup system with natural gas peakers

### Running Analysis
```bash
source venv/bin/activate && cd src/active_projects/power_plant_curtailment
python main_analysis.py plant_165_GRDA/ --no-display
```

## Usage Instructions for Claude

### AI-Assisted Workflow Principles
1. **Always activate venv first** for any chart generation work
2. **Analyze input/ folder comprehensively** before generating outlines, use the read file tool over at least once on everything in there before proceeding.
3. **Generate data-driven outlines** based on available materials and insights
4. **Use PlotBuddy.from_project_config()** for automatic theme loading
5. **Match templates to content** - select appropriate slide templates for each section
6. **Create iterative refinements** based on user feedback
7. **Maintain consistency** across charts, slides, and narrative flow
8. **Use authentic logos only** - download PNG logos from official sources, never create custom SVG logos


### File Paths
- Templates: `src/slides/slide_templates/[NN]_template_name.html`
- Charts: `plots/[chart]_clean.png` (for slides) or `plots/[chart]_branded.png` (standalone)
- Themes: `themes/[theme]/[theme]_theme.css`

Remember: The system is designed for simplicity and professional output. Keep templates minimal, use consistent theming, and focus on content over complexity.


### Virtual Environment Setup
**CRITICAL**: Always activate the virtual environment first before doing anything, whenever the user starts a sessions:
```bash
source venv/bin/activate
pip install -r requirements.txt
```