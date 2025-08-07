#!/usr/bin/env node

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const { PDFDocument: PDFLib } = require('pdf-lib');

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

    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    });

    try {
        // Create array to store individual PDF buffers
        const pdfBuffers = [];
        
        // Process each slide
        for (let i = 0; i < slideFiles.length; i++) {
            const slideFile = slideFiles[i];
            const slidePath = path.join(slidesDir, slideFile);
            console.log(`  📄 Processing ${slideFile}...`);
            
            const page = await browser.newPage();
            
            // Set viewport to match slide dimensions
            await page.setViewport({
                width: 1920,
                height: 1080,
                deviceScaleFactor: 1
            });

            // Load the HTML file
            const fileUrl = `file://${path.resolve(slidePath)}`;
            await page.goto(fileUrl, {
                waitUntil: 'networkidle2',
                timeout: 60000
            });

            // Wait for content to render
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Inject minimal CSS to optimize for PDF printing
            // The slides already have proper CSS, we just need to clean up for PDF
            await page.addStyleTag({
                content: `
                    /* Remove browser viewport styling */
                    body {
                        background: white !important;
                        padding: 0 !important;
                        margin: 0 !important;
                    }
                    
                    /* Ensure slides render at exact dimensions */
                    .slide, section.slide {
                        box-shadow: none !important;
                        border: none !important;
                    }
                `
            });

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

            pdfBuffers.push(pdfBuffer);
            await page.close();
        }

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

    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    });

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

        // Inject CSS to optimize for PDF printing
        await page.addStyleTag({
            content: `
                body {
                    background: white !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    display: block !important;
                    min-height: auto !important;
                }
                .slide, section.slide, div.slide {
                    width: 1920px !important;
                    height: 1080px !important;
                    margin: 0 !important;
                    box-shadow: none !important;
                    border: none !important;
                    overflow: hidden !important;
                }
            `
        });

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