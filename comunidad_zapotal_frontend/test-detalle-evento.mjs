import { chromium } from "playwright";

const browser = await chromium.launch();
const context = await browser.newContext();
const page = await context.newPage();

const errors = [];
const requests = [];
page.on("pageerror", (err) => errors.push("PAGEERROR: " + err.message));
page.on("console", (msg) => {
  if (msg.type() === "error") errors.push("CONSOLE_ERROR: " + msg.text());
  if (msg.type() === "warning" && msg.text().includes("vistas")) errors.push("CONSOLE_WARN: " + msg.text());
});
page.on("response", (res) => {
  const url = res.url();
  if (url.includes("/api/")) {
    requests.push(`${res.status()} ${res.request().method()} ${url.replace("http://127.0.0.1:8000", "")}`);
  }
});

console.log("=== Navegando a http://localhost:5173/eventos/34 ===");
try {
  await page.goto("http://localhost:5173/eventos/34", { waitUntil: "networkidle", timeout: 30000 });
} catch (e) {
  console.log("ERROR en goto:", e.message);
}

await page.waitForTimeout(3000);

const title = await page.title();
console.log("Title:", title);

const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 500));
console.log("Body text (primeros 500 chars):");
console.log(bodyText);

const errorContainer = await page.$(".error-container");
const errorText = errorContainer ? await errorContainer.innerText() : null;
console.log("Error container:", errorText);

const viewsText = await page.evaluate(() => {
  const el = document.querySelector(".yt-desc-views");
  return el ? el.innerText : "NO ENCONTRADO";
});
console.log("Views text:", viewsText);

const fechaText = await page.evaluate(() => {
  const el = document.querySelector(".yt-desc-fecha");
  return el ? el.innerText : "NO ENCONTRADO";
});
console.log("Fecha text:", fechaText);

console.log("\n=== Peticiones API ===");
requests.forEach((r) => console.log(" ", r));

console.log("\n=== Errores JS ===");
if (errors.length === 0) console.log("  (ninguno)");
else errors.forEach((e) => console.log(" ", e));

await page.screenshot({ path: "detalle-evento.png", fullPage: true });
console.log("\nScreenshot: detalle-evento.png");

await browser.close();
