#!/usr/bin/env python3
"""
Generate professional charts for Gregg Lemkau presentation
"""

import os
import sys
sys.path.append('src')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from charts.utils.plot_buddy import PlotBuddy

# Change to project directory
os.chdir('projects/gregg')

# Initialize PlotBuddy from project config
buddy = PlotBuddy.from_project_config()

# Chart 1: Career Timeline
fig, ax = buddy.setup_figure(figsize=(12, 6))

# Career phases
phases = ['Goldman Sachs\nAnalyst-MD', 'Goldman Sachs\nPartner-Co-Head IBD', 'MSD Partners\nCEO', 'BDT & MSD\nCo-CEO']
years = [1998, 2010, 2021.5, 2023.5]
durations = [12, 10, 3, 1.5]

# Create timeline
colors = ['#1f4e79', '#2e5f8a', '#3d709b', '#4c81ac']
bars = ax.barh(range(len(phases)), durations, left=[1992, 2004, 2020, 2023], 
               color=colors, height=0.6, alpha=0.8)

# Add value labels
for i, (bar, phase) in enumerate(zip(bars, phases)):
    width = bar.get_width()
    ax.text(bar.get_x() + width/2, bar.get_y() + bar.get_height()/2, 
            phase, ha='center', va='center', fontsize=11, fontweight='bold', color='white')

ax.set_yticks([])
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_xlim(1990, 2025)
ax.grid(axis='x', alpha=0.3)

buddy.add_titles(ax, "Career Timeline", "28 Years at Goldman Sachs to Merchant Banking Leadership")
buddy.add_logo(fig, "../../themes/private/bdt_msd/bdt_msd_icon_logo.png")

branded_path, clean_path = buddy.save("plots/career_timeline.png", branded=True)
plt.close()

# Chart 2: Goldman Sachs Progression
fig, ax = buddy.setup_figure(figsize=(10, 8))

positions = ['Analyst\n(1992)', 'MD\n(2001)', 'Partner\n(2002)', 'COO IBD\n(2007)', 
             'Co-Head TMT\n(2008)', 'Co-Head M&A\n(2013)', 'Co-Head IBD\n(2017)']
levels = [1, 3, 4, 6, 7, 9, 10]
years_pos = [1992, 2001, 2002, 2007, 2008, 2013, 2017]

# Create step chart
ax.step(years_pos, levels, where='post', linewidth=3, color='#1f4e79', alpha=0.8)
ax.scatter(years_pos, levels, s=120, color='#1f4e79', zorder=5)

# Add position labels
for i, (year, level, pos) in enumerate(zip(years_pos, levels, positions)):
    ax.annotate(pos, (year, level), xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                fontsize=9, ha='left')

ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Seniority Level', fontsize=12, fontweight='bold')
ax.set_ylim(0, 11)
ax.grid(True, alpha=0.3)

buddy.add_titles(ax, "Goldman Sachs Career Progression", "Strategic Ascent Through Investment Banking Hierarchy")
buddy.add_logo(fig, "../../themes/private/bdt_msd/bdt_msd_icon_logo.png")

branded_path, clean_path = buddy.save("plots/goldman_progression.png", branded=True)
plt.close()

# Chart 3: Dell Transactions Value
fig, ax = buddy.setup_figure(figsize=(10, 6))

transactions = ['Dell LBO\n(2013)', 'Dell Return to Public\n(2018)', 'Combined Advisory Value']
values = [24.4, 15.8, 40.2]  # Estimated values in billions
colors = ['#2e5f8a', '#4c81ac', '#1f4e79']

bars = ax.bar(transactions, values, color=colors, alpha=0.8)

# Add value labels
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'${value}B', ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylabel('Transaction Value ($ Billions)', fontsize=12, fontweight='bold')
ax.set_ylim(0, 45)
ax.grid(axis='y', alpha=0.3)

buddy.add_titles(ax, "Michael Dell Relationship Value", "Foundation for Strategic Career Transition")
buddy.add_logo(fig, "../../themes/private/bdt_msd/bdt_msd_icon_logo.png")

branded_path, clean_path = buddy.save("plots/dell_transactions.png", branded=True)
plt.close()

# Chart 4: AUM Growth trajectory
fig, ax = buddy.setup_figure(figsize=(10, 6))

# Simulated AUM growth
years = [2009, 2015, 2020, 2023]
aum_values = [2, 8, 15, 50]  # MSD Capital -> MSD Partners -> BDT & MSD
labels = ['MSD Capital\nFounded', 'Family Office\nGrowth', 'Lemkau Joins\nMSD Partners', 'BDT & MSD\nMerger']

