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
│   │   │   ├── base.css         # Core slide styling
│   │   │   └── print.css        # PDF optimization
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

**CRITICAL**: CSS paths in slides are context-dependent. Each slide file must reference CSS files using the correct relative path from its location:

#### Standard Project Structure:
```
SlideAgent/
├── src/slides/core_css/
│   ├── base.css
│   └── print.css
├── themes/[theme-location]/
│   └── [theme]_theme.css
└── projects/[project]/slides/
    └── slide_XX.html
```

#### Required CSS Links in Each Slide:
```html
<link rel="stylesheet" href="../../../src/slides/core_css/base.css">
<link rel="stylesheet" href="../../../src/slides/core_css/print.css">
<link rel="stylesheet" href="../../../themes/[theme-location]/[theme]_theme.css">
```

#### Path Calculation:
- From `projects/[project]/slides/` to `src/slides/core_css/` = `../../../src/slides/core_css/`
- From `projects/[project]/slides/` to `themes/` = `../../../themes/`

**AI Guidance**: Always verify CSS paths are correct for the specific slide location. Test that files exist at the specified paths before generating slides.


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
- **Fixed 16:9 presentation dimensions** - Optimized for projector display (1920x1080px)
- **Print-focused styling** - No visual effects just static stuff for printed/PDF format
- **PDF-safe CSS only** - No box-shadows, gradients, transparency, or filters that render poorly in PDFs
- **No emojis** - Professional and institutional appearance

# Complete Workflow & AI Guidelines

Core Principles for AI Assistants
1. **ALWAYS use DirectoryClient for project creation** - Never manually create project folders or structure
2. **Always activate venv first** for any chart generation work: `source venv/bin/activate && pip install -r requirements.txt && npm install`
3. **Analyze input/ folder comprehensively** before generating outlines - read every file in input/ before proceeding
4. **Generate data-driven outlines when they make sense** based on available materials and insights
5. **Use PlotBuddy.from_project_config()** for automatic theme loading
6. **Match templates to content** - select appropriate slide templates for each section
8. **Maintain consistency** across charts, slides, and narrative flow
9. **Use authentic logos only** - see Theme System section for logo requirements

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

#### 5. Parallel Slide Generation & Validation Architecture

The system uses a hierarchical agent structure for maximum efficiency and speed:

##### Main Agent (Orchestrator)
- Parses outline into sections
- Spawns ALL section agents simultaneously in parallel  
- Collects validation reports from all agents
- Makes final go/no-go decision for PDF generation
- Handles any cross-section issues or fixes

##### Section Sub-Agents (Workers)
Each section agent is a COMPLETE, self-contained worker that:

**1. GENERATES** - Creates all slides for their section
**2. VALIDATES** - Takes screenshots of their own slides  
**3. REVIEWS** - Visually inspects each screenshot using Read tool
**4. REPORTS** - Writes structured validation report

##### Section Agent Full Workflow:
```
Section Agent receives:
├── Section outline chunk (e.g., slides 4-7)
├── Theme configuration
├── Project context
└── Full system instructions

Section Agent performs:
├── 1. Read slide templates
├── 2. Generate HTML slides
├── 3. Save slides to disk
├── 4. Run screenshotter on own slides
├── 5. Read each screenshot for visual QA
├── 6. Document issues found
└── 7. Write validation report

Section Agent outputs:
├── Generated slide files (slide_XX.html)
├── Screenshots (slide_XX.png)
└── Validation report (section_N_report.txt)
```

##### Parallel Execution Example:
```
User: "Generate presentation"
    ↓
Main Agent: "Spawning 6 section agents in parallel"
    ↓
[PARALLEL EXECUTION]
├── Agent 1: Section 1 (slides 1-3)   → Generate → Screenshot → Review → Report
├── Agent 2: Section 2 (slides 4-7)   → Generate → Screenshot → Review → Report
├── Agent 3: Section 3 (slides 8-10)  → Generate → Screenshot → Review → Report
├── Agent 4: Section 4 (slides 11-14) → Generate → Screenshot → Review → Report
├── Agent 5: Section 5 (slides 15-17) → Generate → Screenshot → Review → Report
└── Agent 6: Section 6 (slides 18-19) → Generate → Screenshot → Review → Report
    ↓
Main Agent: "Collecting all reports"
    ↓
Main Agent: "All sections READY → Generating PDF"
```

