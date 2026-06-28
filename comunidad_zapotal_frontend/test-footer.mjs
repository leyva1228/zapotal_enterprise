import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();
await page.goto("http://localhost:5173/", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2500);
const data = await page.evaluate(() => {
  const cols = document.querySelectorAll(".footer-container > *");
  return Array.from(cols).map((c) => {
    const h = c.querySelector("h2, h3");
    const img = c.querySelector(".libro-reclamaciones-img");
    return { title: h ? h.innerText : null, hasBook: !!img };
  });
});
console.log("=== Footer ===");
for (const c of data) console.log(`  ${c.title}: hasBook=${c.hasBook}`);
await browser.close();
