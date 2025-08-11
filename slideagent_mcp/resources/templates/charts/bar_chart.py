#!/usr/bin/env python3
"""
TEMPLATE_META:
name: bar_chart
title: Bar Chart Template
description: Single or grouped bar charts for categorical comparisons
use_cases: ["Quarterly revenue", "Department budgets", "YoY comparisons", "Product sales"]
data_format: Lists of categories and values, optional grouping
features: ["Single or grouped bars", "Auto-themed colors", "Value labels", "Flexible layout"]
best_for: Comparing discrete categories or time periods
---
Bar Chart Template - Single or Grouped Bars

To use:
1. Copy this file to your project's plots/ directory  
2. Edit the EDIT SECTION with your data
3. Run the script to generate both branded and clean versions
"""
#!/usr/bin/env python3

"""

Bar Chart Template - Single or Grouped Bars

Common uses: Quarterly revenue, department budgets, YoY comparison, product sales



To use:

1. Copy this file to your project's charts/ directory

2. Edit the EDIT SECTION with your data

3. Run the script to generate both branded and clean versions

"""



import sys

import os




from slideagent_mcp.utils.plot_buddy import PlotBuddy

import matplotlib.pyplot as plt

import numpy as np



# Initialize PlotBuddy - automatically detects theme from project's theme folder
buddy = PlotBuddy.from_project_config()



# Create figure with slide-optimized dimensions (16:9)

fig, ax = buddy.setup_figure(figsize=(14, 7.875))



# === EDIT THIS SECTION ===

# Configure your data here



categories = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']

series1_data = [45, 52, 61, 73]

series1_label = "Revenue"

series1_color = None  # None = use theme default



# For grouped bars, add second series (set to None for single bars)

series2_data = None  # Example: [12, 15, 18, 24]

series2_label = "Profit"

series2_color = None  # None = use theme default



# Chart configuration

chart_title = "Quarterly Performance"

chart_subtitle = "Strong growth across all quarters"

y_label = "Amount ($M)"

show_values = True  # Show values on top of bars

footnote_text = "Source: Company financial reports Q1-Q4 2024"  # Set to None to omit



# Output filename (without extension)

output_name = "bar_chart"



# === END EDIT SECTION ===



# Create the chart

x = np.arange(len(categories))



if series2_data:

    # Grouped bars

    width = 0.35

    bars1 = ax.bar(x - width/2, series1_data, width, label=series1_label, color=series1_color)

    bars2 = ax.bar(x + width/2, series2_data, width, label=series2_label, color=series2_color)

    

    if show_values:

        for bars, data in [(bars1, series1_data), (bars2, series2_data)]:

            for bar, value in zip(bars, data):

                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(data)*0.01,

                       f'{value}', ha='center', va='bottom', fontsize=10)

    

    # For branded version: legend inside plot area (top-left)

    ax.legend(loc='upper left', framealpha=0.9)

else:

    # Single series bars

    bars = ax.bar(x, series1_data, color=series1_color)

    

    if show_values:

        for bar, value in zip(bars, series1_data):

            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(series1_data)*0.01,

                   f'{value}', ha='center', va='bottom', fontsize=10)



# Configure axes

ax.set_xticks(x)

ax.set_xticklabels(categories)

ax.set_ylabel(y_label)

ax.set_ylim(0, max(max(series1_data), max(series2_data) if series2_data else 0) * 1.1)



# Add grid for readability

ax.grid(True, axis='y', alpha=0.3, linestyle='--')



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