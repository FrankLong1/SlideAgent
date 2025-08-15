#!/usr/bin/env python3
"""
TEMPLATE_META:
name: boilerplate
title: Boilerplate Chart
description: Basic template for creating custom charts
use_cases: ["Starting point", "Custom visualizations", "Quick prototypes"]
data_format: Any format - customize as needed
features: ["PlotBuddy integration", "Theme support", "Clean and branded versions"]
best_for: Starting a new chart from scratch
---
Boilerplate Chart Template

To use:
1. Copy this file to your project's plots/ directory
2. Rename it to match your chart name
3. Modify the code to create your visualization
4. Run the script to generate both branded and clean versions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from slideagent_mcp.utils.plot_buddy import PlotBuddy
import matplotlib.pyplot as plt
import numpy as np

# Initialize PlotBuddy with project config
buddy = PlotBuddy.from_project_config()

# === EDIT THIS SECTION ===
# Configure your data and chart here
data = [10, 20, 30, 40]
labels = ['A', 'B', 'C', 'D']
chart_title = "Chart Title"
chart_subtitle = "Chart Subtitle"
# === END EDIT SECTION ===

# Create figure with theme styling
fig, ax = buddy.setup_figure(figsize=(14, 7.875))  # Wide format for slides

# Create your visualization
ax.bar(labels, data)
ax.set_xlabel('Categories')
ax.set_ylabel('Values')

# Save branded version (with titles)
buddy.add_titles(ax, chart_title, chart_subtitle)
buddy.add_logo(fig, buddy.icon_logo_path)
output_name = os.path.basename(__file__).replace('.py', '')
buddy.save(f"plots/{output_name}_branded.png", branded=False)

# Create clean version for slides
fig, ax = buddy.setup_figure(figsize=(14, 7.875))
ax.bar(labels, data)
ax.set_xlabel('Categories')
ax.set_ylabel('Values')
ax.text(0.5, 1.02, chart_subtitle, transform=ax.transAxes, 
        ha='center', fontsize=12, color='#666')
plt.tight_layout()
plt.savefig(f"plots/{output_name}_clean.png", dpi=150, bbox_inches='tight')

print("✅ Chart generated successfully!")
print(f"   - Branded version: plots/{output_name}_branded.png")
print(f"   - Clean version: plots/{output_name}_clean.png")