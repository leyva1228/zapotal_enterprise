import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();

async function check(path, name) {
  await page.goto("http://localhost:5173" + path, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2500);
  const data = await page.evaluate(() => {
    const dates = Array.from(document.querySelectorAll(".hero-fecha, .fecha-evento, .nc-card__date, .yt-desc-fecha, .yt-canal-fecha")).slice(0, 6).map((d) => d.innerText);
    const shares = document.querySelectorAll(".nc-card__share, .evento-share-btn, .yt-share-btn");
    const sharesConOnClick = Array.from(shares).filter((b) => b.onclick !== null).length;
    return { dates, nShares: shares.length, sharesConOnClick };
  });
  console.log(`\n=== ${name} (${path}) ===`);
  console.log("Fechas (primeras 6):", data.dates);
  console.log("Botones compartir:", data.nShares, "con onClick:", data.sharesConOnClick);
}

await check("/eventos", "Eventos (lista)");
await check("/noticias", "Noticias (lista)");
await check("/eventos/34", "Detalle Evento");
await check("/noticias/50", "Detalle Noticia");

await browser.close();
