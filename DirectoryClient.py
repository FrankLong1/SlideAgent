#!/usr/bin/env python3
"""
SlideAgent DirectoryClient - Project Management for SlideAgent

A simple CLI tool for managing SlideAgent presentation projects.
Handles project creation, configuration, and workflow coordination.

Usage:
    python DirectoryClient.py new-project <project-name> [--theme <theme>]
    python DirectoryClient.py list-projects
    python DirectoryClient.py list-themes
"""

import os
import sys
import yaml
import argparse
import shutil
from pathlib import Path

class SlideAgentClient:
    """Main client for SlideAgent project management."""
    
    def __init__(self, base_dir=None):
        """Initialize SlideAgent client with base directory."""
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.projects_dir = self.base_dir / "projects"
        self.themes_dir = self.base_dir / "themes"
        self.src_dir = self.base_dir / "src"
        
        # Ensure required directories exist
        self.projects_dir.mkdir(exist_ok=True)
        self.themes_dir.mkdir(exist_ok=True)
    
    def _find_theme(self, theme_name):
        """Find a theme by name in any subdirectory."""
        for root, dirs, files in os.walk(self.themes_dir):
            root_path = Path(root)
            if root_path.name == theme_name and (root_path / f"{theme_name}_theme.css").exists():
                return root_path, root_path.relative_to(self.themes_dir)
        return None, None
    
    
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
        theme_config_path = f"../../themes/{theme_relative_path}"
        
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
        outline_content = f"""# {config['title']}

## Section-Based Outline

# Section 1: Introduction (slides 1-2)
## Slide 1: Title Slide
- Template: 00_title_slide
- Content: {config['title']}, {config['author']}, Date

## Slide 2: Overview
- Template: 01_base_slide
- Content: Agenda and key objectives
- Charts needed: None

# Section 2: Main Content (slides 3-4)
## Slide 3: Key Analysis
- Template: 02_text_left_image_right
- Content: Main findings and insights
- Charts needed: [specify chart names]

## Slide 4: Supporting Data
- Template: 04_full_image_slide
- Content: Full-screen chart or diagram
- Charts needed: [specify chart names]

# Section 3: Conclusion (slide 5)
## Slide 5: Summary
- Template: 01_base_slide
- Content: Key takeaways and next steps
- Charts needed: None

## Implementation Notes
- Place source materials in `input/`
- Charts will be generated in `plots/`
- Theme: {theme}
- Each section will be rendered by separate agents in parallel
- Individual slide HTML files will be created in `slides/` directory
"""
        
        outline_path = project_path / "outline.md"
        with open(outline_path, 'w') as f:
            f.write(outline_content)
        
        # Create memory.md for the project
        memory_content = f"""# Project Memory: {project_name}

## What's Working
- Project structure created with theme '{theme}'
- Initial outline template established
- Section-based parallel generation ready

## What's Not Working
- No issues identified yet

## Ideas & Improvements
- Add specific content to input/ folder
- Customize outline for presentation goals
- Consider which charts will best support the narrative

---
*Last Updated: Project Creation*
"""
        
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
            
            # Replace the theme CSS path
            old_css_path = f"themes/examples/{old_theme}/{old_theme}_theme.css"
            new_css_path = f"themes/{theme_relative_path}/{new_theme}_theme.css"
            
            # Try different possible path formats
            replacements = [
                (f"../../../{old_css_path}", f"../../../themes/{theme_relative_path}/{new_theme}_theme.css"),
                (f"../../{old_css_path}", f"../../themes/{theme_relative_path}/{new_theme}_theme.css"),
                (old_css_path, f"themes/{theme_relative_path}/{new_theme}_theme.css"),
            ]
            
            for old_path, new_path in replacements:
                if old_path in content:
                    content = content.replace(old_path, new_path)
                    break
            
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

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="SlideAgent DirectoryClient - Project Management for SlideAgent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python DirectoryClient.py new-project quarterly-review --theme acme_corp
  python DirectoryClient.py list-projects
  python DirectoryClient.py list-themes
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

if __name__ == "__main__":
    main()