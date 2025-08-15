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
from typing import Dict, List, Optional, Any, Literal
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

# =============================================================================
# METADATA EXTRACTION MARKERS
# =============================================================================

# HTML template metadata markers
HTML_META_START = "<!-- TEMPLATE_META"
HTML_META_END = "-->"
HTML_USE_CASES_FIELD = "use_cases:"
HTML_DESCRIPTION_FIELD = "description:"
HTML_OLD_USE_CASE = "<!-- Use case:"

# Python docstring markers
PY_DOCSTRING_START = '"""'
PY_DOCSTRING_END = '"""'
PY_CHART_PREFIX = "Chart:"

# Markdown metadata markers
MD_DESCRIPTION_MARKER = "## Description"
MD_SUMMARY_MARKER = "## Summary"
MD_OVERVIEW_MARKER = "## Overview"

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

def _get_project_theme(project_dir: Path) -> str:
    """Get theme name from project's .theme file."""
    theme_file = project_dir / ".theme"
    if theme_file.exists():
        return theme_file.read_text().strip()
    return "acme_corp"  # default fallback

def _sanitize_project_name(name: str) -> str:
    """Convert project name to filesystem-safe format."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

def _create_project_structure(project_dir: Path) -> None:
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


def _copy_theme_files(theme_source: Path, project_dir: Path, theme_name: str) -> None:
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
    safe_name = _sanitize_project_name(name)
    project_dir = USER_PROJECTS_DIR / safe_name
    
    if project_dir.exists():
        return f"Error: Project '{safe_name}' already exists"
    
    # Create structure
    _create_project_structure(project_dir)
    
    # Find and copy theme
    theme_info = get_themes(theme)
    if theme_info:
        theme_source = Path(theme_info[0]["path"])
    else:
        # Default to acme_corp if theme not found
        theme_source = SYSTEM_THEMES_DIR / "acme_corp"
        theme = "acme_corp"
    
    _copy_theme_files(theme_source, project_dir, theme)
    
    # Create default outline (slides by default)
    init_from_template(
        project=safe_name,
        resource_type="outline",
        name="outline",
        template="outline_slides.md",
        placeholders={
            "title": safe_name.replace("_", " ").title(),
            "author": "SlideAgent",
            "theme": theme
        }
    )
    
    return f"Created project '{safe_name}' at {project_dir}"

@mcp.tool()
def get_projects(names=None):
    """
    Get project(s) information.
    
    Args:
        names: None for all projects, string for one, list for multiple
    
    Returns:
        List of project dictionaries
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
        
        projects.append({
            "name": name,
            "path": str(project_dir),
            "theme": _get_project_theme(project_dir),
            "has_pdf": (project_dir / f"{name}.pdf").exists()
        })
    
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
        type: Template type - "slides", "reports", "charts", or "outlines" (required)
        names: None for all templates, string for one, list for multiple
    
    Returns:
        List of template dictionaries
    """
    # Map plural types to singular resource types used by _get_resource_config
    type_map = {
        "slides": "slide",
        "reports": "report", 
        "charts": "chart",
        "outlines": "outline"
    }
    
    if type not in type_map:
        raise ValueError(f"Invalid type '{type}'. Must be one of: {', '.join(type_map.keys())}")
    
    resource_type = type_map[type]
    
    # Use a dummy project dir since we just need the template config
    dummy_project_dir = Path("/tmp")
    config = _get_resource_config(resource_type, dummy_project_dir)
    
    # Map file extensions to types for metadata extraction
    ext_to_type = {
        ".html": "html",
        ".py": "py",
        ".md": "md"
    }
    
    # Determine metadata key based on type
    metadata_key = "use_case" if type in ["slides", "reports"] else "description"
    
    all_templates = []
    
    # Collect templates from both user and system directories
    for dir_path in config["template_dirs"]:
        if not dir_path.exists():
            continue
        
        # Determine source (user or system)
        source = "user" if "user_resources" in str(dir_path) else "system"
        
        # Get file pattern from extension
        pattern = f"*{config['extension']}" if config.get("extension") else "*"
        
        for template_file in sorted(dir_path.glob(pattern)):
            # Extract metadata using helper
            file_ext = template_file.suffix
            file_type = ext_to_type.get(file_ext, "txt")
            metadata = _extract_template_metadata(template_file, file_type)
            
            # Use default if no metadata found
            if not metadata:
                metadata = f"{type.rstrip('s').title()} template"
            
            all_templates.append({
                "name": template_file.stem,
                "path": str(template_file),
                "file": template_file.name,
                metadata_key: metadata,
                "source": source,
                "type": type.rstrip('s')  # Remove plural
            })
    
    # Filter by names using helper
    return _filter_templates_by_names(all_templates, names)


# =============================================================================
# HELPER FUNCTIONS (prefixed with _ to indicate internal use)
# =============================================================================

def _get_project_dir(project: str) -> Path:
    """Get and validate project directory."""
    project_dir = USER_PROJECTS_DIR / project
    if not project_dir.exists():
        raise ValueError(f"Project '{project}' not found")
    return project_dir

def _normalize_resource_name(name: str, config: dict) -> str:
    """Normalize resource name based on config prefix/extension rules."""
    # Add prefix if needed
    if config.get("prefix") and not name.startswith(config["prefix"]):
        # Only add zfill for numeric names
        if name.isdigit():
            name = f"{config['prefix']}{name.zfill(2)}"
        else:
            name = f"{config['prefix']}{name}"
    
    # Remove extension if present
    if config.get("extension") and name.endswith(config["extension"]):
        name = name[:-len(config["extension"])]
    
    return name

def _get_output_path(name: str, config: dict) -> Path:
    """Get output path for a resource."""
    config["output_dir"].mkdir(exist_ok=True)
    filename = config["file_pattern"].format(name)
    return config["output_dir"] / filename

def _process_template(template_path: Path, replacements: Dict[str, str]) -> str:
    """Read template and replace all placeholders."""
    with open(template_path, "r") as f:
        content = f.read()
    
    for key, value in replacements.items():
        # Ensure value is a string
        str_value = str(value) if value is not None else ""
        content = content.replace(f'[{key}]', str_value)
    
    return content

def _get_resource_config(resource_type: str, project_dir: Path) -> dict:
    """Get configuration for a resource type including paths."""
    configs = {
        "slide": {
            "output_dir": project_dir / "slides",
            "template_dir": SYSTEM_SLIDE_TEMPLATES_DIR,
            "template_dirs": [(USER_TEMPLATES_DIR / "slides"), SYSTEM_SLIDE_TEMPLATES_DIR],
            "file_pattern": "{}.html",
            "prefix": "slide_",
            "extension": ".html"
        },
        "report": {
            "output_dir": project_dir / "report_pages",
            "template_dir": SYSTEM_REPORT_TEMPLATES_DIR,
            "template_dirs": [(USER_TEMPLATES_DIR / "reports"), SYSTEM_REPORT_TEMPLATES_DIR],
            "file_pattern": "report_{}.html",
            "prefix": "page_",
            "extension": ".html"
        },
        "chart": {
            "output_dir": project_dir / "plots",
            "template_dir": SYSTEM_CHART_TEMPLATES_DIR,
            "template_dirs": [(USER_TEMPLATES_DIR / "charts"), SYSTEM_CHART_TEMPLATES_DIR],
            "file_pattern": "{}.py",
            "prefix": "",
            "extension": ".py"
        },
        "outline": {
            "output_dir": project_dir,
            "template_dir": SYSTEM_OUTLINE_TEMPLATES_DIR,
            "template_dirs": [(USER_TEMPLATES_DIR / "outlines"), SYSTEM_OUTLINE_TEMPLATES_DIR],
            "file_pattern": "{}.md",
            "prefix": "",
            "extension": ".md"
        }
    }
    return configs.get(resource_type)

def _find_template(template_name: str, template_dirs: list) -> Path:
    """Find a template file in a list of directories."""
    for dir_path in template_dirs:
        if dir_path.exists():
            template_path = dir_path / template_name
            if template_path.exists():
                return template_path
    return None

def _extract_between_markers(content: str, start_marker: str, end_marker: str) -> str:
    """Extract text between two markers."""
    start = content.find(start_marker)
    if start == -1:
        return None
    start += len(start_marker)
    end = content.find(end_marker, start)
    if end == -1:
        return None
    return content[start:end].strip()

def _extract_field_value(text: str, field_name: str) -> str:
    """Extract value after a field name up to the next newline."""
    if field_name not in text:
        return None
    start = text.find(field_name) + len(field_name)
    end = text.find("\n", start)
    if end == -1:
        end = len(text)
    return text[start:end].strip()

def _parse_json_array_first_item(text: str) -> str:
    """Parse a JSON-like array and return the first item."""
    if not text.startswith('['):
        return text.strip(' "\'')
    # Strip brackets and split by comma
    text = text.strip('[]')
    items = text.split(',')
    if items:
        return items[0].strip(' "\'')
    return None

def _extract_template_metadata(template_path: Path, file_type: str) -> str:
    """Extract metadata/description from a template file based on its type."""
    with open(template_path, "r") as f:
        content = f.read()
    
    if file_type == "html":
        # Try TEMPLATE_META block first
        meta_block = _extract_between_markers(content, HTML_META_START, HTML_META_END)
        if meta_block:
            # Try description field first
            desc = _extract_field_value(meta_block, HTML_DESCRIPTION_FIELD)
            if desc:
                return desc
            
            # Then try use_cases field
            use_case = _extract_field_value(meta_block, HTML_USE_CASES_FIELD)
            if use_case:
                return _parse_json_array_first_item(use_case)
        
        # Fallback to old format
        old_use_case = _extract_between_markers(content, HTML_OLD_USE_CASE, HTML_META_END)
        if old_use_case:
            return old_use_case
    
    elif file_type == "py":
        # Extract Python docstring
        docstring = _extract_between_markers(content, PY_DOCSTRING_START, PY_DOCSTRING_END)
        if not docstring:
            return None
        
        lines = docstring.split('\n')
        
        # Check for TEMPLATE_META format
        if lines and lines[0].strip().startswith("TEMPLATE_META:"):
            for line in lines[1:]:
                if line.strip().startswith('---'):
                    break
                desc = _extract_field_value(line, HTML_DESCRIPTION_FIELD)
                if desc:
                    return desc
        
        # Fallback: first meaningful line
        for line in lines:
            cleaned = line.strip()
            if (cleaned and 
                not cleaned.startswith('TEMPLATE_META') and 
                not cleaned.startswith('---') and 
                not cleaned.startswith(PY_CHART_PREFIX)):
                return cleaned
    
    elif file_type == "md":
        lines = content.split('\n')
        
        # Look for Description, Summary, or Overview sections
        for marker in [MD_DESCRIPTION_MARKER, MD_SUMMARY_MARKER, MD_OVERVIEW_MARKER]:
            for i, line in enumerate(lines):
                if line.strip() == marker:
                    # Get next non-heading line
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('#'):
                            return next_line.replace('[', '').replace(']', '').strip()
                    break
        
        # Fallback: first content line after title
        for line in lines:
            if line.startswith('# '):
                continue
            cleaned = line.strip()
            if cleaned and not cleaned.startswith('#') and not cleaned.startswith('**') and ':' not in cleaned:
                return cleaned.replace('[', '').replace(']', '').strip()
    
    return None

def _filter_templates_by_names(templates: list, names) -> list:
    """Filter templates by names if specified."""
    if names is None:
        return templates
    
    name_list = [names] if isinstance(names, str) else names
    return [t for t in templates if t["name"] in name_list]

# =============================================================================
# INIT TOOLS  
# =============================================================================
@mcp.tool()
def init_from_template(project: str, 
                      resource_type: Literal["slide", "report", "chart", "outline"], 
                      name: str, 
                      template: str = None, 
                      placeholders: dict = None) -> str:
    """
    Universal template initialization function.
    
    Args:
        project: Project name
        resource_type: Must be one of: "slide", "report", "chart", or "outline"
        name: Resource name/number (e.g., "1" for slide_1, "revenue" for chart)
        template: Template filename (required for all types except charts without template)
        placeholders: Dictionary mapping placeholder names to replacement values
    
    How it works:
        - All templates use bracket placeholders like [TITLE] or [content]
        - This function replaces each [PLACEHOLDER] with the value from the dict
        - Placeholder names are case-sensitive - provide exact names
        - All values will be converted to strings
    
    Examples:
        For slides (ONLY these standard placeholders work):
            placeholders={
                "TITLE": "Q4 Financial Results",
                "SUBTITLE": "Record Breaking Quarter",
                "SECTION": "Executive Summary",
                "PAGE_NUMBER": "1"
            }
        
        For an outline with [title] and [author]:
            placeholders={
                "title": "2025 Strategy Presentation",
                "author": "John Smith"
            }
    
    Note: This tool ONLY replaces the following standard placeholders:
    - For slides/reports: TITLE, SUBTITLE, SECTION, PAGE_NUMBER
    - For outlines: Any placeholders you provide (e.g., title, author, theme, date)
    - For charts: No placeholders - charts are Python scripts that should be edited directly
    - CSS paths are handled automatically for HTML templates
    
    Any template-specific content should be modified with Edit/MultiEdit tools after generation.
    
    Returns:
        Path to created file
    """
    # Default to empty dict if no placeholders provided
    if placeholders is None:
        placeholders = {}
    
    # Get and validate project directory
    try:
        project_dir = _get_project_dir(project)
    except ValueError as e:
        return str(e)
    
    # Get configuration for the resource type
    config = _get_resource_config(resource_type, project_dir)
    
    # Normalize the resource name
    name = _normalize_resource_name(name, config)
    
    # Template is required for all resource types
    if not template:
        return f"Error: Template parameter is required for {resource_type}. Please specify a template filename."
    
    # Find template file using the helper
    template_path = _find_template(template, config["template_dirs"])
    if not template_path:
        return f"Error: Template '{template}' not found in {resource_type} template directories"
    
    # Read template content (always needed)
    with open(template_path, "r") as f:
        content = f.read()
    
    # Process content based on resource type
    if resource_type in ["slide", "report"]:
        # Handle HTML templates (slides and reports)
        theme_dir = project_dir / "theme"
        
        # Determine base CSS based on type
        base_css = f"../theme/{'slide' if resource_type == 'slide' else 'report'}_base.css"
        
        # Find theme CSS (same for both)
        theme_css_files = list(theme_dir.glob("*_theme.css"))
        theme_css = f"../theme/{theme_css_files[0].name}" if theme_css_files else "../theme/acme_corp_theme.css"
        
        # Replace CSS placeholders
        content = content.replace("[BASE_CSS_PATH]", base_css)
        content = content.replace("[THEME_CSS_PATH]", theme_css)
        
        # Replace standard placeholders (same for both slides and reports)
        standard_placeholders = ["TITLE", "SUBTITLE", "SECTION", "PAGE_NUMBER"]
        for key in standard_placeholders:
            if key in placeholders:
                content = content.replace(f"[{key}]", str(placeholders[key]))
    
    elif resource_type == "outline":
        # Outlines: flexible placeholders for metadata
        for key, value in placeholders.items():
            content = content.replace(f"[{key}]", str(value) if value is not None else "")
    
    # Charts don't need any processing - just use content as-is
    
    # Get output path
    output_path = _get_output_path(name, config)
    
    with open(output_path, "w") as f:
        f.write(content)
    
    # Make charts executable
    if resource_type == "chart":
        output_path.chmod(0o755)
    
    return str(output_path)



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
    old_theme = _get_project_theme(project_dir)
    
    # Clear old theme files from project/theme/ (keep base CSS)
    theme_dir = project_dir / "theme"
    if theme_dir.exists():
        for file in theme_dir.glob("*"):
            if file.name not in [SLIDE_BASE_CSS_NAME, REPORT_BASE_CSS_NAME]:
                file.unlink()
    
    # Copy new theme files
    _copy_theme_files(theme_source, project_dir, theme)
    
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
    except FileNotFoundError:
        # lsof might not be available on all systems, continue anyway
        pass
    except Exception as e:
        # Log the error but continue - port cleanup is not critical
        print(f"Warning: Could not clean up port {port}: {e}")
    
    # Also kill any existing live_viewer_server processes
    subprocess.run(["pkill", "-f", "node.*live_viewer_server"], capture_output=True)
    
    # Start viewer from same slideagent_mcp directory
    viewer_script = Path(__file__).parent / "utils" / "live_viewer" / "live_viewer_server.js"
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