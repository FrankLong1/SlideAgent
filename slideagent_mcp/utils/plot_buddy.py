"""
PlotBuddy - Lightweight plotting helper class

A lightweight plotting library that provides a clean class-based interface for chart creation.
Works with local mplstyle files and handles all plotting context and styling.

Design principle: "All my context is handled by the buddy"
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter


class PlotBuddy:
    """
    A lightweight plotting helper class that manages styling and chart components.
    
    Key features:
    - Local style loading without system installation
    - Consistent chart styling and components
    - Generic logo and title functionality
    - All context managed by the buddy instance
    """
    
    # Default constants
    DEFAULT_TIGHT_LAYOUT_RECT = [0, 0.08, 1, 1]
    DEFAULT_WIDE_FIGURE = (16, 10)
    DEFAULT_BOXY_FIGURE = (12, 9)
    DEFAULT_TITLE_FONT_SIZE = 20
    DEFAULT_SUBTITLE_FONT_SIZE = 14
    DEFAULT_STANDARD_FONT_SIZE = 14
    DEFAULT_TITLE_Y_POSITION = 1.12
    DEFAULT_SUBTITLE_Y_POSITION = 1.06
    
    def __init__(self, style_dir_path=None):
        """
        Initialize PlotBuddy with style directory path.
        
        Args:
            style_dir_path (str): Path to directory containing .mplstyle files
                                 If None, uses current directory
        """
        self.style_dir_path = style_dir_path or os.getcwd()
        self.current_style = None
        
        # Auto-detect logo paths from theme directory
        theme_name = os.path.basename(self.style_dir_path)
        icon_logo = os.path.join(self.style_dir_path, f"{theme_name}_icon_logo.png")
        text_logo = os.path.join(self.style_dir_path, f"{theme_name}_text_logo.png")
        
        # Store logo paths if they exist
        self.icon_logo_path = icon_logo if os.path.exists(icon_logo) else None
        self.text_logo_path = text_logo if os.path.exists(text_logo) else None
        
        # Layout and styling constants
        self.tight_layout_rect = self.DEFAULT_TIGHT_LAYOUT_RECT
        self.wide_figure = self.DEFAULT_WIDE_FIGURE
        self.boxy_figure = self.DEFAULT_BOXY_FIGURE
        self.title_font_size = self.DEFAULT_TITLE_FONT_SIZE
        self.subtitle_font_size = self.DEFAULT_SUBTITLE_FONT_SIZE
        self.standard_font_size = self.DEFAULT_STANDARD_FONT_SIZE
        self.title_y_position = self.DEFAULT_TITLE_Y_POSITION
        self.subtitle_y_position = self.DEFAULT_SUBTITLE_Y_POSITION
    
    @classmethod
    def from_theme(cls, theme_name, themes_dir=None):
        """
        Create PlotBuddy instance with a theme loaded automatically.
        
        Args:
            theme_name (str): Name of theme (e.g., 'acme_corp')
            themes_dir (str): Directory containing theme folders (if None, searches standard locations)
        
        Returns:
            PlotBuddy: Configured instance with theme loaded
        """
        if themes_dir:
            theme_path = os.path.join(themes_dir, theme_name)
        else:
            # Search for theme in standard locations
            import pathlib
            base_dir = pathlib.Path(__file__).parent.parent.parent  # Go up to repo root
            
            # Check user themes first
            user_theme_path = base_dir / "user_resources" / "themes" / theme_name
            if user_theme_path.exists():
                theme_path = str(user_theme_path)
            else:
                # Fall back to system themes
                system_theme_path = base_dir / "slideagent_mcp" / "resources" / "themes" / "core" / theme_name
                if system_theme_path.exists():
                    theme_path = str(system_theme_path)
                else:
                    # Default to old location for backward compatibility
                    theme_path = os.path.join("themes", theme_name)
        buddy = cls(style_dir_path=theme_path)
        
        # Try to load the style file
        style_name = f"{theme_name}_style"
        if buddy.load_style_from_file(style_name):
            return buddy
        else:
            print(f"Warning: Could not load style for theme '{theme_name}', using default styling")
            return buddy
    
    @classmethod
    def from_project_config(cls, config_path=None):
        """
        Create PlotBuddy instance from project's theme folder.
        Automatically detects theme from theme/*_theme.css file.
        
        Args:
            config_path (str): Ignored - kept for backward compatibility
        
        Returns:
            PlotBuddy: Configured instance with theme from project
        """
        # Look for theme folder in current directory
        theme_dir = Path("theme")
        if not theme_dir.exists():
            # Try parent directory (in case we're in plots/)
            theme_dir = Path("../theme")
        
        if not theme_dir.exists():
            print(f"Warning: Theme folder not found, using default theme")
            return cls.from_theme("acme_corp")
        
        # Detect theme name from theme folder
        theme_name = None
        for css_file in theme_dir.glob("*_theme.css"):
            # Extract theme name from filename
            theme_name = css_file.stem.replace("_theme", "")
            break
        
        if not theme_name:
            print(f"Warning: No theme CSS file found in {theme_dir}")
            return cls.from_theme("acme_corp")
        
        # Create PlotBuddy using the theme folder
        buddy = cls(style_dir_path=str(theme_dir.resolve()))
        style_name = f"{theme_name}_style"
        buddy.load_style_from_file(style_name)
        return buddy
    
    def load_style_from_file(self, style_name):
        """
        Load matplotlib style from local file without system installation.
        
        Args:
            style_name (str): Name of style file (without .mplstyle extension)
        
        Returns:
            bool: True if style loaded successfully, False otherwise
        """
        style_path = os.path.join(self.style_dir_path, f"{style_name}.mplstyle")
        
        if not os.path.exists(style_path):
            print(f"Warning: Style file not found at {style_path}")
            return False
        
        try:
            plt.style.use(style_path)
            self.current_style = style_name
            return True
        except Exception as e:
            print(f"Error loading style {style_name}: {e}")
            return False
    
    def get_style_context(self, style_name):
        """
        Get a style context manager for local style files.
        
        Args:
            style_name (str): Name of style file (without .mplstyle extension)
        
        Returns:
            matplotlib style context manager
        """
        style_path = os.path.join(self.style_dir_path, f"{style_name}.mplstyle")
        
        if not os.path.exists(style_path):
            print(f"Warning: Style file not found at {style_path}, using default style")
            return plt.style.context('default')
        
        return plt.style.context(style_path)
    
    def setup_figure(self, figsize=None):
        """
        Create a figure with proper styling.
        
        Args:
            figsize (tuple): Figure size tuple (width, height)
                           If None, uses default boxy figure size
        
        Returns:
            tuple: (figure, axis) objects
        """
        if figsize is None:
            figsize = self.boxy_figure
        
        return plt.subplots(figsize=figsize)
    
    def add_logo(self, fig, logo_path, position='bottom-right', 
                 width=0.12, height=0.08, margin=0.01):
        """
        Add logo to figure at specified position.
        
        Args:
            fig: matplotlib figure object
            logo_path (str): Path to logo image file
            position (str): Logo position ('bottom-right', 'bottom-left', 'top-right', 'top-left')
            width (float): Logo width in figure coordinates
            height (float): Logo height in figure coordinates
            margin (float): Margin from figure edges
        
        Raises:
            FileNotFoundError: If logo file doesn't exist
            Exception: If image cannot be loaded
        """
        if not logo_path or not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo file not found: {logo_path}")
        
        try:
            logo_img = mpimg.imread(logo_path)
        except Exception as e:
            raise Exception(f"Could not load logo image: {e}")
        
        # Calculate position based on position parameter
        positions = {
            'bottom-right': (1 - width - margin, margin),
            'bottom-left': (margin, margin),
            'top-right': (1 - width - margin, 1 - height - margin),
            'top-left': (margin, 1 - height - margin)
        }
        
        if position not in positions:
            raise ValueError(f"Invalid position: {position}. Must be one of {list(positions.keys())}")
        
        left, bottom = positions[position]
        
        # Create inset axes for logo
        logo_ax = fig.add_axes([left, bottom, width, height])
        logo_ax.imshow(logo_img)
        logo_ax.axis('off')
    
    def add_source_citation(self, fig, source, position='bottom-left', 
                           fontsize=None, color='black'):
        """
        Add source attribution to figure.
        
        Args:
            fig: matplotlib figure object
            source (str): Source attribution text
            position (str): Position ('bottom-left', 'bottom-right')
            fontsize (int): Font size for source text
            color (str): Text color
        """
        if not source:
            return
        
        if fontsize is None:
            fontsize = self.standard_font_size - 2
        
        positions = {
            'bottom-left': (0.02, 0.01, 'left'),
            'bottom-right': (0.98, 0.01, 'right')
        }
        
        if position not in positions:
            raise ValueError(f"Invalid position: {position}. Must be one of {list(positions.keys())}")
        
        x, y, ha = positions[position]
        
        fig.text(x, y, f"Source: {source}",
                 fontsize=fontsize, color=color,
                 ha=ha, va='bottom')
    
    def add_footnote(self, fig, text, position='bottom-left', fontsize=10, color='#666666'):
        """
        Add footnote text at the bottom of the figure.
        
        Args:
            fig: Matplotlib figure object
            text (str): Footnote text to display
            position (str): Position of footnote ('bottom-left', 'bottom-center', 'bottom-right')
            fontsize (int): Font size for footnote
            color (str): Color of footnote text
        """
        if position == 'bottom-left':
            x = 0.02
            ha = 'left'
        elif position == 'bottom-center':
            x = 0.5
            ha = 'center'
        else:  # bottom-right
            x = 0.98
            ha = 'right'
        
        fig.text(x, 0.02, text, ha=ha, va='bottom', 
                fontsize=fontsize, color=color, 
                transform=fig.transFigure, style='italic')
    
    def add_titles(self, ax, title, subtitle=None, subtitle2=None):
        """
        Add main title and subtitle(s) to chart with enhanced positioning.
        
        Args:
            ax: matplotlib axis object
            title (str): Main title text
            subtitle (str): First subtitle text
            subtitle2 (str): Second subtitle text (optional)
        """
        # Main title
        ax.text(0, self.title_y_position, title,
                transform=ax.transAxes, fontsize=self.title_font_size,
                fontweight='bold', ha='left', va='bottom')
        
        # First subtitle
        if subtitle:
            ax.text(0, self.subtitle_y_position, subtitle,
                    transform=ax.transAxes, fontsize=self.subtitle_font_size,
                    fontweight='normal', ha='left', va='bottom', color='black')
        
        # Second subtitle (positioned below first)
        if subtitle2:
            subtitle2_y = self.subtitle_y_position - 0.04
            ax.text(0, subtitle2_y, subtitle2,
                    transform=ax.transAxes, fontsize=self.subtitle_font_size - 1,
                    fontweight='normal', ha='left', va='bottom', color='gray')
    
    def create_legend(self, ax, legend_entries=None, ncol=None, 
                     position='bottom', **kwargs):
        """
        Create and position a legend with consistent styling.
        
        Args:
            ax: matplotlib axis object
            legend_entries: optional list of tuples (label, color) for manual legend
            ncol: number of columns (if None, uses number of legend items)
            position: legend position ('bottom', 'right', 'top')
            **kwargs: additional legend parameters
        
        Returns:
            legend object
        """
        if legend_entries is not None:
            # Manual mode: create legend from provided entries
            handles = []
            labels = []
            
            for entry in legend_entries:
                if len(entry) == 2:
                    label, color = entry
                    # Create square patch for consistent appearance
                    patch = mpatches.Rectangle((0, 0), 1, 1, facecolor=color,
                                             edgecolor='none', alpha=0.8)
                    handles.append(patch)
                    labels.append(label)
                else:
                    raise ValueError("legend_entries must be tuples of (label, color)")
        else:
            # Automatic mode: use existing plot elements
            handles, labels = ax.get_legend_handles_labels()
            
            # Convert any Line2D handles to patches for consistent square appearance
            new_handles = []
            for handle in handles:
                if isinstance(handle, Line2D):
                    # Get the color from the line
                    color = handle.get_color()
                    # Create a square patch instead
                    patch = mpatches.Rectangle((0, 0), 1, 1, facecolor=color,
                                             edgecolor='none', alpha=0.8)
                    new_handles.append(patch)
                else:
                    new_handles.append(handle)
            handles = new_handles
        
        if not handles or not labels:
            return None
        
        # Auto-calculate ncol to prevent legend overflow if not specified
        if ncol is None:
            # Estimate if labels would be too wide for one row
            # Use a simple heuristic: if average label length > 25 chars, use multiple rows
            avg_label_length = sum(len(label) for label in labels) / len(labels) if labels else 0
            
            if avg_label_length > 40:  # Very long labels - use 2 columns max
                ncol = min(2, len(labels))
            elif avg_label_length > 25:  # Long labels - use 3 columns max  
                ncol = min(3, len(labels))
            elif len(labels) > 5:  # Many items - limit to 4 columns
                ncol = min(4, len(labels))
            else:
                ncol = len(labels)  # Default: all in one row
        
        # Position settings
        positions = {
            'bottom': {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.15)},
            'right': {'loc': 'center left', 'bbox_to_anchor': (1.02, 0.5)},
            'top': {'loc': 'lower center', 'bbox_to_anchor': (0.5, 1.02)}
        }
        
        pos_config = positions.get(position, positions['bottom'])
        
        legend_kwargs = {
            'frameon': False,
            'fancybox': False,
            'edgecolor': '#CCCCCC',
            'facecolor': 'white',
            'handlelength': 0.7,
            'handletextpad': 0.6,
            'columnspacing': 2.25,
            'fontsize': self.standard_font_size,
            'ncol': ncol,
            **pos_config,
            **kwargs
        }
        
        legend = ax.legend(handles, labels, **legend_kwargs)
        return legend
    
    def apply_tight_layout(self, fig):
        """
        Apply tight layout with buddy's default settings.
        
        Args:
            fig: matplotlib figure object
        """
        fig.tight_layout(rect=self.tight_layout_rect)
    
    def save(self, filepath, branded=True, **kwargs):
        """
        Save chart with option for branded or clean output.
        
        Args:
            filepath (str): Path to save the chart
            branded (bool): If True, includes logos and titles. If False, clean chart only.
            **kwargs: Additional arguments passed to matplotlib savefig
        """
        # Extract base filename and extension
        base_path, ext = os.path.splitext(filepath)
        
        # Get current figure
        fig = plt.gcf()
        
        if branded:
            # Save with full branding
            branded_path = f"{base_path}_branded{ext}"
            default_kwargs = {'dpi': 300, 'bbox_inches': 'tight', 'facecolor': 'white'}
            save_kwargs = {**default_kwargs, **kwargs}
            fig.savefig(branded_path, **save_kwargs)
            
            # Also save clean version by temporarily hiding branded elements
            clean_path = f"{base_path}_clean{ext}"
            self._save_clean_version(fig, clean_path, **save_kwargs)
            
            return branded_path, clean_path
        else:
            # Save only clean version
            clean_path = f"{base_path}_clean{ext}"
            default_kwargs = {'dpi': 300, 'bbox_inches': 'tight', 'facecolor': 'white'}
            save_kwargs = {**default_kwargs, **kwargs}
            self._save_clean_version(fig, clean_path, **save_kwargs)
            
            return clean_path
    
    def _save_clean_version(self, fig, filepath, **kwargs):
        """
        Save a clean version of the chart without logos and minimal titles.
        
        Args:
            fig: matplotlib figure object
            filepath (str): Path to save clean version
            **kwargs: Additional arguments passed to matplotlib savefig
        """
        # Store original visibility states
        original_states = {}
        
        # Hide logo axes (they are inset axes)
        for ax in fig.get_axes():
            # Check if this looks like a logo axis (no ticks, labels, etc.)
            if (len(ax.get_xticks()) == 0 and len(ax.get_yticks()) == 0 and 
                not ax.get_xlabel() and not ax.get_ylabel() and
                not ax.get_title()):
                original_states[ax] = ax.get_visible()
                ax.set_visible(False)
        
        # Hide figure text elements (source citations, etc.)
        for text in fig.texts:
            if 'source:' in text.get_text().lower():
                original_states[text] = text.get_visible()
                text.set_visible(False)
        
        # Save clean version
        fig.savefig(filepath, **kwargs)
        
        # Restore original visibility states
        for element, original_state in original_states.items():
            element.set_visible(original_state)
    
    def format_axis_as_currency(self, ax, axis='y', symbol='$', suffix=''):
        """
        Format axis labels as currency.
        
        Args:
            ax: matplotlib axis object
            axis: which axis to format ('x' or 'y')
            symbol: currency symbol
            suffix: suffix to add (e.g., 'M' for millions)
        """
        def currency_formatter(x, pos):
            if x == 0:
                return '0'
            return f'{symbol}{x:,.0f}{suffix}'
        
        formatter = FuncFormatter(currency_formatter)
        if axis == 'y':
            ax.yaxis.set_major_formatter(formatter)
        else:
            ax.xaxis.set_major_formatter(formatter)
    
    def format_axis_as_percentage(self, ax, axis='y'):
        """
        Format axis labels as percentages.
        
        Args:
            ax: matplotlib axis object
            axis: which axis to format ('x' or 'y')
        """
        def percentage_formatter(x, pos):
            return f'{x:.1f}%'
        
        formatter = FuncFormatter(percentage_formatter)
        if axis == 'y':
            ax.yaxis.set_major_formatter(formatter)
        else:
            ax.xaxis.set_major_formatter(formatter)


# Backward compatibility functions
def add_gs_logo(fig, logo_path, left=0.90, bottom=0.01, width=0.12, height=0.08):
    """Backward compatibility wrapper for add_logo"""
    buddy = PlotBuddy()
    buddy.add_logo(fig, logo_path, position='bottom-right', width=width, height=height)

def add_source_citation(fig, source):
    """Backward compatibility wrapper for add_source_citation"""
    buddy = PlotBuddy()
    buddy.add_source_citation(fig, source)

def add_chart_titles(ax, title, subtitle):
    """Backward compatibility wrapper for add_titles"""
    buddy = PlotBuddy()
    buddy.add_titles(ax, title, subtitle)

def setup_figure(figsize=None):
    """Backward compatibility wrapper for setup_figure"""
    buddy = PlotBuddy()
    return buddy.setup_figure(figsize)

def create_legend_at_bottom(ax, legend_entries=None, ncol=None):
    """Backward compatibility wrapper for create_legend"""
    buddy = PlotBuddy()
    return buddy.create_legend(ax, legend_entries, ncol)

# Export constants for backward compatibility
TIGHT_LAYOUT_RECT = PlotBuddy.DEFAULT_TIGHT_LAYOUT_RECT
WIDE_FIGURE = PlotBuddy.DEFAULT_WIDE_FIGURE
BOXY_FIGURE = PlotBuddy.DEFAULT_BOXY_FIGURE
TITLE_FONT_SIZE = PlotBuddy.DEFAULT_TITLE_FONT_SIZE
SUBTITLE_FONT_SIZE = PlotBuddy.DEFAULT_SUBTITLE_FONT_SIZE
STANDARD_FONT_SIZE = PlotBuddy.DEFAULT_STANDARD_FONT_SIZE