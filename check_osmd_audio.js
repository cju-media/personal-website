const { chromium } = require('playwright');
const path = require('path');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('file://' + path.resolve('Scores/way/way.html'));

    await page.addScriptTag({ url: 'https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.3/build/opensheetmusicdisplay.min.js' });
    await page.addScriptTag({ url: 'https://cdn.jsdelivr.net/npm/osmd-audio-player@0.7.0/umd/OsmdAudioPlayer.min.js' });

    const info = await page.evaluate(async () => {
        const ap = new window.OsmdAudioPlayer();

        let info = {};

        return "Hooking into ap.instrumentPlayer.schedule seems perfect. `n` contains `note`, `duration`, `gain`";
    });
    console.log(info);

    await browser.close();
})();