##### Flexible Outline Format (Example)
Organize your outline into logical sections. The format below is a suggestion - adapt sections and slide counts to match your presentation needs:

```markdown
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
- Use `# Section N: Title (slides X-Y)` to mark section boundaries
- Choose appropriate templates for each slide's content type
- Specify required charts that need to be generated
- Organize sections logically for your presentation narrative

##### Parallel Generation Process

**CRITICAL**: Always spawn ALL section agents in parallel using a single message with multiple Task tool calls. This dramatically improves speed and efficiency.

**Step 1:** Parse outline and identify section boundaries using pattern `# Section N:`

**Step 2:** Spawn ALL section agents in parallel via single message with multiple Task tool calls:
```
Main Agent spawns ALL sections simultaneously:
├── Task Agent 1: Section 1 (slides 1-3)
├── Task Agent 2: Section 2 (slides 4-8)  
├── Task Agent 3: Section 3 (slides 9-11)
├── Task Agent 4: Section 4 (slides 12-16)
└── Task Agent 5: Section 5 (slides 17-20)
```

**Example Usage**: Use multiple `<invoke name="Task">` calls in a single message:
```xml
<function_calls>
<invoke name="Task">...</invoke>
<invoke name="Task">...</invoke>  
<invoke name="Task">...</invoke>
<invoke name="Task">...</invoke>
<invoke name="Task">...</invoke>
</function_calls>
```

**Step 3:** Each section agent operates independently and performs COMPLETE validation:
- Receives complete system instructions (same as parent agent)
- Gets section outline chunk + theme config + project context
- Charts already generated (no need to regenerate)
- Reads appropriate slide templates 
- Creates individual **fully self-contained** HTML slide "websites": `slide_XX.html` in slides/ directory
- **GENERATES SCREENSHOTS** of their own slides using screenshotter
- **REVIEWS SCREENSHOTS** using Read tool to identify issues
- **WRITES VALIDATION REPORT** to `validation/section_N_report.txt`

##### CRITICAL - HTML Slide Requirements:
- Each slide should be a properly structured HTML document
- Reference external CSS files using `<link rel="stylesheet">` tags for maintainability
- Include references to: base.css, print.css, and theme CSS files
- **IMPORTANT CSS PATHS**: From `projects/[project]/slides/slide_XX.html`:
  - Base CSS: `../../../src/slides/core_css/base.css`
  - Print CSS: `../../../src/slides/core_css/print.css`
  - Theme CSS: `../../../themes/[theme-location]/[theme]_theme.css` you should use the DirectoryClient.py tool to list out available themes so we know which one to use.
- Charts referenced as `<img src="../plots/chart_name_clean.png">` 
- Each slide must render perfectly when opened in any browser
- Complete DOCTYPE html structure with proper 16:9 slide dimensions
- Dependencies: external CSS files and chart images in plots/
- Clean, maintainable code structure with external stylesheets
- No aggregator HTML files needed - PDF is generated directly from individual slides

##### Section Agent Validation Process:
Each section agent MUST perform these validation steps:

1. **Generate Screenshots** for their slides only:
```bash
# Example for Section 2 (slides 4-7)
# Option A: Using slide range
node src/utils/screenshotter.js projects/[project-name] --range 4-7

# Option B: Using specific slide list
node src/utils/screenshotter.js projects/[project-name] --slides "slide_04.html,slide_05.html,slide_06.html,slide_07.html"

# Option C: Using glob pattern
node src/utils/screenshotter.js projects/[project-name] --pattern "slide_0[4-7].html"
```

2. **MANDATORY: Visual Review & Overflow Fix Protocol**
   - Read EVERY screenshot using the Read tool (no sampling allowed)
   - Check for any content cutoff, overflow, or truncation issues
   - **If overflow detected**, fix it immediately (resize, adjust font, add constraints, split content, etc.)
   - Re-run screenshotter ONLY for fixed slides
   - Re-validate to ensure the fix worked
   - Document what was changed in validation report

**IMPORTANT**: Screenshots represent PDF rendering, not HTML. Issues found WILL appear in the final PDF and MUST be fixed.

