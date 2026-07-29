
const puppeteer = require('puppeteer');

(async () => {
  try {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    page.on('console', msg => console.log('CONSOLE ' + msg.type() + ': ' + msg.text()));
    page.on('pageerror', err => console.log('PAGE ERROR: ' + err.toString()));
    page.on('requestfailed', req => console.log('FAILED REQ: ' + req.url() + ' - ' + (req.failure() ? req.failure().errorText : '')));

    console.log('Navigating to https://ocean-university-map.vercel.app...');
    await page.goto('https://ocean-university-map.vercel.app', { waitUntil: 'networkidle0', timeout: 30000 });
    
    console.log('Page title:', await page.title());
    await browser.close();
  } catch(e) {
    console.log('Puppeteer launch error:', e.message);
  }
})();
