#!/usr/bin/env python3
"""
TEMPLATE_META:
name: stacked_bar
title: Stacked Bar Chart Template
description: Component breakdown within categories
use_cases: ["Budget components", "Sales by region", "Resource allocation", "Multi-part metrics"]
data_format: Categories with multiple component values
features: ["Stacked components", "Total visualization", "Component labels", "Color coding"]
best_for: Showing both totals and component breakdowns
---
Stacked Bar Chart Template - Component Breakdowns

To use:
1. Copy this file to your project's plots/ directory
2. Edit the EDIT SECTION with your data
3. Run the script to generate both branded and clean versions
"""
#!/usr/bin/env python3

"""

Stacked Bar Chart Template

A flexible template for creating stacked bar charts showing component breakdowns.

Perfect for: budget allocation, time distribution, market composition, resource usage

"""



import sys

import os




from slideagent_mcp.utils.plot_buddy import PlotBuddy

import matplotlib.pyplot as plt

import numpy as np



# Initialize PlotBuddy with project config

# When running from templates, use the example theme directly

buddy = PlotBuddy.from_project_config()





# === EDIT THIS SECTION ===

# Configure your data

categories = ['Product A', 'Product B', 'Product C', 'Product D']

component1_data = [20, 35, 30, 25]  # First component

component1_label = "Material Costs"

component2_data = [25, 25, 20, 30]  # Second component  

component2_label = "Labor Costs"

component3_data = [15, 20, 25, 20]  # Third component (optional - set to None if not needed)

component3_label = "Overhead"

component4_data = [10, 10, 15, 15]  # Fourth component (optional - set to None if not needed)

component4_label = "Profit Margin"



# Chart configuration

chart_title = "Cost Breakdown Analysis"

chart_subtitle = "Component distribution by product"

xlabel = "Products"

ylabel = "Cost ($M)"



# Display options

show_values = True  # Show values on each segment

percentage_labels = False  # Show percentages instead of values

horizontal = False  # Make horizontal stacked bar chart

footnote_text = "Source: Internal cost analysis 2024"  # Set to None to omit

# === END EDIT SECTION ===



# Create figure with theme styling

fig, ax = buddy.setup_figure(figsize=(14, 7.875))  # Wide format for slides



# Prepare data

x = np.arange(len(categories))

width = 0.6



# Build component list

components = []

labels = []

if component1_data:

    components.append(component1_data)

    labels.append(component1_label)

if component2_data:

    components.append(component2_data)

    labels.append(component2_label)

if component3_data:

    components.append(component3_data)

    labels.append(component3_label)

if component4_data:

    components.append(component4_data)

    labels.append(component4_label)



# Create stacked bars

if horizontal:

    bottom = np.zeros(len(categories))

    for i, (data, label) in enumerate(zip(components, labels)):

        bars = ax.barh(x, data, width, left=bottom, label=label)

        

        # Add value labels if requested

        if show_values:

            for j, (bar, val) in enumerate(zip(bars, data)):

                if percentage_labels:

                    total = sum(comp[j] for comp in components)

                    pct = (val / total) * 100

                    ax.text(bottom[j] + val/2, bar.get_y() + bar.get_height()/2, 

                           f'{pct:.1f}%', ha='center', va='center', fontsize=10)

                else:

                    ax.text(bottom[j] + val/2, bar.get_y() + bar.get_height()/2, 

                           f'{val}', ha='center', va='center', fontsize=10)

        bottom += data

    

    ax.set_xlabel(ylabel)

    ax.set_ylabel(xlabel)

    ax.set_yticks(x)

    ax.set_yticklabels(categories)

else:

    bottom = np.zeros(len(categories))

    for i, (data, label) in enumerate(zip(components, labels)):

        bars = ax.bar(x, data, width, bottom=bottom, label=label)

        

        # Add value labels if requested

        if show_values:

            for j, (bar, val) in enumerate(zip(bars, data)):

                if percentage_labels:

                    total = sum(comp[j] for comp in components)

                    pct = (val / total) * 100

                    ax.text(bar.get_x() + bar.get_width()/2, bottom[j] + val/2, 

                           f'{pct:.1f}%', ha='center', va='center', fontsize=10)

                else:

                    ax.text(bar.get_x() + bar.get_width()/2, bottom[j] + val/2, 

                           f'{val}', ha='center', va='center', fontsize=10)

        bottom += data

    

    ax.set_xlabel(xlabel)

    ax.set_ylabel(ylabel)

    ax.set_xticks(x)

    ax.set_xticklabels(categories)



# Add legend (inside plot for branded version to avoid logo conflict)

ax.legend(loc='upper left', framealpha=0.9)



# Add grid for better readability

ax.grid(True, alpha=0.3, axis='y' if not horizontal else 'x')



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

branded_path, clean_path = buddy.save("plots/stacked_bar.png", branded=True)



print(f"✅ Charts saved:")

print(f"  Branded: {branded_path}")

print(f"  Clean: {clean_path}")