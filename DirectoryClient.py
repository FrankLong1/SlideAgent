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
    
    def create_project(self, project_name, theme="acme_corp"):
        """Create a new SlideAgent project with proper structure."""
        project_path = self.projects_dir / project_name
        
        if project_path.exists():
            print(f"❌ Project '{project_name}' already exists!")
            return False
        
        # Validate theme exists (check both regular and private themes)
        theme_path = self.themes_dir / theme
        private_theme_file = self.themes_dir / "private" / f"{theme}_theme.css"
        private_theme_dir = self.themes_dir / "private" / theme
        
        theme_exists = (
            (theme_path.exists() and (theme_path / f"{theme}_theme.css").exists()) or  # Regular theme
            private_theme_file.exists() or  # Private theme as file
            (private_theme_dir.exists() and (private_theme_dir / f"{theme}_theme.css").exists())  # Private theme as directory
        )
        
        if not theme_exists:
            print(f"❌ Theme '{theme}' not found! Available themes:")
            self.list_themes()
            return False
        
        # Create project structure
        project_path.mkdir(parents=True)
        (project_path / "input").mkdir()
        (project_path / "plots").mkdir()
        
        # Determine theme path for config
        if theme_path.exists() and (theme_path / f"{theme}_theme.css").exists():
            # Regular theme
            theme_config_path = f"../../themes/{theme}"
        elif private_theme_dir.exists() and (private_theme_dir / f"{theme}_theme.css").exists():
            # Private theme as directory
            theme_config_path = f"../../themes/private/{theme}"
        else:
            # Private theme as file (fallback)
            theme_config_path = f"../../themes/private"
        
        # Create config.yaml
        config = {
            'theme': theme,
            'theme_path': theme_config_path,
            'title': f'Presentation - {project_name.replace("-", " ").title()}',
            'author': 'SlideAgent User',
            'created': str(Path().absolute())
        }
        
        config_path = project_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        # Create initial outline.md
        outline_content = f"""# {config['title']}

## Slide Outline

1. **Title Slide**
   - Title: {config['title']}
   - Author: {config['author']}
   - Date: Today

2. **Overview**
   - Key points to cover
   - Agenda or roadmap

3. **Main Content**
   - Add your content here
   - Use bullet points for clarity

4. **Conclusion**
   - Summary of key takeaways
   - Next steps

## Notes

- Place source materials in the `input/` folder
- Charts will be generated in the `plots/` folder
- Use `{theme}` theme for consistent branding
"""
        
        outline_path = project_path / "outline.md"
        with open(outline_path, 'w') as f:
            f.write(outline_content)
        
        print(f"✅ Created project '{project_name}' with theme '{theme}'")
        print(f"📁 Project directory: {project_path}")
        print(f"📝 Edit outline: {outline_path}")
        print(f"⚙️  Configuration: {config_path}")
        
        return True
    
    def list_projects(self, detailed=False):
        """List all existing projects with optional detailed view."""
        projects = [d for d in self.projects_dir.iterdir() if d.is_dir()]
        
        if not projects:
            print("📂 No projects found. Create one with: python DirectoryClient.py new-project <name>")
            return
        
        print("📂 SlideAgent Projects:")
        for project in sorted(projects):
            config_path = project / "config.yaml"
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                    theme = config.get('theme', 'unknown')
                    title = config.get('title', project.name)
                    author = config.get('author', 'Unknown')
                    theme_path = config.get('theme_path', 'not specified')
                    
                    if detailed:
                        # Check file status
                        files_status = {
                            'outline.md': (project / "outline.md").exists(),
                            'presentation.html': (project / "presentation.html").exists(),
                            'PDF': (project / f"{project.name}.pdf").exists(),
                        }
                        
                        # Count files in subdirectories
                        input_count = len([f for f in (project / "input").iterdir() if f.is_file()]) if (project / "input").exists() else 0
                        plots_count = len([f for f in (project / "plots").iterdir() if f.is_file()]) if (project / "plots").exists() else 0
                        
                        print(f"\n  📊 {project.name}")
                        print(f"      Path: {project}")
                        print(f"      Title: {title}")
                        print(f"      Author: {author}")
                        print(f"      Theme: {theme} ({theme_path})")
                        print(f"      Files:")
                        for filename, exists in files_status.items():
                            status = "✅" if exists else "❌"
                            print(f"        {status} {filename}")
                        print(f"      Content: {input_count} input files, {plots_count} charts")
                    else:
                        print(f"  • {project.name} ({theme}) - {title}")
                        
                except Exception as e:
                    print(f"  • {project.name} (config error: {e})")
            else:
                print(f"  • {project.name} (no config)")
    
    def get_all_projects_data(self):
        """Return structured data for all projects (useful for programmatic access)."""
        projects = [d for d in self.projects_dir.iterdir() if d.is_dir()]
        projects_data = []
        
        for project in sorted(projects):
            config_path = project / "config.yaml"
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                    
                    # File status
                    files_status = {
                        'outline.md': (project / "outline.md").exists(),
                        'presentation.html': (project / "presentation.html").exists(),
                        'pdf': (project / f"{project.name}.pdf").exists(),
                    }
                    
                    # Count files
                    input_count = len([f for f in (project / "input").iterdir() if f.is_file()]) if (project / "input").exists() else 0
                    plots_count = len([f for f in (project / "plots").iterdir() if f.is_file()]) if (project / "plots").exists() else 0
                    
                    project_data = {
                        'name': project.name,
                        'path': str(project),
                        'config': config,
                        'files': files_status,
                        'content_counts': {
                            'input_files': input_count,
                            'plots': plots_count
                        }
                    }
                    projects_data.append(project_data)
                    
                except Exception as e:
                    projects_data.append({
                        'name': project.name,
                        'path': str(project),
                        'error': str(e)
                    })
            else:
                projects_data.append({
                    'name': project.name,
                    'path': str(project),
                    'error': 'No config.yaml found'
                })
        
        return projects_data
    
    def list_themes(self):
        """List all available themes."""
        themes = []
        
        # Check regular theme directories
        for d in self.themes_dir.iterdir():
            if d.is_dir() and d.name != 'private' and (d / f"{d.name}_theme.css").exists():
                themes.append((d.name, d))
        
        # Check private themes (both files and subdirectories in themes/private/)
        private_dir = self.themes_dir / "private"
        if private_dir.exists():
            # Look for theme files directly in private directory
            theme_files = [f for f in private_dir.iterdir() if f.name.endswith('_theme.css')]
            for css_file in theme_files:
                theme_name = css_file.name.replace('_theme.css', '')
                themes.append((theme_name, private_dir, True))  # True indicates private theme
            
            # Look for theme subdirectories in private directory
            for d in private_dir.iterdir():
                if d.is_dir() and (d / f"{d.name}_theme.css").exists():
                    themes.append((d.name, d, True))  # True indicates private theme
        
        if not themes:
            print("🎨 No themes found!")
            return
        
        print("🎨 Available Themes:")
        for theme_info in sorted(themes):
            if len(theme_info) == 3:  # Private theme
                theme_name, theme_dir, is_private = theme_info
                css_file = theme_dir / f"{theme_name}_theme.css"
                mpl_file = theme_dir / f"{theme_name}_style.mplstyle"
                status = "✅🔒" if mpl_file.exists() else "⚠️🔒"
                print(f"  • {theme_name} {status} (private)")
            else:  # Regular theme
                theme_name, theme_dir = theme_info
                css_file = theme_dir / f"{theme_name}_theme.css"
                mpl_file = theme_dir / f"{theme_name}_style.mplstyle"
                status = "✅" if mpl_file.exists() else "⚠️ "
                print(f"  • {theme_name} {status}")
    
    def generate_pdf(self, project_name):
        """Generate PDF for a project."""
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            print(f"❌ Project '{project_name}' not found!")
            return False
        
        html_file = project_path / "presentation.html"
        if not html_file.exists():
            print(f"❌ No presentation.html found in project '{project_name}'")
            print("💡 Generate the HTML file first with your LLM workflow")
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
            print("❌ Node.js not found. Install Node.js to generate PDFs.")
            return False
    
    def get_project_info(self, project_name):
        """Get detailed information about a project."""
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            print(f"❌ Project '{project_name}' not found!")
            return None
        
        config_path = project_path / "config.yaml"
        if not config_path.exists():
            print(f"❌ No config.yaml found in project '{project_name}'")
            return None
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Check for files
        files_status = {
            'outline.md': (project_path / "outline.md").exists(),
            'presentation.html': (project_path / "presentation.html").exists(),
            'PDF': (project_path / f"{project_name}.pdf").exists(),
        }
        
        # Count plots
        plots_dir = project_path / "plots"
        plot_count = len([f for f in plots_dir.iterdir() if f.is_file()]) if plots_dir.exists() else 0
        
        print(f"📊 Project: {project_name}")
        print(f"  Title: {config.get('title', 'N/A')}")
        print(f"  Theme: {config.get('theme', 'N/A')}")
        print(f"  Author: {config.get('author', 'N/A')}")
        print(f"  Files:")
        for filename, exists in files_status.items():
            status = "✅" if exists else "❌"
            print(f"    {status} {filename}")
        print(f"  Plots: {plot_count} files")
        
        return config

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
    list_parser = subparsers.add_parser('list-projects', help='List all projects')
    list_parser.add_argument('--detailed', action='store_true', help='Show detailed project information')
    
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
        client.list_projects(detailed=args.detailed)
    elif args.command == 'list-themes':
        client.list_themes()
    elif args.command == 'generate-pdf':
        client.generate_pdf(args.name)
    elif args.command == 'info':
        client.get_project_info(args.name)

if __name__ == "__main__":
    main()