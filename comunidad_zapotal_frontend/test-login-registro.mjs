import { chromium } from "playwright";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();

const errors = [];
page.on("pageerror", (err) => errors.push("PAGEERROR: " + err.message));
page.on("console", (msg) => {
  if (msg.type() === "error" && !msg.text().includes("401") && !msg.text().includes("ERR_NAME") && !msg.text().includes("font-size:0")) {
    errors.push("CONSOLE_ERROR: " + msg.text());
  }
});

async function inspect(path, name) {
  console.log(`\n=== ${name} (${path}) ===`);
  await page.goto("http://localhost:5173" + path, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForTimeout(2500);

  const data = await page.evaluate(() => {
    // Hero: cualquier section con background-image
    const heroes = document.querySelectorAll("section, aside");
    const heroWithBg = Array.from(heroes).find((el) => {
      const bg = window.getComputedStyle(el).backgroundImage;
      return bg && bg !== "none" && bg.includes("url");
    });
    const heroBg = heroWithBg ? window.getComputedStyle(heroWithBg).backgroundImage : null;

    // Card con sombra (debe ser NONE ahora)
    const cardSelectors = [".rg-card", "[class*='shadow-card']", ".shadow-card"];
    let cardWithShadow = null;
    for (const sel of cardSelectors) {
      const el = document.querySelector(sel);
      if (el) {
        const boxShadow = window.getComputedStyle(el).boxShadow;
        if (boxShadow && boxShadow !== "none") {
          cardWithShadow = { selector: sel, boxShadow };
          break;
        }
      }
    }

    // Elements que NO deberian existir (rg-step, rg-eyebrow "PASO")
    const rgStep = document.querySelector(".rg-step");
    const rgEyebrow = document.querySelector(".rg-eyebrow");
    const rgShield = document.querySelector(".rg-shield");

    // Title
    const h2 = document.querySelector("h2");
    const h2Text = h2 ? h2.innerText : null;

    // Hero title (h1)
    const h1 = document.querySelector("h1");
    const h1Text = h1 ? h1.innerText : null;

    return { heroBg, cardWithShadow, hasRgStep: !!rgStep, hasRgEyebrow: !!rgEyebrow, hasRgShield: !!rgShield, h2Text, h1Text };
  });

  console.log("  Hero bg imagen:", data.heroBg?.includes("Union-fondo") ? "OK" : "FALTA");
  console.log("  h1 (hero):", JSON.stringify(data.h1Text));
  console.log("  h2 (form):", JSON.stringify(data.h2Text));
  console.log("  Card con sombra:", data.cardWithShadow ? "SI (mal): " + JSON.stringify(data.cardWithShadow) : "NO (bien)");
  console.log("  .rg-step existe:", data.hasRgStep ? "SI (mal)" : "NO (bien)");
  console.log("  .rg-eyebrow existe:", data.hasRgEyebrow ? "SI (mal)" : "NO (bien)");
  console.log("  .rg-shield existe:", data.hasRgShield ? "SI (mal)" : "NO (bien)");
  await page.screenshot({ path: `verify-${name}.png`, fullPage: false });
}

await inspect("/login", "login");
await inspect("/registro", "registro");

console.log("\n=== Errores JS relevantes ===");
if (errors.length === 0) console.log("  (ninguno)");
else errors.forEach((e) => console.log(" ", e));

await browser.close();
