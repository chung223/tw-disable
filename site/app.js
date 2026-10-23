"use strict";

const LEVEL_LABELS = {
  central: "中央規定",
  mixed: "中央基準＋縣市加碼",
  local: "縣市自辦",
  private: "民間資源",
};
const CONFIDENCE_LABELS = {
  medium: "待核實：來源較舊或僅有摘要",
  low: "待核實：二手資料",
};
const SCOPE_ORDER = { county: 0, interop: 1, nationwide: 2 };

const els = {
  form: document.getElementById("filters"),
  county: document.getElementById("county"),
  q: document.getElementById("q"),
  categories: document.getElementById("categories"),
  countyInfo: document.getElementById("county-info"),
  status: document.getElementById("status"),
  list: document.getElementById("list"),
  generated: document.getElementById("generated"),
};

let data = null;
let countyNames = {};
let countyOrder = {};

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

function hostname(url) {
  try { return new URL(url).hostname; } catch { return url; }
}

function readState() {
  return {
    county: els.county.value,
    q: els.q.value.trim(),
    categories: [...els.categories.querySelectorAll("input:checked")].map((i) => i.value),
    scopes: [...els.form.querySelectorAll('input[name="scope"]:checked')].map((i) => i.value),
  };
}

function writeHash(state) {
  const p = new URLSearchParams();
  if (state.county) p.set("county", state.county);
  if (state.q) p.set("q", state.q);
  if (state.categories.length) p.set("cat", state.categories.join(","));
  if (state.scopes.length !== 3) p.set("scope", state.scopes.join(","));
  const hash = p.toString();
  history.replaceState(null, "", hash ? `#${hash}` : location.pathname + location.search);
}

function applyHash() {
  const raw = location.hash.slice(1);
  // 也接受只有縣市代碼的短網址，例如 #taipei
  if (countyNames[raw]) { els.county.value = raw; return; }
  const p = new URLSearchParams(raw);
  if (p.has("county") && countyNames[p.get("county")]) els.county.value = p.get("county");
  if (p.has("q")) els.q.value = p.get("q");
  const cats = new Set((p.get("cat") || "").split(",").filter(Boolean));
  els.categories.querySelectorAll("input").forEach((i) => { i.checked = cats.has(i.value); });
  if (p.has("scope")) {
    const scopes = new Set(p.get("scope").split(","));
    els.form.querySelectorAll('input[name="scope"]').forEach((i) => { i.checked = scopes.has(i.value); });
  }
}

function searchText(b) {
  return [
    b.name, b.summary, b.benefit, b.how_to_apply, b.notes, b.provider,
    countyNames[b.county_id], ...(b.eligibility || []), ...(b.target_groups || []),
  ].join(" ").toLowerCase();
}

function matches(b, state, terms) {
  if (!state.scopes.includes(b.scope)) return false;
  if (state.county) {
    if (b.scope === "county" && b.county_id !== state.county) return false;
    if (b.scope === "interop" && !(b.counties || []).includes(state.county)) return false;
  }
  if (state.categories.length && !state.categories.includes(b.category)) return false;
  if (terms.length) {
    const text = b._text;
    if (!terms.every((t) => text.includes(t))) return false;
  }
  return true;
}

function scopeBadge(b) {
  if (b.scope === "county") return countyNames[b.county_id];
  if (b.scope === "interop") return `跨縣市：${(b.counties || []).map((c) => countyNames[c] || c).join("、")}`;
  return "全國通用";
}

function list(items) {
  if (!items || !items.length) return "";
  return `<ul>${items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>`;
}

function row(label, html) {
  return html ? `<dt>${label}</dt><dd>${html}</dd>` : "";
}

