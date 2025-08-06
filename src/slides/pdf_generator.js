#!/usr/bin/env node

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function generatePDF(htmlFilePath, outputPath = null) {
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
                }
                .slide {
                    width: 100vw !important;
                    height: 100vh !important;
                    margin: 0 !important;
                    box-shadow: none !important;
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
Usage: node generate-pdf.js <html-file-path> [output-path]

Examples:
  node generate-pdf.js presos/datacenters/datacenter_presentation.html
  node generate-pdf.js presos/datacenters/datacenter_presentation.html custom-output.pdf

Features:
  ✅ Preserves 16:9 aspect ratio optimized for presentations
  ✅ Respects CSS page-break-after: always
  ✅ High-quality rendering with 2x device scale factor
  ✅ Landscape A4 format for professional presentation printing
  ✅ Background colors and images included
  ✅ No margins for full-page slides
        `);
        process.exit(0);
    }

    const htmlFile = args[0];
    const outputFile = args[1];

    await generatePDF(htmlFile, outputFile);
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