3. **Write Detailed Validation Report** to `validation/section_N_report.txt`:
```
Section N Validation Report
===========================
Generated Slides: [list]
Screenshots Taken: [list]

Visual Inspection Results:
- Slide XX: [PASS/FAIL] - [Issues if any]
- Slide XX: [PASS/FAIL] - [Issues if any]

Overflow Issues Fixed:
- Slide XX: [Description of overflow and fix applied]
- Slide XX: [Description of overflow and fix applied]

Other Issues Found:
1. [Issue description and affected slide]
2. [Issue description and affected slide]

Fixes Applied:
- [List of HTML modifications made]
- [Font-size reductions, max-height additions, etc.]

Recommendations:
- [Any remaining fixes needed before PDF generation]

Status: [READY FOR PDF / NEEDS FIXES]
```

**Step 4:** Main agent collects and reviews all section reports:
```bash
# Main agent reads all validation reports
Read("projects/[project-name]/validation/section_1_report.txt")
Read("projects/[project-name]/validation/section_2_report.txt")
# ... etc

# If all sections report READY FOR PDF, proceed to PDF generation
# If any section reports NEEDS FIXES, address issues first
```

**CRITICAL**: This parallel validation ensures:
- Each section agent is responsible for their own quality control
- Screenshots are generated in parallel, not sequentially
- Validation happens immediately after slide creation
- Structured feedback is documented for review
- Main agent has clear go/no-go decision based on reports

##### Visual Validation Checklist
When reviewing screenshots, check EVERY slide for these issues:

###### PRIORITY 1 - Overflow Issues (MUST FIX):
- **Bottom overflow**: Content cut off at bottom of slide
- **Right overflow**: Content extending past right edge
- **Image/chart cutoff**: Visuals not fully visible
- **Table truncation**: Rows partially visible or cut off
- **Text clipping**: Any text that appears cut off at edges

###### Layout & Spacing:
- **Text overlap**: Headers/subtitles overlapping with content
- **Aspect ratio**: Slides must maintain exact 16:9 (1920x1080px) dimensions
- **Alignment**: Elements properly aligned to grid, no misaligned content
- **White space**: No awkward empty spaces or overcrowding

###### PDF Rendering Issues:
- **Shadow artifacts**: Box-shadows create unwanted halos in PDFs
- **Gradient problems**: CSS gradients render as solid blocks
- **Transparency issues**: Semi-transparent elements appear broken
- **Dimension distortion**: Viewport units causing incorrect sizing

###### Content & Branding:
- **Logo placement**: Consistent positioning and sizing
- **Chart integration**: Proper sizing within allocated space
- **Font readability**: Appropriate sizes and contrast
- **Page numbering**: Correct sequential numbering

##### PDF-Safe CSS Guidelines
**IMPORTANT**: Avoid these CSS features that cause PDF rendering issues:

###### Never Use:
- **`box-shadow`**: Creates unwanted halos and artifacts in PDFs
- **CSS gradients**: `linear-gradient()` or `radial-gradient()` render poorly
- **Opacity/transparency**: `opacity` less than 1 or `rgba()` with alpha
- **CSS filters**: `blur()`, `drop-shadow()`, `brightness()`, etc.
- **Blend modes**: `mix-blend-mode` or `background-blend-mode`
- **Complex transforms**: 3D transforms or perspective effects

###### Use Instead:
- **Solid borders**: Replace `box-shadow` with `border: 1px solid #color`
- **Solid colors**: Use hex or rgb colors without transparency
- **Fixed dimensions**: Use `1920px x 1080px` instead of viewport units for slides
- **Simple backgrounds**: Solid colors only, no gradients or patterns
- **Clear spacing**: Ensure adequate margins between headers and content

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
- [ ] Ready for distribution

**Key Principle**: The system leverages parallel processing for generation and validation, while maintaining quality through automated review at each stage. Final PDF must be verified before distribution.

**Key File Paths:**
- Templates: `src/slides/slide_templates/[NN]_template_name.html`
- Charts: `plots/[chart]_clean.png` (for slides) or `plots/[chart]_branded.png` (standalone)
- Themes: `themes/[theme]/[theme]_theme.css`

**Design Philosophy**: The system generates HTML slides that reference external stylesheets for maintainability and consistency. Slides can be viewed individually in browsers or collectively compiled into PDFs. Keep templates minimal, use consistent theming via external CSS references, and focus on content over complexity.