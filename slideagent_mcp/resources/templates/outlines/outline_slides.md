# [title]

**Author**: [author]  
**Theme**: [theme]  
**Date**: [date]

## Description
Template for creating slide presentation outlines with agent distribution

## Executive Summary
[Brief overview of the presentation]

## Outline

# Section 1: Introduction (slides 1-3)

## Slide 1: Title Slide
- Template: 00_title_slide.html
- Content: [Main title and subtitle]

## Slide 2: Agenda
- Template: 01_base_slide.html
- Content: [Overview of topics to cover]

## Slide 3: Background
- Template: 02_text_image_split.html
- Content: [Context and background information]

# Section 2: Main Content (slides 4-8)

## Slide 4: Key Point 1
- Template: 01_base_slide.html
- Content: [Detailed content for first key point]

[Add more slides as needed]

## Agent Distribution

```yaml
agent_distribution:
  agent_1:
    sections: ["Section 1"]
    slides: [1-3]
  agent_2:
    sections: ["Section 2"]
    slides: [4-8]
```