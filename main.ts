// The World in One Day — Friday 20 November 2026.
// Entry program for news-image-20261120: validates the bundled entry.png
// (a 1024x1024 PNG newspaper page with 69 verified stories) chunk by chunk,
// then copies it to the output directory.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { crc32 } from 'node:zlib';

const LIMIT = 1_048_576;
const SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const DEPTHS = { 0: [1, 2, 4, 8, 16], 2: [8, 16], 3: [1, 2, 4, 8], 4: [8, 16], 6: [8, 16] };

function fail(message) {
  throw new Error(message);
}

function validate(bytes) {
  if (bytes.length < 57 || bytes.length > LIMIT) {
    fail(`entry.png length ${bytes.length} outside [57, ${LIMIT}]`);
  }
  for (let i = 0; i < 8; i += 1) {
    if (bytes[i] !== SIGNATURE[i]) fail('entry.png has a bad PNG signature');
  }
  if (bytes.readUInt32BE(8) !== 13 || bytes.toString('ascii', 12, 16) !== 'IHDR') {
    fail('entry.png does not start with a 13-byte IHDR chunk');
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== 1024 || height !== 1024) {
    fail(`entry.png is ${width}x${height}, expected 1024x1024`);
  }
  const bitDepth = bytes[24];
  const colourType = bytes[25];
  const allowed = DEPTHS[colourType];
  if (!allowed || !allowed.includes(bitDepth)) {
    fail(`entry.png has bit depth ${bitDepth} invalid for colour type ${colourType}`);
  }
  if (bytes[26] !== 0) fail('entry.png has a non-zero IHDR compression byte');
  if (bytes[27] !== 0) fail('entry.png has a non-zero IHDR filter byte');
  if (bytes[28] > 1) fail('entry.png has an invalid IHDR interlace byte');

  let offset = 8;
  let ihdrSeen = false;
  let idatTotal = 0;
  let iendSeen = false;
  while (offset < bytes.length) {
    if (offset + 12 > bytes.length) fail('entry.png ends inside a chunk header');
    const length = bytes.readUInt32BE(offset);
    const type = bytes.toString('ascii', offset + 4, offset + 8);
    for (const ch of type) {
      const code = ch.charCodeAt(0);
      if (!((code >= 65 && code <= 90) || (code >= 97 && code <= 122))) {
        fail(`entry.png has a non-letter chunk type at offset ${offset}`);
      }
    }
    if (offset + 12 + length > bytes.length) {
      fail(`entry.png chunk ${type} at offset ${offset} overruns the file`);
    }
    const dataStart = offset + 8;
    const dataEnd = dataStart + length;
    const storedCrc = bytes.readUInt32BE(dataEnd);
    const actualCrc = crc32(bytes.subarray(offset + 4, dataEnd));
    if (actualCrc !== storedCrc) {
      fail(`entry.png chunk ${type} at offset ${offset} fails its CRC check`);
    }
    if (type === 'IHDR') {
      if (ihdrSeen) fail('entry.png contains a second IHDR chunk');
      ihdrSeen = true;
    }
    if (type === 'IDAT') idatTotal += length;
    if (type === 'IEND') {
      if (length !== 0) fail('entry.png IEND chunk is not empty');
      if (dataEnd + 4 !== bytes.length) fail('entry.png has trailing bytes after IEND');
      iendSeen = true;
    }
    offset = dataEnd + 4;
  }
  if (!ihdrSeen) fail('entry.png has no IHDR chunk');
  if (!iendSeen) fail('entry.png does not end with an IEND chunk');
  if (idatTotal <= 0) fail('entry.png contains no image data');
}

const bytes = readFileSync(new URL('./entry.png', import.meta.url));
validate(bytes);
const outputDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
mkdirSync(outputDir, { recursive: true });
writeFileSync(join(outputDir, 'entry.png'), bytes);
console.log(`entry.png validated and copied (${bytes.length} bytes)`);
