const fs = require('fs');
const path = require('path');

class OutlineParser {
    constructor(projectPath) {
        this.projectPath = projectPath;
        this.outlinePath = path.join(projectPath, 'outline.md');
    }

    parse() {
        console.log('Parsing outline at:', this.outlinePath);
        
        if (!fs.existsSync(this.outlinePath)) {
            console.log('Outline not found!');
            return { sections: [], agentDistribution: null };
        }
        
        const content = fs.readFileSync(this.outlinePath, 'utf8');
        const lines = content.split('\n');
        console.log('Outline has', lines.length, 'lines');
        
        const sections = [];
        let currentSection = null;
        let agentDistribution = null;
        let inYamlBlock = false;
        let yamlContent = [];
        let foundAgentDistHeader = false;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // Check for YAML block start (with ```yaml)
            if (line.includes('```yaml') && !agentDistribution) {
                inYamlBlock = true;
                continue;
            }
            
            // Check for YAML block end
            if (inYamlBlock && line.includes('```')) {
                inYamlBlock = false;
                agentDistribution = this.parseYamlBlock(yamlContent);
                console.log('Found agent distribution in YAML block:', agentDistribution);
                yamlContent = [];
                continue;
            }
            
            // Collect YAML content in code block
            if (inYamlBlock) {
                yamlContent.push(line);
                continue;
            }
            
            // Check for plain text agent_distribution header
            if (line.trim() === '# agent_distribution' || line.includes('agent_distribution:')) {
                foundAgentDistHeader = true;
                // Collect remaining lines as YAML content
                for (let j = i + 1; j < lines.length; j++) {
                    if (lines[j].trim()) {
                        yamlContent.push(lines[j]);
                    }
                }
                agentDistribution = this.parseYamlBlock(yamlContent);
                console.log('Found agent distribution in plain text:', agentDistribution);
                break; // Stop processing since we found agent distribution
            }
            
            // Match section headers (handles both "slides" and "pages")
            const sectionMatch = line.match(/^#\s+(?:Section\s+(\d+):\s+)?(.+?)\s*\((?:slides?|pages?)\s+(\d+)(?:-(\d+))?\)/i);
            if (sectionMatch) {
                const [, sectionNum, title, startSlide, endSlide] = sectionMatch;
                currentSection = {
                    number: sectionNum ? parseInt(sectionNum) : sections.length + 1,
                    title: title.trim(),
                    startSlide: parseInt(startSlide),
                    endSlide: endSlide ? parseInt(endSlide) : parseInt(startSlide),
                    slides: []
                };
                sections.push(currentSection);
                console.log('Found section:', currentSection.title);
            }
            
            // Match individual slide/page entries
            if (currentSection && line.match(/^##\s+(?:Slide|Page)\s+\d+:/i)) {
                const slideMatch = line.match(/^##\s+(?:Slide|Page)\s+(\d+):\s+(.+)/i);
                if (slideMatch) {
                    currentSection.slides.push({
                        number: parseInt(slideMatch[1]),
                        title: slideMatch[2].trim()
                    });
                }
            }
        }
        
        return { sections, agentDistribution };
    }

    parseYamlBlock(yamlContent) {
        // Handle both formats: with or without agent_distribution: header
        const hasHeader = yamlContent.some(line => line.includes('agent_distribution:'));
        if (!hasHeader && !yamlContent.some(line => line.match(/^\s*agent_\d+:/))) {
            return null;
        }

        try {
            const agentDistribution = {};
            let currentAgent = null;
            
            yamlContent.forEach(yamlLine => {
                const agentMatch = yamlLine.match(/^\s*(agent_\d+):/);
                if (agentMatch) {
                    currentAgent = agentMatch[1];
                    agentDistribution[currentAgent] = { sections: [], slides: [] };
                } else if (currentAgent) {
                    // Handle sections
                    const sectionsMatch = yamlLine.match(/sections:\s*\[(.*)\]/);
                    if (sectionsMatch) {
                        const sectionNames = sectionsMatch[1]
                            .split(',')
                            .map(s => s.trim().replace(/['"]/g, ''));
                        agentDistribution[currentAgent].sections = sectionNames;
                    }
                    
                    // Handle slides (format: slides: [1-5])
                    const slidesMatch = yamlLine.match(/slides:\s*\[(\d+)-(\d+)\]/);
                    if (slidesMatch) {
                        agentDistribution[currentAgent].slideRange = {
                            start: parseInt(slidesMatch[1]),
                            end: parseInt(slidesMatch[2])
                        };
                    }
                    
                    // Handle pages (format: pages: [1-5])
                    const pagesMatch = yamlLine.match(/pages:\s*\[(\d+)-(\d+)\]/);
                    if (pagesMatch) {
                        agentDistribution[currentAgent].slideRange = {
                            start: parseInt(pagesMatch[1]),
                            end: parseInt(pagesMatch[2])
                        };
                    }
                }
            });
            
            return agentDistribution;
        } catch (err) {
            console.error('Error parsing agent distribution:', err);
            return null;
        }
    }
}

module.exports = OutlineParser;