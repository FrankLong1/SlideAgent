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

# Constants
BASE_DIR = Path(__file__).parent.parent  # Go up one level from slideagent_mcp/
PROJECTS_DIR = BASE_DIR / "projects"
THEMES_DIR = BASE_DIR / "themes"
SLIDE_TEMPLATES_DIR = BASE_DIR / "src/slides/slide_templates"
CHART_TEMPLATES_DIR = BASE_DIR / "src/charts/chart_templates"
MARKDOWN_TEMPLATES_DIR = BASE_DIR / "markdown_templates"
MEMORY_FILE = BASE_DIR / "MEMORY.md"

# Track live viewer processes
LIVE_VIEWER_PROCESSES = {}

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
    project_dir = PROJECTS_DIR / safe_name
    
    if project_dir.exists():
        return f"Error: Project '{safe_name}' already exists"
    
    # Create directory structure
    dirs = [
        project_dir,
        project_dir / "slides",
        project_dir / "validation",
        project_dir / "plots", 
        project_dir / "input"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create config.yaml
    config = {
        "project_name": safe_name,
        "theme": theme,
        "description": description,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "slides_count": 0,
        "charts_count": 0
    }
    
    with open(project_dir / "config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    # Initialize outline from template
    outline_template_path = MARKDOWN_TEMPLATES_DIR / "outline_template.md"
    if outline_template_path.exists():
        with open(outline_template_path, "r") as f:
            outline_content = f.read()
        
        # Replace placeholders
        outline_content = outline_content.replace("{title}", safe_name.replace("_", " ").title())
        outline_content = outline_content.replace("{author}", "SlideAgent")
        outline_content = outline_content.replace("{theme}", theme)
        
        with open(project_dir / "outline.md", "w") as f:
            f.write(outline_content)
    
    # Create memory.md
    memory_content = f"""# Project Memory: {safe_name}

## Working
- Project initialized successfully

## Not Working
- None yet

## Ideas
- None yet
"""
    
    with open(project_dir / "memory.md", "w") as f:
        f.write(memory_content)
    
    return f"Created project '{safe_name}' at {project_dir}"

@mcp.tool()
def list_projects() -> List[Dict[str, Any]]:
    """
    List all existing SlideAgent projects.
    
    Returns:
        List of project information dictionaries
    """
    projects = []
    
    if not PROJECTS_DIR.exists():
        return projects
    
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        
        config_file = project_dir / "config.yaml"
        if not config_file.exists():
            continue
        
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        
        # Count slides
        slides_dir = project_dir / "slides"
        slide_count = len(list(slides_dir.glob("*.html"))) if slides_dir.exists() else 0
        
        # Count charts
        plots_dir = project_dir / "plots"
        chart_count = len(list(plots_dir.glob("*_clean.png"))) if plots_dir.exists() else 0
        
        projects.append({
            "name": project_dir.name,
            "path": str(project_dir),
            "theme": config.get("theme", "unknown"),
            "created_date": config.get("created_date", "unknown"),
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
    project_dir = PROJECTS_DIR / project
    if not project_dir.exists():
        raise ValueError(f"Project '{project}' not found")
    
    config_file = project_dir / "config.yaml"
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    # Count files
    slides = list((project_dir / "slides").glob("slide_*.html")) if (project_dir / "slides").exists() else []
    charts = list((project_dir / "plots").glob("*_clean.png")) if (project_dir / "plots").exists() else []
    inputs = list((project_dir / "input").glob("*")) if (project_dir / "input").exists() else []
    
    return {
        "name": project,
        "theme": config.get("theme"),
        "title": config.get("title", project),
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
    themes = []
    
    # Check example themes
    examples_dir = THEMES_DIR / "examples"
    if examples_dir.exists():
        for theme_dir in examples_dir.iterdir():
            if theme_dir.is_dir():
                theme_css = theme_dir / f"{theme_dir.name}_theme.css"
                if theme_css.exists():
                    themes.append({
                        "name": theme_dir.name,
                        "path": f"themes/examples/{theme_dir.name}",
                        "type": "example"
                    })
    
    # Check private themes
    private_dir = THEMES_DIR / "private"
    if private_dir.exists():
        for theme_dir in private_dir.iterdir():
            if theme_dir.is_dir():
                theme_css = theme_dir / f"{theme_dir.name}_theme.css"
                if theme_css.exists():
                    themes.append({
                        "name": theme_dir.name,
                        "path": f"themes/private/{theme_dir.name}",
                        "type": "private"
                    })
    
    return themes

@mcp.tool()
def list_slide_templates() -> List[Dict[str, Any]]:
    """
    List all available slide templates with metadata.
    
    Returns:
        List of template information with paths and use cases
    """
    templates = []
    
    if not SLIDE_TEMPLATES_DIR.exists():
        return templates
    
    for template_file in sorted(SLIDE_TEMPLATES_DIR.glob("*.html")):
        # Read template to extract metadata
        with open(template_file, "r") as f:
            content = f.read()
        
        # Extract title from HTML comment if present
        use_case = "General purpose slide"
        if "<!-- Use case:" in content:
            start = content.find("<!-- Use case:") + len("<!-- Use case:")
            end = content.find("-->", start)
            if end > start:
                use_case = content[start:end].strip()
        
        templates.append({
            "name": template_file.stem,
            "path": f"src/slides/slide_templates/{template_file.name}",
            "file": template_file.name,
            "use_case": use_case
        })
    
    return templates

@mcp.tool()
def list_chart_templates() -> List[Dict[str, Any]]:
    """
    List all available chart templates with metadata.
    
    Returns:
        List of template information with paths and descriptions
    """
    templates = []
    
    if not CHART_TEMPLATES_DIR.exists():
        return templates
    
    for template_file in sorted(CHART_TEMPLATES_DIR.glob("*.py")):
        # Read template to extract metadata
        with open(template_file, "r") as f:
            content = f.read()
        
        # Extract description from docstring
        description = "Chart template"
        if '"""' in content:
            start = content.find('"""') + 3
            end = content.find('"""', start)
            if end > start:
                description = content[start:end].strip().split('\n')[0]
        
        templates.append({
            "name": template_file.stem,
            "path": f"src/charts/chart_templates/{template_file.name}",
            "file": template_file.name,
            "description": description
        })
    
    return templates

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
    project_dir = PROJECTS_DIR / project
    if not project_dir.exists():
        return f"Error: Project '{project}' not found"
    
    # Handle template path
    if template:
        template_file = BASE_DIR / template
        if not template_file.exists():
            return f"Error: Template not found at {template}"
    else:
        # Use default blank_slide template
        template_file = BASE_DIR / "src/slides/slide_templates/blank_slide.html"
        if not template_file.exists():
            return f"Error: Default template not found"
    
    # Read template
    with open(template_file, "r") as f:
        content = f.read()
    
    # Read project config for theme
    config_file = project_dir / "config.yaml"
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    theme = config.get("theme", "acme_corp")
    
    # Update CSS paths (from slides/ to root)
    content = content.replace("../core_css/base.css", "../../../src/slides/base.css")
    content = content.replace("../core_css/print.css", "../../../src/slides/print.css")
    content = content.replace("../base.css", "../../../src/slides/base.css")
    
    # Set theme path
    if "private" in theme or (THEMES_DIR / "private" / theme).exists():
        theme_path = f"../../../themes/private/{theme}/{theme}_theme.css"
    else:
        theme_path = f"../../../themes/examples/{theme}/{theme}_theme.css"
    
    # Replace theme references
    import re
    content = re.sub(
        r'<link rel="stylesheet" href="[^"]*_theme\.css">',
        f'<link rel="stylesheet" href="{theme_path}">',
        content
    )
    
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
    project_dir = PROJECTS_DIR / project
    if not project_dir.exists():
        return f"Error: Project '{project}' not found"
    
    # Clean chart name
    if name.endswith('.py'):
        name = name[:-3]
    
    # Handle template
    if template:
        template_file = BASE_DIR / template
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

from src.charts.utils.plot_buddy import PlotBuddy
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
    project_dir = PROJECTS_DIR / project
    if not project_dir.exists():
        return f"Error: Project '{project}' not found"
    
    # Check if theme exists
    theme_found = False
    theme_path = None
    
    for location in ["examples", "private"]:
        test_path = THEMES_DIR / location / theme
        if test_path.exists() and (test_path / f"{theme}_theme.css").exists():
            theme_found = True
            theme_path = f"themes/{location}/{theme}"
            break
    
    if not theme_found:
        return f"Error: Theme '{theme}' not found"
    
    # Update config
    config_file = project_dir / "config.yaml"
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    old_theme = config.get("theme", "acme_corp")
    config["theme"] = theme
    
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    # Update existing slides
    slides_dir = project_dir / "slides"
    if slides_dir.exists():
        import re
        for slide_file in slides_dir.glob("*.html"):
            with open(slide_file, "r") as f:
                content = f.read()
            
            # Replace theme references
            content = re.sub(
                rf'themes/(examples|private)/{old_theme}/',
                f'{theme_path}/',
                content
            )
            
            with open(slide_file, "w") as f:
                f.write(content)
    
    return f"Updated project '{project}' to use theme '{theme}'"

@mcp.tool()
def update_memory(content: str, section: str = "ideas", project: str = None) -> str:
    """
    Update memory (learnings/issues/ideas) for global or project scope.
    
    Args:
        content: The content to add to memory
        section: Section to update (working/not_working/ideas)
        project: Project name (omit for global MEMORY.md)
    
    Returns:
        Success message
    """
    # Determine memory file
    if project:
        project_dir = PROJECTS_DIR / project
        if not project_dir.exists():
            return f"Error: Project '{project}' not found"
        memory_file = project_dir / "memory.md"
    else:
        memory_file = MEMORY_FILE
    
    # Read existing memory or create new
    if memory_file.exists():
        with open(memory_file, "r") as f:
            memory_content = f.read()
    else:
        title = f"Project Memory: {project}" if project else "Global Memory"
        memory_content = f"# {title}\n\n## Working\n\n## Not Working\n\n## Ideas\n"
    
    # Find section and append
    section_map = {
        "working": "## Working",
        "not_working": "## Not Working", 
        "ideas": "## Ideas"
    }
    
    section_header = section_map.get(section, "## Ideas")
    
    if section_header in memory_content:
        # Find the section
        lines = memory_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == section_header:
                # Find next section or end
                j = i + 1
                while j < len(lines) and not lines[j].startswith('##'):
                    j += 1
                # Insert before next section
                lines.insert(j, f"- {content}")
                break
        memory_content = '\n'.join(lines)
    else:
        # Add new section
        memory_content += f"\n{section_header}\n- {content}\n"
    
    # Write back
    with open(memory_file, "w") as f:
        f.write(memory_content)
    
    scope_desc = f"project '{project}'" if project else "global"
    return f"Updated {scope_desc} memory in section '{section}'"

# =============================================================================
# GENERATION TOOLS
# =============================================================================

@mcp.tool()
def generate_pdf(project: str, output_path: str = None) -> Dict[str, Any]:
    """
    Generate PDF from all slides in a project.
    
    Args:
        project: Name of the project
        output_path: Custom output path (optional)
    
    Returns:
        Result dictionary with path or error
    """
    project_dir = PROJECTS_DIR / project
    if not project_dir.exists():
        return {"success": False, "error": f"Project '{project}' not found"}
    
    slides_dir = project_dir / "slides"
    if not slides_dir.exists() or not list(slides_dir.glob("*.html")):
        return {"success": False, "error": f"No slides found in project '{project}'"}
    
    # Run pdf_generator.js from same slideagent_mcp directory
    pdf_script = Path(__file__).parent / "pdf_generator.js"
    if not pdf_script.exists():
        return {"success": False, "error": "PDF generator script not found"}
    
    output = output_path or str(project_dir / f"{project}.pdf")
    
    try:
        result = subprocess.run(
            ["node", str(pdf_script), str(slides_dir), output],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR)
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "path": output,
                "message": "PDF generated successfully"
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
    
    project_dir = PROJECTS_DIR / project
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
    viewer_script = Path(__file__).parent / "live_viewer_server.js"
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

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()