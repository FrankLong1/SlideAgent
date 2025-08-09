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

The system provides 14 professional slide templates in `src/slides/slide_templates/`:

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

### Alternative: Separate Methods for Slide Charts
```python
def generate_slide_chart(data, output_name):
    """Generate a chart optimized for slide presentation"""
    buddy = PlotBuddy.from_project_config()
    
    # Wide 16:9 format
    fig, ax = buddy.setup_figure(figsize=(14, 7.875))
    
    # Create visualization
    # ... your plotting code ...
    
    # Right-side legend
    ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left')
    
    # Save WITHOUT titles for slides
    plt.tight_layout()
    plt.savefig(f"plots/{output_name}_clean.png", dpi=150, bbox_inches='tight')
    
    # Also create branded version with titles if needed
    buddy.add_titles(ax, "Title", "Subtitle")
    plt.savefig(f"plots/{output_name}_branded.png", dpi=150, bbox_inches='tight')
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

### Two-Layer Structure
Core CSS
1. **`core_css/base.css`** - Foundation (layout, typography, slide dimensions, PDF optimization)
2.**`themes/`** - Brand Identity (colors, fonts, brand elements)

### Static Slide Design Philosophy
- **No animations or CSS transitions** - Designed for static presentation and PDF export
- **Fixed 16:9 presentation dimensions** - Optimized for projector display (1920x1080px)
- **Print-focused styling** - No visual effects just static stuff for printed/PDF format
- **PDF-safe CSS only** - No box-shadows, gradients, transparency, or filters that render poorly in PDFs
- **No emojis** - Professional and institutional appearance

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

**For AI Assistants**: Memory files are simple markdown documents that should be updated directly using Read/Edit tools:
- **Global memory**: `/MEMORY.md` - Cross-project learnings
- **Project memory**: `/projects/[project-name]/memory.md` - Project-specific discoveries

Simply read the file, edit the appropriate section (What's Working, What's Not Working, Ideas & Improvements), and update the timestamp at the bottom.

### AI Guidelines for Memory Updates
- Update project memory after completing significant tasks or encountering issues
- Update global memory when discovering patterns that apply across projects
- Be specific and actionable in memory entries
- Include context about why something works or doesn't work
- Document creative solutions that might be reusable
- Track both technical and design-related learnings

# Complete Workflow & AI Guidelines
Always use `init-slide` for creating slides instead of generating HTML from scratch:

```bash
# Initialize a slide from template
python3 DirectoryClient.py init-slide [project] [slide-number] --template [template-path] --title "Title" --subtitle "Subtitle" --section "Section"

# Example:
python3 DirectoryClient.py init-slide quarterly-review 01 --template src/slides/slide_templates/00_title_slide.html --title "Q4 2024 Review" --subtitle "Financial Performance"
```
Core Principles for AI Assistants
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

SlideAgent uses a parallel section-based generation workflow for dramatically improved speed and quality control.

#### 1. Project Setup
**IMPORTANT**: Always use DirectoryClient to create new projects:
```bash
python3 DirectoryClient.py new-project [project-name] --theme [theme-name]
```

For other commands (list projects, themes, etc.), see the Theme System section above.

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

**CRITICAL WORKFLOW - ALWAYS START LIVE VIEWER FIRST**: 
⚠️ **MANDATORY**: The live viewer server MUST be running BEFORE generating any slides. This is NOT optional- Users can't watch progress without the live viewer. Use the Node.js server.


```bash
# Step 1: ALWAYS START THE LIVE VIEWER FIRST (NON-NEGOTIABLE)
node src/utils/live_viewer_server.js [project-name]
# This starts a local server at http://localhost:8080 and opens the browser
# The viewer shows section rows with slide placeholders waiting to be filled