function renderCard(b) {
  const warn = CONFIDENCE_LABELS[b.confidence];
  const badges = [
    `<span class="badge scope">${esc(scopeBadge(b))}</span>`,
    `<span class="badge">${esc(LEVEL_LABELS[b.level] || b.level)}</span>`,
    warn ? `<span class="badge warn">${esc(warn)}</span>` : "",
  ].join("");
  const sources = (b.source_urls || [])
    .map((u, i) => `<li><a href="${esc(u)}" target="_blank" rel="noopener">來源 ${i + 1}：${esc(hostname(u))}</a></li>`)
    .join("");
  const date = b.source_date && b.source_date !== "unknown" ? `資料年份 ${esc(b.source_date)}` : "資料年份不明";
  return `
    <article class="card">
      <h4>${esc(b.name)}</h4>
      <div class="badges">${badges}</div>
      <p class="summary">${esc(b.summary)}</p>
      <details>
        <summary>申請資格與方式</summary>
        <dl>
          ${row("補助內容", esc(b.benefit))}
          ${row("申請資格", list(b.eligibility))}
          ${row("申請方式", esc(b.how_to_apply))}
          ${row("應備文件", list(b.documents))}
          ${row("聯絡電話", esc(b.contact))}
          ${row("提供單位", esc(b.provider))}
          ${row("注意事項", esc(b.notes))}
          ${row("資料來源", `<ul>${sources}</ul><span class="muted">${date}</span>`)}
        </dl>
      </details>
    </article>`;
}

function renderCountyInfo(cid) {
  const c = data.counties.find((x) => x.county_id === cid);
  if (!c) { els.countyInfo.hidden = true; return; }
  const parts = [
    c.agency_url ? `<a href="${esc(c.agency_url)}" target="_blank" rel="noopener">${esc(c.agency)}</a>` : esc(c.agency),
    c.phone ? `電話 ${esc(c.phone)}` : "",
  ].filter(Boolean).join("　");
  els.countyInfo.innerHTML = `<h2>${esc(c.county_name)}</h2><p>主管機關：${parts}</p>`;
  els.countyInfo.hidden = false;
}

function render() {
  const state = readState();
  writeHash(state);
  if (state.county) renderCountyInfo(state.county); else els.countyInfo.hidden = true;

  const terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
  const hits = data.benefits
    .filter((b) => matches(b, state, terms))
    .sort((a, b) =>
      (SCOPE_ORDER[a.scope] - SCOPE_ORDER[b.scope]) ||
      ((countyOrder[a.county_id] ?? 99) - (countyOrder[b.county_id] ?? 99)));

  const groups = data.categories
    .map((cat) => ({ cat, items: hits.filter((b) => b.category === cat.id) }))
    .filter((g) => g.items.length);

  els.status.textContent = hits.length
    ? `共 ${hits.length} 筆${state.county ? `（${countyNames[state.county]}及可使用的全國、跨縣市資源）` : ""}`
    : "找不到符合條件的福利，請放寬篩選條件或換個關鍵字。";
  els.list.innerHTML = groups.map((g) => `
    <section class="group" aria-labelledby="g-${g.cat.id}">
      <h3 id="g-${g.cat.id}">${esc(g.cat.name)}（${g.items.length}）</h3>
      ${g.items.map(renderCard).join("")}
    </section>`).join("");
}

function init(json) {
  data = json;
  data.counties.forEach((c, i) => {
    countyNames[c.county_id] = c.county_name;
    countyOrder[c.county_id] = i;
    els.county.insertAdjacentHTML("beforeend",
      `<option value="${esc(c.county_id)}">${esc(c.county_name)}</option>`);
  });
  data.benefits.forEach((b) => { b._text = searchText(b); });
  els.categories.innerHTML = data.categories.map((c) => `
    <label class="chip" title="${esc(c.description)}">
      <input type="checkbox" name="category" value="${esc(c.id)}"> <span>${esc(c.name)}</span>
    </label>`).join("");
  els.generated.textContent = ` 資料整理日期：${data.generated_at}。`;

  applyHash();
  els.form.addEventListener("input", render);
  els.form.addEventListener("submit", (e) => { e.preventDefault(); render(); });
  els.form.addEventListener("reset", () => setTimeout(render, 0));
  render();
}

// 單檔版本會把資料內嵌在 #benefits-data，否則讀取 data/benefits.json
const inlineData = document.getElementById("benefits-data");
(inlineData
  ? Promise.resolve(JSON.parse(inlineData.textContent))
  : fetch("data/benefits.json").then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); }))
  .then(init)
  .catch(() => { els.status.textContent = "資料載入失敗，請稍後再試。"; });
