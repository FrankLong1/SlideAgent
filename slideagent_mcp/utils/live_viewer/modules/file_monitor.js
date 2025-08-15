const fs = require('fs');
const path = require('path');

class FileMonitor {
    constructor(slidesPath) {
        this.slidesPath = slidesPath;
        this.fileModificationTimes = new Map();
    }

    /**
     * Check for changes in slide files
     * @param {number} maxSlideNumber - Maximum slide number to check (unbounded if not provided)
     * @returns {Array} Array of slide status objects
     */
    checkForUpdates(maxSlideNumber = 100) {
        const slideStatuses = [];
        
        // Check up to maxSlideNumber or until we find 5 consecutive missing slides
        let consecutiveMissing = 0;
        for (let slideNumber = 1; slideNumber <= maxSlideNumber && consecutiveMissing < 5; slideNumber++) {
            const slideStatus = this.getSlideStatus(slideNumber);
            if (!slideStatus.exists) {
                consecutiveMissing++;
            } else {
                consecutiveMissing = 0;
            }
            slideStatuses.push(slideStatus);
        }
        
        return slideStatuses;
    }

    /**
     * Get status for a single slide
     * @param {number} slideNumber - The slide number to check
     * @returns {Object} Slide status object
     */
    getSlideStatus(slideNumber) {
        const paddedNumber = String(slideNumber).padStart(2, '0');
        const fileName = `slide_${paddedNumber}.html`;
        const filePath = path.join(this.slidesPath, fileName);
        
        try {
            const stats = fs.statSync(filePath);
            const currentModTime = stats.mtime.getTime();
            const previousModTime = this.fileModificationTimes.get(fileName);
            
            // Update stored modification time
            this.fileModificationTimes.set(fileName, currentModTime);
            
            return {
                name: fileName,
                exists: true,
                modified: currentModTime,
                isNew: !previousModTime || previousModTime !== currentModTime
            };
        } catch (err) {
            // File doesn't exist yet
            return {
                name: fileName,
                exists: false,
                modified: null,
                isNew: false
            };
        }
    }

    /**
     * Get detailed status for a specific slide file
     * @param {string} fileName - The slide file name
     * @returns {Object} Detailed slide status
     */
    getSlideDetails(fileName) {
        const filePath = path.join(this.slidesPath, fileName);
        
        try {
            const stats = fs.statSync(filePath);
            return {
                exists: true,
                status: 'completed',
                modifiedTime: stats.mtime.getTime()
            };
        } catch (err) {
            return {
                exists: false,
                status: 'waiting',
                modifiedTime: null
            };
        }
    }

    /**
     * Clear cached modification times
     */
    clearCache() {
        this.fileModificationTimes.clear();
    }
}

module.exports = FileMonitor;