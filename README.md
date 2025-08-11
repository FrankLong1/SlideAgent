# SlideAgent

*A minimal presentation framework designed for AI agents*

## What is SlideAgent?

SlideAgent is a presentation generation system built specifically for AI coding agents like Claude Code. Instead of complex UIs and human-centric abstractions, it provides simple HTML/CSS templates that AI agents can efficiently populate with content.

The system follows Richard Sutton's bitter lesson: rather than encoding human presentation design principles, we provide minimal structure and let computational scaling drive quality. 

## Core Architecture

SlideAgent consists of just the essential components needed for professional slide generation:

- **Slide Templates**: Minimal HTML structures covering all presentation needs
- **Theme System**: CSS-based branding (colors, fonts, logos)  
- **Chart Integration**: Python matplotlib with consistent styling via PlotBuddy
- **MCP Integration**: Model Context Protocol for seamless AI agent interaction

## Workflow

1. **Setup**: Activate Python environment and install dependencies
2. **Create Project**: Use MCP tool to initialize project with theme
3. **Add Input**: Place source materials in project's input folder
4. **Generate Outline**: AI analyzes inputs and creates slide structure
5. **Build Slides**: Parallel agents populate templates with content
6. **Preview**: Live viewer shows slides during generation
7. **Export**: Generate PDF for final presentation

## Why It Works

AI agents excel at:
- Selecting appropriate templates for content types
- Extracting key insights from raw materials  
- Populating HTML structures consistently
- Maintaining theme coherence across slides
- Generating slides in parallel for speed

The system avoids human-centric complexity (drag-and-drop UIs, WYSIWYG editors) in favor of simple, scalable template population.

## Quick Start with MCP

### 1. Environment Setup
```bash
# Activate environment
source venv/bin/activate
pip install -r requirements.txt
npm install

# Install Puppeteer MCP globally (one-time setup)
npm install -g @modelcontextprotocol/server-puppeteer
claude mcp add puppeteer
```

### 2. Create Project via MCP
```python
# SlideAgent MCP tools are auto-configured via .mcp.json
create_project("my-presentation", theme="acme_corp")
```

### 3. Project Structure
```
user_projects/my-presentation/
├── theme/                  # Self-contained theme files
│   ├── base.css           # Core styling
│   ├── acme_corp_theme.css
│   └── *.png              # Logo files
├── slides/                # Individual HTML slides
├── plots/                 # Generated charts (_clean.png for slides)
├── input/                 # Source materials
├── validation/            # Screenshot validation
├── outline.md             # Detailed content outline
└── my-presentation.pdf    # Final output
```

## MCP Architecture 

SlideAgent uses Model Context Protocol (MCP) to expose all functionality as tools that AI agents can directly call:

**Project Tools:**
- `create_project` - Initialize new presentation with theme
- `list_projects` - Show existing projects
- `list_slide_templates` - Discover available slide templates
- `list_chart_templates` - Discover chart templates
- `list_themes` - Show available themes

**Generation Tools:**
- `init_slide` - Create slide from template
- `init_chart` - Create chart from template  
- `swap_theme` - Change project theme

**Preview & Export:**
- `start_live_viewer` - Launch real-time preview
- `generate_pdf` - Export final presentation

## Key Features

- **Template Library**: 12+ slide templates for different content types
- **Chart System**: PlotBuddy generates both branded and clean chart versions
- **Theme Support**: Consistent branding across slides and charts
- **Live Preview**: Real-time feedback during development
- **PDF Export**: Professional presentation output
- **MCP Integration**: All functionality exposed as callable tools

## Documentation

See `CLAUDE.md` for detailed AI agent instructions and workflow guidance.