# Step 2: ONLY AFTER viewer is running, spawn parallel agents to generate slides
# Users will see slides appear as mini previews in each section row as they're created
```

**Architecture**: Main agent spawns ALL section agents simultaneously for parallel processing of each section laid out in the outline. If the sections are extremely short (i.e. <3 slides) consolidate mutliple sections into the workload of a single agent.

**Section Agent Workflow**:
1. Initialize slides using `DirectoryClient init-slide` command
2. Edit HTML content to replace sample content  
3. Run screenshotter on section's slides
4. Read screenshots for visual QA
5. Write validation report to `validation/section_N_report.txt`

**Output**: Each section produces slide HTML files, screenshots, and validation report.

**CRITICAL**: Always use the DirectoryClient `init-slide` command to initialize slides from templates. NEVER generate HTML from scratch using Write tool.

```bash
# Initialize a slide from a template
python3 DirectoryClient.py init-slide <project> <number> \
    --template <path-to-template> \
    --title "Title Text" \
    --subtitle "Subtitle Text" \
    --section "Section Label"

# Examples:
# Title slide
python3 DirectoryClient.py init-slide my-project 01 \
    --template src/slides/slide_templates/00_title_slide.html \
    --title "Q4 2024 Results" \
    --subtitle "Financial Performance Review"

# Base slide (uses default blank_slide if no template specified)  
python3 DirectoryClient.py init-slide my-project 02 \
    --title "Overview" \
    --subtitle "Key objectives" \
    --section "Introduction"

# Text with image
python3 DirectoryClient.py init-slide my-project 03 \
    --template src/slides/slide_templates/02_text_left_image_right.html \
    --title "Market Analysis" \
    --section "Main Content"
```

**How Templates Work:**
- All templates use standardized placeholders: `[TITLE]`, `[SUBTITLE]`, `[SECTION]`, `[PAGE_NUMBER]`
- Templates include `<!-- TEMPLATE_TYPE: standard/title/divider -->` metadata
- The init-slide command automatically handles all path fixes and replacements
- Sample content remains in templates - agents edit this directly

**Workflow for Section Agents:**
1. **Initialize slide** using `init-slide` with appropriate template
2. **Edit content** using `Edit` or `MultiEdit` to replace sample content with actual data
3. **Add charts** by replacing image placeholders with actual chart paths
4. **Validate** with screenshots as usual

See **Slide Templates Reference** section above for complete template list.

##### Example Agent Workflow for a Single Slide:
```python
# Step 1: Initialize slide from template
Bash("python3 DirectoryClient.py init-slide my-project 03 --template src/slides/slide_templates/02_text_left_image_right.html --title 'Market Analysis' --subtitle 'Q4 Performance' --section 'FINANCIALS'")

# Step 2: Edit the content area to add actual data
Edit("projects/my-project/slides/slide_03.html",
     old_string="""<ul style="font-size: 18px; line-height: 1.6; color: #333; list-style: none; padding: 0;">
                <li style="margin-bottom: 20px;">
                    <strong style="color: #1B365D;">Market Leadership:</strong> Dominant in cloud infrastructure with 35% market share and strong partnerships.
                </li>
                <li style="margin-bottom: 20px;">
                    <strong style="color: #1B365D;">Leadership Team:</strong> Executive team with deep industry experience and proven success.
                </li>
            </ul>""",
     new_string="""<ul style="font-size: 18px; line-height: 1.6; color: #333; list-style: none; padding: 0;">
                <li style="margin-bottom: 20px;">
                    <strong style="color: #1B365D;">Revenue Growth:</strong> Q4 revenue increased 28% YoY to $4.2B, exceeding guidance.
                </li>
                <li style="margin-bottom: 20px;">
                    <strong style="color: #1B365D;">Market Expansion:</strong> Successfully entered 3 new international markets.
                </li>
                <li style="margin-bottom: 20px;">
                    <strong style="color: #1B365D;">Product Innovation:</strong> Launched 5 new AI-powered features driving adoption.
                </li>
            </ul>""")

# Step 3: Replace image placeholder with actual chart
Edit("projects/my-project/slides/slide_03.html",
     old_string="""<div style="width: 100%; height: 400px; background: linear-gradient(135deg, #e9ecef 0%, #f8f9fa 100%); border: 2px dashed #ced4da; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-direction: column; color: #6c757d; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 10px; opacity: 0.5;">🏢</div>
                <div style="font-weight: 500; margin-bottom: 5px; font-size: 14px;">Image Placeholder</div>
                <div style="font-size: 12px; opacity: 0.7;">Replace with: images/datacenter.png</div>
            </div>""",
     new_string="""<img src="../plots/q4_revenue_growth_clean.png" alt="Q4 Revenue Growth Chart" style="width: 100%; height: 100%; object-fit: contain;">""")
