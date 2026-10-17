#!/usr/bin/env node
// Turns measured numbers into a standalone HTML page: a before/after bar chart plus the same
// numbers as a table (so colour is never the only carrier). Usage:
//   node before-after-chart.mjs data.json out.html
// data.json: { title, subtitle?, unit, scale?: "auto"|"linear"|"log", lowerIsBetter?: true,
//              groups: [{ label, before, after }], method: "how it was measured, one line",
//              caveat: "what this does NOT show, one line", source: "path of the raw output file" }
// Every number must come from a saved raw output file named in `source`. This script invents nothing.
import fs from "node:fs";

const [inFile, outFile] = process.argv.slice(2);
if (!inFile || !outFile) { console.error("usage: before-after-chart.mjs data.json out.html"); process.exit(1); }
const d = JSON.parse(fs.readFileSync(inFile, "utf8"));
for (const k of ["title", "unit", "groups", "method", "caveat", "source"]) if (!d[k]) { console.error(`data.json is missing "${k}"`); process.exit(1); }
const lowerIsBetter = d.lowerIsBetter !== false;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const vals = d.groups.flatMap((g) => [g.before, g.after]);
if (vals.some((v) => !(v > 0))) { console.error("every before/after must be a positive number"); process.exit(1); }
const ratioSpread = Math.max(...vals) / Math.min(...vals);
const scale = d.scale === "linear" || d.scale === "log" ? d.scale : ratioSpread > 50 ? "log" : "linear";

const fmt = (v) => (v >= 100 ? Math.round(v).toLocaleString("en-GB") : v >= 10 ? String(Math.round(v * 10) / 10) : String(Math.round(v * 100) / 100));
// two significant figures for the ratio: never imply more precision than three timed runs give
const times = (r) => { const s = r >= 100 ? Math.round(r / 10) * 10 : r >= 10 ? Math.round(r) : Math.round(r * 10) / 10; return `${s.toLocaleString("en-GB")}x`; };

const W = 880, labelW = 250, barX = labelW + 10, barW = W - barX - 120, rowH = 78, top = 44;
const H = top + d.groups.length * rowH + 50;
const lo = Math.min(...vals) / 2, hi = Math.max(...vals);
const x = (v) => scale === "log" ? barX + (Math.log10(v / lo) / Math.log10(hi / lo)) * barW : barX + (v / hi) * barW;
const ticks = scale === "log"
  ? [...Array(12).keys()].map((i) => 10 ** (i - 2)).filter((t) => t >= lo && t <= hi * 1.001)
  : [0, 0.25, 0.5, 0.75, 1].map((f) => f * hi);

const rows = d.groups.map((g, i) => {
  const y = top + i * rowH;
  const better = lowerIsBetter ? g.before / g.after : g.after / g.before;
  const x0 = scale === "log" ? barX : barX;
  return `
  <text x="0" y="${y + 24}" class="lbl">${esc(g.label)}</text>
  <rect x="${x0}" y="${y + 6}" width="${Math.max(2, x(g.before) - x0)}" height="22" rx="3" class="before"/>
  <text x="${x(g.before) + 8}" y="${y + 22}" class="val">${fmt(g.before)} ${esc(d.unit)}</text>
  <rect x="${x0}" y="${y + 34}" width="${Math.max(2, x(g.after) - x0)}" height="22" rx="3" class="after"/>
  <text x="${x(g.after) + 8}" y="${y + 50}" class="val">${fmt(g.after)} ${esc(d.unit)}</text>
  <text x="${W}" y="${y + 38}" text-anchor="end" class="chip">${times(better)} ${better >= 1 ? "better" : "worse"}</text>`;
}).join("");
const grid = ticks.map((t) => `<line x1="${x(t)}" x2="${x(t)}" y1="${top - 14}" y2="${H - 44}" class="grid"/><text x="${x(t)}" y="${H - 26}" text-anchor="middle" class="tick">${fmt(t)}</text>`).join("");

const table = d.groups.map((g) => {
  const r = lowerIsBetter ? g.before / g.after : g.after / g.before;
  return `<tr><td>${esc(g.label)}</td><td>${fmt(g.before)} ${esc(d.unit)}</td><td>${fmt(g.after)} ${esc(d.unit)}</td><td>${times(r)}</td></tr>`;
}).join("");

fs.writeFileSync(outFile, `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(d.title)}</title>
<style>
:root{--ink:#1c2420;--muted:#55605a;--grid:#d9e0da;--before:#a64b2a;--after:#1f7a4d}
body{margin:0;padding:22px;background:#fff;font-family:ui-rounded,system-ui,sans-serif;color:var(--ink);width:${W}px}
h1{font-size:19px;margin:0 0 4px}.sub{font-size:13px;color:var(--muted);margin:0 0 6px}
svg{display:block;margin-top:8px}.lbl{font-size:14px;font-weight:700;fill:var(--ink)}.val{font-size:13px;font-weight:700;fill:var(--ink)}
.before{fill:var(--before)}.after{fill:var(--after)}.grid{stroke:var(--grid);stroke-width:1}.tick{font-size:11px;fill:var(--muted)}
.chip{font-size:13px;font-weight:800;fill:var(--after)}
.legend{display:flex;gap:18px;font-size:13px;color:var(--muted);margin:2px 0 10px}.legend i{display:inline-block;width:13px;height:13px;border-radius:3px;margin-right:6px;vertical-align:-2px}
table{border-collapse:collapse;font-size:13px;width:100%;margin-top:12px}td,th{text-align:left;padding:5px 8px;border-top:1px solid var(--grid)}th{color:var(--muted);font-weight:600}
.note{font-size:12px;color:var(--muted);margin:10px 0 0;line-height:1.45}.note b{color:var(--ink)}
</style>
<h1>${esc(d.title)}</h1>${d.subtitle ? `<p class="sub">${esc(d.subtitle)}</p>` : ""}
<div class="legend"><span><i style="background:var(--before)"></i>Before</span><span><i style="background:var(--after)"></i>After</span><span>${lowerIsBetter ? "Lower is better" : "Higher is better"} · ${scale === "log" ? "log scale (each gridline is 10x)" : "linear scale"}</span></div>
<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(d.title)}: before and after, values in the table below">${grid}${rows}</svg>
<table><tr><th>Measurement</th><th>Before</th><th>After</th><th>Change</th></tr>${table}</table>
<p class="note"><b>Method:</b> ${esc(d.method)}</p>
<p class="note"><b>Does not show:</b> ${esc(d.caveat)}</p>
<p class="note"><b>Raw output:</b> ${esc(d.source)}</p>
`);
console.log(`wrote ${outFile} (${scale} scale, ${d.groups.length} measurements)`);
