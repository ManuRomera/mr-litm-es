/** MR- Legend in the Mist en español: compendios (Babele), plantilla «Cómo jugar» y textos fijos que el sistema no pasa por i18n. */
const ID = "mr-litm-es";
const SISTEMA = "mist-engine-fvtt";
let literales = {};
let patrones = [];

// Babele: traduce los compendios sin tocar sus datos. «litm» sustituye cada cadena que coincida con el diccionario del documento
Hooks.once("babele.init", babele => {
  const profundo = (v, d) => {
    if (typeof v === "string") return Object.hasOwn(d, v) ? d[v] : v;
    if (Array.isArray(v)) return v.map(x => profundo(x, d));
    if (v && typeof v === "object") return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, profundo(x, d)]));
    return v;
  };
  babele.registerConverters({ litm: (valor, d) => (d ? profundo(valor, d) : valor) });
  babele.register({module: ID, lang: "es", dir: "compendium"});
});

async function cargar() {
  try {
    const j = await (await fetch(`modules/${ID}/lang/literales.json`)).json();
    literales = j.literales ?? {};
    patrones = (j.patrones ?? []).map(p => ({re: new RegExp(p.en), es: p.es, map: p.map ?? {}}));
  } catch (e) { console.warn(`${ID} | no se pudieron cargar los literales`, e); }
}

const activo = () => game.system?.id === SISTEMA && game.i18n.lang === "es";

function traducir(texto) {
  const limpio = texto.replace(/\s+/g, " ").trim();
  if (!limpio) return null;
  let es = Object.hasOwn(literales, limpio) ? literales[limpio] : undefined;
  if (es === undefined) {
    for (const p of patrones) {
      const m = limpio.match(p.re);
      if (m) { es = p.es.replace(/\$(\d)/g, (_, n) => { const c = (m[n] ?? "").trim(); return p.map[c] ?? literales[c] ?? c; }); break; }
    }
  }
  if (es === undefined || es === limpio) return null;
  return texto.match(/^\s*/)[0] + es + texto.match(/\s*$/)[0];
}

const ATTRS = ["placeholder", "title", "data-tooltip", "aria-label"];
const PROSA = "script,style,textarea,input,[contenteditable],.editor-content,.ProseMirror,.journal-page-content";

function recorrer(raiz) {
  if (!raiz) return;
  const w = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    if (n.parentElement?.closest(PROSA)) continue;
    const t = traducir(n.nodeValue);
    if (t !== null) n.nodeValue = t;
  }
  if (raiz.nodeType !== 1) return;
  for (const el of [raiz, ...raiz.querySelectorAll("[placeholder],[title],[data-tooltip],[aria-label]")]) {
    for (const a of ATTRS) {
      const v = el.getAttribute?.(a);
      const t = v && traducir(v);
      if (t) el.setAttribute(a, t);
    }
  }
}

Hooks.once("ready", async () => {
  if (!activo()) return;
  // «Cómo jugar»: el sistema lo trae como una plantilla en inglés; se sirve una copia traducida
  const parchear = () => { if (globalThis.HowToPlayApp) HowToPlayApp.PARTS.dialog.template = `modules/${ID}/templates/how-to-play.hbs`; };
  parchear();
  setTimeout(parchear, 0);
  await cargar();
  // Se traduce al terminar cada ventana: un MutationObserver global chocaba con el renderizado de las hojas y colgaba la página
  const porVentana = (_app, el) => {
    el = el instanceof HTMLElement ? el : el?.[0];
    recorrer(el);
    // el diálogo de tirada reescribe «Power: N» sin volver a renderizar
    const etiqueta = el?.querySelector?.(".power-label");
    if (etiqueta && !etiqueta.dataset.litmEs) {
      etiqueta.dataset.litmEs = "1";
      new MutationObserver(() => recorrer(etiqueta)).observe(etiqueta, {childList: true});
    }
  };
  Hooks.on("renderApplicationV2", porVentana);
  Hooks.on("renderApplication", porVentana);
  Hooks.on("renderChatMessageHTML", (_m, el) => recorrer(el));
  // avisos emergentes: se añaden al contenedor tras renderizar y no pasan por ningún hook
  const avisos = document.getElementById("notifications");
  if (avisos) new MutationObserver(muts => muts.forEach(m => m.addedNodes.forEach(n => n.nodeType === 1 && recorrer(n)))).observe(avisos, {childList: true, subtree: true});
  recorrer(document.body);
});
