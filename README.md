# SlideAgent

*A minimal, AI-first presentation framework inspired by Richard Sutton's Bitter Lesson*

> "The biggest lesson from 70 years of AI research is that general methods that leverage computation are ultimately the most effective, and by a large margin."  
> — Richard Sutton, *The Bitter Lesson*

## Philosophy

SlideAgent embodies the core principle of Sutton's bitter lesson: **computation trumps human-crafted specialization**. Rather than building complex presentation frameworks optimized for human authoring, SlideAgent provides a minimal, template-driven system designed specifically for AI agents to leverage their scaling computational abilities.

> "We have to learn the bitter lesson that building in how we think we think does not work in the long run."

### Machine Editability First as a Design

Traditional presentation tools are built around human cognitive limitations—complex UIs, WYSIWYG editors, and intricate feature sets that feel satisfying to human users but add abstractions between the model and raw context. SlideAgent takes the opposite approach: a deliberately minimal HTML/CSS micro-library as a foundation that is almost useless for humans, but becomes powerful only when paired with increasingly capable AI models The system is intentionally more verbose than any human would want to write directly with very few shared components. 

## Core Architecture

SlideAgent consists of just the essential components needed for professional slide generation:

- **Slide Templates**: Minimal HTML structures covering all presentation needs
- **Theme System**: CSS-based branding (colors, fonts, logos)  
- **Chart Integration**: Python matplotlib with consistent styling via PlotBuddy
- **PDF Generation**: Single-command export to presentation format

### The Workflow

1. **Dump Input**: Raw data files, documents, research materials
2. **AI Outline**: Model analyzes inputs and proposes slide structure  
3. **Iterate Outline**: Human feedback and refinement
4. **Generate Charts**: Automated data visualization with theme consistency
5. **Build Slides**: Template-driven HTML generation
6. **Export PDF**: Professional presentation output

## Why This Approach Works

> "The two methods that seem to scale arbitrarily with computation are search and learning."

Modern coding agents excel at:
- **Pattern Recognition**: Identifying optimal slide templates for content types
- **Data Analysis**: Extracting insights from complex input materials  
- **Template Population**: Generating verbose, structured HTML efficiently
- **Consistency Management**: Maintaining theme coherence across slides and charts
- **Iterative Refinement**: Incorporating feedback through computational cycles

What they struggle with are the human-centric complexities that traditional frameworks prioritize: drag-and-drop interfaces, real-time collaboration, and interactive authoring experiences.

## Quick Start

### 1. Setup Dependencies
```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt
npm install

# Create new presentation
python3 DirectoryClient.py new-project my-presentation --theme acme_corp

# Generate PDF
node src/utils/pdf_generator.js projects/my-presentation/slides/
```

### Project Structure
```
projects/my-presentation/
├── config.yaml         # Theme and metadata
├── input/              # Source materials (dump everything here)
├── plots/              # Generated charts  
├── outline.md          # AI-generated content outline
├── slides/             # Individual HTML slide files
└── my-presentation.pdf # Export output
```

## Template System

SlideAgent provides 12 fundamental slide templates. Each template is deliberately minimal—just enough structure for consistent styling while remaining flexible for AI content generation. This is probably one of the key areas of development where contributions from others would be awesome!

## Chart Integration

The PlotBuddy system generates dual-output charts:
- **Branded versions**: Complete with logos and corporate styling
- **Clean versions**: Optimized for slide integration

```python
from src.charts.utils.plot_buddy import PlotBuddy

buddy = PlotBuddy.from_project_config()
fig, ax = buddy.setup_figure()
# ... plotting code ...
branded_path, clean_path = buddy.save("plots/analysis.png", branded=True)
```


CLAUDE.md provides more context on how the system works (written for Claude Code, but easily adaptable to other coding agents as well.)