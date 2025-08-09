# {title}

## Agent Distribution
```yaml
agent_distribution:
  agent_1:
    sections: ["Introduction", "Analysis"]
    slides: [1-6]
  agent_2:
    sections: ["Results", "Implementation"]
    slides: [7-12]
  agent_3:
    sections: ["Next Steps", "Conclusion"]
    slides: [13-15]
```

## Section-Based Outline

# Section 1: Introduction (slides 1-2)
## Slide 1: Title Slide
- Template: 00_title_slide
- Content: {title}, {author}, Date

## Slide 2: Overview
- Template: 01_base_slide
- Content: Agenda and key objectives
- Charts needed: None

# Section 2: Analysis (slides 3-6)
## Slide 3: Market Analysis
- Template: 02_text_left_image_right
- Content: Key market insights
- Charts needed: market_trends.png

## Slide 4: Competitive Landscape
- Template: 08_grid_matrix
- Content: Competitor comparison matrix
- Charts needed: None

## Slide 5: Financial Analysis
- Template: 07_financial_data_table
- Content: Revenue and cost breakdown
- Charts needed: None

## Slide 6: Performance Metrics
- Template: 11_quadrants
- Content: Four key KPIs
- Charts needed: None

# Section 3: Results (slides 7-10)
## Slide 7: Section Divider
- Template: 06_section_divider
- Content: Key Results

## Slide 8: Growth Metrics
- Template: 04_full_image_slide
- Content: Growth chart visualization
- Charts needed: growth_chart.png

## Slide 9: Customer Feedback
- Template: 05_quote_slide
- Quote: Customer testimonial
- Attribution: Customer Name, Title

## Slide 10: ROI Analysis
- Template: 03_two_column_slide
- Content: Before/after comparison
- Charts needed: roi_comparison.png

# Section 4: Implementation (slides 11-12)
## Slide 11: Timeline
- Template: 10_timeline_process_flow
- Content: 6-month implementation plan
- Charts needed: None

## Slide 12: Process Flow
- Template: 12_value_chain_flow
- Content: End-to-end process
- Charts needed: None

# Section 5: Next Steps (slide 13)
## Slide 13: Action Items
- Template: 01_base_slide
- Content: Immediate next steps
- Charts needed: None

# Section 6: Conclusion (slides 14-15)
## Slide 14: Key Takeaways
- Template: 01_base_slide
- Content: Summary of main points
- Charts needed: None

## Slide 15: Thank You
- Template: 00_title_slide
- Content: Thank you slide with contact info

## Implementation Notes
- Place source materials in `input/`
- Charts will be generated in `plots/`
- Theme: {theme}
- Each section will be rendered by separate agents in parallel
- Individual slide HTML files will be created in `slides/` directory
- When assigning slides to agents, consider slide complexity—not just quantity. Simpler slides (e.g., title, base) can be grouped together, while more complex slides (e.g., tables) may warrant fewer per agent. Distribute work accordingly.