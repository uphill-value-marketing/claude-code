// Renders index.html frame-by-frame with Playwright and pipes PNGs into ffmpeg.
// Usage: node render.js                -> out/frames.mp4 (video only)
//        node render.js --stills 1,5.2  -> out/still_<t>.png
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
const MIME = { '.html': 'text/html', '.json': 'application/json', '.svg': 'image/svg+xml', '.ttf': 'font/ttf', '.js': 'text/javascript' };

function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      fs.readFile(f, (err, buf) => {
        if (err) { rsp.writeHead(404); return rsp.end(); }
        rsp.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); rsp.end(buf);
      });
    }).listen(0, '127.0.0.1', () => res(srv));
  });
}

(async () => {
  const srv = await serve();
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--disable-web-security'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.error('[page error]', e.message));
  await page.goto(`http://127.0.0.1:${port}/index.html?render`);
  await page.waitForFunction('window.READY === true');
  const { DUR, FPS } = await page.evaluate(() => ({ DUR: window.DUR, FPS: window.FPS }));
  fs.mkdirSync(path.join(ROOT, 'out'), { recursive: true });

  const grab = async (t, samples) => {
    const b64 = await page.evaluate(([t, s]) => { window.render(t, s); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, [t, samples]);
    return Buffer.from(b64, 'base64');
  };

  const si = process.argv.indexOf('--stills');
  if (si > 0) {
    for (const t of process.argv[si + 1].split(',').map(Number)) {
      fs.writeFileSync(path.join(ROOT, 'out', `still_${t}.png`), await grab(t, 1));
    }
  } else {
    const n = Math.round(DUR * FPS);
    const ff = spawn(FFMPEG, ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', path.join(ROOT, 'out', 'frames.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < n; i++) {
      const png = await grab(i / FPS, 4);
      if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log(`frame ${i}/${n}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close(); srv.close();
})();
