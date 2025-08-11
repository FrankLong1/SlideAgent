#!/usr/bin/env python3
"""
TEMPLATE_META:
name: line_chart
title: Line Chart Template
description: Trend lines and time series for showing patterns over time
use_cases: ["Growth trends", "Stock prices", "Temperature changes", "Performance metrics"]
data_format: X and Y coordinate lists, multiple series supported
features: ["Multiple lines", "Markers optional", "Trend visualization", "Time series support"]
best_for: Showing trends and changes over continuous variables
---
Line Chart Template - Trends and Time Series

To use:
1. Copy this file to your project's plots/ directory
2. Edit the EDIT SECTION with your data  
3. Run the script to generate both branded and clean versions
"""
#!/usr/bin/env python3

"""

Line Chart Template - Single or Multiple Lines

Common uses: Trends over time, stock prices, growth trajectories, comparative trends



To use:

1. Copy this file to your project's charts/ directory

2. Edit the EDIT SECTION with your data

3. Run the script to generate both branded and clean versions

"""



import sys

import os




from slideagent_mcp.utils.plot_buddy import PlotBuddy

import matplotlib.pyplot as plt



# Initialize PlotBuddy for theme consistency

# When running from templates, use the example theme directly

buddy = PlotBuddy.from_project_config()





# Create figure with slide-optimized dimensions (16:9)

fig, ax = buddy.setup_figure(figsize=(14, 7.875))



# === EDIT THIS SECTION ===

# Configure your data here



x_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

line1_data = [100, 105, 103, 108, 112, 118]

line1_label = "Revenue"

line1_color = None  # None = use theme default

line1_style = '-'   # Line style: '-', '--', '-.', ':'



# Optional: Add more lines (set to None if not needed)

line2_data = [95, 98, 102, 107, 115, 120]  # Set to None for single line

line2_label = "Profit"

line2_color = None

line2_style = '-'



line3_data = None  # Set to None if not needed

line3_label = "Costs"

line3_color = None

line3_style = '-'



# Chart configuration

chart_title = "6-Month Performance Trend"

chart_subtitle = "Revenue and profit growth analysis"

y_label = "Value ($M)"

x_label = ""  # Leave empty if x_labels are self-explanatory

show_markers = True  # Show data point markers

show_grid = True     # Show grid lines

footnote_text = "Source: Market analysis reports 2024"  # Set to None to omit



# Output filename (without extension)

output_name = "line_chart"



# === END EDIT SECTION ===



# Plot the lines

if line1_data:

    marker = 'o' if show_markers else None

    ax.plot(x_labels, line1_data, marker=marker, label=line1_label, 

            color=line1_color, linestyle=line1_style, linewidth=2, markersize=6)



if line2_data:

    marker = 's' if show_markers else None

    ax.plot(x_labels, line2_data, marker=marker, label=line2_label,

            color=line2_color, linestyle=line2_style, linewidth=2, markersize=6)



if line3_data:

    marker = '^' if show_markers else None

    ax.plot(x_labels, line3_data, marker=marker, label=line3_label,

            color=line3_color, linestyle=line3_style, linewidth=2, markersize=6)



# Configure axes

ax.set_ylabel(y_label)

if x_label:

    ax.set_xlabel(x_label)



# Add legend if multiple lines (inside plot for branded version)

if line2_data or line3_data:

    ax.legend(loc='upper left', framealpha=0.9)



# Add grid

if show_grid:

    ax.grid(True, alpha=0.3, linestyle='--')



# Set y-axis to start at 0 for better comparison (optional)

# ax.set_ylim(bottom=0)



# Apply PlotBuddy branding for branded version

buddy.add_titles(ax, chart_title, chart_subtitle)



# Add source/footnote at bottom left

if footnote_text:

    fig.text(0.12, 0.02, footnote_text, fontsize=8, style='italic', 

             transform=fig.transFigure, ha='left')



# Add logo at bottom right (text logo preferred for branded charts)

if buddy.text_logo_path:

    buddy.add_logo(fig, buddy.text_logo_path, position='bottom-right', 

                   width=0.20, height=0.06, margin=0.02)

elif buddy.icon_logo_path:

    buddy.add_logo(fig, buddy.icon_logo_path, position='bottom-right',

                   width=0.12, height=0.06, margin=0.02)



# Save both versions using buddy.save()

branded_path, clean_path = buddy.save(f"plots/{output_name}.png", branded=True)



print(f"✅ Charts saved:")

print(f"  Branded: {branded_path}")

print(f"  Clean: {clean_path}")