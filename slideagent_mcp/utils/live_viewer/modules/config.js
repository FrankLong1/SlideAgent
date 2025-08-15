const path = require('path');

module.exports = {
    // Server configuration
    server: {
        defaultPort: 8080,
        pollInterval: 500,  // milliseconds
        cacheControl: 'no-cache, no-store, must-revalidate'
    },
    
    // File paths
    paths: {
        getRootDir: () => path.join(__dirname, '..', '..', '..', '..'),
        getProjectPath: (projectName) => {
            const rootDir = module.exports.paths.getRootDir();
            return path.join(rootDir, 'user_projects', projectName);
        },
        getSlidesPath: (projectName) => {
            const projectPath = module.exports.paths.getProjectPath(projectName);
            return path.join(projectPath, 'slides');
        }
    },
    
    // Slide configuration
    slides: {
        dimensions: {
            width: 1920,
            height: 1080,
            thumbnailScale: 0.130208  // Scale factor for thumbnails
        }
    },
    
    // Content types mapping
    contentTypes: {
        '.css': 'text/css',
        '.html': 'text/html',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg': 'image/svg+xml',
        '.gif': 'image/gif'
    },
    
    // CORS headers
    cors: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
};