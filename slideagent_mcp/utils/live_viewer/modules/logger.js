class Logger {
    constructor(prefix = 'LiveViewer') {
        this.prefix = prefix;
        this.colors = {
            reset: '\x1b[0m',
            bright: '\x1b[1m',
            dim: '\x1b[2m',
            red: '\x1b[31m',
            green: '\x1b[32m',
            yellow: '\x1b[33m',
            blue: '\x1b[34m',
            magenta: '\x1b[35m',
            cyan: '\x1b[36m'
        };
    }

    /**
     * Format timestamp
     */
    getTimestamp() {
        return new Date().toISOString().split('T')[1].split('.')[0];
    }

    /**
     * Format message with prefix and timestamp
     */
    formatMessage(level, message, data = null) {
        const timestamp = this.getTimestamp();
        const prefix = `[${timestamp}] [${this.prefix}] [${level}]`;
        
        if (data) {
            return `${prefix} ${message}\n${JSON.stringify(data, null, 2)}`;
        }
        return `${prefix} ${message}`;
    }

    /**
     * Log info message
     */
    info(message, data = null) {
        const formatted = this.formatMessage('INFO', message, data);
        console.log(`${this.colors.cyan}${formatted}${this.colors.reset}`);
    }

    /**
     * Log success message
     */
    success(message, data = null) {
        const formatted = this.formatMessage('SUCCESS', message, data);
        console.log(`${this.colors.green}${formatted}${this.colors.reset}`);
    }

    /**
     * Log warning message
     */
    warn(message, data = null) {
        const formatted = this.formatMessage('WARN', message, data);
        console.warn(`${this.colors.yellow}${formatted}${this.colors.reset}`);
    }

    /**
     * Log error message
     */
    error(message, error = null) {
        const formatted = this.formatMessage('ERROR', message);
        console.error(`${this.colors.red}${formatted}${this.colors.reset}`);
        
        if (error && error.stack) {
            console.error(`${this.colors.dim}${error.stack}${this.colors.reset}`);
        }
    }

    /**
     * Log server startup info
     */
    logServerStart(port, projectName, features) {
        console.log('\n' + '='.repeat(60));
        console.log(`${this.colors.bright}${this.colors.green}🚀 Live Viewer Server Started${this.colors.reset}`);
        console.log('='.repeat(60));
        console.log(`${this.colors.cyan}📁 Project:${this.colors.reset} ${projectName}`);
        console.log(`${this.colors.cyan}🌐 URL:${this.colors.reset} http://localhost:${port}`);
        console.log(`${this.colors.cyan}✨ Features:${this.colors.reset}`);
        features.forEach(feature => {
            console.log(`   • ${feature}`);
        });
        console.log('='.repeat(60) + '\n');
    }

    /**
     * Log section found during parsing
     */
    logSection(section) {
        this.info(`Found section: ${section.title} (slides ${section.startSlide}-${section.endSlide})`);
    }

    /**
     * Log agent distribution
     */
    logAgentDistribution(distribution) {
        if (!distribution) {
            this.info('No agent distribution found in outline');
            return;
        }
        
        this.success('Agent distribution detected:', distribution);
    }
}

module.exports = Logger;