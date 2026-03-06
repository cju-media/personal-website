const fs = require('fs');

const htmlContent = fs.readFileSync('Scores/way/way.html', 'utf8');

// We just want to extract the replacer function to test it isolated
const regexMatch = htmlContent.match(/xmlText = xmlText\.replace\(\/\(<score-part id="\(\[\^"\]\+\)">\[\\s\\S\]\*\?\)<\/score-part>\/g, \([\s\S]*?return \`\$\{p1\}[\s\S]*?<\/score-part>\`;\n\s*\}\);/);

if (!regexMatch) {
    console.error("Could not extract replacer function!");
    // Wait, let's just do it directly here to test the logic block:
}

const replacerText = `
(match, p1, partId) => {
    if (match.includes('<midi-instrument')) return match;

    const instMatch = match.match(/<score-instrument id="([^"]+)">/);
    const instId = instMatch ? instMatch[1] : \`\${partId}-I1\`;

    // Extract part-name to guess instrument if possible
    let midiProgram = 1; // Default to Acoustic Grand Piano
    const nameMatch = match.match(/<part-name[^>]*>([\\s\\S]*?)<\\/part-name>/);
    if (nameMatch) {
        const partName = nameMatch[1].toLowerCase();
        // General MIDI Program mappings
        const instrumentMap = {
            'piano': 1, 'harpsichord': 7, 'celesta': 9, 'glockenspiel': 10, 'music box': 11, 'vibraphone': 12, 'marimba': 13, 'xylophone': 14, 'tubular bells': 15, 'dulcimer': 16,
            'organ': 20, 'accordion': 22, 'harmonica': 23, 'bandoneon': 24,
            'guitar': 25, 'acoustic guitar': 26, 'electric guitar': 28, 'bass': 33, 'acoustic bass': 33, 'electric bass': 34,
            'violin': 41, 'viola': 42, 'cello': 43, 'violoncello': 43, 'contrabass': 44, 'double bass': 44, 'tremolo strings': 45, 'pizzicato strings': 46, 'harp': 47, 'timpani': 48,
            'strings': 49, 'string ensemble': 49, 'synth strings': 51, 'choir': 53, 'voice': 54, 'synth choir': 55,
            'trumpet': 57, 'trombone': 58, 'tuba': 59, 'muted trumpet': 60, 'french horn': 61, 'horn': 61, 'brass': 62, 'synth brass': 63,
            'soprano sax': 65, 'alto sax': 66, 'tenor sax': 67, 'baritone sax': 68, 'oboe': 69, 'english horn': 70, 'bassoon': 71, 'clarinet': 72,
            'piccolo': 73, 'flute': 74, 'recorder': 75, 'pan flute': 76, 'blown bottle': 77, 'shakuhachi': 78, 'whistle': 79, 'ocarina': 80
        };

        for (const [key, programId] of Object.entries(instrumentMap)) {
            if (partName.includes(key)) {
                midiProgram = programId;
                break;
            }
        }
    }

    return \`\${p1}
        <midi-device id="\${instId}" port="1"></midi-device>
        <midi-instrument id="\${instId}">
            <midi-channel>1</midi-channel>
            <midi-program>\${midiProgram}</midi-program>
            <volume>78.7402</volume>
            <pan>0</pan>
        </midi-instrument>
    </score-part>\`;
}
`;

const replacerFunc = eval(`(${replacerText})`);

let testXml = `
<score-part id="P1">
    <part-name>Flute</part-name>
</score-part>
<score-part id="P2">
    <part-name>Violoncello</part-name>
</score-part>
<score-part id="P3">
    <part-name>Some Weird Synth</part-name>
</score-part>
`;

let result = testXml.replace(/(<score-part id="([^"]+)">[\s\S]*?)<\/score-part>/g, replacerFunc);

console.log("Result:");
console.log(result);
