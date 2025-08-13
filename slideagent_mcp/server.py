#!/usr/bin/env python3
"""
SlideAgent MCP Helper Server

A Model Context Protocol (MCP) helper server that provides project management
tools specifically for SlideAgent. This server wraps SlideAgent functionality
as MCP tools, enabling AI agents to manage presentation projects efficiently.

Tool Categories:
- Project Management: create, list, and manage projects
- List Tools: discover templates, projects, and themes  
- Init Tools: initialize slides and charts from templates
- Update Tools: modify project configuration and memory
- Generation Tools: PDF generation and live viewing
"""

import os
import sys
import json
import yaml
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("slideagent")

# =============================================================================
# DIRECTORY STRUCTURE CONSTANTS
# =============================================================================

# Base directories
BASE_DIR = Path(__file__).parent.parent  # SlideAgent project root
MCP_PACKAGE_DIR = Path(__file__).parent  # slideagent_mcp package directory

# System resources (inside MCP package - read-only)
SYSTEM_RESOURCES_DIR = MCP_PACKAGE_DIR / "resources"
SYSTEM_TEMPLATES_DIR = SYSTEM_RESOURCES_DIR / "templates"
SYSTEM_SLIDE_TEMPLATES_DIR = SYSTEM_TEMPLATES_DIR / "slides"
SYSTEM_CHART_TEMPLATES_DIR = SYSTEM_TEMPLATES_DIR / "charts"
SYSTEM_REPORT_TEMPLATES_DIR = SYSTEM_TEMPLATES_DIR / "reports"
SYSTEM_OUTLINE_TEMPLATES_DIR = SYSTEM_TEMPLATES_DIR / "outlines"
SYSTEM_THEMES_DIR = SYSTEM_RESOURCES_DIR / "themes" / "core"

# =============================================================================
# FILE NAMING CONVENTIONS
# =============================================================================

# CSS file names
SLIDE_BASE_CSS_NAME = "slide_base.css"  # Core 16:9 slide styling
REPORT_BASE_CSS_NAME = "report_base.css"  # Core 8.5x11 report styling

# CSS source paths
SLIDE_BASE_CSS_SOURCE = SYSTEM_SLIDE_TEMPLATES_DIR / SLIDE_BASE_CSS_NAME
REPORT_BASE_CSS_SOURCE = SYSTEM_REPORT_TEMPLATES_DIR / REPORT_BASE_CSS_NAME

# Relative paths for HTML to CSS references
REL_PATH_TO_THEME_FROM_SLIDES = "../theme"  # From slides/*.html to theme/
REL_PATH_TO_THEME_FROM_REPORTS = "../theme"  # From reports/*.html to theme/

# Theme file naming patterns: {theme_name}{suffix}
THEME_CSS_SUFFIX = "_theme.css"  # e.g., acme_corp_theme.css
THEME_STYLE_SUFFIX = "_style.mplstyle"  # e.g., acme_corp_style.mplstyle
THEME_ICON_LOGO_SUFFIX = "_icon_logo.png"  # e.g., acme_corp_icon_logo.png
THEME_TEXT_LOGO_SUFFIX = "_text_logo.png"  # e.g., acme_corp_text_logo.png

# =============================================================================
# USER SPACE DIRECTORIES
# =============================================================================

# User directories (writable space for user content)
USER_PROJECTS_DIR = BASE_DIR / "user_projects"  # User presentation projects
USER_RESOURCES_DIR = BASE_DIR / "user_resources"  # User custom resources
USER_THEMES_DIR = USER_RESOURCES_DIR / "themes"  # User custom themes
USER_TEMPLATES_DIR = USER_RESOURCES_DIR / "templates"  # User custom templates

# =============================================================================
# LEGACY DIRECTORIES (for backward compatibility)
# =============================================================================

LEGACY_PROJECTS_DIR = BASE_DIR / "projects"  # Deprecated: use user_projects
LEGACY_THEMES_DIR = BASE_DIR / "themes"  # Deprecated: being phased out
LEGACY_SLIDE_TEMPLATES_DIR = BASE_DIR / "slide_templates"  # Deprecated
LEGACY_CHART_TEMPLATES_DIR = BASE_DIR / "chart_templates"  # Deprecated
LEGACY_MARKDOWN_TEMPLATES_DIR = BASE_DIR / "markdown_templates"  # Deprecated


# Resolvers with precedence: user → legacy → system (for templates/themes),
# and user → legacy for projects.
def resolve_projects_dir() -> Path:
    # Always use user_projects/ directory
    return USER_PROJECTS_DIR

def resolve_slide_template_dirs() -> List[Path]:
    candidates = [
        USER_TEMPLATES_DIR / "slides",
        SYSTEM_SLIDE_TEMPLATES_DIR,
    ]
    return [p for p in candidates if p.exists()]

