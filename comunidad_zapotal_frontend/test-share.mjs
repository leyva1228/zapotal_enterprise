import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();

async function check(path, name) {
  await page.goto("http://localhost:5173" + path, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2000);
  const data = await page.evaluate(() => {
    const sels = [".nc-card__share", ".evento-share-btn", ".yt-share-btn"];
    const out = {};
    for (const sel of sels) {
      const els = document.querySelectorAll(sel);
      if (els.length > 0) {
        out[sel] = [];
        for (const el of els) {
          const cs = window.getComputedStyle(el);
          out[sel].push({ color: cs.color });
        }
      }
    }
    return out;
  });
  console.log(`\n=== ${name} (${path}) ===`);
  for (const [sel, vals] of Object.entries(data)) {
    console.log(`  ${sel}: count=${vals.length}`);
    if (vals[0]) console.log(`    base color: ${vals[0].color}`);
  }
}

await check("/noticias", "Noticias");
await check("/eventos", "Eventos");
await check("/noticias/50", "Detalle Noticia");
await check("/eventos/34", "Detalle Evento");

await browser.close();
