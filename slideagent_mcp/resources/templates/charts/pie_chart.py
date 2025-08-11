#!/usr/bin/env python3
"""
TEMPLATE_META:
name: pie_chart
title: Pie Chart Template  
description: Proportional representation for parts of a whole
use_cases: ["Market share", "Budget allocation", "Survey responses", "Portfolio mix"]
data_format: Categories and values that sum to a meaningful whole
features: ["Percentage labels", "Exploded slices", "Auto colors", "Clean styling"]
best_for: Showing composition or distribution of a total
---
Pie Chart Template - Proportions and Distributions

To use:
1. Copy this file to your project's plots/ directory
2. Edit the EDIT SECTION with your data
3. Run the script to generate both branded and clean versions
"""
#!/usr/bin/env python3

"""

Pie Chart Template - Proportions and Market Share

Common uses: Market share, budget allocation, customer segments, revenue mix



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



labels = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Other']

sizes = [45, 25, 20, 7, 3]  # Should sum to 100 for percentages

colors = None  # None = use theme defaults, or provide list of colors



# Explode slices (0 = no separation, 0.1 = slight separation)

# One value per slice, typically explode the largest

explode = (0.05, 0, 0, 0, 0)  # Explode first slice slightly



# Chart configuration

chart_title = "Market Share by Region"

chart_subtitle = "FY 2024 Revenue Distribution"

show_percentages = True  # Show percentage labels

show_legend = True       # Show legend

startangle = 45          # Rotation angle for better presentation

footnote_text = "Source: Industry analysis Q4 2024"  # Set to None to omit



# Output filename (without extension)

output_name = "pie_chart"



# === END EDIT SECTION ===



# Create the pie chart

if colors is None:

    # Use theme colors if not specified

    colors = plt.cm.Set3.colors[:len(labels)]



if show_percentages:

    autopct = '%1.1f%%'

else:

    autopct = None



wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 

                                   autopct=autopct, startangle=startangle,

                                   explode=explode, shadow=False)



# Improve text readability

for text in texts:

    text.set_fontsize(11)

if show_percentages:

    for autotext in autotexts:

        autotext.set_color('white')

        autotext.set_fontsize(10)

        autotext.set_weight('bold')



# Add legend if requested

if show_legend:

    ax.legend(labels, loc='upper left', framealpha=0.9)  # Inside plot for branded version



# Equal aspect ratio ensures circular pie

ax.axis('equal')



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