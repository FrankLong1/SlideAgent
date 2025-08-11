# Outline Generation Prompts

## Critical Outline Format

The outline MUST follow this exact format for the live viewer to work correctly:

```markdown
# Project Title

# Section 1: Section Name (slides X-Y)    ← Use single # for sections
## Slide X: Slide Title                   ← Use double ## for slides
- Template: [exact path from list_slide_templates]
- Content: [DETAILED CONTENT - see requirements below]
```

### Format Rules
- Use `#` (single hash) for section headers, NOT `##` 
- Use `##` (double hash) for slide headers, NOT `###`
- Include `(slides X-Y)` in section headers

## Content Requirements

The outline should contain **ACTUAL DETAILED CONTENT** for each slide, not placeholders. Include:

- **Bias toward verbosity and specificity**: Include exact numbers, quotes, labels, and chart references from source materials
- **For text slides**: Complete bullet points, full sentences, specific data points
- **For data tables**: Actual numbers, percentages, dollar amounts with proper formatting
- **For comparison slides**: Specific comparison points, metrics, advantages/disadvantages
- **For quote slides**: The exact quote text and attribution
- **For timeline slides**: Specific dates, milestones, and descriptions
- **For chart slides**: Exact data values, axis labels, legend items
- **For architecture slides**: Component names, relationships, descriptions

### Good Example
```markdown
## Slide 2: Financial Performance
- Template: slideagent_mcp/resources/templates/slides/07_financial_data_table.html
- Content:
  - Revenue FY2024: $1.9B (737% YoY growth)
  - Revenue FY2023: $229M (1,346% YoY growth)  
  - Revenue FY2022: $16M
  - Gross Margin: 42% (up from 38% in FY2023)
  - Operating Loss: ($863M) in FY2024
  - Adjusted EBITDA: ($65M) vs ($45M) in FY2023
  - Cash & Equivalents: $450M
  - Total Debt: $8.0B
  - RPO (Remaining Performance Obligations): $15.1B
```

### Bad Example
```markdown
## Slide 2: Financial Performance
- Template: slideagent_mcp/resources/templates/slides/07_financial_data_table.html
- Content: Financial metrics and performance data
```

## Template Selection

- **Use templates that match your content** - variety is nice but ensure proper fit
- **Repeat templates as needed** - it's fine to have multiple consecutive base slides
- **Use ANY templates in ANY order** - don't force content into inappropriate templates
- **Skip templates that don't fit** - not every template needs to be used

## Agent Distribution

Add `agent_distribution` YAML **AFTER** creating the full outline to enable parallel generation:

### Complexity Weights for Load Balancing
- Simple slides (title, base, quote): 1x weight
- Medium slides (two-column, text+image): 1.5x weight  
- Complex slides (tables, matrices, dashboards): 2x weight

### Example Distribution
```yaml
agent_distribution:
  agent_1:
    sections: ["Introduction", "Market Analysis"]
    slides: [1-5]  # 2 simple + 3 medium = ~6 weight units
  agent_2:
    sections: ["Financial Data"]
    slides: [6-9]  # 2 complex tables + 2 charts = ~8 weight units
  agent_3:
    sections: ["Implementation", "Conclusion"]
    slides: [10-15]  # 4 simple + 2 medium = ~7 weight units
```

## Generation Steps

1. Call `list_slide_templates` to discover all available templates with paths
2. Call `list_chart_templates` to see chart options
3. Review the metadata to understand best use cases
4. **EXTRACT DETAILED CONTENT** from source materials (input files, S1 filings, etc.)
5. Generate the outline with **COMPLETE, SPECIFIC CONTENT** for each slide
6. **AS THE FINAL STEP**: Add `agent_distribution` YAML for parallel workload balancing