import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();
await page.goto("http://localhost:5173/noticias", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2500);

const data = await page.evaluate(() => {
  const dates = Array.from(document.querySelectorAll(".nc-card__date"))
    .slice(0, 5)
    .map((d) => d.innerText);
  const shares = Array.from(document.querySelectorAll(".nc-card__share"));
  return { dates, nShares: shares.length, hasOnClick: shares.every((b) => b.onclick !== null) };
});
console.log("=== Noticias ===");
console.log("Fechas (primeras 5):", data.dates);
console.log("Botones compartir:", data.nShares, "todos con onClick:", data.hasOnClick);

console.log("\n=== Click test en el primer boton compartir ===");
await page.locator(".nc-card__share").first().click();
await page.waitForTimeout(1000);
console.log("Click ejecutado OK (sin error de Playwright)");

await browser.close();
