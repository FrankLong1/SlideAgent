#!/usr/bin/env node

const puppeteer = require('puppeteer');
const cliProgress = require('cli-progress');
const path = require('path');
const fs = require('fs');
const { PDFDocument: PDFLib } = require('pdf-lib');

// Run async operations with concurrency limit for better performance
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

    // Generate output path if not provided
    if (!outputPath) {
        const projectDir = path.dirname(slidesDir);
        const projectName = path.basename(projectDir);
        outputPath = path.join(projectDir, `${projectName}.pdf`);
    }

    console.log(`📂 Generating PDF from ${slideFiles.length} slides in ${slidesDir}`);
    console.log(`📝 Output: ${outputPath}`);

    // Create progress bar
    const progressBar = new cliProgress.SingleBar({
        format: '🗝 PDF Generation |{bar}| {percentage}% | {value}/{total} | {slide}',
        barCompleteChar: '█',
        barIncompleteChar: '░',
        hideCursor: true
    });
    
    progressBar.start(slideFiles.length, 0, { slide: 'Starting...' });

    // Launch browser with page pool for parallel processing
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
        // Create page pool for parallel processing
        const POOL_SIZE = 4;
        const pages = [];
        for (let i = 0; i < POOL_SIZE; i++) {
            pages.push(await browser.newPage());
        }
        
        let pageIndex = 0;
        const getNextPage = () => {
            const page = pages[pageIndex];
            pageIndex = (pageIndex + 1) % POOL_SIZE;
            return page;
        };

        // Array to store PDF buffers in order
        const pdfBuffers = new Array(slideFiles.length);
        let completed = 0;

        // Process slides in parallel with concurrency limit
        const CONCURRENCY_LIMIT = 8; // Fast parallel processing
        await processWithConcurrency(slideFiles, CONCURRENCY_LIMIT, async (slideFile, i) => {
            const slidePath = path.join(slidesDir, slideFile);
            const page = getNextPage();
            
            try {
                const fileUrl = `file://${path.resolve(slidePath)}`;
                
                // Navigate to the slide
                await page.goto(fileUrl, {
                    waitUntil: 'networkidle0',
                    timeout: 30000
                });
                
                // Brief wait for any dynamic content
                await page.waitForTimeout(300);

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
            } catch (error) {
                console.error(`Error processing ${slideFile}:`, error);
                throw error;
            }
        });
        
        progressBar.stop();

        // Close all pages
        for (const page of pages) {
            await page.close();
        }

        // Merge all PDFs into one
        console.log('📚 Merging PDFs...');
        const mergedPdf = await PDFLib.create();
        
        for (const pdfBuffer of pdfBuffers) {
            const pdf = await PDFLib.load(pdfBuffer);
            const pages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
            pages.forEach(page => mergedPdf.addPage(page));
        }

        const mergedPdfBytes = await mergedPdf.save();
        fs.writeFileSync(outputPath, mergedPdfBytes);
        
        console.log(`✅ PDF generated successfully: ${outputPath}`);
        console.log(`📄 Total pages: ${slideFiles.length}`);
    } catch (error) {
        progressBar.stop();
        console.error('❌ Error generating PDF:', error);
        process.exit(1);
    } finally {
        await browser.close();
    }
}

async function generatePDFFromSingleFile(htmlPath, outputPath = null) {
    // Legacy support for single file
    if (!outputPath) {
        outputPath = htmlPath.replace(/\.html$/, '.pdf');
    }

    console.log(`📄 Generating PDF from ${htmlPath}`);
    console.log(`📝 Output: ${outputPath}`);

    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
        const page = await browser.newPage();
        const fileUrl = `file://${path.resolve(htmlPath)}`;
        
        await page.goto(fileUrl, {
            waitUntil: 'networkidle0',
            timeout: 30000
        });
        
        await page.waitForTimeout(500);

        await page.pdf({
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
    } catch (error) {
        console.error('❌ Error generating PDF:', error);
        process.exit(1);
    } finally {
        await browser.close();
    }
}

// Main execution
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.error('Usage: node pdf_generator.js <slides-directory-or-html-file> [output.pdf]');
        process.exit(1);
    }

    const input = args[0];
    const outputPath = args[1] || null;

    generatePDF(input, outputPath).catch(err => {
        console.error('Error:', err);
        process.exit(1);
    });
}

module.exports = { generatePDF };