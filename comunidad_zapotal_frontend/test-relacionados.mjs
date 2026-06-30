import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();

async function check(path, name) {
  await page.goto("http://localhost:5173" + path, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2500);
  const data = await page.evaluate(() => {
    const sidebar = document.querySelector(".detalle-sidebar");
    const main = document.querySelector(".detalle-contenido-principal");
    const sidebarRect = sidebar ? sidebar.getBoundingClientRect() : null;
    const mainRect = main ? main.getBoundingClientRect() : null;
    return {
      sidebar: sidebarRect ? { h: Math.round(sidebarRect.height) } : null,
      main: mainRect ? { h: Math.round(mainRect.height) } : null,
      ratio: (sidebarRect && mainRect) ? Math.round(sidebarRect.height / mainRect.height * 100) / 100 : null,
    };
  });
  console.log(`\n=== ${name} (${path}) ===`);
  console.log("  Sidebar height:", data.sidebar?.h, "px");
  console.log("  Main height:   ", data.main?.h, "px");
  console.log("  Ratio:         ", data.ratio, "(sidebar/main)");
  console.log(data.ratio >= 0.95 && data.ratio <= 1.05 ? "  Sidebar iguala al main (estirado) ✓" : "  Sidebar NO iguala al main");
}

await check("/noticias/50", "Detalle Noticia");
await check("/eventos/34", "Detalle Evento");

await browser.close();
