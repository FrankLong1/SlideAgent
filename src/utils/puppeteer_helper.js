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
            '--disable-gpu',
            // Performance optimizations
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials',
            '--no-first-run',
            '--disable-extensions',
            '--disable-default-apps',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-ipc-flooding-protection',
            '--enable-features=NetworkService',
            '--disable-features=TranslateUI',
            '--disable-sync',
            '--metrics-recording-only',
            '--no-default-browser-check',
            '--mute-audio',
            '--no-pings',
            '--disable-domain-reliability',
            '--disable-background-networking',
            '--disable-breakpad',
            '--disable-component-update',
            '--disable-client-side-phishing-detection'
        ]
    });
}

async function injectCommonCSS(page) {
    await page.addStyleTag({ content: COMMON_CSS });
}

class PagePool {
    constructor(browser, size = 8) {
        this.browser = browser;
        this.size = size;
        this.pages = [];
        this.available = [];
        this.initialized = false;
        this.createdCount = 0;
    }

    async init(lazyLoad = false) {
        if (this.initialized) return;
        this.initialized = true;
        
        if (!lazyLoad) {
            // Create all pages upfront (original behavior)
            for (let i = 0; i < this.size; i++) {
                const page = await this.browser.newPage();
                await page.setViewport({ width: 1920, height: 1080 });
                this.pages.push(page);
                this.available.push(page);
                this.createdCount++;
            }
        }
        // If lazyLoad is true, pages will be created on-demand in acquire()
    }

    async acquire() {
        if (!this.initialized) await this.init();
        
        // Wait for an available page
        while (this.available.length === 0) {
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        return this.available.pop();
    }

    async release(page) {
        // Reset page to blank state
        try {
            await page.goto('about:blank', { waitUntil: 'domcontentloaded' });
        } catch (e) {
            // Page might be closed, create a new one
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

async function waitForSlideReady(page, slideUrl) {
    // Navigate with network idle
    await page.goto(slideUrl, { 
        waitUntil: ['domcontentloaded', 'networkidle0'],
        timeout: 30000 
    });
    
    // Smart wait for all content to be ready
    try {
        await page.waitForFunction(() => {
            // Check document is fully loaded
            if (document.readyState !== 'complete') return false;
            
            // Check all images are loaded
            const images = document.querySelectorAll('img');
            for (let img of images) {
                if (!img.complete) return false;
                // Skip naturalHeight check as it might be 0 for some valid images
            }
            
            // Check fonts are loaded (but don't fail if fonts API not available)
            if (document.fonts && document.fonts.status === 'loading') return false;
            
            // Check main slide container exists (try multiple selectors)
            const slide = document.querySelector('.slide, section, div[class*="slide"]');
            if (!slide) {
                // If no slide container, just check body exists
                return document.body !== null;
            }
            
            // All checks passed
            return true;
        }, { timeout: 5000 });
    } catch (e) {
        // If waitForFunction times out, continue anyway
        console.warn('Warning: Slide readiness check timed out, continuing anyway');
    }
    
    // Small delay for final rendering
    await new Promise(resolve => setTimeout(resolve, 100));
}

module.exports = {
    launchBrowser,
    injectCommonCSS,
    PagePool,
    waitForSlideReady,
    COMMON_CSS
};
