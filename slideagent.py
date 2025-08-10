#!/usr/bin/env python3
"""
SlideAgent - Project Management for SlideAgent with MCP Server Support

A unified tool for managing SlideAgent presentation projects.
Handles project creation, configuration, and workflow coordination.
Provides MCP server mode for Claude Code integration.

Usage:
    python slideagent.py new-project <project-name> [--theme <theme>]
    python slideagent.py list-projects
    python slideagent.py list-themes
    python slideagent.py init-slide <project> <number> [--template <path>]
    python slideagent.py mcp serve  # Run as MCP server for Claude Code
"""

import os
import sys
import yaml
import argparse
import shutil
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

DEFAULT_BLANK_SLIDE_PATH = "src/slides/slide_templates/blank_slide.html"

class SlideAgentClient:
    """Main client for SlideAgent project management."""
    
    def __init__(self, base_dir=None):
        """Initialize SlideAgent client with base directory."""
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.projects_dir = self.base_dir / "projects"
        self.themes_dir = self.base_dir / "themes"
        self.src_dir = self.base_dir / "src"
        self.templates_dir = self.base_dir / "markdown_templates"
        
        # Ensure required directories exist
        self.projects_dir.mkdir(exist_ok=True)
        self.themes_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Load templates
        self._load_templates()
    
    def _load_templates(self):
        """Load template files from templates directory."""
        memory_template_path = self.templates_dir / "memory_template.md"
        outline_template_path = self.templates_dir / "outline_template.md"
        
        # Load memory template
        if memory_template_path.exists():
            with open(memory_template_path, 'r') as f:
                self.memory_template = f.read()
        else:
            # Fallback template if file doesn't exist
            self.memory_template = "# Project Memory: {project_name}\n\n## What's Working\n- Project created\n\n## What's Not Working\n- TBD\n\n## Ideas & Improvements\n- TBD\n"
        
        # Load outline template
        if outline_template_path.exists():
            with open(outline_template_path, 'r') as f:
                self.outline_template = f.read()
        else:
            # Fallback template if file doesn't exist
            self.outline_template = "# {title}\n\n## Outline\n\nTBD"
    
    def _find_theme(self, theme_name):
        """Find a theme by name in any subdirectory."""
        for root, dirs, files in os.walk(self.themes_dir):
            root_path = Path(root)
            if root_path.name == theme_name and (root_path / f"{theme_name}_theme.css").exists():
                return root_path, root_path.relative_to(self.themes_dir)
        return None, None
    
    def _get_theme_css_path(self, theme_name, from_slide=True):
        """Get the CSS path for a theme from slide location."""
        _, theme_relative = self._find_theme(theme_name)
        if not theme_relative:
            return None
        if from_slide:
            return f"../../../themes/{theme_relative}/{theme_name}_theme.css"
        else:
            return f"../../themes/{theme_relative}"
    
    def _update_slide_paths(self, content, old_theme, new_theme):
        """Update theme paths in slide content."""
        old_css = self._get_theme_css_path(old_theme)
        new_css = self._get_theme_css_path(new_theme)
        
        if old_css and new_css:
            content = content.replace(old_css, new_css)
        
        return content
    
    
    def create_project(self, project_name, theme="acme_corp"):
        """Create a new SlideAgent project with proper structure."""
        project_path = self.projects_dir / project_name
        
        if project_path.exists():
            print(f"❌ Project '{project_name}' already exists!")
            return False
        
        # Find theme
        theme_dir, theme_relative_path = self._find_theme(theme)
        
        if not theme_dir:
            print(f"❌ Theme '{theme}' not found!")
            self.list_themes()
            return False
        
        # Create project structure with new section-based layout
        project_path.mkdir(parents=True)
        (project_path / "input").mkdir()
        (project_path / "plots").mkdir()
        (project_path / "slides").mkdir()
        (project_path / "validation").mkdir()
        (project_path / "validation" / "screenshots").mkdir()
        
        # Determine theme path for config
        theme_config_path = self._get_theme_css_path(theme, from_slide=False)
        
        # Create config.yaml
        config = {
            'theme': theme,
            'theme_path': theme_config_path,
            'title': f'{project_name.replace("-", " ").title()}',
            'author': 'SlideAgent User'
        }
        
        config_path = project_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        # Create initial outline.md with section-based structure
        outline_content = self.outline_template.format(
            title=config['title'],
            author=config['author'],
            theme=theme
        )
        
        outline_path = project_path / "outline.md"
        with open(outline_path, 'w') as f:
            f.write(outline_content)
        
        # Create memory.md for the project
        memory_content = self.memory_template.format(
            project_name=project_name,
            theme=theme
        )
        
        memory_path = project_path / "memory.md"
        with open(memory_path, 'w') as f:
            f.write(memory_content)
        
        print(f"✅ Created project '{project_name}' with theme '{theme}'")
        print(f"📁 {project_path}")
        print(f"📝 New structure: slides/, validation/, memory.md")
        
        return True
    
    def list_projects(self):
        """List all existing projects."""
        projects = [d for d in self.projects_dir.iterdir() if d.is_dir()]
        
        if not projects:
            print("📂 No projects found")
            return
        
        print("📂 Projects:")
        for project in sorted(projects):
            config_path = project / "config.yaml"
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                    theme = config.get('theme', 'unknown')
                    title = config.get('title', project.name)
                    print(f"  • {project.name} ({theme}) - {title}")
                except Exception as e:
                    print(f"  • {project.name} (error)")
            else:
                print(f"  • {project.name} (no config)")
    
    def list_themes(self):
        """List all available themes."""
        themes = []
        
        # Recursively check all subdirectories in themes folder
        for root, dirs, files in os.walk(self.themes_dir):
            root_path = Path(root)
            dir_name = root_path.name
            theme_css = root_path / f"{dir_name}_theme.css"
            
            if theme_css.exists():
                relative_path = root_path.relative_to(self.themes_dir)
                themes.append((dir_name, root_path, str(relative_path)))
        
        if not themes:
            print("🎨 No themes found!")
            return
        
        print("🎨 Themes:")
        for theme_info in sorted(themes):
            theme_name, theme_dir, relative_path = theme_info
            print(f"  • {theme_name}")
    
    
    def show_project(self, project_name):
        """Show detailed information about a project."""
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            print(f"❌ Project '{project_name}' not found!")
            return
        
        config_path = project_path / "config.yaml"
        if not config_path.exists():
            print(f"❌ No config.yaml found")
            return
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Count files
        plots_count = len(list((project_path / "plots").glob('*'))) if (project_path / "plots").exists() else 0
        input_count = len(list((project_path / "input").glob('*'))) if (project_path / "input").exists() else 0
        
        print(f"📊 {project_name}")
        print(f"  Theme: {config.get('theme', 'N/A')}")
        print(f"  Files: {input_count} inputs, {plots_count} charts")
        slides_count = len(list((project_path / "slides").glob('slide_*.html'))) if (project_path / "slides").exists() else 0
        print(f"  Slides: {slides_count} HTML files")
        print(f"  PDF: {'✅' if (project_path / f'{project_name}.pdf').exists() else '❌'}")
    
    def swap_theme(self, project_name, new_theme):
        """Swap the theme for all slides in a project."""
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            print(f"❌ Project '{project_name}' not found!")
            return False
        
        # Find new theme
        theme_dir, theme_relative_path = self._find_theme(new_theme)
        
        if not theme_dir:
            print(f"❌ Theme '{new_theme}' not found!")
            self.list_themes()
            return False
        
        # Load current config to get old theme
        config_path = project_path / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                old_theme = config.get('theme', 'acme_corp')
        else:
            print(f"❌ No config.yaml found in project!")
            return False
        
        # Update all HTML files in slides directory
        slides_dir = project_path / "slides"
        if not slides_dir.exists():
            print(f"❌ No slides directory found!")
            return False
        
        slide_files = list(slides_dir.glob('slide_*.html'))
        if not slide_files:
            print(f"❌ No slide files found!")
            return False
        
        print(f"🔄 Swapping theme from '{old_theme}' to '{new_theme}'...")
        
        # Update each slide file
        for slide_file in slide_files:
            with open(slide_file, 'r') as f:
                content = f.read()
            
            # Update theme CSS path using helper method
            content = self._update_slide_paths(content, old_theme, new_theme)
            
            with open(slide_file, 'w') as f:
                f.write(content)
        
        # Update config.yaml
        config['theme'] = new_theme
        config['theme_path'] = f"../../themes/{theme_relative_path}"
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print(f"✅ Successfully updated {len(slide_files)} slides to use '{new_theme}' theme")
        print(f"📝 Updated config.yaml with new theme settings")
        return True
    
    def init_slide(self, project_name, slide_number, template_path=None, title="", subtitle="", section=""):
        """Initialize a slide from template with proper paths and content.
        
        Args:
            project_name: Name of the project
            slide_number: Slide number (e.g., "01" or "slide_01")
            template_path: Path to template file (e.g., "src/slides/slide_templates/00_title_slide.html")
            title: Main title for the slide
            subtitle: Subtitle for the slide
            section: Section label for the slide
        """
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            print(f"❌ Project '{project_name}' not found!")
            return False
        
        # Load project config to get theme
        config_path = project_path / "config.yaml"
        if not config_path.exists():
            print(f"❌ No config.yaml found in project!")
            return False
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            theme = config.get('theme', 'acme_corp')
        
        # Find theme for logo paths
        _, theme_relative_path = self._find_theme(theme)
        
        # Ensure slide number is formatted correctly
        if not slide_number.startswith('slide_'):
            slide_number = f"slide_{slide_number.zfill(2)}"
        
        slide_path = project_path / "slides" / f"{slide_number}.html"
        
        # Get the HTML content
        if template_path:
            # Convert to Path and handle relative/absolute paths
            template_file = Path(template_path)
            if not template_file.is_absolute():
                # Try relative to base directory
                template_file = self.base_dir / template_path
            
            if not template_file.exists():
                print(f"❌ Template not found at: {template_file}")
                return False
            
            with open(template_file, 'r') as f:
                html_content = f.read()
            
            # Fix CSS paths (from template location to project slide location)
            # Templates use ../base.css, we need ../../../src/slides/base.css
            html_content = html_content.replace('../base.css', '../../../src/slides/base.css')
            
            # Fix theme CSS path
            # Replace any existing theme CSS link with the correct one
            theme_css_pattern = r'<link rel="stylesheet" href="[^"]*_theme\.css">'
            theme_css_replacement = f'<link rel="stylesheet" href="../../../themes/{theme_relative_path}/{theme}_theme.css">'
            html_content = re.sub(theme_css_pattern, theme_css_replacement, html_content)
            
            # Also handle cases where theme path might be different
            # Generic pattern to catch various theme paths
            html_content = re.sub(
                r'href="[^"]*themes/[^/]+/[^/]+/[^"]+_theme\.css"',
                f'href="../../../themes/{theme_relative_path}/{theme}_theme.css"',
                html_content
            )
            
            # Fix logo paths - replace any existing logo paths with current theme logos
            html_content = re.sub(
                r'src="[^"]*_icon_logo\.(png|svg)"',
                f'src="../../../themes/{theme_relative_path}/{theme}_icon_logo.png"',
                html_content
            )
            html_content = re.sub(
                r'src="[^"]*_text_logo\.(png|svg)"',
                f'src="../../../themes/{theme_relative_path}/{theme}_text_logo.png"',
                html_content
            )
            
            # Simple, standardized replacements
            slide_num = slide_number.replace('slide_', '')
            
            # Core replacements - these work for ALL templates now
            html_content = html_content.replace('[TITLE]', title or '')
            html_content = html_content.replace('[SUBTITLE]', subtitle or '')
            html_content = html_content.replace('[SECTION]', section or '')
            html_content = html_content.replace('[PAGE_NUMBER]', slide_num)
            
            # Legacy support for XX placeholder
            html_content = html_content.replace('XX', slide_num)
            
        else:
            # Use default blank_slide template
            default_template = self.base_dir / DEFAULT_BLANK_SLIDE_PATH
            if default_template.exists():
                # Use blank_slide template as fallback
                return self.init_slide(project_name, slide_number, str(default_template), title, subtitle, section)
            else:
                print(f"❌ Default blank_slide template not found at {default_template}")
                return False
        
        # Save the slide
        slides_dir = project_path / "slides"
        slides_dir.mkdir(exist_ok=True)
        
        with open(slide_path, 'w') as f:
            f.write(html_content)
        
        template_name = Path(template_path).name if template_path else "boilerplate"
        print(f"✅ Initialized {slide_number}.html from {template_name}")
        print(f"📄 {slide_path}")
        
        return True
    
    def init_chart(self, project_name, chart_name, template_path=None):
        """Initialize a chart from a template.
        
        Args:
            project_name: Name of the project
            chart_name: Name for the chart file (without .py extension)
            template_path: Path to template file (e.g., src/charts/chart_templates/bar_chart.py)
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Get project path
        project_dir = self.projects_dir / project_name
        if not project_dir.exists():
            print(f"❌ Project '{project_name}' does not exist")
            return False
        
        # Ensure plots directory exists
        plots_dir = project_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # Clean chart name (remove .py extension if provided)
        if chart_name.endswith('.py'):
            chart_name = chart_name[:-3]
        
        chart_path = plots_dir / f"{chart_name}.py"
        
        # Read template or create minimal boilerplate
        if template_path:
            template_file = Path(template_path)
            if not template_file.exists():
                print(f"❌ Template file not found: {template_path}")
                return False
            
            with open(template_file, 'r') as f:
                python_content = f.read()
            
            # No path adjustment needed - both templates and project charts are 3 levels deep
            # Templates: src/charts/chart_templates/ -> 3 up to root
            # Projects: projects/[project]/plots/ -> 3 up to root
            
            # Update output filenames in the template
            # Replace the OUTPUT_NAME placeholder with actual chart name
            python_content = python_content.replace('OUTPUT_NAME', chart_name)
            
            # Also replace any specific template output names (for backward compatibility)
            python_content = python_content.replace('plots/bar_chart_', f'plots/{chart_name}_')
            python_content = python_content.replace('plots/line_chart_', f'plots/{chart_name}_')
            python_content = python_content.replace('plots/pie_chart_', f'plots/{chart_name}_')
            python_content = python_content.replace('plots/stacked_bar_', f'plots/{chart_name}_')
        else:
            # Create minimal boilerplate if no template specified
            python_content = f'''#!/usr/bin/env python3
"""
Chart: {chart_name}
Generated chart for {project_name} project
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
buddy.save("plots/{chart_name}_branded.png", branded=False)

