# Slide Outline Generation Template

## Critical Format for Slides (16:9 Horizontal)

The outline MUST follow this exact format for the live viewer to work correctly:

```markdown
# Project Title

# Section 1: Section Name (slides X-Y)    ← Use single # for sections
## Slide X: Slide Title                   ← Use double ## for slides
- Template: [filename from list_slide_templates, e.g., 01_base_slide.html]
- Content: [DETAILED CONTENT - see requirements below]
```

### Format Rules
- Use `#` (single hash) for section headers, NOT `##` 
- Use `##` (double hash) for slide headers, NOT `###`
- Include `(slides X-Y)` in section headers
- Templates are from `slides/` folder only

## Content Requirements for Slides

Slides require **GENERATIVE CONTENT** - you'll be creating persuasive narratives:

- **For text slides**: Craft compelling bullet points that tell a story
- **For data tables**: Generate insights and comparisons from raw data
- **For comparison slides**: Develop strategic analysis points
- **For quote slides**: Select impactful quotes that support the narrative
- **For timeline slides**: Create a logical flow of events/milestones
- **For chart slides**: Design visualizations that highlight key trends
- **For architecture slides**: Structure complex information clearly

### Good Slide Example
```markdown
## Slide 2: Market Opportunity
- Template: 03_two_column_slide.html
- Content:
  Left Column - Addressable Market:
  - Total Addressable Market: $75B by 2028
  - Current penetration: <5% of enterprises
  - Growth drivers: Digital transformation, AI adoption
  - Geographic expansion: 40 new markets in 2025
  
  Right Column - Competitive Advantages:
  - First-mover in conversational AI space
  - 95% customer retention rate
  - 2x faster deployment than competitors
  - Proprietary technology with 50+ patents
```

## Template Selection for Slides
- **Build narrative flow** - sequence templates to tell a story
- **Variety enhances engagement** - mix different visual formats
- **Match complexity to content** - use advanced templates for complex data
- **Create visual rhythm** - alternate dense and simple slides

## Agent Distribution for Slides

Slides benefit from parallel generation by section:

### Complexity Weights
- Simple slides (title, quote, divider): 1x
- Medium slides (base, two-column): 1.5x  
- Complex slides (tables, matrices, charts): 2x

### Example Distribution
```yaml
agent_distribution:
  agent_1:
    sections: ["Introduction", "Problem Statement"]
    slides: [1-5]
    focus: "Setting context and challenges"
  agent_2:
    sections: ["Solution Overview", "Technical Architecture"]
    slides: [6-12]
    focus: "Core value proposition and implementation"
  agent_3:
    sections: ["Business Case", "Next Steps"]
    slides: [13-18]
    focus: "ROI and call to action"
```

## Generation Steps for Slides

1. **Analyze source materials** to identify key themes and narratives
2. **Structure the story arc** - introduction → problem → solution → impact
3. **Call list_slide_templates** to see all available slide formats
4. **Generate persuasive content** that flows between slides
5. **Include chart references** where data visualization enhances the message
6. **CRITICAL: Always end with agent_distribution YAML** for parallel generation

## REQUIRED: Agent Distribution YAML

**You MUST include this at the end of every slide outline:**

```yaml
agent_distribution:
  agent_1:
    sections: ["Section names from your outline"]
    slides: [1-X]  # Actual slide ranges
  agent_2:
    sections: ["More section names"]
    slides: [X-Y]
  agent_3:
    sections: ["Final sections"]
    slides: [Y-Z]
```

This enables parallel agent execution for faster slide generation!