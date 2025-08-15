# [title]

**Author**: [author]  
**Theme**: [theme]  
**Date**: [date]

## Description
Template for creating report outlines with page structure and agent distribution

## Executive Summary
[Brief overview of the report]

## Report Structure

# Section 1: Executive Overview

## Page 1: Cover Page
- Template: 01_cover_page.html
- Content: [Title, subtitle, organization branding]

## Page 2: Table of Contents
- Template: 02_table_of_contents.html
- Content: [Navigation structure]

## Page 3: Executive Letter
- Template: 03_executive_letter.html
- Content: [Letter from leadership]

# Section 2: Analysis

## Page 4: Section Divider
- Template: 04_section_divider.html
- Content: [Section title and visual]

## Page 5: Key Findings
- Template: 05_content_page.html
- Content: [Main findings and analysis]

## Page 6: Data Visualization
- Template: 06_data_visualization.html
- Content: [Charts and metrics]

[Add more pages as needed]

## Agent Distribution

```yaml
agent_distribution:
  agent_1:
    sections: ["Executive Overview"]
    pages: [1-3]
  agent_2:
    sections: ["Analysis"]
    pages: [4-6]
```