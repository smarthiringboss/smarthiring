const devices = require('puppeteer/DeviceDescriptors')

const puppeteer = require('puppeteer');

(async () => {

    const browser = await puppeteer.launch({

        headless: false

    })

    const page = await browser.newPage()

    await page.emulate(devices['iPhone X'])

    await page.goto('https://www.zhipin.com/c100010000-p100101/')

    await page.screenshot({

        path: 'example.png'

    })

})()