ax.plot(years, aum_values, marker='o', linewidth=3, markersize=8, color='#1f4e79')
ax.fill_between(years, aum_values, alpha=0.3, color='#1f4e79')

# Add labels
for year, aum, label in zip(years, aum_values, labels):
    ax.annotate(f'${aum}B AUM\n{label}', (year, aum), xytext=(0, 20), 
                textcoords='offset points', ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                fontsize=9)

ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Assets Under Management ($ Billions)', fontsize=12, fontweight='bold')
ax.set_ylim(0, 55)
ax.grid(True, alpha=0.3)

buddy.add_titles(ax, "AUM Growth Trajectory", "From Dell Family Office to $50B+ Merchant Bank")
buddy.add_logo(fig, "../../themes/private/bdt_msd/bdt_msd_icon_logo.png")

branded_path, clean_path = buddy.save("plots/aum_growth.png", branded=True)
plt.close()

# Chart 5: BDT & MSD Structure
fig, ax = buddy.setup_figure(figsize=(12, 8))

# Create organizational structure visualization
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.patches as mpatches

ax.set_xlim(0, 10)
ax.set_ylim(0, 8)

# Main entity
main_box = FancyBboxPatch((2, 6), 6, 1.5, boxstyle="round,pad=0.1", 
                         facecolor='#1f4e79', edgecolor='black', linewidth=2)
ax.add_patch(main_box)
ax.text(5, 6.75, 'BDT & MSD PARTNERS\n$50B+ AUM', ha='center', va='center', 
        fontsize=14, fontweight='bold', color='white')

# Leadership
leader1 = FancyBboxPatch((0.5, 4.5), 3, 1, boxstyle="round,pad=0.1", 
                        facecolor='#2e5f8a', edgecolor='black')
ax.add_patch(leader1)
ax.text(2, 5, 'Byron Trott\nChairman & Co-CEO', ha='center', va='center', 
        fontsize=10, fontweight='bold', color='white')

leader2 = FancyBboxPatch((6.5, 4.5), 3, 1, boxstyle="round,pad=0.1", 
                        facecolor='#2e5f8a', edgecolor='black')
ax.add_patch(leader2)
ax.text(8, 5, 'Gregg Lemkau\nCo-CEO', ha='center', va='center', 
        fontsize=10, fontweight='bold', color='white')

# Investment pillars
pillars = ['Private Capital', 'Private Credit', 'Real Estate', 'Growth Equity']
pillar_colors = ['#4c81ac', '#5d92bd', '#6ea3ce', '#7fb4df']

for i, (pillar, color) in enumerate(zip(pillars, pillar_colors)):
    x = 0.5 + i * 2.25
    pillar_box = FancyBboxPatch((x, 2.5), 2, 1, boxstyle="round,pad=0.1", 
                               facecolor=color, edgecolor='black')
    ax.add_patch(pillar_box)
    ax.text(x + 1, 3, pillar, ha='center', va='center', 
            fontsize=9, fontweight='bold', color='white')

# Advisory services
advisory_box = FancyBboxPatch((2, 0.5), 6, 1, boxstyle="round,pad=0.1", 
                             facecolor='#3d709b', edgecolor='black')
ax.add_patch(advisory_box)
ax.text(5, 1, 'Advisory Services\nM&A • Capital Structure • Governance', ha='center', va='center', 
        fontsize=11, fontweight='bold', color='white')

# Add connection lines
ax.plot([2, 2], [5.5, 6], 'k-', linewidth=2)
ax.plot([8, 8], [5.5, 6], 'k-', linewidth=2)

for i in range(4):
    x = 1.5 + i * 2.25
    ax.plot([x, 5], [3.5, 6], 'k-', linewidth=1, alpha=0.6)

ax.plot([5, 5], [1.5, 6], 'k-', linewidth=2)

ax.axis('off')

buddy.add_titles(ax, "BDT & MSD Partners Structure", "Integrated Merchant Banking Platform")
buddy.add_logo(fig, "../../themes/private/bdt_msd/bdt_msd_icon_logo.png")

branded_path, clean_path = buddy.save("plots/bdtmsd_structure.png", branded=True)
plt.close()

# Chart 6: Network Map (simplified)
fig, ax = buddy.setup_figure(figsize=(12, 10))

