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

# Relative path from content folders to theme folder within a project
REL_PATH_TO_THEME_IN_PROJECT = "../theme"  # From slides/ or report_pages/ to theme/

# Theme file naming patterns: {theme_name}{suffix}
THEME_FILES = {
    "css": "_theme.css",  # e.g., acme_corp_theme.css
    "style": "_style.mplstyle",  # e.g., acme_corp_style.mplstyle
    "icon_logo": "_icon_logo.png",  # e.g., acme_corp_icon_logo.png
    "text_logo": "_text_logo.png"  # e.g., acme_corp_text_logo.png
}

# =============================================================================
# USER SPACE DIRECTORIES
# =============================================================================

# User directories (writable space for user content)
USER_PROJECTS_DIR = BASE_DIR / "user_projects"  # User presentation projects
USER_RESOURCES_DIR = BASE_DIR / "user_resources"  # User custom resources
USER_THEMES_DIR = USER_RESOURCES_DIR / "themes"  # User custom themes
USER_TEMPLATES_DIR = USER_RESOURCES_DIR / "templates"  # User custom templates




# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_project_theme(project_dir: Path) -> str:
    """Get theme name from project's .theme file."""
    theme_file = project_dir / ".theme"
    if theme_file.exists():
        return theme_file.read_text().strip()
    return "acme_corp"  # default fallback

