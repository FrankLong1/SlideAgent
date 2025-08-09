#!/usr/bin/env node

const { launchBrowser, injectCommonCSS, PagePool, waitForSlideReady } = require('./puppeteer_helper');
const cliProgress = require('cli-progress');
const path = require('path');
const fs = require('fs');
const { PDFDocument: PDFLib } = require('pdf-lib');

// Run an array of async operations with a concurrency limit
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

async function generatePDF(input, outputPath = null) {
    // Check if input is a directory (for multiple slides) or single file
    const isDirectory = fs.existsSync(input) && fs.lstatSync(input).isDirectory();
    
    if (isDirectory) {
        // Handle directory of slides
        return await generatePDFFromSlides(input, outputPath);
    } else {
        // Handle single HTML file (legacy support)
        return await generatePDFFromSingleFile(input, outputPath);
    }
}

async function generatePDFFromSlides(slidesDir, outputPath = null) {
    // Find all slide HTML files in the directory
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
        // Create array to store individual PDF buffers
        const pdfBuffers = new Array(slideFiles.length);
        let completed = 0;

        // Process slides concurrently with a limit
        const CONCURRENCY_LIMIT = 8; // Increased for modern CPUs
        await processWithConcurrency(slideFiles, CONCURRENCY_LIMIT, async (slideFile, i) => {
            const slidePath = path.join(slidesDir, slideFile);
            const page = await pagePool.acquire();
            try {
                const fileUrl = `file://${path.resolve(slidePath)}`;
                await waitForSlideReady(page, fileUrl);

                await injectCommonCSS(page);

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
        
        // Get file size for confirmation
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

async function generatePDFFromSingleFile(htmlFilePath, outputPath = null) {
    // Validate input file exists
    if (!fs.existsSync(htmlFilePath)) {
        console.error(`Error: HTML file not found: ${htmlFilePath}`);
        process.exit(1);
    }

    // Generate output path if not provided
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
        
        // Set viewport to match slide dimensions (16in x 9in at 96 DPI)
        // 16in x 9in = 1536px x 864px at 96 DPI
        await page.setViewport({
            width: 1536,
            height: 864,
            deviceScaleFactor: 1
        });

        // Load the HTML file
        const fileUrl = `file://${path.resolve(htmlFilePath)}`;
        await page.goto(fileUrl, {
            waitUntil: 'networkidle0',
            timeout: 30000
        });

        // Wait for any dynamic content to load
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Inject common slide CSS
        await injectCommonCSS(page);

        // Generate PDF with settings that respect CSS dimensions
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
            pageRanges: '',
            displayHeaderFooter: false,
            scale: 1.0
        });

        console.log(`✅ PDF generated successfully: ${outputPath}`);
        
        // Get file size for confirmation
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

// Command line interface
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

// Handle process termination gracefully
process.on('SIGINT', () => {
    console.log('\n⚠️  PDF generation cancelled by user');
    process.exit(0);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

// Run the script
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Fatal error:', error.message);
        process.exit(1);
    });
}

module.exports = { generatePDF };