def resolve_chart_template_dirs() -> List[Path]:
    candidates = [
        USER_TEMPLATES_DIR / "charts",
        SYSTEM_CHART_TEMPLATES_DIR,
    ]
    return [p for p in candidates if p.exists()]

def resolve_theme_dirs() -> List[Path]:
    # User themes root, legacy examples/private, then system core
    candidates = []
    if USER_THEMES_DIR.exists():
        candidates.append(USER_THEMES_DIR)
    # Legacy: themes/examples and themes/private
    examples_dir = LEGACY_THEMES_DIR / "examples"
    private_dir = LEGACY_THEMES_DIR / "private"
    if examples_dir.exists():
        candidates.append(examples_dir)
    if private_dir.exists():
        candidates.append(private_dir)
    if SYSTEM_THEMES_DIR.exists():
        candidates.append(SYSTEM_THEMES_DIR)
    return candidates

def resolve_outline_template_paths() -> List[Path]:
    candidates = [
        USER_TEMPLATES_DIR / "outlines" / "outline_template.md",
        LEGACY_MARKDOWN_TEMPLATES_DIR / "outline_template.md",
        SYSTEM_OUTLINE_TEMPLATES_DIR / "outline_template.md",
    ]
    return [p for p in candidates if p.exists()]

# Track live viewer processes
LIVE_VIEWER_PROCESSES = {}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_project_theme(project_dir: Path) -> str:
    """
    Derive theme name from theme folder files.
    Looks for *_theme.css file and extracts the theme name.
    Raises error if no theme found.
    """
    theme_dir = project_dir / "theme"
    if not theme_dir.exists():
        raise ValueError(f"No theme folder found in project {project_dir.name}")
    
    # Look for *_theme.css file
    for css_file in theme_dir.glob("*_theme.css"):
        # Extract theme name from filename
        theme_name = css_file.stem.replace("_theme", "")
        return theme_name
    
    raise ValueError(f"No theme CSS file found in {theme_dir}")