# Central node
central_x, central_y = 5, 5
ax.scatter(central_x, central_y, s=800, color='#1f4e79', alpha=0.8, zorder=3)
ax.text(central_x, central_y, 'Gregg\nLemkau', ha='center', va='center', 
        fontsize=12, fontweight='bold', color='white', zorder=4)

# Network categories and positions
networks = {
    'Tech Founders': [(3, 8), ['Musk', 'Kalanick', 'Ek', 'Benioff']],
    'Private Equity': [(8, 8), ['Silver Lake', 'KKR', 'Apollo']],
    'Family Offices': [(2, 2), ['Dell Family', 'Ultra-HNW', 'Founders']],
    'Academia': [(8, 2), ['Dartmouth', 'Rockefeller U.']],
    'Non-Profits': [(1, 5), ['Team Rubicon', 'Grassroot Soccer']],
    'Goldman Alumni': [(9, 5), ['IBD Network', 'M&A Leaders']]
}

colors = ['#2e5f8a', '#4c81ac', '#5d92bd', '#6ea3ce', '#7fb4df', '#90c5f0']

for i, (category, data) in enumerate(networks.items()):
    (x, y), members = data
    # Category node
    ax.scatter(x, y, s=400, color=colors[i], alpha=0.8, zorder=2)
    ax.text(x, y+0.7, category, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Connection to center
    ax.plot([central_x, x], [central_y, y], 'k-', alpha=0.4, linewidth=2)
    
    # Member nodes
    for j, member in enumerate(members[:3]):  # Limit to 3 members
        angle = (j - 1) * 0.8
        member_x = x + 1.2 * np.cos(angle)
        member_y = y + 1.2 * np.sin(angle)
        ax.scatter(member_x, member_y, s=100, color=colors[i], alpha=0.6)
        ax.text(member_x, member_y-0.3, member, ha='center', va='top', fontsize=8)

ax.set_xlim(-1, 11)
ax.set_ylim(0, 10)
ax.axis('off')

buddy.add_titles(ax, "The Lemkau Network", "Strategic Relationships Across Finance, Technology, and Society")
buddy.add_logo(fig, "../../themes/private/bdt_msd/bdt_msd_icon_logo.png")

branded_path, clean_path = buddy.save("plots/network_map.png", branded=True)
plt.close()

# Chart 7: Competitive Positioning
fig, ax = buddy.setup_figure(figsize=(12, 8))

# Competitive landscape matrix
firms = ['Traditional IB', 'PE Funds', 'Family Offices', 'BDT & MSD']
advisory_strength = [9, 3, 2, 9]
capital_strength = [2, 9, 7, 8]
duration_focus = [2, 5, 9, 9]

# Create scatter plot
colors = ['#cccccc', '#999999', '#666666', '#1f4e79']
sizes = [100, 150, 120, 300]

for firm, adv, cap, dur, color, size in zip(firms, advisory_strength, capital_strength, 
                                           duration_focus, colors, sizes):
    ax.scatter(adv, cap, s=size, c=color, alpha=0.7, edgecolors='black', linewidth=2)
    
    if firm == 'BDT & MSD':
        ax.annotate(firm, (adv, cap), xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='#1f4e79', alpha=0.8),
                   fontsize=12, fontweight='bold', color='white')
    else:
        ax.annotate(firm, (adv, cap), xytext=(5, 5), textcoords='offset points',
                   fontsize=10)

ax.set_xlabel('Advisory Strength', fontsize=12, fontweight='bold')
ax.set_ylabel('Capital Deployment Capability', fontsize=12, fontweight='bold')
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.grid(True, alpha=0.3)

# Add quadrant labels
ax.text(2, 8.5, 'High Capital\nLow Advisory', ha='center', fontsize=10, alpha=0.6)
ax.text(8, 8.5, 'High Capital\nHigh Advisory', ha='center', fontsize=10, alpha=0.6, 
        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
ax.text(2, 1.5, 'Low Capital\nLow Advisory', ha='center', fontsize=10, alpha=0.6)
ax.text(8, 1.5, 'High Advisory\nLow Capital', ha='center', fontsize=10, alpha=0.6)

buddy.add_titles(ax, "Competitive Positioning", "Unique Integration of Elite Advisory + Patient Capital")
buddy.add_logo(fig, "../../themes/private/bdt_msd/bdt_msd_icon_logo.png")

branded_path, clean_path = buddy.save("plots/competitive_positioning.png", branded=True)
plt.close()

print("✅ All charts created successfully!")
print("Charts available in projects/gregg/plots/")