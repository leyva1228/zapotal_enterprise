import { chromium } from "playwright";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();

async function check(path, name) {
  await page.goto("http://localhost:5173" + path, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForTimeout(2500);
  const data = await page.evaluate(() => {
    const result = {};
    // Todos los elementos con max-width explicito
    const all = document.querySelectorAll("*");
    const seen = new Set();
    for (const el of all) {
      const cs = window.getComputedStyle(el);
      const mw = cs.maxWidth;
      if (mw && mw !== "none" && /^\d+px$/.test(mw)) {
        const cls = el.className || el.tagName;
        const sig = cls.toString().split(" ")[0] + "@" + mw;
        if (!seen.has(sig) && seen.size < 10) {
          seen.add(sig);
          result[sig] = { tag: el.tagName, cls: cls.toString().slice(0, 60), maxW: mw, padL: cs.paddingLeft, padR: cs.paddingRight };
        }
      }
    }
    return result;
  });
  console.log(`\n=== ${name} (${path}) ===`);
  for (const [k, v] of Object.entries(data)) {
    console.log(`  ${k}: maxW=${v.maxW} padL=${v.padL} padR=${v.padR}`);
  }
}

await check("/noticias", "Noticias (lista)");
await check("/eventos", "Eventos (lista)");
await check("/noticias/50", "Detalle Noticia");
await check("/eventos/34", "Detalle Evento");

await browser.close();
