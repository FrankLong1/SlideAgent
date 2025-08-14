#!/usr/bin/env node
/**
 * PDF Generator - High-quality PDF export for SlideAgent presentations
 * 
 * Converts HTML slides to PDF using Chromium headless browser.
 * Handles 16:9 aspect ratio for slides and 8.5x11 for reports.
 */

const puppeteer = require('puppeteer');
const cliProgress = require('cli-progress');
const path = require('path');
const fs = require('fs');
const { PDFDocument: PDFLib } = require('pdf-lib');
const http = require('http');
const express = require('express');

// Common CSS to inject for consistent rendering
const SLIDE_CSS = `
    body {
        background: white !important;
        padding: 0 !important;
        margin: 0 !important;
        display: block !important;
        min-height: auto !important;
        transform: none !important;
    }
    .slide, section.slide, div.slide {
        width: 1920px !important;
        height: 1080px !important;
        margin: 0 !important;
        box-shadow: none !important;
        border: none !important;
        overflow: hidden !important;
    }
`;

const REPORT_CSS = `
    @page {
        size: 8.5in 11in !important;
        margin: 0 !important;
    }
    body {
        background: white !important;
        padding: 0 !important;
        margin: 0 !important;
        display: block !important;
        min-height: auto !important;
        transform: none !important;
    }
    .report-page {
        width: 8.5in !important;
        height: 11in !important;
        margin: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        border: none !important;
        overflow: hidden !important;
        position: relative !important;
    }
`;

// Launch browser with optimized settings
async function launchBrowser() {
    return puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials'
        ]
    });
}

// Start a local Express server to serve the project files
async function startLocalServer(projectDir) {
    const app = express();
    const port = await getAvailablePort(9000);
    
    // Serve static files from project directory
    app.use(express.static(projectDir, {
        setHeaders: (res, path) => {
            // Set proper MIME types
            if (path.endsWith('.css')) {
                res.setHeader('Content-Type', 'text/css');
            } else if (path.endsWith('.js')) {
                res.setHeader('Content-Type', 'application/javascript');
            } else if (path.endsWith('.png')) {
                res.setHeader('Content-Type', 'image/png');
            } else if (path.endsWith('.jpg') || path.endsWith('.jpeg')) {
                res.setHeader('Content-Type', 'image/jpeg');
            } else if (path.endsWith('.svg')) {
                res.setHeader('Content-Type', 'image/svg+xml');
            }
        }
    }));
    
    // Also serve theme files from parent directory
    app.use('/theme', express.static(path.join(projectDir, 'theme')));
    
    return new Promise((resolve) => {
        const server = app.listen(port, () => {
            console.log(`🌐 Local server started on port ${port}`);
            resolve({ server, port });
        });
    });
}

// Get an available port
async function getAvailablePort(startPort = 9000) {
    return new Promise((resolve) => {
        const server = http.createServer();
        server.listen(startPort, () => {
            const port = server.address().port;
            server.close(() => resolve(port));
        });
        server.on('error', () => {
            resolve(getAvailablePort(startPort + 1));
        });
    });
}

// Page pool for concurrent processing
class PagePool {
    constructor(browser, size = 8, format = 'slides') {
        this.browser = browser;
        this.size = size;
        this.format = format;
        this.pages = [];
        this.available = [];
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        this.initialized = true;
        
        const viewport = this.format === 'report' 
            ? { width: 1275, height: 1650, deviceScaleFactor: 1 }  // 8.5x11 at 150 DPI
            : { width: 1920, height: 1080 };  // 16:9 for slides
        
        for (let i = 0; i < this.size; i++) {
            const page = await this.browser.newPage();
            await page.setViewport(viewport);
            this.pages.push(page);
            this.available.push(page);
        }
    }

