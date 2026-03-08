const { chromium } = require('playwright');
const path = require('path');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();

    // We mock the Github calls
    await page.route('https://api.github.com/repos/cju-media/Scores/contents/The%20Way?ref=main', route => {
        route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([{ name: "2-24-25", type: "dir", path: "The Way/2-24-25" }])
        });
    });

    await page.route('https://api.github.com/repos/cju-media/Scores/contents/The%20Way/2-24-25?ref=main', route => {
        route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([{ name: "2-24-25.musicxml", download_url: "https://raw.githubusercontent.com/cju-media/Scores/main/The%20Way/2-24-25/2-24-25.musicxml" }])
        });
    });

    // Provide a valid score but let it play
    await page.route('https://raw.githubusercontent.com/cju-media/Scores/main/The%20Way/2-24-25/2-24-25.musicxml', route => {
        route.fulfill({
            status: 200,
            contentType: 'application/xml',
            body: `<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0"><part-list>
<score-part id="P1"><part-name>Flute</part-name></score-part>
</part-list>
<part id="P1"><measure number="1"><attributes><divisions>256</divisions><key><fifths>0</fifths></key><time><beats>4</beats><beat-type>4</beat-type></time><clef><sign>G</sign><line>2</line></clef></attributes>
<note><pitch><step>C</step><octave>4</octave></pitch><duration>1024</duration><type>whole</type></note></measure>
</part>
</score-partwise>`
        });
    });

    await page.goto('file://' + path.resolve('Scores/way/way.html'));

    await page.waitForSelector('.repo-button', { timeout: 15000 });
    await page.click('.repo-button');

    // Wait until play button is enabled
    await page.waitForFunction(() => {
        const btn = document.getElementById('osmd-play-pause-btn');
        return btn && !btn.disabled;
    }, { timeout: 30000 });

    // Ensure the color is actually gray
    const titleColor = await page.evaluate(() => {
        const title = document.getElementById('midi-modal-title');
        return window.getComputedStyle(title).color;
    });

    console.log("Computed title color:", titleColor);

    // Screenshot to check layout visually
    await page.screenshot({ path: 'test_title_color.png' });

    console.log("Screenshot taken.");
    await browser.close();
})();
