const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();

    let bufferErrorFound = false;
    page.on('console', msg => {
        if (msg.type() === 'error' || msg.type() === 'warning') {
            console.log(`[Console] ${msg.type()}: ${msg.text()}`);
        }
        if (msg.text().includes('Buffer') && msg.text().includes('not found')) {
            bufferErrorFound = true;
        }
    });

    // Mock the API for folders
    await page.route('https://api.github.com/repos/cju-media/Scores/contents/The%20Way?ref=main', route => {
        route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([
                { name: "2-24-25", type: "dir", path: "The Way/2-24-25" },
                { name: "TEMPLATES", type: "dir" }
            ])
        });
    });

    // Mock API for getting the XML file list in the folder
    await page.route('https://api.github.com/repos/cju-media/Scores/contents/The%20Way/2-24-25?ref=main', route => {
        route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([
                { name: "2-24-25.musicxml", download_url: "https://raw.githubusercontent.com/cju-media/Scores/main/The%20Way/2-24-25/2-24-25.musicxml" }
            ])
        });
    });

    // Mock the actual XML download! Here we provide a clean MusicXML without the midi-instrument so we test the RegEx!
    await page.route('https://raw.githubusercontent.com/cju-media/Scores/main/The%20Way/2-24-25/2-24-25.musicxml', route => {
        route.fulfill({
            status: 200,
            contentType: 'application/xml',
            body: `<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
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

    console.log(`Going to local server...`);
    await page.goto('http://localhost:8080/Scores/way/way.html');

    console.log("Waiting for .repo-button...");
    try {
        await page.waitForSelector('.repo-button', { timeout: 15000 });
        console.log("Button found, clicking...");
        await page.click('.repo-button');

        await page.waitForSelector('#osmd-loading', { state: 'visible', timeout: 5000 });

        console.log("Waiting for play-pause button #osmd-play-pause-btn to be enabled...");
        // Wait for it to become enabled (disabled attribute removed)
        await page.waitForFunction(() => {
            const btn = document.getElementById('osmd-play-pause-btn');
            return btn && !btn.disabled;
        }, { timeout: 30000 });

        console.log("Play button is enabled! Playing audio...");
        await page.click('#osmd-play-pause-btn');

        // Wait another bit to see if there's buffer errors during initialization / loading
        await page.waitForTimeout(3000);

        if (bufferErrorFound) {
            console.error("FAIL: 'Buffer 12 not found' error occurred.");
            process.exit(1);
        } else {
            console.log("SUCCESS: No buffer errors found!");
            process.exit(0);
        }
    } catch (e) {
        console.error("Error:", e.message);
        process.exit(1);
    }

    await browser.close();
})();
