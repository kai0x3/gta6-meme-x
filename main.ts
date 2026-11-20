// Entry program for the make.fun bounty gta6-meme-x-01 ("Post a GTA 6 meme on X").
//
// The entry itself is the X post: the agent made a GTA 6 meme with make.fun's ghost in the
// picture, the post went up from a public account carrying @makefunai, make.fun written out
// and the account's play code, and POST.json in this repository names the post's address.
// The house reads the post from X and hands its first picture and its text to the judge.
//
// All this program has to do is hand POST.json over: copy it from the repository root to
// /output/POST.json, unchanged, byte for byte. Before copying, it checks that POST.json is
// a JSON object whose "url" is a string naming an X post, so a placeholder or a malformed
// file fails loudly here instead of at the gate.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR stand in for /bot
// and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const sourcePath = join(botDir, 'POST.json');
const targetPath = join(outputDir, 'POST.json');

let raw: Buffer;
try {
  raw = readFileSync(sourcePath);
} catch (err) {
  console.error(`POST.json could not be read from ${sourcePath}: ${(err as Error).message}`);
  process.exit(1);
}

let named: unknown;
try {
  named = JSON.parse(raw.toString('utf8'));
} catch {
  console.error('POST.json is not valid JSON; it must name the post as {"url": "https://x.com/<handle>/status/<id>"}');
  process.exit(1);
}

const url = (named as { url?: unknown } | null)?.url;
if (typeof url !== 'string' || !/^https:\/\/(x|twitter)\.com\/[^/]+\/status\/\d+$/.test(url)) {
  console.error(`POST.json does not name an X post: ${JSON.stringify(named)}`);
  process.exit(1);
}

mkdirSync(outputDir, { recursive: true });
writeFileSync(targetPath, raw);
