const fs = require('fs');
const path = require('path');
const config = require('./config');
const OutlineParser = require('./outline_parser');
const FileMonitor = require('./file_monitor');

class RouteHandler {
    constructor(projectName) {
        this.projectName = projectName;
        this.projectPath = config.paths.getProjectPath(projectName);
        this.slidesPath = config.paths.getSlidesPath(projectName);
        this.outlineParser = new OutlineParser(this.projectPath);
        this.fileMonitor = new FileMonitor(this.slidesPath);
    }

    /**
     * Handle API status endpoint
     */
    handleStatusRequest(res) {
        const { sections, agentDistribution } = this.outlineParser.parse();
        const status = this.buildProjectStatus(sections, agentDistribution);
        
        this.sendJsonResponse(res, status);
    }

    /**
     * Handle API slides endpoint
     */
    handleSlidesRequest(res) {
        const slides = this.fileMonitor.checkForUpdates();
        this.sendJsonResponse(res, slides);
    }

    /**
     * Handle slide HTML requests
     */
    handleSlideRequest(url, res) {
        const slideName = path.basename(url).split('?')[0];
        const slidePath = path.join(this.slidesPath, slideName);
        
        this.serveFile(slidePath, 'text/html', res);
    }

    /**
     * Handle static file requests (CSS, images, etc.)
     */
    handleStaticFileRequest(url, res) {
        const relativePath = this.extractRelativePath(url);
        const filePath = path.join(this.projectPath, relativePath);
        const contentType = this.getContentType(filePath);
        
        this.serveFile(filePath, contentType, res);
    }

    /**
     * Handle viewer HTML page
     */
    handleViewerRequest(res) {
        const templatePath = path.join(__dirname, '..', 'viewer_template.html');
        
        try {
            let html = fs.readFileSync(templatePath, 'utf8');
            // Replace project name placeholder
            html = html.replace(/{{PROJECT_NAME}}/g, this.projectName);
            
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(html);
        } catch (err) {
            this.sendError(res, 500, 'Failed to load viewer template');
        }
    }

    /**
     * Handle viewer assets (CSS and JS)
     */
    handleViewerAsset(filename, res) {
        const assetPath = path.join(__dirname, '..', filename);
        const contentType = this.getContentType(assetPath);
        
        this.serveFile(assetPath, contentType, res);
    }

    /**
     * Build project status object
     */
    buildProjectStatus(sections, agentDistribution) {
        const status = {
            sections: [],
            totalSlides: 0,
            completedSlides: 0,
            agentDistribution: agentDistribution
        };
        
        if (agentDistribution) {
            status.sections = this.buildAgentBasedSections(sections, agentDistribution, status);
        } else {
            status.sections = this.buildRegularSections(sections, status);
        }
        
        return status;
    }

    /**
     * Build sections grouped by agent
     */
    buildAgentBasedSections(sections, agentDistribution, status) {
        const agentSections = [];
        
        Object.keys(agentDistribution).forEach((agentKey, index) => {
            const agent = agentDistribution[agentKey];
            const agentNumber = index + 1;
            
            // Find matching sections
            const matchingSections = this.findAgentSections(sections, agent);
            const combinedTitle = agent.sections.join(', ');
            
            // Collect slides for this agent
            const agentSlides = this.collectAgentSlides(matchingSections, status);
            
            if (agentSlides.length > 0) {
                agentSections.push({
                    number: agentNumber,
                    title: combinedTitle,
                    slides: agentSlides,
                    isAgent: true
                });
            }
        });
        
        return agentSections;
    }

    /**
     * Build regular sections (no agent distribution)
     */
    buildRegularSections(sections, status) {
        return sections.map(section => {
            const sectionData = {
                number: section.number,
                title: section.title,
                slides: []
            };
            
            for (let slideNum = section.startSlide; slideNum <= section.endSlide; slideNum++) {
                const slideData = this.getSlideData(slideNum);
                sectionData.slides.push(slideData);
                
                status.totalSlides++;
                if (slideData.status === 'completed') {
                    status.completedSlides++;
                }
            }
            
            return sectionData;
        });
    }

    /**
     * Find sections assigned to an agent
     */
    findAgentSections(sections, agent) {
        let matchingSections = sections.filter(section => 
            agent.sections.some(sectionName => 
                section.title.toLowerCase().includes(sectionName.toLowerCase())
            )
        );
        
        // Fallback to slide range if no name matches
        if (matchingSections.length === 0 && agent.slideRange) {
            matchingSections = sections.filter(section => 
                section.startSlide >= agent.slideRange.start && 
                section.endSlide <= agent.slideRange.end
            );
        }
        
        return matchingSections;
    }

    /**
     * Collect slides for an agent
     */
    collectAgentSlides(sections, status) {
        const slides = [];
        
        for (const section of sections) {
            for (let slideNum = section.startSlide; slideNum <= section.endSlide; slideNum++) {
                const slideData = this.getSlideData(slideNum);
                slides.push(slideData);
                
                status.totalSlides++;
                if (slideData.status === 'completed') {
                    status.completedSlides++;
                }
            }
        }
        
        return slides;
    }

    /**
     * Get data for a specific slide
     */
    getSlideData(slideNumber) {
        const paddedNumber = String(slideNumber).padStart(2, '0');
        const fileName = `slide_${paddedNumber}.html`;
        const details = this.fileMonitor.getSlideDetails(fileName);
        
        return {
            number: slideNumber,
            file: fileName,
            status: details.status,
            modified: details.modifiedTime
        };
    }

    /**
     * Extract relative path from URL
     */
    extractRelativePath(url) {
        if (url.includes('/theme/')) {
            return 'theme' + url.split('/theme')[1];
        } else if (url.includes('/plots/')) {
            return 'plots' + url.split('/plots')[1];
        }
        return url;
    }

    /**
     * Get content type for a file
     */
    getContentType(filePath) {
        const ext = path.extname(filePath).toLowerCase();
        return config.contentTypes[ext] || 'application/octet-stream';
    }

    /**
     * Serve a file with proper headers
     */
    serveFile(filePath, contentType, res) {
        try {
            const content = fs.readFileSync(filePath);
            res.writeHead(200, { 
                'Content-Type': contentType,
                'Cache-Control': config.server.cacheControl
            });
            res.end(content);
        } catch (err) {
            const errorMessage = `File not found: ${path.basename(filePath)}`;
            this.sendError(res, 404, errorMessage);
        }
    }

    /**
     * Send JSON response
     */
    sendJsonResponse(res, data) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(data));
    }

    /**
     * Send error response
     */
    sendError(res, statusCode, message) {
        res.writeHead(statusCode);
        res.end(message);
    }
}

module.exports = RouteHandler;