def sanitize_project_name(name: str) -> str:
    """Convert project name to filesystem-safe format."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

def create_project_structure(project_dir: Path) -> None:
    """Create the standard project directory structure."""
    dirs = [
        project_dir,
        project_dir / "slides",  # For horizontal presentations (16:9)
        project_dir / "report_pages",  # For vertical reports (8.5x11)
        project_dir / "validation",
        project_dir / "plots", 
        project_dir / "input",
        project_dir / "theme"
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)


def copy_theme_files(theme_source: Path, project_dir: Path, theme_name: str) -> None:
    """Copy theme files to project and save theme name."""
    theme_dest = project_dir / "theme"
    
    # Copy all theme files
    for theme_file in theme_source.glob("*"):
        if theme_file.is_file():
            shutil.copy2(theme_file, theme_dest / theme_file.name)
    
    # Copy base CSS files
    if SLIDE_BASE_CSS_SOURCE.exists():
        shutil.copy2(SLIDE_BASE_CSS_SOURCE, theme_dest / SLIDE_BASE_CSS_NAME)
    if REPORT_BASE_CSS_SOURCE.exists():
        shutil.copy2(REPORT_BASE_CSS_SOURCE, theme_dest / REPORT_BASE_CSS_NAME)
    
    # Save theme name in .theme file
    (project_dir / ".theme").write_text(theme_name)


# =============================================================================
# PROJECT MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
def create_project(name: str, theme: str = "acme_corp", description: str = "") -> str:
    """
    Create a new SlideAgent project with proper directory structure.
    Creates separate folders for horizontal slides (16:9) and vertical reports (8.5x11).
    
    Args:
        name: Project name (will be sanitized for filesystem)
        theme: Theme to use (default: acme_corp)
        description: Optional project description
    
    Returns:
        Success message with project path
    """
    # Sanitize and validate
    safe_name = sanitize_project_name(name)
    project_dir = USER_PROJECTS_DIR / safe_name
    
    if project_dir.exists():
        return f"Error: Project '{safe_name}' already exists"
    
    # Create structure
    create_project_structure(project_dir)
    
    # Find and copy theme
    theme_info = get_themes(theme)
    if theme_info:
        theme_source = Path(theme_info[0]["path"])
    else:
        # Default to acme_corp if theme not found
        theme_source = SYSTEM_THEMES_DIR / "acme_corp"
        theme = "acme_corp"
    
    copy_theme_files(theme_source, project_dir, theme)
    
    # Create default outline (could be slides or report based on user preference)
    # For now, create a slides outline by default
    init_from_template(
        project=safe_name, 
        resource_type="outline",
        name="outline",
        template="outline_slides.md",
        title=safe_name.replace("_", " ").title(),
        author="SlideAgent",
        theme=theme
    )
    
    return f"Created project '{safe_name}' at {project_dir}"

@mcp.tool()
def get_projects(names=None, fields=None):
    """
    Get project(s) information.
    
    Args:
        names: None for all projects, string for one, list for multiple
        fields: Optional fields to include (name, theme, path, slides_count, 
                charts_count, inputs_count, has_pdf, created_date)
    
    Returns:
        List of project dictionaries (consistent return type)
    """
    if not USER_PROJECTS_DIR.exists():
        return []
    
    # Determine which projects to get
    if names is None:
        # Get all projects
        project_names = [p.name for p in USER_PROJECTS_DIR.iterdir() if p.is_dir()]
    elif isinstance(names, str):
        project_names = [names]
    else:
        project_names = names
    
    # Collect project info
    projects = []
    for name in project_names:
        project_dir = USER_PROJECTS_DIR / name
        if not project_dir.exists():
            continue
        
        # Build info dict
        info = {
            "name": name,
            "path": str(project_dir),
            "theme": get_project_theme(project_dir),
            "created_date": project_dir.stat().st_ctime,
        }
        
        # Add counts if needed
        if not fields or any(f in fields for f in ["slides_count", "charts_count", "inputs_count", "has_pdf"]):
            slides_dir = project_dir / "slides"
            info["slides_count"] = len(list(slides_dir.glob("*.html"))) if slides_dir.exists() else 0
            
            plots_dir = project_dir / "plots"
            info["charts_count"] = len(list(plots_dir.glob("*_clean.png"))) if plots_dir.exists() else 0
            
            input_dir = project_dir / "input"
            info["inputs_count"] = len(list(input_dir.glob("*"))) if input_dir.exists() else 0
            
            info["has_pdf"] = (project_dir / f"{name}.pdf").exists()
        
        # Filter fields if specified
        if fields:
            info = {k: v for k, v in info.items() if k in fields}
        
        projects.append(info)
    
    return projects

# =============================================================================
# GET TOOLS (unified getters for resources)
# =============================================================================

@mcp.tool()
def get_themes(names=None):
    """
    Get theme(s) information.
    
    Args:
        names: None for all themes, string for one, list for multiple
    
    Returns:
        List of theme dictionaries
    """
    # Determine which themes to get
    if names is None:
        # Get all themes from both locations
        theme_names = set()
        for location in [USER_THEMES_DIR, SYSTEM_THEMES_DIR]:
            if location.exists():
                theme_names.update(d.name for d in location.iterdir() if d.is_dir())
        theme_names = list(theme_names)
    elif isinstance(names, str):
        theme_names = [names]
    else:
        theme_names = names
    
    # Collect theme info
    themes = []
    for name in theme_names:
        # Check user first, then system
        for location in [USER_THEMES_DIR, SYSTEM_THEMES_DIR]:
            theme_dir = location / name
            if theme_dir.exists() and (theme_dir / f"{name}{THEME_FILES['css']}").exists():
                themes.append({
                    "name": name,
                    "path": str(theme_dir),
                    "source": "user" if location == USER_THEMES_DIR else "system",
                    "files": [f.name for f in theme_dir.glob("*") if f.is_file()]
                })
                break  # Found it, don't check other locations
    
    return themes

@mcp.tool()
def get_templates(type, names=None):
    """
    Get template(s) of specified type.
    
    Args:
        type: Template type - "slides", "reports", or "charts" (required)
        names: None for all templates, string for one, list for multiple
    
    Returns:
        List of template dictionaries
    """
    if type not in ["slides", "reports", "charts"]:
        raise ValueError(f"Invalid type '{type}'. Must be 'slides', 'reports', or 'charts'")
    
    # Configuration for each template type
    configs = {
        "slides": {
            "dirs": [(USER_TEMPLATES_DIR / "slides", "user"), (SYSTEM_SLIDE_TEMPLATES_DIR, "system")],
            "pattern": "*.html",
            "metadata_key": "use_case",
            "default_metadata": "General purpose slide"
        },
        "reports": {
            "dirs": [(USER_TEMPLATES_DIR / "reports", "user"), (SYSTEM_REPORT_TEMPLATES_DIR, "system")],
            "pattern": "*.html",
            "metadata_key": "use_case",
            "default_metadata": "Report page template",
            "use_cases": {
                "00_endnotes": "Endnotes and references",
                "01_cover_page": "Cover page with title, subtitle, and branding",
                "02_table_of_contents": "Table of contents with section navigation",
                "04_section_divider": "Section divider with visual impact",
                "05_quote_page": "Pull quote or key insight page",
                "06_executive_summary": "Executive summary with key points"
            }
        },
        "charts": {
            "dirs": [(USER_TEMPLATES_DIR / "charts", "user"), (SYSTEM_CHART_TEMPLATES_DIR, "system")],
            "pattern": "*.py",
            "metadata_key": "description",
            "default_metadata": "Chart template"
        }
    }
    
    config = configs[type]
    all_templates = []
    
    # Collect all templates
    for dir_path, source in config["dirs"]:
        if not dir_path.exists():
            continue
        for template_file in sorted(dir_path.glob(config["pattern"])):
            # Extract metadata
            metadata = config["default_metadata"]
            if type == "reports" and "use_cases" in config:
                metadata = config["use_cases"].get(template_file.stem, metadata)
            elif type in ["slides", "charts"]:
                # Try to extract from file content
                with open(template_file, "r") as f:
                    content = f.read()
                if type == "slides" and "<!-- Use case:" in content:
                    start = content.find("<!-- Use case:") + len("<!-- Use case:")
                    end = content.find("-->", start)
                    if end > start:
                        metadata = content[start:end].strip()
                elif type == "charts" and '"""' in content:
                    start = content.find('"""') + 3
                    end = content.find('"""', start)
                    if end > start:
                        metadata = content[start:end].strip().split('\n')[0]
            
            all_templates.append({
                "name": template_file.stem,
                "path": str(template_file),
                "file": template_file.name,
                config["metadata_key"]: metadata,
                "source": source,
                "type": type.rstrip('s')  # Remove plural
            })
    
    # Filter by names if specified
    if names is not None:
        name_list = [names] if isinstance(names, str) else names
        all_templates = [t for t in all_templates if t["name"] in name_list]
    
    # De-duplicate preferring user over system
    unique = {}
    for t in all_templates:
        if t["name"] not in unique or t["source"] == "user":
            unique[t["name"]] = t
    
    return list(unique.values())