# Create clean version for slides
fig, ax = buddy.setup_figure(figsize=(14, 7.875))
ax.bar(labels, data)
ax.set_xlabel('Categories')
ax.set_ylabel('Values')
ax.text(0.5, 1.02, 'Chart Subtitle', transform=ax.transAxes, 
        ha='center', fontsize=12, color='#666')
plt.tight_layout()
plt.savefig("plots/{chart_name}_clean.png", dpi=150, bbox_inches='tight')

print("✅ Chart generated successfully!")
print("   - Branded version: plots/{chart_name}_branded.png")
print("   - Clean version: plots/{chart_name}_clean.png")
'''
        
        # Write chart file
        with open(chart_path, 'w') as f:
            f.write(python_content)
        
        # Make executable
        chart_path.chmod(0o755)
        
        template_name = Path(template_path).name if template_path else "boilerplate"
        print(f"✅ Initialized {chart_name}.py from {template_name}")
        print(f"📊 {chart_path}")
        print(f"💡 To generate the chart: cd {project_dir} && python {chart_path.relative_to(project_dir)}")
        
        return True


class SlideAgentMCPServer:
    """MCP Server implementation for SlideAgent"""
    
    def __init__(self, base_dir=None):
        """Initialize MCP server with SlideAgent client"""
        self.client = SlideAgentClient(base_dir)
        self.base_dir = self.client.base_dir
        
    def parse_template_metadata(self, filepath: Path, is_chart: bool = False) -> Dict[str, Any]:
        """Extract TEMPLATE_META from HTML or Python files"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            metadata = {
                "path": str(filepath.relative_to(self.base_dir)),
                "name": filepath.stem
            }
            
            if is_chart:
                # Parse Python docstring format
                if "TEMPLATE_META:" in content:
                    meta_section = content.split("TEMPLATE_META:")[1].split("---")[0]
                    for line in meta_section.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            # Parse lists in brackets
                            if value.startswith('[') and value.endswith(']'):
                                value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
                            metadata[key] = value
            else:
                # Parse HTML comment format
                if "TEMPLATE_META" in content:
                    meta_section = content.split("TEMPLATE_META")[1].split("-->")[0]
                    for line in meta_section.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            # Parse lists
                            if value.startswith('[') and value.endswith(']'):
                                value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
                            metadata[key] = value
                            
            return metadata
        except Exception as e:
            return {
                "path": str(filepath.relative_to(self.base_dir)),
                "name": filepath.stem,
                "error": str(e)
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            # Route to appropriate handler
            if method == "tools/list":
                result = self.list_tools()
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_params = params.get("arguments", {})
                result = self.call_tool(tool_name, tool_params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def list_tools(self) -> Dict[str, Any]:
        """Return list of available tools"""
        return {
            "tools": [
                {
                    "name": "create_project",
                    "description": "Create a new SlideAgent project with proper structure",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Project name (use hyphens for spaces)"},
                            "theme": {"type": "string", "description": "Theme name", "default": "acme_corp"}
                        },
                        "required": ["name"]
                    }
                },
                {
                    "name": "list_projects",
                    "description": "List all existing SlideAgent projects",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_project_info",
                    "description": "Get detailed information about a specific project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name"}
                        },
                        "required": ["project"]
                    }
                },
                {
                    "name": "list_themes",
                    "description": "List all available themes",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "swap_theme",
                    "description": "Change theme for all slides in a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name"},
                            "theme": {"type": "string", "description": "New theme name"}
                        },
                        "required": ["project", "theme"]
                    }
                },
                {
                    "name": "init_slide",
                    "description": "Initialize a slide from a template",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name"},
                            "number": {"type": "string", "description": "Slide number (e.g., '01' or 'slide_01')"},
                            "template": {"type": "string", "description": "Template path from list_slide_templates"},
                            "title": {"type": "string", "description": "Main title for the slide", "default": ""},
                            "subtitle": {"type": "string", "description": "Subtitle for the slide", "default": ""},
                            "section": {"type": "string", "description": "Section label for the slide", "default": ""}
                        },
                        "required": ["project", "number"]
                    }
                },
                {
                    "name": "init_chart",
                    "description": "Initialize a chart from a template",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name"},
                            "name": {"type": "string", "description": "Chart name (without .py extension)"},
                            "template": {"type": "string", "description": "Template path from list_chart_templates"}
                        },
                        "required": ["project", "name"]
                    }
                },
                {
                    "name": "list_slide_templates",
                    "description": "List all available slide templates with metadata and paths",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "verbose": {"type": "boolean", "description": "Include full metadata", "default": False}
                        }
                    }
                },
                {
                    "name": "list_chart_templates",
                    "description": "List all available chart templates with metadata and paths",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "verbose": {"type": "boolean", "description": "Include full metadata", "default": False}
                        }
                    }
                },
                {
                    "name": "get_outline",
                    "description": "Read the outline.md file for a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name"}
                        },
                        "required": ["project"]
                    }
                },
                {
                    "name": "update_memory",
                    "description": "Update project or global memory file",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Project name (omit for global memory)"},
                            "content": {"type": "string", "description": "New memory content to append"},
                            "section": {"type": "string", "description": "Section to update", 
                                      "enum": ["working", "not_working", "ideas"]}
                        },
                        "required": ["content", "section"]
                    }
                }
            ]
        }
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a specific tool"""
        
        # Project management tools
        if tool_name == "create_project":
            success = self.client.create_project(params["name"], params.get("theme", "acme_corp"))
            return {
                "success": success,
                "message": f"Created project '{params['name']}'" if success else "Failed to create project",
                "path": str(self.client.projects_dir / params["name"]) if success else None
            }
            
        elif tool_name == "list_projects":
            projects = []
            for project_dir in self.client.projects_dir.iterdir():
                if project_dir.is_dir():
                    config_path = project_dir / "config.yaml"
                    if config_path.exists():
                        with open(config_path) as f:
                            config = yaml.safe_load(f)
                        projects.append({
                            "name": project_dir.name,
                            "theme": config.get("theme", "unknown"),
                            "title": config.get("title", project_dir.name),
                            "path": str(project_dir)
                        })
            return {"projects": projects}
            
        elif tool_name == "get_project_info":
            project_path = self.client.projects_dir / params["project"]
            if not project_path.exists():
                raise ValueError(f"Project '{params['project']}' not found")
            
            config_path = project_path / "config.yaml"
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            # Count files
            slides = list((project_path / "slides").glob("slide_*.html")) if (project_path / "slides").exists() else []
            charts = list((project_path / "plots").glob("*_clean.png")) if (project_path / "plots").exists() else []
            inputs = list((project_path / "input").glob("*")) if (project_path / "input").exists() else []
            
            return {
                "name": params["project"],
                "theme": config.get("theme"),
                "title": config.get("title"),
                "slides_count": len(slides),
                "charts_count": len(charts),
                "inputs_count": len(inputs),
                "has_pdf": (project_path / f"{params['project']}.pdf").exists(),
                "path": str(project_path)
            }
            
        # Theme tools
        elif tool_name == "list_themes":
            themes = []
            for root, dirs, files in os.walk(self.client.themes_dir):
                root_path = Path(root)
                dir_name = root_path.name
                theme_css = root_path / f"{dir_name}_theme.css"
                if theme_css.exists():
                    themes.append({
                        "name": dir_name,
                        "path": str(root_path.relative_to(self.client.themes_dir))
                    })
            return {"themes": sorted(themes, key=lambda x: x["name"])}
            
        elif tool_name == "swap_theme":
            success = self.client.swap_theme(params["project"], params["theme"])
            return {
                "success": success,
                "message": f"Swapped theme to '{params['theme']}'" if success else "Failed to swap theme"
            }
            
        # Slide tools
        elif tool_name == "init_slide":
            success = self.client.init_slide(
                params["project"],
                params["number"],
                params.get("template"),
                params.get("title", ""),
                params.get("subtitle", ""),
                params.get("section", "")
            )
            slide_num = params["number"] if params["number"].startswith("slide_") else f"slide_{params['number'].zfill(2)}"
            return {
                "success": success,
                "message": f"Initialized {slide_num}.html" if success else "Failed to initialize slide",
                "path": str(self.client.projects_dir / params["project"] / "slides" / f"{slide_num}.html") if success else None
            }
            
        # Chart tools
        elif tool_name == "init_chart":
            success = self.client.init_chart(
                params["project"],
                params["name"],
                params.get("template")
            )
            return {
                "success": success,
                "message": f"Initialized {params['name']}.py" if success else "Failed to initialize chart",
                "path": str(self.client.projects_dir / params["project"] / "plots" / f"{params['name']}.py") if success else None
            }
            
        # Template listing tools
        elif tool_name == "list_slide_templates":
            templates = []
            template_dir = self.client.src_dir / "slides" / "slide_templates"
            
            for template_file in sorted(template_dir.glob("*.html")):
                metadata = self.parse_template_metadata(template_file, is_chart=False)
                
                if params.get("verbose"):
                    templates.append(metadata)
                else:
                    templates.append({
                        "path": metadata["path"],
                        "name": metadata["name"],
                        "title": metadata.get("title", metadata["name"]),
                        "description": metadata.get("description", ""),
                        "best_for": metadata.get("best_for", "")
                    })
            
            return {"templates": templates}
            
        elif tool_name == "list_chart_templates":
            templates = []
            template_dir = self.client.src_dir / "charts" / "chart_templates"
            
            for template_file in sorted(template_dir.glob("*.py")):
                metadata = self.parse_template_metadata(template_file, is_chart=True)
                
                if params.get("verbose"):
                    templates.append(metadata)
                else:
                    templates.append({
                        "path": metadata["path"],
                        "name": metadata["name"],
                        "title": metadata.get("title", metadata["name"]),
                        "description": metadata.get("description", ""),
                        "best_for": metadata.get("best_for", "")
                    })
            
            return {"templates": templates}
            
        # Utility tools
        elif tool_name == "get_outline":
            project_path = self.client.projects_dir / params["project"]
            outline_path = project_path / "outline.md"
            
            if not outline_path.exists():
                raise ValueError(f"No outline.md found for project '{params['project']}'")
            
            with open(outline_path, 'r') as f:
                content = f.read()
            
            return {
                "project": params["project"],
                "content": content,
                "path": str(outline_path)
            }
            
        elif tool_name == "update_memory":
            if params.get("project"):
                memory_path = self.client.projects_dir / params["project"] / "memory.md"
            else:
                memory_path = self.client.base_dir / "MEMORY.md"
            
            if not memory_path.exists():
                # Create with template
                content = f"# Memory: {params.get('project', 'Global')}\n\n"
                content += "## What's Working\n\n## What's Not Working\n\n## Ideas & Improvements\n\n"
                with open(memory_path, 'w') as f:
                    f.write(content)
            
            # Read current content
            with open(memory_path, 'r') as f:
                content = f.read()
            
            # Add to appropriate section
            section_map = {
                "working": "## What's Working",
                "not_working": "## What's Not Working",
                "ideas": "## Ideas & Improvements"
            }
            
            section_header = section_map[params["section"]]
            new_item = f"- {params['content']}\n"
            
            # Find section and add item
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() == section_header:
                    # Find next section or end
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith('##'):
                        j += 1
                    # Insert before next section
                    lines.insert(j - 1, new_item)
                    break
            
            # Write back
            with open(memory_path, 'w') as f:
                f.write('\n'.join(lines))
            
            return {
                "success": True,
                "message": f"Updated {params.get('project', 'global')} memory",
                "path": str(memory_path)
            }
            
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def serve(self):
        """Run the MCP server in stdio mode"""
        while True:
            try:
                # Read line from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                # Parse JSON-RPC request
                request = json.loads(line)
                
                # Handle request
                response = self.handle_request(request)
                
                # Send response
                sys.stdout.write(json.dumps(response) + '\n')
                sys.stdout.flush()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                # Send error response
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + '\n')
                sys.stdout.flush()


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="SlideAgent - Project Management for SlideAgent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python slideagent.py new-project quarterly-review --theme acme_corp
  python slideagent.py list-projects
  python slideagent.py list-themes
  python slideagent.py init-slide quarterly-review 01 --template src/slides/slide_templates/00_title_slide.html
  python slideagent.py init-chart quarterly-review revenue_analysis --template src/charts/chart_templates/bar_chart.py
  python slideagent.py mcp serve  # Run as MCP server
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # New project command
    new_parser = subparsers.add_parser('new-project', help='Create a new project')
    new_parser.add_argument('name', help='Project name (use hyphens for spaces)')
    new_parser.add_argument('--theme', default='acme_corp', help='Theme to use (default: acme_corp)')
    
    # List projects command
    subparsers.add_parser('list-projects', help='List all projects')
    
    # List themes command
    subparsers.add_parser('list-themes', help='List available themes')
    
    # Project info command
    info_parser = subparsers.add_parser('info', help='Show project information')
    info_parser.add_argument('name', help='Project name')
    
    # Swap theme command
    swap_parser = subparsers.add_parser('swap-theme', help='Swap theme for all slides in a project')
    swap_parser.add_argument('project', help='Project name')
    swap_parser.add_argument('theme', help='New theme name')
    
    # Init slide command
    init_parser = subparsers.add_parser('init-slide', help='Initialize a slide from template')
    init_parser.add_argument('project', help='Project name')
    init_parser.add_argument('number', help='Slide number (e.g., 01 or slide_01)')
    init_parser.add_argument('--template', help='Path to template file (e.g., src/slides/slide_templates/00_title_slide.html)')
    init_parser.add_argument('--title', default='', help='Main title for the slide')
    init_parser.add_argument('--subtitle', default='', help='Subtitle for the slide')
    init_parser.add_argument('--section', default='', help='Section label for the slide')
    
    # Init chart command
    chart_parser = subparsers.add_parser('init-chart', help='Initialize a chart from template')
    chart_parser.add_argument('project', help='Project name')
    chart_parser.add_argument('name', help='Chart name (e.g., quarterly_revenue)')
    chart_parser.add_argument('--template', help='Path to template file (e.g., src/charts/chart_templates/bar_chart.py)')
    
    # MCP server command
    mcp_parser = subparsers.add_parser('mcp', help='MCP server operations')
    mcp_subparsers = mcp_parser.add_subparsers(dest='mcp_command', help='MCP commands')
    mcp_serve_parser = mcp_subparsers.add_parser('serve', help='Run as MCP server')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = SlideAgentClient()
    
    if args.command == 'new-project':
        client.create_project(args.name, args.theme)
    elif args.command == 'list-projects':
        client.list_projects()
    elif args.command == 'list-themes':
        client.list_themes()
    elif args.command == 'info':
        client.show_project(args.name)
    elif args.command == 'swap-theme':
        client.swap_theme(args.project, args.theme)
    elif args.command == 'init-slide':
        client.init_slide(args.project, args.number, args.template, args.title, args.subtitle, args.section)
    elif args.command == 'init-chart':
        client.init_chart(args.project, args.name, args.template)
    elif args.command == 'mcp' and args.mcp_command == 'serve':
        # Run as MCP server
        server = SlideAgentMCPServer()
        server.serve()

if __name__ == "__main__":
    main()