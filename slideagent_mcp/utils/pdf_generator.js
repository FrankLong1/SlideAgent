#!/usr/bin/env node

const puppeteer = require('puppeteer');
const cliProgress = require('cli-progress');
const path = require('path');
const fs = require('fs');
const { PDFDocument: PDFLib } = require('pdf-lib');

// Common CSS to inject for consistent rendering
const COMMON_CSS = `
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
            '--disable-site-isolation-trials',
            '--allow-file-access-from-files',
            '--enable-local-file-accesses'
        ]
    });
}

// Page pool for concurrent processing
class PagePool {
    constructor(browser, size = 8) {
        this.browser = browser;
        this.size = size;
        this.pages = [];
        this.available = [];
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        this.initialized = true;
        
        for (let i = 0; i < this.size; i++) {
            const page = await this.browser.newPage();
            await page.setViewport({ width: 1920, height: 1080 });
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
            const newPage = await this.browser.newPage();
            await newPage.setViewport({ width: 1920, height: 1080 });
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
    
    await new Promise(resolve => setTimeout(resolve, 100));
}

// Inject CSS into page
async function injectCommonCSS(page) {
    await page.addStyleTag({ content: COMMON_CSS });
}

// Main PDF generation function
async function generatePDF(input, outputPath = null) {
    const isDirectory = fs.existsSync(input) && fs.lstatSync(input).isDirectory();
    
    if (isDirectory) {
        return await generatePDFFromSlides(input, outputPath);
    } else {
        return await generatePDFFromSingleFile(input, outputPath);
    }
}

// Generate PDF from directory of slides
async function generatePDFFromSlides(slidesDir, outputPath = null) {
    // Find all slide HTML files
    const slideFiles = fs.readdirSync(slidesDir)
        .filter(file => file.match(/^slide_\d+\.html$/))
        .sort((a, b) => {
            const numA = parseInt(a.match(/\d+/)[0]);
            const numB = parseInt(b.match(/\d+/)[0]);
            return numA - numB;
        });

    if (slideFiles.length === 0) {
        console.error(`Error: No slide files found in ${slidesDir}`);
        process.exit(1);
    }

    console.log(`📑 Found ${slideFiles.length} slides to process`);

    // Generate output path if not provided
    if (!outputPath) {
        const projectName = path.basename(path.dirname(slidesDir));
        outputPath = path.join(path.dirname(slidesDir), `${projectName}.pdf`);
    }

    console.log(`📝 Generating PDF from ${slideFiles.length} slides`);
    console.log(`📁 Output will be saved to: ${outputPath}`);

    const browser = await launchBrowser();
    const pagePool = new PagePool(browser, 8);
    await pagePool.init();

    // Create progress bar
    const progressBar = new cliProgress.SingleBar({
        format: '🗝 PDF Generation |{bar}| {percentage}% | {value}/{total} | {slide}',
        barCompleteChar: '█',
        barIncompleteChar: '░',
        hideCursor: true
    });
    
    progressBar.start(slideFiles.length, 0, { slide: 'Starting...' });

    try {
        const pdfBuffers = new Array(slideFiles.length);
        let completed = 0;

        // Process slides concurrently
        const CONCURRENCY_LIMIT = 8;
        await processWithConcurrency(slideFiles, CONCURRENCY_LIMIT, async (slideFile, i) => {
            const slidePath = path.join(slidesDir, slideFile);
            const page = await pagePool.acquire();
            
            try {
                // Read HTML and inject CSS inline
                let htmlContent = fs.readFileSync(slidePath, 'utf8');
                
                // Extract CSS paths from the HTML itself
                const cssLinkRegex = /<link\s+rel="stylesheet"\s+href="([^"]+)"/g;
                const cssLinks = [];
                let match;
                while ((match = cssLinkRegex.exec(htmlContent)) !== null) {
                    cssLinks.push(match[1]);
                }
                
                // Read and inline all CSS files found
                let combinedCSS = '';
                
                for (const cssLink of cssLinks) {
                    // Resolve relative path to absolute
                    const cssPath = path.resolve(path.dirname(slidePath), cssLink);
                    
                    if (fs.existsSync(cssPath)) {
                        let cssContent = fs.readFileSync(cssPath, 'utf8');
                        
                        // Fix relative URLs in CSS (for images, fonts, etc.)
                        const cssDir = path.dirname(cssPath);
                        cssContent = cssContent.replace(/url\(['"]?([^'")]+)['"]?\)/g, (match, url) => {
                            // Skip data URLs and absolute URLs
                            if (url.startsWith('data:') || url.startsWith('http') || url.startsWith('file:')) {
                                return match;
                            }
                            // Convert relative URL to absolute file:// URL
                            const absolutePath = path.resolve(cssDir, url);
                            return `url('file://${absolutePath}')`;
                        });
                        
                        combinedCSS += `\n/* From ${cssLink} */\n${cssContent}\n`;
                    } else {
                        console.warn(`Warning: CSS file not found: ${cssPath}`);
                    }
                }
                
                // Remove existing CSS links and inject inline
                htmlContent = htmlContent.replace(/<link rel="stylesheet"[^>]*>/g, '');
                
                // Inject CSS into head
                const cssInjection = `
                    <style>
                        /* Combined CSS from all linked stylesheets */
                        ${combinedCSS}
                        
                        /* Override for PDF */
                        ${COMMON_CSS}
                    </style>
                </head>`;
                
                htmlContent = htmlContent.replace('</head>', cssInjection);
                
                // Fix all relative image paths to absolute file:// URLs
                htmlContent = htmlContent.replace(/src="([^"]+)"/g, (match, src) => {
                    // Skip data URLs, absolute URLs, and file:// URLs
                    if (src.startsWith('data:') || src.startsWith('http') || src.startsWith('file:')) {
                        return match;
                    }
                    // Convert relative path to absolute file:// URL
                    const absolutePath = path.resolve(path.dirname(slidePath), src);
                    return `src="file://${absolutePath}"`;
                });
                
                // Set content
                await page.setContent(htmlContent, {
                    waitUntil: ['networkidle0', 'domcontentloaded'],
                    timeout: 30000
                });
                
                // Wait for rendering
                await new Promise(resolve => setTimeout(resolve, 500));

                // Generate PDF for this slide
                const pdfBuffer = await page.pdf({
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
                });

                pdfBuffers[i] = pdfBuffer;
                completed++;
                progressBar.update(completed, { slide: slideFile });
            } finally {
                await pagePool.release(page);
            }
        });
        
        progressBar.stop();

        // Merge all PDFs into one
        console.log(`🔀 Merging ${pdfBuffers.length} slides into single PDF...`);
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
    }
}

// Generate PDF from single HTML file
async function generatePDFFromSingleFile(htmlFilePath, outputPath = null) {
    if (!fs.existsSync(htmlFilePath)) {
        console.error(`Error: HTML file not found: ${htmlFilePath}`);
        process.exit(1);
    }

    if (!outputPath) {
        const dir = path.dirname(htmlFilePath);
        const filename = path.basename(htmlFilePath, '.html');
        outputPath = path.join(dir, `${filename}.pdf`);
    }

    console.log(`Generating PDF from: ${htmlFilePath}`);
    console.log(`Output will be saved to: ${outputPath}`);

    const browser = await launchBrowser();

    try {
        const page = await browser.newPage();
        
        await page.setViewport({
            width: 1536,
            height: 864,
            deviceScaleFactor: 1
        });

        const fileUrl = `file://${path.resolve(htmlFilePath)}`;
        await waitForSlideReady(page, fileUrl);

        await injectCommonCSS(page);

        const pdfBuffer = await page.pdf({
            path: outputPath,
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
        });

        console.log(`✅ PDF generated successfully: ${outputPath}`);
        
        const stats = fs.statSync(outputPath);
        const fileSizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
        console.log(`📄 File size: ${fileSizeInMB} MB`);

    } catch (error) {
        console.error('❌ Error generating PDF:', error.message);
        process.exit(1);
    } finally {
        await browser.close();
    }
}

// Main function
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log(`
Usage: 
  node pdf_generator.js <slides-directory> [output-path]
  node pdf_generator.js <html-file-path> [output-path]

Examples:
  node pdf_generator.js projects/myproject/slides/
  node pdf_generator.js projects/myproject/slides/ output.pdf
  node pdf_generator.js single-slide.html output.pdf

Features:
  ✅ Automatically detects and processes all slide_XX.html files in directory
  ✅ Preserves 16:9 aspect ratio optimized for presentations
  ✅ Merges multiple slides into single PDF maintaining order
  ✅ High-quality rendering with proper dimensions
  ✅ Background colors and images included
  ✅ No margins for full-page slides
        `);
        process.exit(0);
    }

    const input = args[0];
    const outputFile = args[1];

    await generatePDF(input, outputFile);
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

module.exports = { generatePDF };