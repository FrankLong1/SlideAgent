#!/usr/bin/env node
/**
 * Screenshotter for SlideAgent
 * Takes screenshots of slides and prepares them for AI visual analysis
 */

const { launchBrowser, injectCommonCSS, PagePool, waitForSlideReady } = require('./puppeteer_helper');
const cliProgress = require('cli-progress');
const fs = require('fs').promises;
const path = require('path');

// Concurrency helper
async function processWithConcurrency(items, limit, iteratorFn) {
    const ret = [];
    const executing = [];
    for (const [i, item] of items.entries()) {
        const p = Promise.resolve().then(() => iteratorFn(item, i));
        ret.push(p);
        const e = p.then(() => executing.splice(executing.indexOf(e), 1));
        executing.push(e);
        if (executing.length >= limit) {
            await Promise.race(executing);
        }
    }
    return Promise.all(ret);
}

class Screenshotter {
    constructor(projectPath) {
        this.projectPath = projectPath;
        this.slidesDir = path.join(projectPath, 'slides');
        this.validationDir = path.join(projectPath, 'validation');
        this.screenshotsDir = path.join(this.validationDir, 'screenshots');
    }

    async init() {
        // Ensure directories exist
        await fs.mkdir(this.screenshotsDir, { recursive: true });
        
        // Launch browser
        this.browser = await launchBrowser();
        
        // Initialize page pool with 8 pages
        this.pagePool = new PagePool(this.browser, 8);
        await this.pagePool.init();
    }

    async validateAllSlides() {
        try {
            // Step 1: Take all screenshots
            const slideFiles = await this.takeAllScreenshots();
            
            // Step 2: Analyze screenshots with AI
            console.log(`🤖 Analyzing ${slideFiles.length} screenshots with AI...`);
            const analysisResults = await this.analyzeWithAI(slideFiles);
            
            // Step 3: Save results
            await this.saveValidationResults(analysisResults);
            
            return analysisResults;
            
        } catch (error) {
            console.error('❌ AI validation failed:', error);
            throw error;
        }
    }

    async takeAllScreenshots() {
        const slideFiles = await fs.readdir(this.slidesDir);
        const htmlFiles = slideFiles.filter(file => file.endsWith('.html')).sort();
        
        console.log(`📸 Taking screenshots of ${htmlFiles.length} slides...`);

        // Create progress bar
        const progressBar = new cliProgress.SingleBar({
            format: '📸 Screenshots |{bar}| {percentage}% | {value}/{total} | {slide}',
            barCompleteChar: '█',
            barIncompleteChar: '░',
            hideCursor: true
        });
        
        progressBar.start(htmlFiles.length, 0, { slide: 'Starting...' });
        
        let completed = 0;
        const CONCURRENCY_LIMIT = 8; // Increased for better CPU utilization
        await processWithConcurrency(htmlFiles, CONCURRENCY_LIMIT, async slideFile => {
            await this.takeScreenshot(slideFile);
            completed++;
            progressBar.update(completed, { slide: slideFile });
        });
        
        progressBar.stop();
        console.log('✅ All screenshots captured!');

        return htmlFiles;
    }

    async takeScreenshot(slideFile) {
        const page = await this.pagePool.acquire();

        try {
            // Load slide with smart waiting
            const slidePath = path.join(this.slidesDir, slideFile);
            const slideUrl = `file://${path.resolve(slidePath)}`;
            await waitForSlideReady(page, slideUrl);

            // Inject common slide CSS
            await injectCommonCSS(page);

            // Take screenshot
            const screenshotPath = path.join(this.screenshotsDir, `${slideFile.replace('.html', '.png')}`);
            await page.screenshot({
                path: screenshotPath,
                fullPage: false,
                clip: { x: 0, y: 0, width: 1920, height: 1080 }
            });
            
        } finally {
            await this.pagePool.release(page);
        }
    }

    async analyzeWithAI(slideFiles) {
        const screenshotPaths = slideFiles.map(slide => 
            path.join(this.screenshotsDir, slide.replace('.html', '.png'))
        );
        
        console.log('📸 Screenshots ready for manual review:');
        screenshotPaths.forEach((path, i) => {
            console.log(`  ${i + 1}. ${slideFiles[i]} → ${path}`);
        });
        
        return {
            slides_analyzed: slideFiles.length,
            screenshots: screenshotPaths,
            message: 'Screenshots ready - review manually or with AI for visual issues'
        };
    }


    async saveValidationResults(results) {
        const reportPath = path.join(this.validationDir, 'ai_validation_report.json');
        await fs.writeFile(reportPath, JSON.stringify(results, null, 2));
        
        console.log(`📊 AI validation setup complete!`);
        console.log(`📋 Next: Run the AI analysis prompt with Claude Code`);
    }

    async close() {
        if (this.pagePool) {
            await this.pagePool.destroy();
        }
        if (this.browser) {
            await this.browser.close();
        }
    }
}

// CLI Usage
async function main() {
    const projectPath = process.argv[2];

    if (!projectPath) {
        console.error('Usage: node screenshotter.js <project-path>');
        console.error('Example: node screenshotter.js /path/to/projects/test-sections');
        process.exit(1);
    }
    
    const validator = new Screenshotter(projectPath);
    
    try {
        await validator.init();
        await validator.validateAllSlides();
    } catch (error) {
        console.error('❌ Validation failed:', error);
        process.exit(1);
    } finally {
        await validator.close();
    }
}

if (require.main === module) {
    main();
}

module.exports = Screenshotter;