# =============================================================================
# INIT TOOLS
# =============================================================================

def process_template(template_path: Path, replacements: Dict[str, str]) -> str:
    """Read template and replace all placeholders."""
    with open(template_path, "r") as f:
        content = f.read()
    
    for key, value in replacements.items():
        content = content.replace(f'[{key}]', value)
    
    return content

@mcp.tool()
def init_from_template(project: str, resource_type: str, name: str, 
                      template: str = None, **kwargs) -> str:
    """
    Universal template initialization function.
    
    Args:
        project: Project name
        resource_type: "slide", "report", or "chart"
        name: Resource name/number
        template: Template filename (optional)
        **kwargs: Additional placeholders (title, subtitle, section, etc.)
    
    Returns:
        Path to created file
    """
    project_dir = USER_PROJECTS_DIR / project
    if not project_dir.exists():
        return f"Error: Project '{project}' not found"
    
    theme = get_project_theme(project_dir)
    
    # Configuration for each resource type
    configs = {
        "slide": {
            "output_dir": project_dir / "slides",
            "template_dir": SYSTEM_SLIDE_TEMPLATES_DIR,
            "default_template": "01_base_slide.html",
            "file_pattern": "{}.html",
            "prefix": "slide_",
            "extension": ".html"
        },
        "report": {
            "output_dir": project_dir / "report_pages",
            "template_dir": SYSTEM_REPORT_TEMPLATES_DIR, 
            "default_template": "06_executive_summary.html",
            "file_pattern": "report_{}.html",
            "prefix": "page_",
            "extension": ".html"
        },
        "chart": {
            "output_dir": project_dir / "plots",
            "template_dir": SYSTEM_CHART_TEMPLATES_DIR,
            "default_template": None,  # Charts have no default
            "file_pattern": "{}.py",
            "prefix": "",
            "extension": ".py"
        },
        "outline": {
            "output_dir": project_dir,
            "template_dir": SYSTEM_OUTLINE_TEMPLATES_DIR,
            "default_template": "outline_slides.md",
            "file_pattern": "{}.md",
            "prefix": "",
            "extension": ".md"
        }
    }
    
    config = configs.get(resource_type)
    if not config:
        return f"Error: Unknown resource type '{resource_type}'"
    
    # Ensure output directory exists
    config["output_dir"].mkdir(exist_ok=True)
    
    # Normalize name
    if config["prefix"] and not name.startswith(config["prefix"]):
        name = f"{config['prefix']}{name.zfill(2)}"
    if name.endswith(config["extension"]):
        name = name[:-len(config["extension"])]
    
    # Find template file
    if template:
        template_file = config["template_dir"] / template
        if not template_file.exists():
            template_file = config["template_dir"] / Path(template).name
            if not template_file.exists():
                return f"Error: Template '{template}' not found"
    elif config["default_template"]:
        template_file = config["template_dir"] / config["default_template"]
        if not template_file.exists():
            return f"Error: Default template not found"
    else:
        # For charts without template, create boilerplate
        if resource_type == "chart":
            content = create_chart_boilerplate(name, project)
        else:
            return f"Error: No template specified for {resource_type}"
    
    # Process template if we have one
    if template or config["default_template"]:
        if resource_type == "chart":
            # Charts don't use placeholders - just copy as-is
            with open(template_file, "r") as f:
                content = f.read()
        elif resource_type == "outline":
            # Outlines use curly brace placeholders
            with open(template_file, "r") as f:
                content = f.read()
            # Replace curly brace placeholders
            for key, value in kwargs.items():
                content = content.replace(f"{{{key}}}", str(value))
            content = content.replace("{theme}", theme)
        else:
            # HTML templates use bracket placeholders
            replacements = {
                "THEME": theme,
                "PAGE_NUMBER": name.split('_')[1] if '_' in name else name,
                **kwargs  # Add any extra kwargs as replacements
            }
            
            # Add CSS paths for HTML templates
            base_css = SLIDE_BASE_CSS_NAME if resource_type == "slide" else REPORT_BASE_CSS_NAME
            replacements["BASE_CSS_PATH"] = f"{REL_PATH_TO_THEME_IN_PROJECT}/{base_css}"
            replacements["THEME_CSS_PATH"] = f"{REL_PATH_TO_THEME_IN_PROJECT}/{theme}{THEME_FILES['css']}"
            
            # Map common aliases
            for key in ["TITLE", "SUBTITLE", "SECTION"]:
                if key.lower() in kwargs:
                    replacements[key] = kwargs[key.lower()]
            
            # Report-specific aliases
            if resource_type == "report":
                replacements["REPORT_TITLE"] = replacements.get("TITLE", "")
                replacements["CONTENT_TITLE"] = replacements.get("TITLE", "")
                replacements["CONTENT_SUBTITLE"] = replacements.get("SUBTITLE", "")
                replacements["SECTION_NAME"] = replacements.get("SECTION", "")
            
            content = process_template(template_file, replacements)
    
    # Create output file
    filename = config["file_pattern"].format(name)
    output_path = config["output_dir"] / filename
    
    with open(output_path, "w") as f:
        f.write(content)
    
    # Make charts executable
    if resource_type == "chart":
        output_path.chmod(0o755)
    
    return str(output_path)

