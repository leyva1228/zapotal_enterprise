import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();
const errors = [];
page.on("pageerror", (err) => errors.push("PAGEERROR: " + err.message));
page.on("console", (msg) => {
  if (msg.type() === "error" && !msg.text().includes("401") && !msg.text().includes("ERR_NAME")) {
    errors.push("CONSOLE_ERROR: " + msg.text());
  }
});

console.log("=== /admin (login) ===");
await page.goto("http://localhost:5173/login", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(1500);
await page.fill('input[type=email]', 'admin@zapotal.com');
await page.fill('input[type=password]', 'admin1234');
await page.click('button[type=submit]');
await page.waitForTimeout(2000);
console.log("URL despues de login:", page.url());

console.log("\n=== /admin/noticias (modal crear) ===");
await page.goto("http://localhost:5173/admin/noticias", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2000);
// Buscar el boton "Nueva noticia" o "+"
const newBtn = await page.$('button:has-text("Nueva"), button:has-text("Agregar"), button:has-text("Crear")');
if (newBtn) {
  await newBtn.click();
  await page.waitForTimeout(1500);
  const hasSubir = await page.$('.subir-multimedia');
  console.log("Componente SubirMultimedia presente en modal noticias:", !!hasSubir);
  // Tomar screenshot del modal
  await page.screenshot({ path: "verify-subir-noticias.png", fullPage: false });
}

console.log("\n=== /admin/eventos (modal crear) ===");
await page.goto("http://localhost:5173/admin/eventos", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2000);
const newBtnEv = await page.$('button:has-text("Nuevo"), button:has-text("Agregar"), button:has-text("Crear")');
if (newBtnEv) {
  await newBtnEv.click();
  await page.waitForTimeout(1500);
  const hasSubirEv = await page.$('.subir-multimedia');
  console.log("Componente SubirMultimedia presente en modal eventos:", !!hasSubirEv);
  await page.screenshot({ path: "verify-subir-eventos.png", fullPage: false });
}

console.log("\n=== Errores JS ===");
if (errors.length === 0) console.log("  (ninguno)");
else errors.forEach((e) => console.log(" ", e));

await browser.close();
