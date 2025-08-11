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
    
    def __init__(self, theme_folder=None):
        """
        Initialize PlotBuddy with a theme folder.
        The theme folder should contain:
        - {theme}_style.mplstyle - matplotlib style
        - {theme}_icon_logo.png - icon logo
        - {theme}_text_logo.png - text logo
        - {theme}_theme.css - CSS (not used by PlotBuddy but indicates theme name)
        
        Args:
            theme_folder (str): Path to theme folder. If None, looks for 'theme' or '../theme'
        """
        # Find theme folder
        if theme_folder:
            self.theme_folder = Path(theme_folder)
        else:
            # Try to auto-detect theme folder
            if Path("theme").exists():
                self.theme_folder = Path("theme")
            elif Path("../theme").exists():
                self.theme_folder = Path("../theme")
            else:
                raise ValueError("No theme folder found. Please specify theme_folder path.")
        
        # Detect theme name from CSS file
        self.theme_name = None
        for css_file in self.theme_folder.glob("*_theme.css"):
            self.theme_name = css_file.stem.replace("_theme", "")
            break
        
        if not self.theme_name:
            raise ValueError(f"No theme CSS file found in {self.theme_folder}")
        
        # Set paths
        self.style_dir_path = str(self.theme_folder)
        self.current_style = None
        
        # Logo paths
        self.icon_logo_path = self.theme_folder / f"{self.theme_name}_icon_logo.png"
        self.text_logo_path = self.theme_folder / f"{self.theme_name}_text_logo.png"
        
        # Convert to string and check existence
        self.icon_logo_path = str(self.icon_logo_path) if self.icon_logo_path.exists() else None
        self.text_logo_path = str(self.text_logo_path) if self.text_logo_path.exists() else None
        
        # Auto-load the theme's matplotlib style
        style_file = self.theme_folder / f"{self.theme_name}_style.mplstyle"
        if style_file.exists():
            self.load_style_from_file(self.theme_name + "_style")
        
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
        # Use the new constructor that takes theme_folder
        buddy = cls(theme_folder=theme_path)
        
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
        Just a convenience wrapper around the main constructor.
        
        Args:
            config_path: Ignored - kept for backward compatibility
        
        Returns:
            PlotBuddy: Configured instance
        """
        # Just use the default constructor which auto-detects theme folder
        return cls()
    
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
        
        IMPORTANT: This should be called BEFORE adding titles, logos, or footnotes.
        It will save the clean version first, then return so you can add branding.
        
        Args:
            filepath (str): Path to save the chart
            branded (bool): If True, saves both clean and branded. If False, clean only.
            **kwargs: Additional arguments passed to matplotlib savefig
        """
        # Extract base filename and extension
        base_path, ext = os.path.splitext(filepath)
        
        # Get current figure
        fig = plt.gcf()
        
        # Default save kwargs
        default_kwargs = {'dpi': 300, 'bbox_inches': 'tight', 'facecolor': 'white'}
        save_kwargs = {**default_kwargs, **kwargs}
        
        # Always save clean version first (current state without branding)
        clean_path = f"{base_path}_clean{ext}"
        fig.savefig(clean_path, **save_kwargs)
        
        if branded:
            # Branded path for later
            branded_path = f"{base_path}_branded{ext}"
            return branded_path, clean_path
        else:
            return clean_path
    
    def save_branded(self, filepath, **kwargs):
        """
        Save the branded version after titles, logos, and footnotes have been added.
        This should be called AFTER adding all branding elements.
        
        Args:
            filepath (str): Path to save the branded chart
            **kwargs: Additional arguments passed to matplotlib savefig
        """
        fig = plt.gcf()
        default_kwargs = {'dpi': 300, 'bbox_inches': 'tight', 'facecolor': 'white'}
        save_kwargs = {**default_kwargs, **kwargs}
        fig.savefig(filepath, **save_kwargs)
    
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
        
        # Hide ALL figure text elements for clean version
        # This includes source citations, footnotes, and any other text added to the figure
        for text in fig.texts:
            # Hide all figure-level text (these are typically titles, footers, sources, etc.)
            # We want clean charts to only have axis labels and data
            original_states[text] = text.get_visible()
            text.set_visible(False)
        
        # Hide axis text elements (titles and subtitles added via ax.text)
        for ax in fig.get_axes():
            # Skip logo axes that we already handled
            if ax in original_states:
                continue
                
            # Go through all text objects in the axis
            for text in ax.texts:
                text_str = text.get_text()
                # Hide titles and subtitles based on position
                # Titles are at y=1.12, subtitles at y=1.06 and y=1.02 in axis coords
                transform = text.get_transform()
                if transform == ax.transAxes:
                    _, y = text.get_position()
                    # Hide text positioned at the top of the plot (titles/subtitles)
                    # This captures titles at y=1.12, subtitles at y=1.06 and y=1.02
                    if y >= 1.0:
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