'use strict';

/**
 * Manual smoke test: hits a *running* data-serve server over real HTTP,
 * from Node instead of Python - same checks as smoke_test.py, so either
 * one can confirm the server actually works without needing a browser.
 *
 * Uses Node's built-in `http`/`https` modules rather than `fetch` -
 * `fetch` is only global since Node 18, and this script shouldn't need a
 * Node-version bump or an extra dependency just to make a GET request.
 *
 * Usage (after starting a server per README.md):
 *   node data-serve/smoke_test.js
 *   node data-serve/smoke_test.js http://localhost:5000
 *
 * Exits with a non-zero status if any check fails.
 */

const http = require('http');
const https = require('https');

const baseUrl = process.argv[2] || 'http://localhost:5000';

let allPassed = true;

/** Logs PASS/FAIL for one assertion and folds it into the overall result. */
function check(description, condition) {
  const status = condition ? 'PASS' : 'FAIL';
  console.log(`[${status}] ${description}`);
  allPassed = allPassed && condition;
  return condition;
}

/** GETs a path against baseUrl, resolving to { status, headers, body, json() }. */
function get(path) {
  return new Promise((resolve, reject) => {
    const client = baseUrl.startsWith('https') ? https : http;
    client
      .get(baseUrl + path, (res) => {
        const chunks = [];
        res.on('data', (chunk) => chunks.push(chunk));
        res.on('end', () => {
          const body = Buffer.concat(chunks);
          resolve({
            status: res.statusCode,
            headers: res.headers,
            body,
            json: () => JSON.parse(body.toString('utf-8')),
          });
        });
      })
      .on('error', reject);
  });
}

async function run() {
  const meta = await get('/api/meta');
  check('GET /api/meta -> 200', meta.status === 200);
  const metaJson = meta.json();
  console.log(`       backend=${JSON.stringify(metaJson.backend)}, count=${metaJson.count}`);
  check('meta.count is a positive number', Number.isInteger(metaJson.count) && metaJson.count > 0);

  const listing = await get('/api/pokemon?limit=5');
  check('GET /api/pokemon?limit=5 -> 200', listing.status === 200);
  const entries = listing.json();
  check('...returns exactly 5 entries', entries.length === 5);
  const numbers = entries.map((entry) => entry.national_number);
  const sortedNumbers = [...numbers].sort((a, b) => a - b);
  check('...sorted by national_number', JSON.stringify(numbers) === JSON.stringify(sortedNumbers));

  const filtered = await get('/api/pokemon?type=fire&generation=1');
  check('GET /api/pokemon?type=fire&generation=1 -> 200', filtered.status === 200);
  const fireGen1 = filtered.json();
  check(
    '...every result is actually Fire-type and Generation 1',
    fireGen1.every((entry) => entry.generation === 1 && entry.types.includes('Fire'))
  );

  const detail = await get('/api/pokemon/pikachu');
  check('GET /api/pokemon/pikachu -> 200', detail.status === 200);
  const pikachu = detail.json();
  check("...name is 'pikachu'", pikachu.name === 'pikachu');
  check(
    '...artwork_url points back at this API, not a local path',
    pikachu.artwork_url === '/api/pokemon/pikachu/artwork'
  );

  const missing = await get('/api/pokemon/missingno');
  check('GET /api/pokemon/missingno -> 404', missing.status === 404);

  const artwork = await get('/api/pokemon/pikachu/artwork');
  check('GET /api/pokemon/pikachu/artwork -> 200', artwork.status === 200);
  check(
    '...Content-Type is image/jpeg',
    (artwork.headers['content-type'] || '').startsWith('image/jpeg')
  );
  check(
    '...body actually starts with a JPEG magic number',
    artwork.body.subarray(0, 3).equals(Buffer.from([0xff, 0xd8, 0xff]))
  );
}

console.log(`Smoke-testing ${baseUrl} ...\n`);
run()
  .then(() => {
    console.log(allPassed ? '\nAll checks passed.' : '\nSome checks FAILED.');
    process.exit(allPassed ? 0 : 1);
  })
  .catch((error) => {
    console.error('\nSmoke test errored out:', error.message);
    console.error(`Is a server actually running at ${baseUrl}? See README.md's "Running" section.`);
    process.exit(1);
  });
