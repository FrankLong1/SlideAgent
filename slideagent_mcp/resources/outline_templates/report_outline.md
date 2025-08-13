# Report Outline Generation Template

## Critical Format for Reports (8.5x11 Vertical)

The outline MUST follow this exact format for vertical reports:

```markdown
# Report Title

# Section 1: Section Name (pages X-Y)    ← Use single # for sections
## Page X: Page Title                    ← Use double ## for pages
- Template: [filename from list_report_templates, e.g., 01_cover_page.html]
- Content: [EXACT CONTENT - see requirements below]
```

### Format Rules
- Use `#` (single hash) for section headers
- Use `##` (double hash) for page headers
- Include `(pages X-Y)` in section headers
- Templates are from `report_pages/` folder only

## Content Requirements for Reports

Reports require **EXACT CONTENT PLACEMENT** - you're formatting existing data:

- **Verbatim text**: Copy exact paragraphs, quotes, data from source
- **Precise numbers**: Transfer exact figures, percentages, amounts
- **Complete tables**: Include all rows and columns from source data
- **Full citations**: Preserve all references and attributions
- **Exact terminology**: Maintain technical terms and definitions
- **Complete lists**: Include all items from source materials

### Good Report Example
```markdown
## Page 3: Executive Summary
- Template: 01_base_page.html
- Content:
  EXACT TEXT FROM SOURCE:
  
  "In fiscal year 2024, the company achieved revenue of $1,923 million, 
  representing year-over-year growth of 737%. This growth was primarily 
  driven by enterprise adoption of our AI platform, with 85% of Fortune 
  500 companies now using our services."
  
  KEY METRICS (from Table 2.1):
  - Revenue: $1,923M (FY2024)
  - Gross Margin: 42.3%
  - Operating Cash Flow: ($456M)
  - Total Customers: 15,234
  - Enterprise Customers: 2,145
  - Net Revenue Retention: 152%
```

## Template Selection for Reports
- **Match content density** - reports can handle more text per page
- **Sequential flow** - maintain document structure
- **Standard formatting** - consistency is key for reports
- **Use branded charts** - include `_branded.png` versions with titles

## Content Sources for Reports

Reports typically transform existing documents:

- **Financial filings**: Extract exact data from 10-K, 10-Q, S-1
- **Research papers**: Preserve methodology, findings, conclusions
- **Technical documentation**: Maintain specifications and requirements
- **Market analysis**: Include all data points and projections
- **Legal documents**: Preserve exact language and terms

## Agent Distribution for Reports

Reports benefit from section-based distribution:

### Page Weights
- Cover/TOC pages: 0.5x
- Text-heavy pages: 1x
- Data table pages: 1.5x
- Chart/visual pages: 2x

### Example Distribution
```yaml
agent_distribution:
  agent_1:
    sections: ["Cover", "Executive Summary", "Introduction"]
    pages: [1-5]
    focus: "Front matter and context setting"
  agent_2:
    sections: ["Financial Analysis", "Market Data"]
    pages: [6-15]
    focus: "Data-heavy sections with tables and charts"
  agent_3:
    sections: ["Risk Factors", "Appendices"]
    pages: [16-25]
    focus: "Detailed text and supporting materials"
```

## Generation Steps for Reports

1. **Read ALL source materials** completely before starting
2. **Extract exact content** - copy verbatim where appropriate
3. **Call list_report_templates** to see available page formats
4. **Organize content** into logical sections maintaining source structure
5. **Preserve data integrity** - no rounding or approximation
6. **Use branded charts** that include titles and sources
7. **CRITICAL: Always end with agent_distribution YAML** for parallel generation

## REQUIRED: Agent Distribution YAML

**You MUST include this at the end of every report outline:**

```yaml
agent_distribution:
  agent_1:
    sections: ["Section names from your outline"]
    pages: [1-X]  # Actual page ranges (note: pages not slides)
  agent_2:
    sections: ["More section names"]
    pages: [X-Y]
  agent_3:
    sections: ["Final sections"]
    pages: [Y-Z]
```

This enables parallel agent execution for faster report generation!