```


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

1. **Screenshot Generation**: Use screenshotter with `--range`, `--slides`, or `--pattern` options
2. **Visual Review**: Read ALL screenshots, fix any overflow/truncation immediately
3. **Validation Report**: Write structured report to `validation/section_N_report.txt` with status
4. **Main Agent Review**: Collect all reports for go/no-go PDF decision

**Key**: Screenshots show exact PDF rendering - fix issues immediately.

##### Visual Validation Checklist

**Priority Issues**: Overflow (bottom/right), content cutoff, truncation
**Layout**: Proper 16:9 aspect ratio, alignment, spacing
**PDF Rendering**: Avoid box-shadows, gradients, transparency
**Content**: Logo placement, chart sizing, readability

##### PDF-Safe CSS

**Never use**: box-shadow, gradients, opacity<1, CSS filters, blend modes, 3D transforms
**Use instead**: Solid borders/colors, fixed dimensions (1920x1080px), simple backgrounds

##### Critical HTML vs PDF Rendering Differences

**WARNING**: HTML files may look perfect in browsers but render incorrectly in PDFs. Common issues:

###### Layout Differences:
- **Flexbox/Grid**: Complex flex layouts often break in PDF - use simpler table or absolute positioning for critical layouts
- **Two-column layouts**: May overlap in PDF even if perfect in browser - ensure adequate spacing and test with screenshots
- **Image positioning**: Images may shift or scale differently - use fixed dimensions and positioning
- **Text wrapping**: PDF text wrap differs from browser - leave extra margin for safety

###### Why Screenshots Matter:
- **Screenshots use Puppeteer**: Same engine that generates PDFs, so screenshots show EXACTLY what PDF will look like
- **Browser preview lies**: Chrome/Safari/Firefox rendering ≠ PDF rendering
- **Always validate screenshots**: If it looks wrong in screenshot, it WILL be wrong in PDF

###### Best Practices:
1. **Test with screenshots first** - Don't trust browser preview
2. **Use simpler layouts** for PDF-critical content
3. **Add buffer space** between elements that appear close
4. **Fixed positioning** over flexible layouts when possible
5. **Validate EVERY slide** via screenshots before PDF generation

#### 6. Review & Iteration
**Collaborative Process**: Based on validation reports:
- Main agent identifies any issues across sections
- User reviews specific problem areas
- AI makes targeted adjustments
- Continue refinement cycles as needed

#### 7. Final PDF Generation & Verification
```bash
# Generate the PDF
node src/utils/pdf_generator.js projects/[project-name]/slides/

# CRITICAL: Verify the PDF
# Check file exists and has correct name
ls -la projects/[project-name]/*.pdf

# Open or distribute as needed
# Common actions:
# - Upload to cloud storage
# - Email to stakeholders  
# - Convert to other formats
# - Archive with version control
```

**Post-Generation Checklist:**
- [ ] PDF file generated with correct filename
- [ ] File size is reasonable (typically 2-10MB for 20 slides)
- [ ] All pages present (match slide count)
- [ ] No rendering artifacts from validation reports
- [ ] Ready for distribution, open the PDF file when everything is done!

**Key Principle**: The system leverages parallel processing for generation and validation, while maintaining quality through automated review at each stage. Final PDF must be verified before distribution.

**Key File Paths:**
- Templates: `src/slides/slide_templates/[NN]_template_name.html`
- Charts: `plots/[chart]_clean.png` (for slides) or `plots/[chart]_branded.png` (standalone)
- Themes: `themes/[theme]/[theme]_theme.css`

**Design Philosophy**: The system generates HTML slides that reference external stylesheets for maintainability and consistency. Slides can be viewed individually in browsers or collectively compiled into PDFs. Keep templates minimal, use consistent theming via external CSS references, and focus on content over complexity.