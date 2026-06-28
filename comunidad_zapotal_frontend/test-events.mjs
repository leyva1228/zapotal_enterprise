import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();
await page.goto("http://localhost:5173/eventos", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2500);
const data = await page.evaluate(() => {
  const tarjeta = document.querySelector(".tarjeta-evento");
  if (!tarjeta) return null;
  const cs = window.getComputedStyle(tarjeta);
  // Buscar la primera etiqueta y el primer share
  const etiqueta = tarjeta.querySelector(".etiqueta-evento");
  const share = tarjeta.querySelector(".evento-share-btn");
  const eRect = etiqueta ? etiqueta.getBoundingClientRect() : null;
  const sRect = share ? share.getBoundingClientRect() : null;
  const tRect = tarjeta.getBoundingClientRect();
  return {
    tarjetaRight: Math.round(tRect.right),
    etiqueta: eRect ? { right: Math.round(eRect.right), top: Math.round(eRect.top), text: etiqueta.innerText } : null,
    share: sRect ? { right: Math.round(sRect.right), top: Math.round(sRect.top) } : null,
  };
});
console.log("Tarjeta right:", data.tarjetaRight);
console.log("Etiqueta (PROXIMO):", data.etiqueta);
console.log("Boton share (TALLER):", data.share);
if (data.etiqueta) {
  const distRight = data.tarjetaRight - data.etiqueta.right;
  const distLeft = data.etiqueta.right - 0;
  console.log(`  dist al borde derecho: ${distRight}px, al izquierdo: ~${data.etiqueta.right}px`);
}
if (data.share) {
  const distRight = data.tarjetaRight - data.share.right;
  console.log(`  dist al borde derecho: ${distRight}px`);
}
await page.screenshot({ path: "verify-evento-tarjeta.png", fullPage: false, clip: { x: 0, y: 0, width: 1280, height: 1200 } });
await browser.close();
