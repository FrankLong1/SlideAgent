#!/usr/bin/env python3
"""
SlideAgent DirectoryClient - Project Management for SlideAgent

A simple CLI tool for managing SlideAgent presentation projects.
Handles project creation, configuration, and workflow coordination.

Usage:
    python DirectoryClient.py new-project <project-name> [--theme <theme>]
    python DirectoryClient.py list-projects
    python DirectoryClient.py list-themes
    python DirectoryClient.py generate-pdf <project-name>
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
        
        # Create project structure
        project_path.mkdir(parents=True)
        (project_path / "input").mkdir()
        (project_path / "plots").mkdir()
        
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
        
        # Create initial outline.md
        outline_content = f"""# {config['title']}

## Slide Outline

1. **Title Slide**
2. **Overview**
3. **Main Content**
4. **Conclusion**

## Notes
- Place source materials in `input/`
- Charts in `plots/`
- Theme: {theme}
"""
        
        outline_path = project_path / "outline.md"
        with open(outline_path, 'w') as f:
            f.write(outline_content)
        
        print(f"✅ Created project '{project_name}' with theme '{theme}'")
        print(f"📁 {project_path}")
        
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
    
    def generate_pdf(self, project_name):
        """Generate PDF for a project."""
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            print(f"❌ Project '{project_name}' not found!")
            return False
        
        html_file = project_path / "presentation.html"
        if not html_file.exists():
            print(f"❌ No presentation.html found")
            return False
        
        # Run PDF generation
        pdf_script = self.src_dir / "slides" / "pdf_generator.js"
        output_pdf = project_path / f"{project_name}.pdf"
        
        import subprocess
        try:
            cmd = ["node", str(pdf_script), str(html_file), str(output_pdf)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ PDF generated: {output_pdf}")
                return True
            else:
                print(f"❌ PDF generation failed: {result.stderr}")
                return False
        except FileNotFoundError:
            print("❌ Node.js not found")
            return False
    
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
        print(f"  HTML: {'✅' if (project_path / 'presentation.html').exists() else '❌'}")
        print(f"  PDF: {'✅' if (project_path / f'{project_name}.pdf').exists() else '❌'}")

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
  python DirectoryClient.py generate-pdf quarterly-review
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
    
    # Generate PDF command
    pdf_parser = subparsers.add_parser('generate-pdf', help='Generate PDF for a project')
    pdf_parser.add_argument('name', help='Project name')
    
    # Project info command
    info_parser = subparsers.add_parser('info', help='Show project information')
    info_parser.add_argument('name', help='Project name')
    
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
    elif args.command == 'generate-pdf':
        client.generate_pdf(args.name)
    elif args.command == 'info':
        client.show_project(args.name)

if __name__ == "__main__":
    main()