    async acquire() {
        if (!this.initialized) await this.init();
        
        while (this.available.length === 0) {
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        return this.available.pop();
    }

    async release(page) {
        try {
            await page.goto('about:blank', { waitUntil: 'domcontentloaded' });
        } catch (e) {
            const viewport = this.format === 'report' 
                ? { width: 1275, height: 1650, deviceScaleFactor: 1 }  // 8.5x11 at 150 DPI
                : { width: 1920, height: 1080 };  // 16:9 for slides
            
            const newPage = await this.browser.newPage();
            await newPage.setViewport(viewport);
            page = newPage;
        }
        
        this.available.push(page);
    }

    async destroy() {
        for (const page of this.pages) {
            try {
                await page.close();
            } catch (e) {
                // Page already closed
            }
        }
        this.pages = [];
        this.available = [];
        this.initialized = false;
    }
}

// Run async operations with concurrency limit
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

// Wait for slide to be ready
async function waitForSlideReady(page, slideUrl) {
    await page.goto(slideUrl, { 
        waitUntil: ['domcontentloaded', 'networkidle0'],
        timeout: 30000 
    });
    
    // Wait for content to be ready
    try {
        await page.waitForFunction(() => {
            if (document.readyState !== 'complete') return false;
            
            const images = document.querySelectorAll('img');
            for (let img of images) {
                if (!img.complete) return false;
            }
            
            // Check for background images in CSS
            const elements = document.querySelectorAll('*');
            for (let el of elements) {
                const style = window.getComputedStyle(el);
                const bgImage = style.backgroundImage;
                if (bgImage && bgImage !== 'none' && bgImage.includes('url')) {
                    // Give background images time to load
                    return true; // We'll rely on networkidle0 for these
                }
            }
            
            if (document.fonts && document.fonts.status === 'loading') return false;
            
            const slide = document.querySelector('.slide, section, div[class*="slide"]');
            if (!slide) {
                return document.body !== null;
            }
            
            return true;
        }, { timeout: 5000 });
    } catch (e) {
        console.warn('Warning: Slide readiness check timed out, continuing anyway');
    }
    
    // Extra wait for background images to fully render
    await new Promise(resolve => setTimeout(resolve, 500));
}

// Main PDF generation function using HTTP server
async function generatePDFWithServer(htmlDir, outputPath = null, format = 'slides') {
    // Find HTML files based on format
    let htmlFiles;
    if (format === 'report') {
        // For reports, find report_*.html files
        htmlFiles = fs.readdirSync(htmlDir)
            .filter(file => file.match(/^report.*\.html$/))
            .sort((a, b) => {
                // Try to extract numbers for sorting
                const numA = a.match(/\d+/) ? parseInt(a.match(/\d+/)[0]) : 999;
                const numB = b.match(/\d+/) ? parseInt(b.match(/\d+/)[0]) : 999;
                return numA - numB;
            });
    } else {
        // For slides, find slide_*.html files
        htmlFiles = fs.readdirSync(htmlDir)
            .filter(file => file.match(/^slide_\d+\.html$/))
            .sort((a, b) => {
                const numA = parseInt(a.match(/\d+/)[0]);
                const numB = parseInt(b.match(/\d+/)[0]);
                return numA - numB;
            });
    }
    
    const htmlFilesList = htmlFiles;

    if (htmlFilesList.length === 0) {
        console.error(`Error: No HTML files found in ${htmlDir}`);
        process.exit(1);
    }

    console.log(`📑 Found ${htmlFilesList.length} ${format === 'report' ? 'report pages' : 'slides'} to process`);

    // Generate output path if not provided
    if (!outputPath) {
        const projectName = path.basename(path.dirname(htmlDir));
        outputPath = path.join(path.dirname(htmlDir), `${projectName}.pdf`);
    }

    console.log(`📝 Generating PDF from ${htmlFilesList.length} ${format === 'report' ? 'report pages' : 'slides'} (${format} format)`);
    console.log(`📁 Output will be saved to: ${outputPath}`);

    // Start local server for the project
    const projectDir = path.dirname(htmlDir);
    const { server, port } = await startLocalServer(projectDir);

    const browser = await launchBrowser();
    const pagePool = new PagePool(browser, 8, format);
    await pagePool.init();

    // Create progress bar
    const progressBar = new cliProgress.SingleBar({
        format: '🔑 PDF Generation |{bar}| {percentage}% | {value}/{total} | {slide}',
        barCompleteChar: '█',
        barIncompleteChar: '░',
        hideCursor: true
    });
    
    progressBar.start(htmlFilesList.length, 0, { slide: 'Starting...' });

    try {
        const pdfBuffers = new Array(htmlFilesList.length);
        let completed = 0;

        // Process HTML files concurrently
        const CONCURRENCY_LIMIT = 8;
        await processWithConcurrency(htmlFilesList, CONCURRENCY_LIMIT, async (htmlFile, i) => {
            const page = await pagePool.acquire();
            
            try {
                // Navigate to HTML file via HTTP server
                const dirName = path.basename(htmlDir);
                const htmlUrl = `http://localhost:${port}/${dirName}/${htmlFile}`;
                await waitForSlideReady(page, htmlUrl);
                
                // Inject override CSS for PDF based on format
                await page.addStyleTag({ content: format === 'report' ? REPORT_CSS : SLIDE_CSS });

                // Generate PDF with appropriate dimensions
                const pdfOptions = format === 'report' ? {
                    width: '8.5in',
                    height: '11in',
                    printBackground: true,
                    preferCSSPageSize: false,  // Don't use CSS page size, use exact dimensions
                    margin: {
                        top: 0,
                        right: 0,
                        bottom: 0,
                        left: 0
                    },
                    displayHeaderFooter: false,
                    scale: 1.0
                } : {
                    width: '16in',
                    height: '9in',
                    printBackground: true,
                    preferCSSPageSize: false,
                    margin: {
                        top: 0,
                        right: 0,
                        bottom: 0,
                        left: 0
                    },
                    displayHeaderFooter: false,
                    scale: 1.0
                };
                
                const pdfBuffer = await page.pdf(pdfOptions);

                pdfBuffers[i] = pdfBuffer;
                completed++;
                progressBar.update(completed, { slide: htmlFile });
            } finally {
                await pagePool.release(page);
            }
        });
        
        progressBar.stop();

        // Merge all PDFs into one
        console.log(`🔀 Merging ${pdfBuffers.length} ${format === 'report' ? 'pages' : 'slides'} into single PDF...`);
        const mergedPdf = await PDFLib.create();
        
        for (const pdfBuffer of pdfBuffers) {
            const pdf = await PDFLib.load(pdfBuffer);
            const pages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
            pages.forEach(page => mergedPdf.addPage(page));
        }

        const mergedPdfBytes = await mergedPdf.save();
        fs.writeFileSync(outputPath, mergedPdfBytes);

        console.log(`✅ PDF generated successfully: ${outputPath}`);
        
        const stats = fs.statSync(outputPath);
        const fileSizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
        console.log(`📄 File size: ${fileSizeInMB} MB`);

    } catch (error) {
        console.error('❌ Error generating PDF:', error.message);
        process.exit(1);
    } finally {
        await pagePool.destroy();
        await browser.close();
        server.close();
        console.log('🛑 Local server stopped');
    }
}

// Main function
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log(`
Usage: 
  node pdf_generator.js <html-directory> [output-path] [format]

Examples:
  node pdf_generator.js projects/myproject/slides/
  node pdf_generator.js projects/myproject/report_pages/
  node pdf_generator.js projects/myproject/slides/ output.pdf
  node pdf_generator.js projects/myproject/slides/ output.pdf slides
  node pdf_generator.js projects/myproject/report_pages/ report.pdf report

Formats:
  slides - 16:9 horizontal format (default)
  report - 8.5x11 vertical format

Features:
  ✅ Uses HTTP server for proper asset loading
  ✅ Ensures parity with live viewer
  ✅ Handles all relative paths correctly
  ✅ Supports both slides (16:9) and reports (8.5x11)
  ✅ High-quality rendering with proper dimensions
        `);
        process.exit(0);
    }

    const htmlDir = args[0];
    const outputFile = args[1];
    const format = args[2] || 'slides';

    if (!fs.existsSync(htmlDir)) {
        console.error(`Error: Directory not found: ${htmlDir}`);
        process.exit(1);
    }

    await generatePDFWithServer(htmlDir, outputFile, format);
}

// Handle process termination
process.on('SIGINT', () => {
    console.log('\n⚠️  PDF generation cancelled by user');
    process.exit(0);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Fatal error:', error.message);
        process.exit(1);
    });
}

module.exports = { generatePDFWithServer };