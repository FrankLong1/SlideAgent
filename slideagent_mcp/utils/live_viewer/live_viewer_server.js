#!/usr/bin/env node
/**
 * Live Viewer Server
 * Real-time slide preview with hot reload using modular architecture
 */

const http = require('http');
const { exec } = require('child_process');
const config = require('./modules/config');
const RouteHandler = require('./modules/routes');
const Logger = require('./modules/logger');

// Initialize logger
const logger = new Logger('LiveViewer');

// Parse command line arguments
const projectName = process.argv[2];
const port = process.argv[3] || config.server.defaultPort;

if (!projectName) {
    logger.error('Usage: node live_viewer_server.js <project-name> [port]');
    process.exit(1);
}

// Initialize route handler
const routeHandler = new RouteHandler(projectName);

/**
 * Main HTTP server
 */
const server = http.createServer((req, res) => {
    // Set CORS headers for all requests
    Object.entries(config.cors).forEach(([header, value]) => {
        res.setHeader(header, value);
    });

    // Handle OPTIONS requests for CORS
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    try {
        // Route the request to appropriate handler
        switch (true) {
            // API endpoints
            case req.url === '/api/status':
                routeHandler.handleStatusRequest(res);
                break;
                
            case req.url === '/api/slides':
                routeHandler.handleSlidesRequest(res);
                break;
                
            // Viewer assets
            case req.url === '/viewer_styles.css':
                routeHandler.handleViewerAsset('viewer_styles.css', res);
                break;
                
            case req.url === '/viewer_client.js':
                routeHandler.handleViewerAsset('viewer_client.js', res);
                break;
                
            // Slide content
            case /slide_\d+\.html/.test(req.url):
                routeHandler.handleSlideRequest(req.url, res);
                break;
                
            // Static files (theme, plots)
            case req.url.includes('/theme/') || req.url.includes('/plots/'):
                routeHandler.handleStaticFileRequest(req.url, res);
                break;
                
            // Main viewer page
            case req.url === '/' || req.url === '/viewer':
                routeHandler.handleViewerRequest(res);
                break;
                
            // 404 for everything else
            default:
                res.writeHead(404);
                res.end('Not found');
        }
    } catch (error) {
        logger.error('Request handling error', error);
        res.writeHead(500);
        res.end('Internal server error');
    }
});

/**
 * Start the server
 */
server.listen(port, () => {
    const features = [
        'Agent-based slide generation tracking',
        'Real-time progress monitoring',
        'Auto-refresh on file changes',
        'Modular architecture with clean separation of concerns'
    ];
    
    logger.logServerStart(port, projectName, features);
    
    // Auto-open in browser
    openBrowser(port);
});

/**
 * Open browser with platform-specific command
 */
function openBrowser(port) {
    const url = `http://localhost:${port}`;
    const platform = process.platform;
    
    const commands = {
        'darwin': `open ${url}`,
        'win32': `start ${url}`,
        'linux': `xdg-open ${url}`
    };
    
    const command = commands[platform] || commands['linux'];
    
    exec(command, (err) => {
        if (!err) {
            logger.success(`Browser opened at ${url}`);
        } else {
            logger.warn('Could not auto-open browser', err);
        }
    });
}

/**
 * Handle graceful shutdown
 */
process.on('SIGINT', () => {
    logger.info('Shutting down viewer server...');
    server.close(() => {
        logger.success('Server closed gracefully');
        process.exit(0);
    });
});

/**
 * Handle uncaught errors
 */
process.on('uncaughtException', (error) => {
    logger.error('Uncaught exception', error);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    logger.error('Unhandled rejection at:', promise);
    logger.error('Reason:', reason);
});