// Checks pr-948.html in a headless browser.
// At 1280 and 1920, in 基线 and PR 948:
// - no two visible cards overlap
// - every baseline card keeps the same box (relative to the baseline columns)
//   in both modes
// Requires puppeteer-core and Chrome. Example:
//   CHROME_PATH=/usr/bin/google-chrome-stable node site/scripts/check-pr948-layout.mjs

import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import path from "node:path";

const require = createRequire(import.meta.url);
const puppeteer = require("puppeteer-core");

const pagePath = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../static/architecture-flow/pr-948.html",
);
const chrome = process.env.CHROME_PATH || "/usr/bin/google-chrome-stable";
const widths = [1280, 1920];
const tolerance = 1;

function overlapArea(a, b) {
  const w = Math.min(a.r, b.r) - Math.max(a.l, b.l);
  const h = Math.min(a.b, b.b) - Math.max(a.t, b.t);
  if (w <= tolerance || h <= tolerance) return 0;
  return w * h;
}

async function readBoxes(page) {
  return page.evaluate(() => {
    const scroll = document.getElementById("diagram-scroll");
    scroll.scrollLeft = 0;
    const cols = document.getElementById("cols").getBoundingClientRect();
    const laneEl = document.getElementById("col-deploy");
    const lane = laneEl.getClientRects().length ? laneEl.getBoundingClientRect() : null;
    const cards = [...document.querySelectorAll(".card")]
      .filter((el) => el.getClientRects().length > 0)
      .map((el) => {
        const r = el.getBoundingClientRect();
        return {
          id: el.id,
          title: (el.querySelector(".card-title") || {}).textContent || "",
          baseline: !el.closest("#col-deploy"),
          l: r.left,
          t: r.top,
          r: r.right,
          b: r.bottom,
          x: r.left - cols.left,
          y: r.top - cols.top,
          w: r.width,
          h: r.height,
        };
      });
    return {
      cols: { l: cols.left, r: cols.right, w: cols.width },
      lane: lane ? { l: lane.left, r: lane.right, w: lane.width } : null,
      scrollLeft: scroll.scrollLeft,
      cards,
    };
  });
}

function checkOverlaps(boxes, label) {
  const errors = [];
  const seen = new Map();
  for (const card of boxes.cards) {
    if (seen.has(card.title)) {
      errors.push(`${label}: duplicate visible title 「${card.title}」 on #${seen.get(card.title)} and #${card.id}`);
    } else {
      seen.set(card.title, card.id);
    }
  }
  for (let i = 0; i < boxes.cards.length; i++) {
    for (let j = i + 1; j < boxes.cards.length; j++) {
      const area = overlapArea(boxes.cards[i], boxes.cards[j]);
      if (area > 0) {
        errors.push(
          `${label}: #${boxes.cards[i].id} overlaps #${boxes.cards[j].id} (${Math.round(area)}px²)`,
        );
      }
    }
  }
  if (boxes.lane && boxes.lane.l < boxes.cols.r - tolerance) {
    errors.push(
      `${label}: deploy lane starts at ${Math.round(boxes.lane.l)} which is left of the baseline columns' right edge ${Math.round(boxes.cols.r)}`,
    );
  }
  return errors;
}

function checkPositions(base, pr, width) {
  const errors = [];
  const prById = new Map(pr.cards.filter((c) => c.baseline).map((c) => [c.id, c]));
  for (const card of base.cards) {
    const other = prById.get(card.id);
    if (!other) {
      errors.push(`${width}: baseline card #${card.id} is missing in PR 948 mode`);
      continue;
    }
    const dx = Math.abs(card.x - other.x);
    const dy = Math.abs(card.y - other.y);
    const dw = Math.abs(card.w - other.w);
    const dh = Math.abs(card.h - other.h);
    if (dx > tolerance || dy > tolerance || dw > tolerance || dh > tolerance) {
      errors.push(
        `${width}: #${card.id} moved between 基线 and PR 948 ` +
          `(Δx ${dx.toFixed(1)} Δy ${dy.toFixed(1)} Δw ${dw.toFixed(1)} Δh ${dh.toFixed(1)})`,
      );
    }
  }
  return errors;
}

const browser = await puppeteer.launch({
  executablePath: chrome,
  headless: "new",
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--hide-scrollbars"],
});
const page = await browser.newPage();
await page.evaluateOnNewDocument(() => {
  localStorage.setItem("burncloud-arch-theme", "dark");
});
const failures = [];
for (const width of widths) {
  await page.setViewport({ width, height: 900, deviceScaleFactor: 1 });
  await page.goto("file://" + pagePath, { waitUntil: "load" });
  await page.evaluate(() => (document.fonts ? document.fonts.ready : null));
  await new Promise((r) => setTimeout(r, 400));
  const pr = await readBoxes(page);
  failures.push(...checkOverlaps(pr, `${width} PR 948`));
  await page.click('.view-toggle button[data-view="base"]');
  await new Promise((r) => setTimeout(r, 400));
  const base = await readBoxes(page);
  failures.push(...checkOverlaps(base, `${width} 基线`));
  failures.push(...checkPositions(base, pr, width));
  console.log(
    `${width}: 基线 ${base.cards.length} cards, PR 948 ${pr.cards.length} cards, ` +
      `columns ${Math.round(pr.cols.w)}px, lane starts ${pr.lane ? Math.round(pr.lane.l - pr.cols.r) : "hidden"}px to the right`,
  );
}
await browser.close();
if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
console.log("ok: no overlapping cards, baseline positions match");
