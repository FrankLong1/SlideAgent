#!/usr/bin/env node
/**
 * Live Viewer Server - Real-time slide preview with hot reload
 * 
 * Serves SlideAgent project slides with automatic browser refresh
 * when files change. Used for development and presentation preview.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = 8080;

// Parse command line arguments
const projectName = process.argv[2];
if (!projectName) {
    console.error('Usage: node live_viewer_server.js <project-name>');
    process.exit(1);
}

// Calculate paths - we're in slideagent_mcp/utils/, need to go up to root
const ROOT_DIR = path.join(__dirname, '..', '..');  // SlideAgent root (from utils/ up to SlideAgent root)
const projectPath = path.join(ROOT_DIR, 'user_projects', projectName);
const slidesPath = path.join(projectPath, 'slides');

console.log('ROOT_DIR:', ROOT_DIR);
console.log('projectPath:', projectPath);
console.log('slidesPath:', slidesPath);

// Track slide modifications and sections
const slideModTimes = new Map();
const sectionQueues = new Map();

// Parse outline to get section info and agent distribution
function parseOutline() {
    const outlinePath = path.join(projectPath, 'outline.md');
    console.log('Parsing outline at:', outlinePath);
    if (!fs.existsSync(outlinePath)) {
        console.log('Outline not found!');
        return { sections: [], agentDistribution: null };
    }
    
    const content = fs.readFileSync(outlinePath, 'utf8');
    const lines = content.split('\n');
    console.log('Outline has', lines.length, 'lines');
    const sections = [];
    let currentSection = null;
    let agentDistribution = null;
    let inYamlBlock = false;
    let yamlContent = [];
    
    for (const line of lines) {
        // Check for YAML block start
        if (line.includes('```yaml') && !agentDistribution) {
            inYamlBlock = true;
            continue;
        }
        
        // Check for YAML block end
        if (inYamlBlock && line.includes('```')) {
            inYamlBlock = false;
            // Parse the YAML content
            const yamlText = yamlContent.join('\n');
            if (yamlText.includes('agent_distribution:')) {
                try {
                    // Simple YAML parsing for agent_distribution
                    agentDistribution = {};
                    let currentAgent = null;
                    
                    yamlContent.forEach(yamlLine => {
                        const agentMatch = yamlLine.match(/^\s*(agent_\d+):/);
                        if (agentMatch) {
                            currentAgent = agentMatch[1];
                            agentDistribution[currentAgent] = { sections: [], slides: [] };
                        } else if (currentAgent) {
                            const sectionsMatch = yamlLine.match(/sections:\s*\[(.*)\]/);
                            if (sectionsMatch) {
                                // Parse section names from ["Section1", "Section2"] format
                                const sectionNames = sectionsMatch[1]
                                    .split(',')
                                    .map(s => s.trim().replace(/['"]/g, ''));
                                agentDistribution[currentAgent].sections = sectionNames;
                            }
                            const slidesMatch = yamlLine.match(/slides:\s*\[(\d+)-(\d+)\]/);
                            if (slidesMatch) {
                                agentDistribution[currentAgent].slideRange = {
                                    start: parseInt(slidesMatch[1]),
                                    end: parseInt(slidesMatch[2])
                                };
                            }
                        }
                    });
                } catch (err) {
                    console.error('Error parsing agent distribution:', err);
                }
            }
            console.log('Found agent distribution:', agentDistribution);
            yamlContent = [];
            continue;
        }
        
        // Collect YAML content
        if (inYamlBlock) {
            yamlContent.push(line);
            continue;
        }
        
        // Match section headers like "# Section 1: Introduction (slides 1-2)"
        const sectionMatch = line.match(/^#\s+Section\s+(\d+):\s+(.+?)\s*\(slides?\s+(\d+)(?:-(\d+))?\)/i);
        if (sectionMatch) {
            const [, sectionNum, title, startSlide, endSlide] = sectionMatch;
            currentSection = {
                number: parseInt(sectionNum),
                title: title.trim(),
                startSlide: parseInt(startSlide),
                endSlide: endSlide ? parseInt(endSlide) : parseInt(startSlide),
                slides: []
            };
            sections.push(currentSection);
            console.log('Found section:', currentSection.title);
        }
        
        // Match individual slide entries
        if (currentSection && line.match(/^##\s+Slide\s+\d+:/)) {
            const slideMatch = line.match(/^##\s+Slide\s+(\d+):\s+(.+)/);
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

// Create HTTP server
const server = http.createServer((req, res) => {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // Note: CSS and image files are now served through the project directory handler below

    // API endpoint to get sections and slide status
    if (req.url === '/api/status') {
        const { sections, agentDistribution } = parseOutline();
        const status = {
            sections: [],
            totalSlides: 0,
            completedSlides: 0,
            agentDistribution: agentDistribution
        };
        
        // If we have agent distribution, group sections by agent
        if (agentDistribution) {
            // Create agent-based groups
            Object.keys(agentDistribution).forEach((agentKey, index) => {
                const agent = agentDistribution[agentKey];
                const agentNumber = index + 1;
                
                // Collect all sections for this agent
                const agentSections = sections.filter(section => 
                    agent.sections.some(sectionName => 
                        section.title.toLowerCase().includes(sectionName.toLowerCase())
                    )
                );
                
                // If no sections matched by name, use slide range
                if (agentSections.length === 0 && agent.slideRange) {
                    agentSections.push(...sections.filter(section => 
                        section.startSlide >= agent.slideRange.start && 
                        section.endSlide <= agent.slideRange.end
                    ));
                }
                
                // Create combined title for this agent
                const combinedTitle = agent.sections.join(', ');
                
                // Collect all slides for this agent
                const agentSlides = [];
                for (const section of agentSections) {
                    for (let i = section.startSlide; i <= section.endSlide; i++) {
                        const slideNum = String(i).padStart(2, '0');
                        const slideFile = `slide_${slideNum}.html`;
                        const slidePath = path.join(slidesPath, slideFile);
                        
                        let slideStatus = 'waiting';
                        let modTime = null;
                        
                        try {
                            const stats = fs.statSync(slidePath);
                            slideStatus = 'completed';
                            modTime = stats.mtime.getTime();
                            status.completedSlides++;
                        } catch (err) {
                            // File doesn't exist yet
                        }
                        
                        agentSlides.push({
                            number: i,
                            file: slideFile,
                            status: slideStatus,
                            modified: modTime
                        });
                        
                        status.totalSlides++;
                    }
                }
                
                if (agentSlides.length > 0) {
                    status.sections.push({
                        number: agentNumber,
                        title: combinedTitle,
                        slides: agentSlides,
                        isAgent: true
                    });
                }
            });
        } else {
            // Fall back to section-based display if no agent distribution
            for (const section of sections) {
                const sectionStatus = {
                    number: section.number,
                    title: section.title,
                    slides: []
                };
                
                for (let i = section.startSlide; i <= section.endSlide; i++) {
                    const slideNum = String(i).padStart(2, '0');
                    const slideFile = `slide_${slideNum}.html`;
                    const slidePath = path.join(slidesPath, slideFile);
                    
                    let slideStatus = 'waiting';
                    let modTime = null;
                    
                    try {
                        const stats = fs.statSync(slidePath);
                        slideStatus = 'completed';
                        modTime = stats.mtime.getTime();
                        status.completedSlides++;
                    } catch (err) {
                        // File doesn't exist yet
                    }
                    
                    sectionStatus.slides.push({
                        number: i,
                        file: slideFile,
                        status: slideStatus,
                        modified: modTime
                    });
                    
                    status.totalSlides++;
                }
                
                status.sections.push(sectionStatus);
            }
        }
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(status));
        return;
    }

    // API endpoint to check for slide updates
    if (req.url === '/api/slides') {
        const slides = [];
        
        try {
            // Check for slides 1-20 (typical max)
            for (let i = 1; i <= 20; i++) {
                const slideNum = String(i).padStart(2, '0');
                const slideFile = `slide_${slideNum}.html`;
                const slidePath = path.join(slidesPath, slideFile);
                
                try {
                    const stats = fs.statSync(slidePath);
                    const prevModTime = slideModTimes.get(slideFile);
                    const currentModTime = stats.mtime.getTime();
                    
                    slides.push({
                        name: slideFile,
                        exists: true,
                        modified: currentModTime,
                        isNew: !prevModTime || prevModTime !== currentModTime
                    });
                    
                    slideModTimes.set(slideFile, currentModTime);
                } catch (err) {
                    // File doesn't exist yet
                    slides.push({
                        name: slideFile,
                        exists: false,
                        modified: null,
                        isNew: false
                    });
                }
            }
        } catch (err) {
            console.error('Error reading slides:', err);
        }
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(slides));
        return;
    }

    // Serve slide content
    if (req.url.match(/slide_\d+\.html/)) {
        const slideName = path.basename(req.url).split('?')[0];
        const slidePath = path.join(slidesPath, slideName);
        
        try {
            const content = fs.readFileSync(slidePath, 'utf8');
            res.writeHead(200, { 
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            });
            res.end(content);
        } catch (err) {
            res.writeHead(404);
            res.end('Slide not found');
        }
        return;
    }
    
    // Serve any file from the project directory (theme files, plots, etc)
    // This handles all relative paths from slides like ../theme/base.css
    if (req.url.includes('/theme/') || req.url.includes('/plots/')) {
        // Extract the relative path part (theme/base.css or plots/chart.png)
        let relativePath = req.url;
        if (relativePath.includes('/theme/')) {
            relativePath = 'theme' + relativePath.split('/theme')[1];
        } else if (relativePath.includes('/plots/')) {
            relativePath = 'plots' + relativePath.split('/plots')[1];
        }
        
        const filePath = path.join(projectPath, relativePath);
        
        try {
            const content = fs.readFileSync(filePath);
            
            // Determine content type
            const ext = path.extname(filePath).toLowerCase();
            let contentType = 'application/octet-stream';
            if (ext === '.css') contentType = 'text/css';
            else if (ext === '.png') contentType = 'image/png';
            else if (ext === '.jpg' || ext === '.jpeg') contentType = 'image/jpeg';
            else if (ext === '.svg') contentType = 'image/svg+xml';
            else if (ext === '.gif') contentType = 'image/gif';
            
            res.writeHead(200, { 
                'Content-Type': contentType,
                'Cache-Control': 'no-cache'
            });
            res.end(content);
        } catch (err) {
            res.writeHead(404);
            res.end('File not found: ' + relativePath);
        }
        return;
    }

    // Serve files from project directory (plots, theme files, etc)
    if (req.url.startsWith('/user_projects/')) {
        const filePath = path.join(ROOT_DIR, req.url.substring(1));
        try {
            const content = fs.readFileSync(filePath);
            res.writeHead(200, { 
                'Cache-Control': 'no-cache'
            });
            res.end(content);
        } catch (err) {
            res.writeHead(404);
            res.end('File not found');
        }
        return;
    }

    // Serve the enhanced viewer HTML
    if (req.url === '/' || req.url === '/viewer') {
        const viewerHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${projectName} - Live Generation Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #1a1a2e;
            min-height: 100vh;
            color: #eee;
        }

        #viewer-header {
            background: rgba(22, 22, 40, 0.95);
            padding: 20px 30px;
            border-bottom: 2px solid rgba(102, 126, 234, 0.3);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-content {
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stats {
            display: flex;
            gap: 30px;
            font-size: 14px;
            color: #aaa;
        }

        .stat {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .stat-value {
            font-weight: 600;
            color: #fff;
        }

        #main-container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px 20px;
        }

        .progress-overview {
            background: rgba(40, 40, 60, 0.6);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }

        .progress-bar {
            height: 30px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
        }

        .sections-container {
            margin-bottom: 40px;
        }

        .section-row {
            background: rgba(40, 40, 60, 0.4);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .section-row:hover {
            background: rgba(40, 40, 60, 0.6);
            border-color: rgba(102, 126, 234, 0.4);
        }

        .section-header {
            padding: 15px 20px;
            background: rgba(102, 126, 234, 0.1);
            border-bottom: 1px solid rgba(102, 126, 234, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .section-title {
            font-size: 13px;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.7);
            font-style: italic;
        }

        .section-progress {
            background: rgba(102, 126, 234, 0.2);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .slides-row {
            display: flex;
            gap: 15px;
            padding: 20px;
            overflow-x: auto;
            min-height: 200px;
            align-items: center;
        }

        .slides-row::-webkit-scrollbar {
            height: 8px;
        }

        .slides-row::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }

        .slides-row::-webkit-scrollbar-thumb {
            background: rgba(102, 126, 234, 0.5);
            border-radius: 4px;
        }

        .slide-container {
            flex: 0 0 250px;
            height: 140px;
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .slide-container.waiting {
            background: rgba(0, 0, 0, 0.3);
            border: 2px dashed rgba(102, 126, 234, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }

        .slide-container.waiting .waiting-number {
            font-size: 24px;
            color: rgba(102, 126, 234, 0.5);
            font-weight: 600;
            margin-bottom: 5px;
        }

        .slide-container.waiting .waiting-text {
            font-size: 11px;
            color: rgba(102, 126, 234, 0.4);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .slide-container.completed {
            background: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .slide-container.completed:hover {
            transform: translateY(-4px) scale(1.05);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        }

        .slide-container.new-slide {
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .slide-number-overlay {
            position: absolute;
            top: 5px;
            left: 5px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            z-index: 10;
        }

        .slide-iframe {
            width: 1920px;
            height: 1080px;
            border: none;
            transform: scale(0.130208);
            transform-origin: top left;
            pointer-events: none;
        }

        .no-sections {
            text-align: center;
            padding: 60px 20px;
            color: rgba(102, 126, 234, 0.6);
        }

        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(102, 126, 234, 0.1);
            padding: 8px 16px;
            border-radius: 20px;
            color: rgba(102, 126, 234, 0.8);
            font-size: 14px;
            margin-top: 20px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }

        .section-label {
            font-size: 18px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #fff;
            margin-bottom: 8px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
    </style>
</head>
<body>
    <header id="viewer-header">
        <div class="header-content">
            <h1>${projectName} - Live Generation</h1>
            <div class="stats">
                <div class="stat">
                    <span>Progress:</span>
                    <span class="stat-value" id="slide-count">0/0</span>
                </div>
                <div class="stat">
                    <span>Agents:</span>
                    <span class="stat-value" id="section-count">0</span>
                </div>
                <div class="stat">
                    <span>Last Update:</span>
                    <span class="stat-value" id="last-update">--</span>
                </div>
            </div>
        </div>
    </header>

    <div id="main-container">
        <div class="progress-overview">
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: 0%">
                    0%
                </div>
            </div>
        </div>

        <div class="sections-container" id="sections-container">
            <div class="no-sections" id="no-sections">
                <div style="font-size: 48px; margin-bottom: 20px;">⏳</div>
                <div style="font-size: 20px; margin-bottom: 10px;">Waiting for agents to start...</div>
                <div class="status-indicator">
                    <span class="status-dot"></span>
                    <span>Viewer Active - Monitoring for slides</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        class LiveViewer {
            constructor() {
                this.sections = [];
                this.slideElements = new Map();
                this.init();
            }

            async init() {
                await this.updateStatus();
                setInterval(() => this.updateStatus(), 500);
            }

            async updateStatus() {
                try {
                    const response = await fetch('/api/status');
                    const status = await response.json();
                    
                    this.sections = status.sections;
                    this.renderSections();
                    this.updateProgress(status.completedSlides, status.totalSlides);
                    
                    // Update stats
                    document.getElementById('slide-count').textContent = 
                        status.completedSlides + '/' + status.totalSlides;
                    document.getElementById('section-count').textContent = 
                        status.sections.length;
                    document.getElementById('last-update').textContent = 
                        new Date().toLocaleTimeString();
                    
                    // Hide no-sections message if we have sections
                    if (status.sections.length > 0) {
                        document.getElementById('no-sections').style.display = 'none';
                    }
                } catch (err) {
                    console.error('Error updating status:', err);
                }
            }

            renderSections() {
                const container = document.getElementById('sections-container');
                
                this.sections.forEach(section => {
                    let sectionRow = document.getElementById(\`section-\${section.number}\`);
                    
                    if (!sectionRow) {
                        // Create new section row
                        sectionRow = document.createElement('div');
                        sectionRow.className = 'section-row';
                        sectionRow.id = \`section-\${section.number}\`;
                        
                        const completed = section.slides.filter(s => s.status === 'completed').length;
                        const total = section.slides.length;
                        
                        const labelText = section.isAgent ? 
                            \`🤖 AI Agent \${section.number}\` : 
                            \`🤖 AI Analyst \${section.number}\`;
                        const titleText = section.isAgent ? 
                            \`Working on "\${section.title}" Sections\` : 
                            \`Working on "\${section.title}" Section\`;
                        
                        sectionRow.innerHTML = \`
                            <div class="section-header">
                                <div>
                                    <div class="section-label">\${labelText}</div>
                                    <div class="section-title">\${titleText}</div>
                                </div>
                                <div class="section-progress" id="section-progress-\${section.number}">
                                    \${completed}/\${total} slides
                                </div>
                            </div>
                            <div class="slides-row" id="slides-row-\${section.number}">
                                <!-- Slides will be added here -->
                            </div>
                        \`;
                        
                        container.appendChild(sectionRow);
                    } else {
                        // Update progress
                        const completed = section.slides.filter(s => s.status === 'completed').length;
                        const total = section.slides.length;
                        const progressEl = document.getElementById(\`section-progress-\${section.number}\`);
                        if (progressEl) {
                            progressEl.textContent = \`\${completed}/\${total} slides\`;
                        }
                    }
                    
                    // Render slides for this section
                    this.renderSectionSlides(section);
                });
            }

            renderSectionSlides(section) {
                const slidesRow = document.getElementById(\`slides-row-\${section.number}\`);
                if (!slidesRow) return;
                
                section.slides.forEach(slide => {
                    const slideId = \`slide-\${slide.file}\`;
                    let slideEl = this.slideElements.get(slideId);
                    
                    if (!slideEl) {
                        // Create new slide element
                        slideEl = document.createElement('div');
                        slideEl.className = \`slide-container \${slide.status}\`;
                        slideEl.id = slideId;
                        
                        if (slide.status === 'waiting') {
                            slideEl.innerHTML = \`
                                <div class="waiting-number">\${slide.number}</div>
                                <div class="waiting-text">Waiting</div>
                            \`;
                        } else if (slide.status === 'completed') {
                            slideEl.className += ' new-slide';
                            slideEl.innerHTML = \`
                                <div class="slide-number-overlay">Slide \${slide.number}</div>
                                <iframe class="slide-iframe" src="/\${slide.file}?t=\${Date.now()}"></iframe>
                            \`;
                            slideEl.onclick = () => window.open(\`/\${slide.file}\`, '_blank');
                        }
                        
                        slidesRow.appendChild(slideEl);
                        this.slideElements.set(slideId, slideEl);
                    } else if (slide.status === 'completed' && slideEl.classList.contains('waiting')) {
                        // Update from waiting to completed
                        slideEl.className = 'slide-container completed new-slide';
                        slideEl.innerHTML = \`
                            <div class="slide-number-overlay">Slide \${slide.number}</div>
                            <iframe class="slide-iframe" src="/\${slide.file}?t=\${Date.now()}"></iframe>
                        \`;
                        slideEl.onclick = () => window.open(\`/\${slide.file}\`, '_blank');
                        
                        // Scroll the row to show the new slide
                        slidesRow.scrollLeft = slideEl.offsetLeft - 20;
                    }
                });
            }

            updateProgress(completed, total) {
                const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
                const fill = document.getElementById('progress-fill');
                fill.style.width = percentage + '%';
                fill.textContent = percentage + '%';
            }
        }

        const viewer = new LiveViewer();
    </script>
</body>
</html>`;
        
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(viewerHtml);
        return;
    }

    // Default 404
    res.writeHead(404);
    res.end('Not found');
});

server.listen(PORT, () => {
    console.log(`🚀 Live viewer server running at http://localhost:${PORT}`);
    console.log(`📁 Project: ${projectName}`);
    console.log(`📂 Slides path: ${slidesPath}`);
    console.log(`\n✨ Features:`);
    console.log(`   - Section-based queue visualization`);
    console.log(`   - Auto-refresh on file changes`);
    console.log(`   - CSS and assets properly served`);
    console.log(`   - Progress tracking per agent/section`);
    
    // Auto-open in browser
    const url = `http://localhost:${PORT}`;
    const platform = process.platform;
    const command = platform === 'darwin' ? `open ${url}` :
                   platform === 'win32' ? `start ${url}` :
                   `xdg-open ${url}`;
    
    exec(command, (err) => {
        if (!err) {
            console.log(`\n🌐 Opened browser at ${url}`);
        }
    });
});

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down viewer server...');
    server.close(() => {
        process.exit(0);
    });
});