# =============================================================================
# PROJECT MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
def create_project(name: str, theme: str = "acme_corp", description: str = "") -> str:
    """
    Create a new SlideAgent project with proper directory structure.
    
    Args:
        name: Project name (will be sanitized for filesystem)
        theme: Theme to use (default: acme_corp)
        description: Optional project description
    
    Returns:
        Success message with project path
    """
    # Sanitize project name
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    project_dir = resolve_projects_dir() / safe_name
    
    if project_dir.exists():
        return f"Error: Project '{safe_name}' already exists"
    
    # Create directory structure
    dirs = [
        project_dir,
        project_dir / "slides",  # Can contain both slides (16:9) and report pages (8.5x11)
        project_dir / "validation",
        project_dir / "plots", 
        project_dir / "input",
        project_dir / "theme"  # Contains both slide_base.css and report_base.css
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Copy theme files to project
    theme_source = None
    # First check user themes
    if (USER_THEMES_DIR / theme).exists():
        theme_source = USER_THEMES_DIR / theme
    # Then check system themes
    elif (SYSTEM_THEMES_DIR / theme).exists():
        theme_source = SYSTEM_THEMES_DIR / theme
    else:
        # Default to system acme_corp theme
        theme_source = SYSTEM_THEMES_DIR / "acme_corp"
        theme = "acme_corp"
    
    if theme_source and theme_source.exists():
        # Copy all theme files to project/theme/
        for theme_file in theme_source.glob("*"):
            if theme_file.is_file():
                shutil.copy2(theme_file, project_dir / "theme" / theme_file.name)
    
    # Also copy slide_base.css to project/theme/ for self-containment
    if SLIDE_BASE_CSS_SOURCE.exists():
        shutil.copy2(SLIDE_BASE_CSS_SOURCE, project_dir / "theme" / SLIDE_BASE_CSS_NAME)
    
    # Also copy report_base.css to project/theme/ for report support
    if REPORT_BASE_CSS_SOURCE.exists():
        shutil.copy2(REPORT_BASE_CSS_SOURCE, project_dir / "theme" / REPORT_BASE_CSS_NAME)
    
    # No longer creating config.yaml - theme is derived from theme folder files
    
    # Initialize outline from template
    outline_paths = resolve_outline_template_paths()
    if outline_paths:
        with open(outline_paths[0], "r") as f:
            outline_content = f.read()
        
        # Replace placeholders
        outline_content = outline_content.replace("{title}", safe_name.replace("_", " ").title())
        outline_content = outline_content.replace("{author}", "SlideAgent")
        outline_content = outline_content.replace("{theme}", theme)
        
        with open(project_dir / "outline.md", "w") as f:
            f.write(outline_content)
    
    
    return f"Created project '{safe_name}' at {project_dir}"

@mcp.tool()
def list_projects() -> List[Dict[str, Any]]:
    """
    List all existing SlideAgent projects.
    
    Returns:
        List of project information dictionaries
    """
    projects = []
    
    projects_root = resolve_projects_dir()
    if not projects_root.exists():
        return projects
    
    for project_dir in projects_root.iterdir():
        if not project_dir.is_dir():
            continue
        
        # Get theme from theme folder
        try:
            theme = get_project_theme(project_dir)
        except ValueError:
            theme = "unknown"  # Handle projects without proper theme
        
        # Count slides
        slides_dir = project_dir / "slides"
        slide_count = len(list(slides_dir.glob("*.html"))) if slides_dir.exists() else 0
        
        # Count charts
        plots_dir = project_dir / "plots"
        chart_count = len(list(plots_dir.glob("*_clean.png"))) if plots_dir.exists() else 0
        
        projects.append({
            "name": project_dir.name,
            "path": str(project_dir),
            "theme": theme,
            "created_date": project_dir.stat().st_ctime,  # Use folder creation time
            "slides_count": slide_count,
            "charts_count": chart_count,
            "has_pdf": (project_dir / f"{project_dir.name}.pdf").exists()
        })
    
    return projects

@mcp.tool()
def get_project_info(project: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific project.
    
    Args:
        project: Project name
    
    Returns:
        Project details dictionary
    """
    project_dir = resolve_projects_dir() / project
    if not project_dir.exists():
        raise ValueError(f"Project '{project}' not found")
    
    # Get theme from theme folder
    try:
        theme = get_project_theme(project_dir)
    except ValueError:
        theme = "unknown"
    
    # Count files
    slides = list((project_dir / "slides").glob("slide_*.html")) if (project_dir / "slides").exists() else []
    charts = list((project_dir / "plots").glob("*_clean.png")) if (project_dir / "plots").exists() else []
    inputs = list((project_dir / "input").glob("*")) if (project_dir / "input").exists() else []
    
    return {
        "name": project,
        "theme": theme,
        "title": project,  # No config, so use project name
        "slides_count": len(slides),
        "charts_count": len(charts),
        "inputs_count": len(inputs),
        "has_pdf": (project_dir / f"{project}.pdf").exists(),
        "path": str(project_dir)
    }

# =============================================================================
# LIST TOOLS
# =============================================================================

@mcp.tool()
def list_themes() -> List[Dict[str, str]]:
    """
    List all available themes for SlideAgent projects.
    
    Returns:
        List of theme information with paths
    """
    themes: List[Dict[str, str]] = []

    def add_theme_entry(root: Path, theme_dir: Path, source_type: str):
        theme_css = theme_dir / f"{theme_dir.name}_theme.css"
        if theme_css.exists():
            # Build a display path relative to BASE_DIR when possible
            try:
                rel = theme_dir.relative_to(BASE_DIR)
                rel_path = str(rel)
            except Exception:
                rel_path = str(theme_dir)
            themes.append({
                "name": theme_dir.name,
                "path": rel_path,
                "type": source_type,
            })

    for root in resolve_theme_dirs():
        source_type = (
            "user" if root == USER_THEMES_DIR else
            "example" if root.name == "examples" else
            "private" if root.name == "private" else
            "system"
        )
        for theme_dir in root.iterdir():
            if theme_dir.is_dir():
                add_theme_entry(root, theme_dir, source_type)

    # De-duplicate by theme name preferring earlier (user > legacy > system)
    unique: Dict[str, Dict[str, str]] = {}
    ordered = []
    for t in themes:
        if t["name"] not in unique:
            unique[t["name"]] = t
            ordered.append(t)
    return ordered

@mcp.tool()
def list_slide_templates() -> List[Dict[str, Any]]:
    """
    List all available slide templates with metadata.
    
    Returns:
        List of template information with paths and use cases
    """
    templates: List[Dict[str, Any]] = []

    for root in resolve_slide_template_dirs():
        source = (
            "user" if root == USER_TEMPLATES_DIR / "slides" else
            "legacy" if root == LEGACY_SLIDE_TEMPLATES_DIR else
            "system"
        )
        for template_file in sorted(root.glob("*.html")):
            with open(template_file, "r") as f:
                content = f.read()
            use_case = "General purpose slide"
            if "<!-- Use case:" in content:
                start = content.find("<!-- Use case:") + len("<!-- Use case:")
                end = content.find("-->", start)
                if end > start:
                    use_case = content[start:end].strip()
            try:
                rel = template_file.relative_to(BASE_DIR)
                rel_path = str(rel)
            except Exception:
                rel_path = str(template_file)
            templates.append({
                "name": template_file.stem,
                "path": rel_path,
                "file": template_file.name,
                "use_case": use_case,
                "source": source,
            })

    # De-duplicate by name preferring earlier (user > legacy > system)
    unique: Dict[str, Dict[str, Any]] = {}
    ordered = []
    for t in templates:
        if t["name"] not in unique:
            unique[t["name"]] = t
            ordered.append(t)
    return ordered

@mcp.tool()
def list_report_templates() -> List[Dict[str, Any]]:
    """
    List all available report page templates with metadata.
    
    Returns:
        List of template information with paths and use cases
    """
    templates: List[Dict[str, Any]] = []
    
    # List templates from system report templates directory
    if SYSTEM_REPORT_TEMPLATES_DIR.exists():
        for template_file in sorted(SYSTEM_REPORT_TEMPLATES_DIR.glob("*.html")):
            # Map template names to use cases
            use_cases = {
                "01_cover_page": "Cover page with title, subtitle, and branding",
                "02_table_of_contents": "Table of contents with section navigation",
                "03_executive_letter": "Executive letter or foreword",
                "04_section_divider": "Section divider with visual impact",
                "05_content_page": "Standard content page with text and images",
                "06_data_visualization": "Full-page data visualization with metrics",
                "07_pull_quote": "Pull quote or key insight page",
                "08_conclusion": "Conclusion with key takeaways and next steps"
            }
            
            use_case = use_cases.get(template_file.stem, "Report page template")
            
            templates.append({
                "name": template_file.stem,
                "path": str(template_file.relative_to(BASE_DIR)),
                "file": template_file.name,
                "use_case": use_case,
                "source": "system",
            })
    
    # Also check user templates
    user_report_templates = USER_TEMPLATES_DIR / "reports"
    if user_report_templates.exists():
        for template_file in sorted(user_report_templates.glob("*.html")):
            templates.append({
                "name": template_file.stem,
                "path": str(template_file.relative_to(BASE_DIR)),
                "file": template_file.name,
                "use_case": "User custom report template",
                "source": "user",
            })
    
    return templates

@mcp.tool()
def list_chart_templates() -> List[Dict[str, Any]]:
    """
    List all available chart templates with metadata.
    
    Returns:
        List of template information with paths and descriptions
    """
    templates: List[Dict[str, Any]] = []

    for root in resolve_chart_template_dirs():
        source = (
            "user" if root == USER_TEMPLATES_DIR / "charts" else
            "legacy" if root == LEGACY_CHART_TEMPLATES_DIR else
            "system"
        )
        for template_file in sorted(root.glob("*.py")):
            with open(template_file, "r") as f:
                content = f.read()
            description = "Chart template"
            if '"""' in content:
                start = content.find('"""') + 3
                end = content.find('"""', start)
                if end > start:
                    description = content[start:end].strip().split('\n')[0]
            try:
                rel = template_file.relative_to(BASE_DIR)
                rel_path = str(rel)
            except Exception:
                rel_path = str(template_file)
            templates.append({
                "name": template_file.stem,
                "path": rel_path,
                "file": template_file.name,
                "description": description,
                "source": source,
            })

    # De-duplicate by name preferring earlier (user > legacy > system)
    unique: Dict[str, Dict[str, Any]] = {}
    ordered = []
    for t in templates:
        if t["name"] not in unique:
            unique[t["name"]] = t
            ordered.append(t)
    return ordered

# =============================================================================
# INIT TOOLS
# =============================================================================

@mcp.tool()
def init_slide(project: str, number: str, template: str = None, 
              title: str = "", subtitle: str = "", section: str = "") -> str:
    """
    Initialize a slide from a template for a specific project.
    
    Args:
        project: Name of the project
        number: Slide number (e.g., '01' or 'slide_01')
        template: Path to the template file
        title: Main title for the slide
        subtitle: Subtitle for the slide
        section: Section label for the slide
    
    Returns:
        Path to the created slide file
    """
    project_dir = resolve_projects_dir() / project
    if not project_dir.exists():
        return f"Error: Project '{project}' not found"
    
    # Handle template path - try to resolve from multiple locations
    if template:
        # First try as absolute path from BASE_DIR
        template_file = BASE_DIR / template
        if not template_file.exists():
            # Try relative to system templates
            template_file = SYSTEM_SLIDE_TEMPLATES_DIR / Path(template).name
            if not template_file.exists():
                return f"Error: Template not found at {template}"
    else:
        # Use default base_slide template from system
        template_file = SYSTEM_SLIDE_TEMPLATES_DIR / "01_base_slide.html"
        if not template_file.exists():
            return f"Error: Default template not found"
    
    # Read template
    with open(template_file, "r") as f:
        content = f.read()
    
    # Get theme from theme folder
    try:
        theme = get_project_theme(project_dir)
    except ValueError as e:
        return f"Error: {e}"
    
    # Replace CSS path placeholders
    # Both CSS files are now local to the project (in project/theme/)
    # From slides/ to theme/ is ../theme/
    base_css_path = f"{REL_PATH_TO_THEME_FROM_SLIDES}/{SLIDE_BASE_CSS_NAME}"
    theme_css_path = f"{REL_PATH_TO_THEME_FROM_SLIDES}/{theme}{THEME_CSS_SUFFIX}"
    
    # Replace the placeholders
    content = content.replace('[BASE_CSS_PATH]', base_css_path)
    content = content.replace('[THEME_CSS_PATH]', theme_css_path)
    
    # Replace placeholders
    if not number.startswith('slide_'):
        number = f"slide_{number.zfill(2)}"
    
    slide_num = number.replace('slide_', '')
    content = content.replace('[TITLE]', title)
    content = content.replace('[SUBTITLE]', subtitle)
    content = content.replace('[SECTION]', section)
    content = content.replace('[PAGE_NUMBER]', slide_num)
    content = content.replace('XX', slide_num)  # Legacy support
    
    # Create slide file
    slide_name = f"{number}.html"
    slide_path = project_dir / "slides" / slide_name
    
    with open(slide_path, "w") as f:
        f.write(content)
    
    return str(slide_path)

@mcp.tool()
def init_report_page(project: str, number: str, template: str = None, 
                     title: str = "", subtitle: str = "", section: str = "") -> str:
    """
    Initialize a report page from a template for a specific project.
    
    Args:
        project: Name of the project
        number: Page number (e.g., '01' or 'page_01')
        template: Filename of the template (e.g., '01_cover_page.html')
        title: Main title for the page
        subtitle: Subtitle for the page
        section: Section label for the page
    
    Returns:
        Path to the created report file
    """
    project_dir = resolve_projects_dir() / project
    if not project_dir.exists():
        return f"Error: Project '{project}' not found"
    
    # Use the slides directory for all HTML content (slides and reports)
    slides_dir = project_dir / "slides"
    if not slides_dir.exists():
        slides_dir.mkdir(exist_ok=True)  # Create if missing
    
    # Handle template
    if template:
        # Try to find template in system reports templates
        template_file = SYSTEM_REPORT_TEMPLATES_DIR / template
        if not template_file.exists():
            # Try with just the filename
            template_file = SYSTEM_REPORT_TEMPLATES_DIR / Path(template).name
            if not template_file.exists():
                return f"Error: Template '{template}' not found"
    else:
        # Default to content page template
        template_file = SYSTEM_REPORT_TEMPLATES_DIR / "05_content_page.html"
        if not template_file.exists():
            return f"Error: Default template not found"
    
    # Read template
    with open(template_file, "r") as f:
        content = f.read()
    
    # Get theme from theme folder
    try:
        theme = get_project_theme(project_dir)
    except ValueError as e:
        return f"Error: {e}"
    
    # Replace CSS path placeholders
    # From reports/ to theme/ is ../theme/
    base_css_path = f"{REL_PATH_TO_THEME_FROM_REPORTS}/{REPORT_BASE_CSS_NAME}"
    theme_css_path = f"{REL_PATH_TO_THEME_FROM_REPORTS}/{theme}{THEME_CSS_SUFFIX}"
    
    # Replace placeholders
    content = content.replace('[THEME]', theme)
    content = content.replace('[REPORT_TITLE]', title)
    content = content.replace('[CONTENT_TITLE]', title)
    content = content.replace('[CONTENT_SUBTITLE]', subtitle)
    content = content.replace('[SECTION_NAME]', section)
    
    # Normalize page number
    if not number.startswith('page_'):
        number = f"page_{number.zfill(2)}"
    
    page_num = number.replace('page_', '')
    content = content.replace('[PAGE_NUMBER]', page_num)
    
    # Create report file (in slides directory with report_ prefix for clarity)
    page_name = f"report_{number}.html"
    page_path = slides_dir / page_name
    
    with open(page_path, "w") as f:
        f.write(content)
    
    return str(page_path)

@mcp.tool()
def init_chart(project: str, name: str, template: str = None) -> str:
    """
    Initialize a chart from a template for a specific project.
    
    Args:
        project: Name of the project
        name: Name for the chart file (without .py extension)
        template: Path to the template file
    
    Returns:
        Path to the created chart file
    """
    project_dir = resolve_projects_dir() / project
    if not project_dir.exists():
        return f"Error: Project '{project}' not found"
    
    # Clean chart name
    if name.endswith('.py'):
        name = name[:-3]
    
    # Handle template - try to resolve from multiple locations
    if template:
        # First try as absolute path from BASE_DIR
        template_file = BASE_DIR / template
        if not template_file.exists():
            # Try relative to system templates
            template_file = SYSTEM_CHART_TEMPLATES_DIR / Path(template).name
            if not template_file.exists():
                return f"Error: Template not found at {template}"
        
        with open(template_file, "r") as f:
            content = f.read()
        
        # Update output filenames
        content = content.replace('OUTPUT_NAME', name)
    else:
        # Create minimal boilerplate
        content = f'''#!/usr/bin/env python3
"""
Chart: {name}
Generated chart for {project} project
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from slideagent_mcp.utils.plot_buddy import PlotBuddy
import matplotlib.pyplot as plt
import numpy as np

# Initialize PlotBuddy with project config
buddy = PlotBuddy.from_project_config()

# === EDIT THIS SECTION ===
# Configure your data and chart here
data = [10, 20, 30, 40]
labels = ['A', 'B', 'C', 'D']
# === END EDIT SECTION ===

# Create figure with theme styling
fig, ax = buddy.setup_figure(figsize=(14, 7.875))  # Wide format for slides

# Create your visualization
ax.bar(labels, data)
ax.set_xlabel('Categories')
ax.set_ylabel('Values')

# Save branded version (with titles)
buddy.add_titles(ax, "Chart Title", "Chart Subtitle")
buddy.add_logo(fig, buddy.icon_logo_path)
buddy.save("plots/{name}_branded.png", branded=False)

# Create clean version for slides
fig, ax = buddy.setup_figure(figsize=(14, 7.875))
ax.bar(labels, data)
ax.set_xlabel('Categories')
ax.set_ylabel('Values')
ax.text(0.5, 1.02, 'Chart Subtitle', transform=ax.transAxes, 
        ha='center', fontsize=12, color='#666')
plt.tight_layout()
plt.savefig("plots/{name}_clean.png", dpi=150, bbox_inches='tight')

print("✅ Chart generated successfully!")
print("   - Branded version: plots/{name}_branded.png")
print("   - Clean version: plots/{name}_clean.png")
'''
    
    # Create chart file
    chart_path = project_dir / "plots" / f"{name}.py"
    
    with open(chart_path, "w") as f:
        f.write(content)
    
    # Make executable
    chart_path.chmod(0o755)
    
    return str(chart_path)

# =============================================================================
# UPDATE TOOLS
# =============================================================================

@mcp.tool()
def swap_theme(project: str, theme: str) -> str:
    """
    Change the theme for an existing project.
    
    Args:
        project: Name of the project
        theme: Name of the new theme to apply
    
    Returns:
        Success message
    """
    project_dir = resolve_projects_dir() / project
    if not project_dir.exists():
        return f"Error: Project '{project}' not found"
    
    # Check if theme exists
    theme_found = False
    theme_path = None
    
    # Search in user themes first
    if USER_THEMES_DIR.exists():
        test_path = USER_THEMES_DIR / theme
        if test_path.exists() and (test_path / f"{theme}_theme.css").exists():
            theme_found = True
            theme_path = str(test_path)
    # Then legacy examples/private
    if not theme_found:
        for location in ["examples", "private"]:
            test_path = LEGACY_THEMES_DIR / location / theme
            if test_path.exists() and (test_path / f"{theme}_theme.css").exists():
                theme_found = True
                theme_path = f"themes/{location}/{theme}"
                break
    # Finally system core themes
    if not theme_found and (SYSTEM_THEMES_DIR / theme).exists():
        test_path = SYSTEM_THEMES_DIR / theme
        if (test_path / f"{theme}_theme.css").exists():
            theme_found = True
            theme_path = str(test_path)
    
    if not theme_found:
        return f"Error: Theme '{theme}' not found"
    
    # Get current theme from theme folder
    try:
        old_theme = get_project_theme(project_dir)
    except ValueError:
        old_theme = "unknown"
    
    # Clear old theme files from project/theme/
    theme_dir = project_dir / "theme"
    if theme_dir.exists():
        for file in theme_dir.glob("*"):
            if file.name not in [SLIDE_BASE_CSS_NAME, REPORT_BASE_CSS_NAME]:  # Keep base CSS files
                file.unlink()
    
    # Copy new theme files to project/theme/
    theme_source = Path(theme_path) if Path(theme_path).is_absolute() else BASE_DIR / theme_path
    if theme_source.exists():
        for theme_file in theme_source.glob("*"):
            if theme_file.is_file():
                shutil.copy2(theme_file, theme_dir / theme_file.name)
    
    # Update existing slides to use new theme
    slides_dir = project_dir / "slides"
    if slides_dir.exists():
        import re
        for slide_file in slides_dir.glob("*.html"):
            with open(slide_file, "r") as f:
                content = f.read()
            
            # Replace theme CSS references
            if old_theme != "unknown":
                content = re.sub(
                    rf'{old_theme}_theme\.css',
                    f'{theme}_theme.css',
                    content
                )
            
            with open(slide_file, "w") as f:
                f.write(content)
    
    return f"Updated project '{project}' to use theme '{theme}'"

# =============================================================================
# GENERATION TOOLS
# =============================================================================

@mcp.tool()
def generate_pdf(project: str, output_path: str = None, format: str = "slides") -> Dict[str, Any]:
    """
    Generate PDF from slides or report pages in a project.
    
    Args:
        project: Name of the project
        output_path: Custom output path (optional)
        format: "slides" for horizontal 16:9, "report" for vertical 8.5x11 (default: "slides")
    
    Returns:
        Result dictionary with path or error
    """
    project_dir = resolve_projects_dir() / project
    if not project_dir.exists():
        return {"success": False, "error": f"Project '{project}' not found"}
    
    slides_dir = project_dir / "slides"
    if not slides_dir.exists():
        return {"success": False, "error": f"No slides directory found in project '{project}'"}
    
    # Determine which files to include based on format
    if format == "report":
        # For reports, include only report_*.html files
        html_files = list(slides_dir.glob("report*.html"))
        if not html_files:
            return {"success": False, "error": f"No report pages found in project '{project}'"}
        default_output = str(project_dir / f"{project}-report.pdf")
    else:
        # For slides, include slide_*.html files (or all if no specific pattern)
        html_files = list(slides_dir.glob("slide_*.html"))
        if not html_files:
            # Fallback to all HTML files if no slide_ pattern
            html_files = list(slides_dir.glob("*.html"))
            # Exclude report files from slide generation
            html_files = [f for f in html_files if not f.name.startswith("report")]
        if not html_files:
            return {"success": False, "error": f"No slides found in project '{project}'"}
        default_output = str(project_dir / f"{project}.pdf")
    
    output = output_path or default_output
    
    # Run pdf_generator.js from utils directory with format parameter
    pdf_script = Path(__file__).parent / "utils" / "pdf_generator.js"
    if not pdf_script.exists():
        return {"success": False, "error": "PDF generator script not found"}
    
    try:
        # Pass format as third argument to the generator
        result = subprocess.run(
            ["node", str(pdf_script), str(slides_dir), output, format],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR)
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "path": output,
                "message": f"PDF generated successfully ({format} format)",
                "format": format
            }
        else:
            return {
                "success": False,
                "error": result.stderr or "PDF generation failed"
            }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# Note: Screenshot validation is now done via Puppeteer MCP tools
# Use mcp__puppeteer__puppeteer_navigate and mcp__puppeteer__puppeteer_screenshot

@mcp.tool()
def start_live_viewer(project: str, port: int = 8080) -> Dict[str, Any]:
    """
    Start the live viewer server for a project.
    
    Args:
        project: Name of the project
        port: Port to run the server on (default 8080)
    
    Returns:
        Result dictionary with viewer URL or error
    """
    global LIVE_VIEWER_PROCESSES
    
    project_dir = resolve_projects_dir() / project
    if not project_dir.exists():
        return {"success": False, "error": f"Project '{project}' not found"}
    
    # Kill anything on the target port first
    try:
        lsof_cmd = ["lsof", "-ti", f":{port}"]
        result = subprocess.run(lsof_cmd, capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(["kill", "-9", pid], capture_output=True)
    except:
        pass  # If lsof fails, continue anyway
    
    # Also kill any existing live_viewer_server processes
    subprocess.run(["pkill", "-f", "node.*live_viewer_server"], capture_output=True)
    
    # Start viewer from same slideagent_mcp directory
    viewer_script = Path(__file__).parent / "utils" / "live_viewer_server.js"
    if not viewer_script.exists():
        return {"success": False, "error": "Live viewer script not found"}
    
    try:
        env = os.environ.copy()
        env["PORT"] = str(port)
        
        process = subprocess.Popen(
            ["node", str(viewer_script), project],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        LIVE_VIEWER_PROCESSES[project] = process
        
        return {
            "success": True,
            "url": f"http://localhost:{port}",
            "message": f"Live viewer started for project '{project}'",
            "pid": process.pid
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def stop_live_viewer(project: str = None) -> Dict[str, Any]:
    """
    Stop the live viewer server.
    
    Args:
        project: Name of the project (optional, stops all if not specified)
    
    Returns:
        Result dictionary
    """
    global LIVE_VIEWER_PROCESSES
    
    if project and project in LIVE_VIEWER_PROCESSES:
        process = LIVE_VIEWER_PROCESSES[project]
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()
        
        del LIVE_VIEWER_PROCESSES[project]
        return {"success": True, "message": f"Stopped live viewer for project '{project}'"}
    else:
        # Kill all live viewer processes
        subprocess.run(["pkill", "-f", "node.*live_viewer_server"], capture_output=True)
        LIVE_VIEWER_PROCESSES.clear()
        return {"success": True, "message": "Stopped all live viewers"}

def _build_tree(path: Path, prefix: str = "", is_last: bool = True, max_depth: int = 3, current_depth: int = 0, stop_at_project_level: bool = False) -> List[str]:
    """Helper to recursively build directory tree visualization."""
    lines = []
    
    if current_depth >= max_depth:
        return lines
    
    # Skip certain directories
    skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.pytest_cache', '.DS_Store'}
    
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        items = [item for item in items if item.name not in skip_dirs and not item.name.startswith('.')]
        
        for i, item in enumerate(items):
            is_last_item = (i == len(items) - 1)
            connector = "└── " if is_last_item else "├── "
            extension = "    " if is_last_item else "│   "
            
            # Add docstring for Python files
            doc_info = ""
            if item.is_file() and item.suffix == '.py':
                try:
                    content = item.read_text()
                    # Extract module-level docstring (handle shebang lines)
                    file_lines = content.split('\n')
                    for j, line in enumerate(file_lines[:5]):  # Check first 5 lines
                        if line.strip().startswith('"""'):
                            # Found start of docstring
                            docstring_parts = content.split('"""')
                            if len(docstring_parts) >= 2:
                                docstring = docstring_parts[1].strip().split('\n')[0]
                                if docstring and not docstring.startswith('TEMPLATE_META'):
                                    # Show full docstring, not truncated
                                    doc_info = f"  # {docstring}"
                                elif docstring.startswith('TEMPLATE_META'):
                                    # For template meta, get the title
                                    meta_lines = docstring_parts[1].strip().split('\n')
                                    for meta_line in meta_lines:
                                        if 'title:' in meta_line:
                                            title = meta_line.split('title:')[1].strip()
                                            doc_info = f"  # {title}"
                                            break
                            break
                except:
                    pass
            
            lines.append(f"{prefix}{connector}{item.name}{doc_info}")
            
            # For user_projects, stop at project level (don't recurse into project folders)
            if item.is_dir() and not (stop_at_project_level and current_depth == 0):
                new_prefix = prefix + extension
                lines.extend(_build_tree(item, new_prefix, is_last_item, max_depth, current_depth + 1, stop_at_project_level))
    except PermissionError:
        pass
    
    return lines

@mcp.tool()
def view_repo_structure() -> str:
    """
    View the complete SlideAgent repository structure with actual directory traversal.
    
    Provides a comprehensive view including:
    - Actual directory tree visualization
    - Template discovery for slides, reports, and charts
    - Naming conventions and path relationships
    - Python module docstrings where relevant
    
    Returns:
        String: Formatted repository structure with live directory tree
    """
    structure = []
    structure.append("=" * 80)
    structure.append("SLIDEAGENT REPOSITORY STRUCTURE - LIVE VIEW")
    structure.append("=" * 80)
    structure.append("")
    
    # Actual directory tree
    structure.append("📁 ACTUAL DIRECTORY TREE:")
    structure.append("-" * 40)
    structure.append("")
    
    # Show slideagent_mcp directory tree
    mcp_dir = Path(__file__).parent
    if mcp_dir.exists():
        structure.append("slideagent_mcp/")
        tree_lines = _build_tree(mcp_dir, "", max_depth=4)
        structure.extend(tree_lines)
    structure.append("")
    
    # Show user_projects if it exists (stop at project level)
    projects_dir = resolve_projects_dir()
    if projects_dir.exists():
        structure.append("user_projects/")
        # Only show project names, not their internal structure
        structure.extend(_build_tree(projects_dir, "", max_depth=1, stop_at_project_level=True))
        structure.append("")
    
    
    # Path relationships
    structure.append("🔗 PATH RELATIONSHIPS:")
    structure.append("-" * 40)
    structure.append("From slides/slide_*.html:")
    structure.append(f"  • Base CSS: {REL_PATH_TO_THEME_FROM_SLIDES}/{SLIDE_BASE_CSS_NAME}")
    structure.append(f"  • Theme CSS: {REL_PATH_TO_THEME_FROM_SLIDES}/{{theme-name}}{THEME_CSS_SUFFIX}")
    structure.append("  • Charts: ../plots/{chart-name}_clean.png")
    structure.append("")
    structure.append("From reports/report_*.html:")
    structure.append(f"  • Base CSS: {REL_PATH_TO_THEME_FROM_SLIDES}/{REPORT_BASE_CSS_NAME}")
    structure.append(f"  • Theme CSS: {REL_PATH_TO_THEME_FROM_SLIDES}/{{theme-name}}{THEME_CSS_SUFFIX}")
    structure.append("")
    
    # Naming conventions
    structure.append("📝 NAMING CONVENTIONS:")
    structure.append("-" * 40)
    structure.append("Slides: slide_01.html, slide_02.html, ...")
    structure.append("Reports: report_01.html, report_02.html, ...")
    structure.append("Charts: {name}_clean.png (for slides/reports)")
    structure.append("        {name}_branded.png (standalone)")
    structure.append("")
    
    # System constants
    structure.append("⚙️ SYSTEM CONSTANTS:")
    structure.append("-" * 40)
    structure.append(f"Slide Base CSS: {SLIDE_BASE_CSS_NAME}")
    structure.append(f"Report Base CSS: {REPORT_BASE_CSS_NAME}")
    structure.append(f"Theme path from content: {REL_PATH_TO_THEME_FROM_SLIDES}")
    structure.append("")
    
    # Quick tips
    structure.append("💡 QUICK TIPS:")
    structure.append("-" * 40)
    structure.append("• Slides use 16:9 aspect ratio (1920x1080)")
    structure.append("• Reports use 8.5x11 vertical layout")
    structure.append("• Use _clean.png charts in slides/reports (no titles)")
    structure.append("• Use _branded.png charts for standalone docs")
    structure.append("• Each project has its own theme/ folder")
    structure.append("• CSS paths are relative to content location")
    structure.append("")
    
    structure.append("=" * 80)
    
    return "\n".join(structure)


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()