def create_chart_boilerplate(name: str, project: str) -> str:
    """Create default chart boilerplate when no template is provided."""
    return f'''#!/usr/bin/env python3
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
    project_dir = USER_PROJECTS_DIR / project
    if not project_dir.exists():
        return f"Error: Project '{project}' not found"
    
    # Find theme source
    theme_info = get_themes(theme)
    if not theme_info:
        return f"Error: Theme '{theme}' not found"
    theme_source = Path(theme_info[0]["path"])
    
    # Get current theme
    old_theme = get_project_theme(project_dir)
    
    # Clear old theme files from project/theme/ (keep base CSS)
    theme_dir = project_dir / "theme"
    if theme_dir.exists():
        for file in theme_dir.glob("*"):
            if file.name not in [SLIDE_BASE_CSS_NAME, REPORT_BASE_CSS_NAME]:
                file.unlink()
    
    # Copy new theme files
    copy_theme_files(theme_source, project_dir, theme)
    
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
    Slides come from slides/ folder, report pages from report_pages/ folder.
    
    Args:
        project: Name of the project
        output_path: Custom output path (optional)
        format: "slides" for horizontal 16:9, "report" for vertical 8.5x11 (default: "slides")
    
    Returns:
        Result dictionary with path or error
    """
    project_dir = USER_PROJECTS_DIR / project
    if not project_dir.exists():
        return {"success": False, "error": f"Project '{project}' not found"}
    
    # Determine source directory and files based on format
    if format == "report":
        # For reports, use report_pages directory
        source_dir = project_dir / "report_pages"
        # Fallback to slides directory for backward compatibility
        if not source_dir.exists() or not list(source_dir.glob("*.html")):
            source_dir = project_dir / "slides"
            html_files = list(source_dir.glob("report*.html")) if source_dir.exists() else []
        else:
            html_files = list(source_dir.glob("*.html"))
        
        if not html_files:
            return {"success": False, "error": f"No report pages found in project '{project}'"}
        default_output = str(project_dir / f"{project}-report.pdf")
    else:
        # For slides, use slides directory
        slides_dir = project_dir / "slides"
        if not slides_dir.exists():
            return {"success": False, "error": f"No slides directory found in project '{project}'"}
        
        source_dir = slides_dir
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
            ["node", str(pdf_script), str(source_dir), output, format],
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
    
    project_dir = USER_PROJECTS_DIR / project
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
        
        return {
            "success": True,
            "url": f"http://localhost:{port}",
            "message": f"Live viewer started for project '{project}'",
            "pid": process.pid
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}



# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()