const { chromium } = require('playwright');
const path = require('path');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    const filePath = 'file://' + path.resolve('Scores/way/way.html');

    // Stub the fetch to GitHub API so we can actually load buttons,
    // otherwise it might fail without network or get rate-limited.
    await page.route('https://api.github.com/repos/cju-media/Scores/contents/The%20Way', route => {
        route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([
                { name: "2-24-25", type: "dir", path: "The Way/2-24-25" },
                { name: "TEMPLATES", type: "dir" }
            ])
        });
    });

    await page.route('https://api.github.com/repos/cju-media/Scores/contents/The%20Way/2-24-25', route => {
        route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([
                { name: "2-24-25.musicxml", download_url: "https://raw.githubusercontent.com/cju-media/Scores/main/The%20Way/2-24-25/2-24-25.musicxml" }
            ])
        });
    });

    // We should also stub the raw github user content in case we can't fetch it
    await page.route('https://raw.githubusercontent.com/cju-media/Scores/main/The%20Way/2-24-25/2-24-25.musicxml', route => {
        route.fulfill({
            status: 200,
            contentType: 'application/xml',
            body: `<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
      <!-- OMITTED MIDI-INSTRUMENT TO TEST REGEX FIX -->
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>256</divisions>
        <key><fifths>0</fifths></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
        <clef><sign>G</sign><line>2</line></clef>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>1024</duration>
        <type>whole</type>
      </note>
    </measure>
  </part>
</score-partwise>`
        });
    });

    let bufferErrorFound = false;
    page.on('console', msg => {
        console.log(`[Browser Console] ${msg.type()}: ${msg.text()}`);
        if (msg.text().includes('Buffer') && msg.text().includes('not found')) {
            bufferErrorFound = true;
        }
    });

    console.log(`Going to: ${filePath}`);
    await page.goto(filePath);

    // Simulate DOMContentLoaded since this is a fragment and not a full document
    await page.evaluate(() => {
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });

    // Wait for the buttons to render
    console.log("Waiting for buttons to render...");
    try {
        await page.waitForSelector('.way-btn', { timeout: 5000 });
        console.log("Clicking the first button...");
        const buttons = await page.$$('.way-btn');
        if (buttons.length > 0) {
            await buttons[0].click();
        }

        await page.waitForSelector('#way-loading');

        await page.waitForSelector('#way-play-pause', { state: 'visible', timeout: 20000 });
        console.log("Play button became visible. Instrument loading seems to have succeeded.");

        if (bufferErrorFound) {
            console.error("Error: 'Buffer X not found' was still logged.");
            process.exit(1);
        } else {
            console.log("Success! No buffer errors detected.");
        }
    } catch (e) {
        console.error("Error occurred:", e.message);
        process.exit(1);
    }

    await browser.close();
})();
