const puppeteer = require('puppeteer');

const COMMON_CSS = `
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
`;

async function launchBrowser() {
    return puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    });
}

async function injectCommonCSS(page) {
    await page.addStyleTag({ content: COMMON_CSS });
}

module.exports = {
    launchBrowser,
    injectCommonCSS,
    COMMON_CSS
};
