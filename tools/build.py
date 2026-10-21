#!/usr/bin/env python3
"""
BAVARIA static site generator (v2).

    python3 tools/build.py          -> writes the finished site to ./public

Edit CONFIG / PRODUCTS below, rebuild, push. Every fact on the site comes from here.
"""
import html
import json
import re
import datetime as dt
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
TODAY = dt.date.today()

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
CONFIG = {
    "domain": "https://bavaria.com.gr",
    "brand": "BAVARIA",
    "legal_name": "ΤΣΙΛΙΓΙΑΝΝΗΣ ΣΠΥΡΙΔΩΝ",
    "afm": "046741460",
    "doy": "Γ΄ Πατρών",
    "gemi": "36514116000",
    "responsible": "Σπυρίδων Τσιλιγιάννης",
    "founded": 1985,
    "phone": "+30 2610 220982",
    "mobile": "+30 6944 318691",
    "email": "bavaria@hotmail.gr",
    # Warranty — from the official BAVARIA warranty document
    "warranty_system_years": 5,
    "warranty_parts_years": 5,
    "warranty_electric_years": 1,
    "service_every_years": 3,
    # Solar Keymark licence for the collectors (DQS Hellas). Claims appear on the site ONLY
    # while this date is in the future. Update it when the renewed certificate arrives.
    "keymark_no": "SKM 10078.2",
    "keymark_valid_until": dt.date(2027, 8, 30),
    "keymark_pdf": "/assets/docs/bavaria-solar-keymark-skm-10078-2.pdf",
    # Show recommended retail prices (incl. VAT) on product pages?
    "show_prices": True,
    "updated": "21 Οκτωβρίου 2026",
}
KEYMARK = CONFIG["keymark_valid_until"] >= TODAY

DAYS = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
SCHEMA_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# Opening hours as published on each store's Google Business Profile (Oct 2026)
LOCATIONS = [
    {"key": "pantanassis", "tag": "Κατάστημα", "name": "Κατάστημα Παντανάσσης", "store": True,
     "street": "Παντανάσσης 79", "city": "Πάτρα", "zip": "26221", "phone": "+30 2610 220982",
     "hours": [[("08:45", "14:00")], [("08:45", "14:00"), ("17:30", "21:00")], [("08:45", "14:00")],
               [("08:45", "14:00"), ("17:30", "21:00")], [("08:45", "14:00"), ("17:30", "21:00")], [("08:45", "14:00")], []],
     "maps": "https://maps.google.com/?cid=13694090949006186721",
     "embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d12534.102638873219!2d21.717220855419924!3d38.24411290000002!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x135e49ddd0ef44cf%3A0xbe0b2f29e967d8e1!2zQkFWQVJJQSDOl86bzpnOkc6azp_OmSDOmM6VzqHOnM6fzqPOmc6mzqnOnc6VzqM!5e0!3m2!1sel!2sgr!4v1721805584480!5m2!1sel!2sgr"},
    {"key": "neo", "tag": "Κατάστημα", "name": "Κατάστημα Ν.Ε.Ο. Πατρών–Αθηνών", "store": True,
     "street": "Ν.Ε.Ο. Πατρών–Αθηνών 86", "city": "Πάτρα", "zip": "26443", "phone": "+30 6944 318691",
     "hours": [[("09:30", "13:30")], [("09:30", "13:30"), ("17:30", "21:00")], [("09:30", "13:30")],
               [("09:30", "13:30"), ("17:30", "21:00")], [("09:30", "13:30"), ("17:30", "21:00")], [("10:00", "14:00")], []],
     "maps": "https://maps.google.com/?cid=9264382084163234918",
     "embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d12529.786311994329!2d21.738169555419915!3d38.2691396!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x135e49c99e5acb05%3A0x8091b26bb60aec66!2zQkFWQVJJQSDOl86bzpnOkc6azp_OmSDOmM6VzqHOnM6fzqPOmc6mzqnOnc6VzqM!5e0!3m2!1sel!2sgr!4v1721805612991!5m2!1sel!2sgr"},
    {"key": "ergostasio", "tag": "Εργοστάσιο", "name": "Εργοστάσιο", "store": False,
     "street": "Διοδώρου 190, Βελβίτσι", "city": "Πάτρα", "zip": "26504", "phone": None, "hours": None,
     "maps": "https://www.google.com/maps/search/?api=1&query=" + quote("Διοδώρου 190, Πάτρα 26504"),
     "embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3132.544264314359!2d21.79829477603418!3d38.26687457186559!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x135e4bad0c6dc01d%3A0x481742e3eed7be20!2zzpTOuc-MzrTPic-Bzr_PhSAxOTAsIM6gzqzPhM-BzrEgMjY1IDA0!5e0!3m2!1sel!2sgr!4v1721805639864!5m2!1sel!2sgr"},
]

# Tank energy labels (Regulation (EU) 812/2013) — from the BAVARIA labels L130 / L150 / L220
TANK = {130: {"cls": "B", "loss": 48}, 150: {"cls": "B", "loss": 46}, 220: {"cls": "C", "loss": 85}}
PEOPLE = {130: "1–2 άτομα", 150: "3–4 άτομα", 220: "5–6 άτομα"}

# From «Λίστα Εξοπλισμού» (official product list). msrp = recommended retail price incl. VAT.
PRODUCTS = [
    {"model": "GLASS 130BV",   "cap": 130, "energy": 2, "area": 1.5, "n": 1, "msrp": 806},
    {"model": "GLASS 130BV2",  "cap": 130, "energy": 2, "area": 2.0, "n": 1, "msrp": 905},
    {"model": "GLASS 150BV",   "cap": 150, "energy": 2, "area": 2.3, "n": 1, "msrp": 1116},
    {"model": "GLASS 220BV3",  "cap": 220, "energy": 2, "area": 3.0, "n": 2, "msrp": 1302},
    {"model": "GLASS 220BV4",  "cap": 220, "energy": 2, "area": 4.0, "n": 2, "msrp": 1488},
    {"model": "GLASS 130BVR",  "cap": 130, "energy": 3, "area": 1.5, "n": 1, "msrp": 930},
    {"model": "GLASS 130BVR2", "cap": 130, "energy": 3, "area": 2.0, "n": 1, "msrp": 1030},
    {"model": "GLASS 150BVR",  "cap": 150, "energy": 3, "area": 2.3, "n": 1, "msrp": 1240},
    {"model": "GLASS 220BVR3", "cap": 220, "energy": 3, "area": 3.0, "n": 2, "msrp": 1426},
    {"model": "GLASS 220BVR4", "cap": 220, "energy": 3, "area": 4.0, "n": 2, "msrp": 1612},
]
for p in PRODUCTS:
    p["slug"] = p["model"].lower().replace(" ", "-")
    p["url"] = f"/proionta/{p['slug']}/"
    p["series"] = "BVR" if p["energy"] == 3 else "BV"

ENERGY_NAME = {2: "Διπλής ενέργειας", 3: "Τριπλής ενέργειας"}
ENERGY_DESC = {2: "Ήλιος + ηλεκτρική αντίσταση", 3: "Ήλιος + ηλεκτρική αντίσταση + κεντρική θέρμανση (λέβητας)"}

PHOTOS = {
    "roof": ("iliakoi-thermosifones-bavaria-taratsa-patra", (4032, 2268), [640, 1024, 1600, 2400],
             "Ηλιακοί θερμοσίφωνες BAVARIA σε ταράτσα στην Πάτρα, με θέα τον Παναχαϊκό και τη θάλασσα"),
    "install": ("egkatastasi-iliakou-thermosifona-bavaria", (3472, 1955), [640, 1024, 1600, 2400],
                "Τεχνικός της BAVARIA συνδέει ηλιακό θερμοσίφωνα σε ταράτσα"),
    "single": ("iliakos-thermosifonas-bavaria-glass-taratsa", (2500, 3333), [480, 800, 1200],
               "Ηλιακός θερμοσίφωνας BAVARIA με επιλεκτικό συλλέκτη σε ταράτσα"),
    "tiles": ("iliakoi-thermosifones-bavaria-keramoskepi", (4032, 2268), [640, 1024, 1600, 2400],
              "Ηλιακοί θερμοσίφωνες BAVARIA τοποθετημένοι σε κεραμοσκεπή"),
}

# ---------------------------------------------------------------------------
E = html.escape
YEAR = TODAY.year
YEARS = (YEAR - CONFIG["founded"]) // 10 * 10
VERSION = dt.datetime.now().strftime("%Y%m%d%H%M")


def num(x):
    return f"{x:.1f}".replace(".", ",") if x % 1 else f"{int(x)}"


def eur(x):
    return f"{x:,.0f}".replace(",", ".") + " €"


def tel(n):
    return "tel:" + n.replace(" ", "")


def hours_rows(l):
    rows = ""
    for d, slots in zip(DAYS, l["hours"]):
        t = " · ".join(f"{a}–{b}" for a, b in slots) if slots else "Κλειστά"
        rows += f"<tr><th scope=\"row\">{d}</th><td>{t}</td></tr>"
    return f'<table class="hours"><caption class="visually-hidden">Ωράριο {E(l["name"])}</caption><tbody>{rows}</tbody></table>'


def hours_schema(l):
    spec = []
    for day, slots in zip(SCHEMA_DAYS, l["hours"]):
        for a, b in slots:
            spec.append({"@type": "OpeningHoursSpecification", "dayOfWeek": day, "opens": a, "closes": b})
    return spec


def url(path):
    return CONFIG["domain"] + path


def cert_short():
    return "Solar Keymark · CE" if KEYMARK else "Σήμανση CE"


ICONS = {
    "factory": '<path d="M3 21V10l6 4V10l6 4V5h6v16z"/><path d="M7 17h2M12 17h2M17 17h2"/>',
    "badge": '<circle cx="12" cy="9" r="6"/><path d="m9.5 9 1.8 1.8L15 7.2"/><path d="M8.5 14 7 22l5-3 5 3-1.5-8"/>',
    "shield": '<path d="M12 3 4 6v6c0 5 3.4 8.3 8 9 4.6-.7 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "phone": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2"/>',
    "mobile": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "flame": '<path d="M12 22c4 0 7-3 7-7 0-5-5-7-5-12-3 2-4 5-4 7-1-1-2-2-2-4-2 2-3 5-3 8 0 5 3 8 7 8z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/>',
}


def icon(name, cls="tile__icon"):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def eyebrow(text, center=False):
    return f'<span class="eyebrow{" c" if center else ""}"><i class="stripes" aria-hidden="true"></i>{E(text)}</span>'


def tank_svg(cap, n):
    """Schematic drawing (not a photo): tank length ∝ capacity, number of collectors."""
    w = {130: 84, 150: 100, 220: 136}[cap]
    vw = 150; x0 = (vw - w) / 2
    tank = f'<rect x="{x0}" y="6" width="{w}" height="26" rx="13" fill="#e5e5ea" stroke="#aeaeb2"/>'
    tank += f'<rect x="{x0 + w/2 - 14}" y="15" width="28" height="8" rx="2" fill="#d41728"/>'
    cw = w - 6; cx = (vw - cw) / 2; pw = cw / n; coll = ""
    for i in range(n):
        coll += f'<rect x="{cx + i*pw + (1 if i else 0)}" y="40" width="{pw - (1 if n > 1 else 0)}" height="70" rx="2" fill="#3a3a3c" stroke="#8e8e93"/>'
    legs = f'<path d="M{x0+14} 32v8M{x0+w-14} 32v8" stroke="#8e8e93" stroke-width="2"/>'
    return (f'<svg viewBox="0 0 {vw} 116" width="{vw}" height="116" role="img" '
            f'aria-label="Σχηματική απεικόνιση: {cap} λίτρα, {n} συλλέκτ{"ης" if n == 1 else "ες"}">{legs}{tank}{coll}</svg>')


def photo(key, sizes, eager=False, cls=""):
    slug, (w, h), widths, alt = PHOTOS[key]
    base = "/assets/img/" + slug
    srcset = lambda ext: ", ".join(f"{base}-{x}.{ext} {x}w" for x in widths)
    fb = 1024 if 1024 in widths else 800
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img src="{base}-{fb}.jpg" width="{w}" height="{h}" alt="{E(alt)}" {load}{f' class="{cls}"' if cls else ""}></picture>')


NAV = [("/proionta/", "Προϊόντα"), ("/odigos-epilogis/", "Οδηγός επιλογής"), ("/eggyisi/", "Εγγύηση & Service"),
       ("/etaireia/", "Εταιρεία"), ("/syxnes-erotiseis/", "Ερωτήσεις")]


def header(active):
    links = "".join(f'<li><a href="{h}"{" aria-current=\"page\"" if active and active.startswith(h) else ""}>{E(t)}</a></li>' for h, t in NAV)
    cur = ' aria-current="page"' if active == "/epikoinonia/" else ""
    return f'''<a class="skip" href="#main">Μετάβαση στο περιεχόμενο</a>
<header class="nav">
  <div class="wrap">
    <a class="nav__brand" href="/" aria-label="BAVARIA — Αρχική">
      <picture><source type="image/webp" srcset="/assets/img/bavaria-logo-240.webp 1x, /assets/img/bavaria-logo-480.webp 2x">
      <img src="/assets/img/bavaria-logo-240.png" width="240" height="44" alt="BAVARIA"></picture>
    </a>
    <button class="nav__toggle" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="Άνοιγμα μενού"><span></span><span></span><span></span></button>
    <nav aria-label="Κύριο μενού"><ul class="nav__links" id="nav-links">{links}<li><a class="nav__cta" href="/epikoinonia/"{cur}>Επικοινωνία</a></li></ul></nav>
  </div>
</header>'''


def footer():
    c = CONFIG
    locs = "".join(f'<li>{E(l["name"] if l["store"] else l["tag"])}: {E(l["street"])}, {E(l["zip"])} {E(l["city"])}</li>' for l in LOCATIONS)
    return f'''<div class="brandbar" aria-hidden="true"></div>
<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <h2>BAVARIA — Ηλιακοί Θερμοσίφωνες</h2>
        <p>Ηλιακοί θερμοσίφωνες υψηλής απόδοσης από την Πάτρα, από το {c["founded"]}.</p>
        <address><ul>{locs}</ul></address>
      </div>
      <div>
        <h2>Προϊόντα</h2>
        <ul>
          <li><a href="/proionta/?cap=130#montela">130 λίτρα</a></li>
          <li><a href="/proionta/?cap=150#montela">150 λίτρα</a></li>
          <li><a href="/proionta/?cap=220#montela">220 λίτρα</a></li>
          <li><a href="/odigos-epilogis/">Οδηγός επιλογής</a></li>
        </ul>
      </div>
      <div>
        <h2>Υποστήριξη</h2>
        <ul>
          <li><a href="/eggyisi/">Εγγύηση {c["warranty_system_years"]} ετών</a></li>
          <li><a href="/eggyisi/#service">Service</a></li>
          <li><a href="/syxnes-erotiseis/">Συχνές ερωτήσεις</a></li>
          <li><a href="/etaireia/">Η εταιρεία</a></li>
        </ul>
      </div>
      <div>
        <h2>Επικοινωνία</h2>
        <ul>
          <li><a href="{tel(c["phone"])}">{E(c["phone"])}</a></li>
          <li><a href="{tel(c["mobile"])}">{E(c["mobile"])}</a></li>
          <li><a href="mailto:{E(c["email"])}">{E(c["email"])}</a></li>
          <li><a href="/epikoinonia/">Σημεία &amp; χάρτες</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__legal">
      <div>
        <p>© {YEAR} {E(c["legal_name"])} — BAVARIA®. Με την επιφύλαξη παντός δικαιώματος.</p>
        <p class="footer__company">ΑΦΜ {E(c["afm"])} · ΔΟΥ {E(c["doy"])} · Αρ. ΓΕΜΗ {E(c["gemi"])} · Παντανάσσης 79, 26221 Πάτρα</p>
      </div>
      <ul>
        <li><a href="/politiki-aporritou/">Πολιτική απορρήτου</a></li>
        <li><a href="/politiki-cookies/">Cookies</a></li>
        <li><a href="/oroi-xrisis/">Όροι χρήσης</a></li>
      </ul>
    </div>
  </div>
</footer>'''


def org_schema():
    c = CONFIG
    org = {"@type": "Organization", "@id": url("/#organization"), "name": c["brand"], "legalName": c["legal_name"],
           "url": url("/"), "logo": url("/assets/img/bavaria-logo-480.png"), "foundingDate": str(c["founded"]),
           "email": c["email"], "telephone": c["phone"].replace(" ", ""), "vatID": "EL" + c["afm"],
           "taxID": c["afm"], "areaServed": "GR",
           "description": "Κατασκευαστής ηλιακών θερμοσιφώνων στην Πάτρα από το 1985.",
           "address": {"@type": "PostalAddress", "streetAddress": "Παντανάσσης 79", "addressLocality": "Πάτρα",
                       "postalCode": "26221", "addressRegion": "Αχαΐα", "addressCountry": "GR"}}
    places = [{
        "@type": "HomeAndConstructionBusiness", "@id": url(f"/#{l['key']}"),
        "name": f"BAVARIA Ηλιακοί Θερμοσίφωνες — {l['name']}", "image": url("/assets/img/og-bavaria.jpg"),
        "telephone": l["phone"].replace(" ", ""), "email": c["email"], "url": url("/epikoinonia/"), "hasMap": l["maps"],
        "priceRange": "€€", "openingHoursSpecification": hours_schema(l),
        "parentOrganization": {"@id": url("/#organization")},
        "address": {"@type": "PostalAddress", "streetAddress": l["street"], "addressLocality": l["city"],
                    "postalCode": l["zip"], "addressRegion": "Αχαΐα", "addressCountry": "GR"}} for l in LOCATIONS if l["store"]]
    website = {"@type": "WebSite", "@id": url("/#website"), "url": url("/"), "name": "BAVARIA Ηλιακοί Θερμοσίφωνες",
               "inLanguage": "el-GR", "publisher": {"@id": url("/#organization")}}
    return [org, website] + places


def crumbs_html(crumbs):
    if not crumbs:
        return "", None
    items = [("/", "Αρχική")] + crumbs
    lis = "".join((f'<li><a href="{h}">{E(t)}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{E(t)}</li>')
                  for i, (h, t) in enumerate(items))
    schema = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, "item": url(h)} for i, (h, t) in enumerate(items)]}
    return f'<nav class="crumbs wrap" aria-label="Διαδρομή"><ol>{lis}</ol></nav>', schema


CSP = ("default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; font-src 'self'; "
       "connect-src 'self'; frame-src https://www.google.com; form-action 'self' mailto:; base-uri 'self'; "
       "object-src 'none'; upgrade-insecure-requests")

PAGES = []  # (path, [image urls])


def page(path, title, desc, body, crumbs=None, schema=None, active=None, noindex=False, out_name=None,
         images=None, og_image=None):
    ch, cschema = crumbs_html(crumbs or [])
    graph = org_schema() if path == "/" else [{"@type": "Organization", "@id": url("/#organization"),
                                               "name": CONFIG["brand"], "url": url("/")}]
    graph.append({"@type": "WebPage", "@id": url(path), "url": url(path), "name": title, "description": desc,
                  "inLanguage": "el-GR", "isPartOf": {"@id": url("/#website")}})
    if cschema:
        graph.append(cschema)
    if schema:
        graph.extend(schema)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    canonical = "" if noindex else f'<link rel="canonical" href="{url(path)}">'
    og = og_image or "/assets/img/og-bavaria.jpg"
    doc = f'''<!doctype html>
<html lang="el">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="{robots}">
{canonical}
<meta name="theme-color" content="#ffffff">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="website">
<meta property="og:locale" content="el_GR">
<meta property="og:site_name" content="BAVARIA Ηλιακοί Θερμοσίφωνες">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url(path)}">
<meta property="og:image" content="{url(og)}">
<meta property="og:image:alt" content="Ηλιακοί θερμοσίφωνες BAVARIA">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="/assets/css/site.css?v={VERSION}">
<script src="/assets/js/site.js?v={VERSION}" defer></script>
<script type="application/ld+json">{ld}</script>
</head>
<body>
{header(active)}
{ch}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''
    target = OUT / (out_name or (path.strip("/") + "/index.html" if path != "/" else "index.html"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    if not noindex:
        PAGES.append((path, images or []))


def img_url(key, w=1600):
    slug, _, widths, _ = PHOTOS[key]
    w = w if w in widths else widths[-1]
    return f"/assets/img/{slug}-{w}.jpg" if w in (1024, 800) else f"/assets/img/{slug}-{w}.webp"


# ---------------------------------------------------------------------------
# Shared blocks
# ---------------------------------------------------------------------------
def lineup(section_cls="section--alt"):
    cards = ""
    for cap in (130, 150, 220):
        models = [p for p in PRODUCTS if p["cap"] == cap]
        areas = sorted({p["area"] for p in models})
        n = max(p["n"] for p in models)
        lis = "".join(f'<li><a href="{p["url"]}">{E(p["model"])}</a></li>' for p in models)
        cards += f'''<article class="model reveal">
  <div class="model__tank">{tank_svg(cap, n)}</div>
  <h3 class="model__cap">{cap}<small>λίτρα</small></h3>
  <p class="model__people">Για {PEOPLE[cap]} · συλλέκτης {" ή ".join(num(a) for a in areas)} m²</p>
  <hr>
  <ul class="model__list">{lis}</ul>
  <div class="actions"><a class="btn btn--primary" href="/proionta/?cap={cap}#montela">Μοντέλα</a>
  <a class="link-more" href="/epikoinonia/?model={quote(f'{cap} λίτρα')}#forma">Προσφορά</a></div>
</article>'''
    return f'''<section class="section {section_cls}" aria-labelledby="lineup-title">
  <div class="wrap">
    <div class="section__head center">
      <h2 class="headline" id="lineup-title">Ποιος σας ταιριάζει;</h2>
      <p class="lead">Τρία μεγέθη, δέκα μοντέλα. Διπλής ή τριπλής ενέργειας.</p>
    </div>
    <div class="lineup">{cards}</div>
  </div>
</section>'''


def faq_items():
    c = CONFIG
    km = (f"<p>Οι επιλεκτικοί συλλέκτες BAVARIA είναι πιστοποιημένοι Solar Keymark (Αρ. πιστοποιητικού {E(c['keymark_no'])}, "
          f"DQS Hellas, ισχύει έως 30/08/2027) σύμφωνα με το πρότυπο EN 12975:2022 και δοκιμές ISO 9806:2013. <a href=\"{CONFIG['keymark_pdf']}\">Δείτε το πιστοποιητικό</a>.</p>") if KEYMARK else ""
    return [
        ("Πόσα λίτρα ηλιακό θερμοσίφωνα χρειάζομαι;",
         "<p>Για 1–2 άτομα αρκούν 130 λίτρα, για 3–4 άτομα προτείνουμε 150 λίτρα και για 5–6 άτομα 220 λίτρα. "
         "Αν η κατανάλωση ζεστού νερού είναι αυξημένη, επιλέξτε το επόμενο μέγεθος ή μεγαλύτερο συλλέκτη. "
         "Δοκιμάστε τον <a href=\"/odigos-epilogis/\">οδηγό επιλογής</a> — σας προτείνει συγκεκριμένο μοντέλο.</p>"),
        ("Ποια η διαφορά BV και BVR;",
         "<p>Τα μοντέλα <strong>BV</strong> είναι διπλής ενέργειας: ζεσταίνουν το νερό με τον ήλιο και, όταν χρειαστεί, με ηλεκτρική αντίσταση. "
         "Τα μοντέλα <strong>BVR</strong> είναι τριπλής ενέργειας: έχουν επιπλέον σύνδεση με την κεντρική θέρμανση (λέβητα), "
         "ώστε τον χειμώνα το νερό να ζεσταίνεται και από αυτή.</p>"),
        ("Τι σημαίνει ο αριθμός 2, 3 ή 4 στο τέλος του μοντέλου;",
         "<p>Δείχνει μεγαλύτερο συλλέκτη. Για παράδειγμα, ο GLASS 130BV έχει συλλέκτη 1,5 m² και ο 130BV2 συλλέκτη 2 m². "
         "Στα 220 λίτρα, το 3 σημαίνει δύο συλλέκτες συνολικά 3 m² και το 4 δύο συλλέκτες συνολικά 4 m². "
         "Μεγαλύτερη επιφάνεια σημαίνει περισσότερο ζεστό νερό τις μέρες με λίγο ήλιο.</p>"),
        ("Πόσα χρόνια εγγύηση έχει;",
         f"<p>Η εγγύηση του ηλιακού συστήματος BAVARIA είναι <strong>{c['warranty_system_years']} χρόνια</strong> από την ημερομηνία εγκατάστασης "
         f"και καλύπτει την αντικατάσταση ελαττωματικών εξαρτημάτων. Η ηλεκτρική αντίσταση και ο θερμοστάτης έχουν εγγύηση "
         f"{c['warranty_electric_years']} έτους. Δείτε όλους τους <a href=\"/eggyisi/\">όρους εγγύησης</a>.</p>"),
        ("Κάθε πότε θέλει service;",
         f"<p>Προτείνουμε service κάθε {c['service_every_years']} χρόνια, για την προστασία και τη μακροζωία του ηλιακού. "
         "Στο service ελέγχεται κυρίως η ανόδιο μαγνησίου που προστατεύει το δοχείο από τη διάβρωση, καθώς και οι συνδέσεις. "
         f"Κλείστε ραντεβού στο <a href=\"{tel(c['phone'])}\">{E(c['phone'])}</a>.</p>"),
        ("Τι σημαίνει «GLASS»;",
         "<p>Η σειρά GLASS έχει δοχείο νερού με εσωτερική υαλώδη επίστρωση, που προστατεύει το μέταλλο από τη διάβρωση.</p>"),
        ("Τι ενεργειακή κλάση έχουν τα δοχεία;",
         "<p>Σύμφωνα με την ενεργειακή σήμανση του Κανονισμού (ΕΕ) 812/2013: το δοχείο 130 λίτρων είναι κλάσης B (θερμικές απώλειες 48 W), "
         "το δοχείο 150 λίτρων κλάσης B (46 W) και το δοχείο 220 λίτρων κλάσης C (85 W).</p>"),
        ("Είναι πιστοποιημένοι;",
         "<p>Κάθε μοντέλο συνοδεύεται από Δήλωση Συμμόρφωσης CE (EN ISO 9806:2017) και ενεργειακή σήμανση κατά τον Κανονισμό (ΕΕ) 812/2013.</p>" + km),
        ("Μπορώ να τον βάλω σε κεραμοσκεπή;",
         "<p>Ναι. Τοποθετούμε ηλιακούς θερμοσίφωνες τόσο σε ταράτσες όσο και σε κεραμοσκεπές, με την κατάλληλη βάση στήριξης.</p>"),
        ("Κάνετε εγκατάσταση;",
         "<p>Ναι. Το συνεργείο μας εγκαθιστά ηλιακούς θερμοσίφωνες, καθώς και συστήματα θέρμανσης και ψύξης για σπίτια και "
         "επαγγελματικούς χώρους. Για να ισχύει η εγγύηση, η εγκατάσταση γίνεται από το συνεργείο μας ή από εξειδικευμένο "
         "συνεργείο σύμφωνα με τις οδηγίες μας.</p>"),
    ]


def faq_html(items):
    return "".join(f'<details><summary>{E(q)}</summary><div class="faq__a">{a}</div></details>' for q, a in items)


def faq_schema(items):
    return [{"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).strip()}}
        for q, a in items]}]


def cta_band(title="Μιλήστε με τον κατασκευαστή.", text="Απαντάμε σε κάθε ερώτηση για μέγεθος, τοποθέτηση και τιμή — χωρίς δέσμευση."):
    c = CONFIG
    return f'''<section class="section section--dark cta-band" aria-labelledby="cta-title">
  <div class="wrap">
    <h2 class="headline" id="cta-title">{E(title)}</h2>
    <p class="lead">{E(text)}</p>
    <div class="actions">
      <a class="btn btn--primary" href="{tel(c["phone"])}">Κλήση {E(c["phone"])}</a>
      <a class="btn btn--ghost" href="/epikoinonia/#forma">Ζητήστε προσφορά</a>
    </div>
  </div>
</section>'''


def gallery():
    return f'''<section class="section" aria-labelledby="gal-title">
  <div class="wrap">
    <div class="section__head center">
      {eyebrow("Πραγματικές εγκαταστάσεις", True)}
      <h2 class="headline" id="gal-title">Στις στέγες της Πάτρας.</h2>
      <p class="lead">Ταράτσες, κεραμοσκεπές, σπίτια και πολυκατοικίες. Τοποθετημένοι από το δικό μας συνεργείο.</p>
    </div>
    <div class="gallery">
      <figure class="g-tall reveal">{photo("single", "(max-width: 760px) 100vw, 640px", cls="crop-top")}<figcaption>Σε ταράτσα</figcaption></figure>
      <figure class="reveal">{photo("tiles", "(max-width: 760px) 100vw, 840px")}<figcaption>Σε κεραμοσκεπή</figcaption></figure>
      <figure class="reveal">{photo("install", "(max-width: 760px) 100vw, 840px")}<figcaption>Εγκατάσταση από το συνεργείο μας</figcaption></figure>
    </div>
  </div>
</section>'''


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def build_home():
    c = CONFIG
    cert_tile = (f'''<article class="tile reveal">{icon("badge")}<h3>Solar Keymark &amp; CE.</h3>
        <p>Συλλέκτες πιστοποιημένοι Solar Keymark (Αρ. {E(c["keymark_no"])}) και Δήλωση Συμμόρφωσης CE για κάθε μοντέλο.</p></article>'''
                 if KEYMARK else
                 f'''<article class="tile reveal">{icon("badge")}<h3>Σήμανση CE.</h3>
        <p>Κάθε μοντέλο συνοδεύεται από Δήλωση Συμμόρφωσης CE (EN ISO 9806:2017) και ευρωπαϊκή ενεργειακή σήμανση.</p></article>''')
    body = f'''
<section class="hero hero--photo" aria-labelledby="hero-title">
  <div class="wrap center">
    {eyebrow(f"Από την Πάτρα, από το {c['founded']}", True)}
    <h1 class="display" id="hero-title">Ηλιακοί θερμοσίφωνες.<br><span class="grad">Φτιαγμένοι από εμάς.</span></h1>
    <p class="lead">Κατασκευάζουμε, πουλάμε και εγκαθιστούμε ηλιακούς θερμοσίφωνες υψηλής απόδοσης. Με εγγύηση {c["warranty_system_years"]} ετών.</p>
    <div class="actions actions--center">
      <a class="btn btn--primary" href="/proionta/">Δείτε τα μοντέλα</a>
      <a class="link-more" href="/odigos-epilogis/">Βρείτε το σωστό μοντέλο</a>
    </div>
  </div>
  <figure class="hero__photo">{photo("roof", "(max-width: 1272px) 100vw, 1240px", eager=True)}<figcaption>BAVARIA σε ταράτσα στην Πάτρα</figcaption></figure>
</section>

<section class="section section--flush" aria-label="Η BAVARIA με αριθμούς">
  <div class="wrap">
    <div class="stats reveal">
      <div class="stat"><span class="stat__num">{YEARS}+</span><span class="stat__label">χρόνια κατασκευής</span></div>
      <div class="stat"><span class="stat__num">{c["warranty_system_years"]} έτη</span><span class="stat__label">εγγύηση συστήματος</span></div>
      <div class="stat"><span class="stat__num">{len(PRODUCTS)}</span><span class="stat__label">μοντέλα GLASS</span></div>
      <div class="stat"><span class="stat__num">130–220</span><span class="stat__label">λίτρα χωρητικότητα</span></div>
    </div>
  </div>
</section>

<section class="section section--alt" aria-labelledby="why-title">
  <div class="wrap">
    <div class="section__head center">
      {eyebrow("Γιατί BAVARIA", True)}
      <h2 class="headline" id="why-title">Απευθείας από τον κατασκευαστή.</h2>
      <p class="lead">Ένας υπεύθυνος από την παραγωγή ως την εγκατάσταση και το service.</p>
    </div>
    <div class="bento">
      <article class="tile tile--wide tile--dark reveal">
        {icon("factory")}
        <h3>Δικό μας εργοστάσιο στην Πάτρα.</h3>
        <p>Παράγουμε τους θερμοσίφωνές μας στο εργοστάσιό μας στο Βελβίτσι και τους ελέγχουμε σε όλα τα στάδια της παραγωγής, με πιστοποιημένες πρώτες ύλες.</p>
        <ul class="chips" aria-label="Πρώτες ύλες"><li>Ορείχαλκος</li><li>Σίδηρος</li><li>Χαλκός</li><li>Αλουμίνιο</li></ul>
      </article>
      {cert_tile}
      <article class="tile reveal">
        {icon("shield")}
        <h3>Εγγύηση {c["warranty_system_years"]} ετών.</h3>
        <p>Για την αντοχή, τη διάρκεια ζωής και την καλή λειτουργία του συστήματος, με αντικατάσταση ελαττωματικών εξαρτημάτων.</p>
      </article>
      <article class="tile tile--third tile--sun reveal">
        {icon("sun")}
        <h3>Επιλεκτικοί συλλέκτες.</h3>
        <p>Από 1,5 έως 4 m², για ζεστό νερό και τις μέρες με λίγο ήλιο.</p>
      </article>
      <article class="tile tile--third reveal">
        {icon("flame")}
        <h3>Διπλής ή τριπλής.</h3>
        <p>Τα μοντέλα BVR συνδέονται και με την κεντρική θέρμανση.</p>
      </article>
      <article class="tile tile--third reveal">
        {icon("wrench")}
        <h3>Εγκατάσταση &amp; service.</h3>
        <p>Το δικό μας συνεργείο, σε ταράτσα ή κεραμοσκεπή.</p>
      </article>
    </div>
  </div>
</section>

{gallery()}

{lineup("section--alt")}

<section class="section" aria-labelledby="guide-teaser">
  <div class="wrap center">
    {eyebrow("Οδηγός επιλογής", True)}
    <h2 class="headline" id="guide-teaser">Τρεις ερωτήσεις.<br>Το σωστό μοντέλο.</h2>
    <p class="lead narrow lead--gap">Πόσοι είστε, πόσο ζεστό νερό χρησιμοποιείτε και αν έχετε κεντρική θέρμανση. Σας λέμε αμέσως ποιο μοντέλο σας ταιριάζει.</p>
    <div class="actions"><a class="btn btn--dark" href="/odigos-epilogis/">Ξεκινήστε τον οδηγό</a></div>
  </div>
</section>

<section class="section section--alt" aria-labelledby="faq-title">
  <div class="wrap"><div class="narrow">
    <div class="section__head center"><h2 class="headline" id="faq-title">Συχνές ερωτήσεις</h2></div>
    <div class="faq">{faq_html(faq_items()[:5])}</div>
    <div class="actions actions--center mt-32"><a class="link-more" href="/syxnes-erotiseis/">Όλες οι ερωτήσεις</a></div>
  </div></div>
</section>

{cta_band()}
'''
    page("/", "Ηλιακοί Θερμοσίφωνες Πάτρα | Κατασκευαστής από το 1985 | BAVARIA",
         f"Ηλιακοί θερμοσίφωνες BAVARIA GLASS 130, 150 και 220 λίτρων, διπλής και τριπλής ενέργειας, από τον κατασκευαστή στην Πάτρα. Εγγύηση {c['warranty_system_years']} ετών, εγκατάσταση και service.",
         body, active="/", schema=faq_schema(faq_items()[:5]),
         images=[img_url("roof"), img_url("tiles"), img_url("install"), img_url("single")])


def spec_rows(p):
    c = CONFIG
    t = TANK[p["cap"]]
    coll = (f'{num(p["area"])} m² · 1 συλλέκτης' if p["n"] == 1 else f'{num(p["area"])} m² συνολικά · 2 συλλέκτες × {num(p["area"]/2)} m²')
    rows = [
        ("Χωρητικότητα δοχείου", f'{p["cap"]} λίτρα'),
        ("Κατάλληλος για", PEOPLE[p["cap"]]),
        ("Λειτουργία", f'{ENERGY_NAME[p["energy"]]} — {ENERGY_DESC[p["energy"]]}'),
        ("Συλλέκτης", f"Επιλεκτικός, {coll}"),
        ("Δοχείο", "GLASS — εσωτερική υαλώδης επίστρωση"),
        ("Ενεργειακή κλάση δοχείου", f'{t["cls"]} (Κανονισμός ΕΕ 812/2013)'),
        ("Θερμικές απώλειες δοχείου", f'{t["loss"]} W'),
        ("Εγγύηση", f'{c["warranty_system_years"]} χρόνια σύστημα · {c["warranty_electric_years"]} χρόνος αντίσταση & θερμοστάτης'),
        ("Συμμόρφωση", "Δήλωση Συμμόρφωσης CE · EN ISO 9806:2017" + (f' · Solar Keymark συλλέκτη ({c["keymark_no"]})' if KEYMARK else "")),
    ]
    if c["show_prices"]:
        rows.append(("Προτεινόμενη τιμή λιανικής", f'{eur(p["msrp"])} με ΦΠΑ 24%'))
    return rows


def build_products():
    cards = ""
    for p in PRODUCTS:
        t = TANK[p["cap"]]
        specs = [("Λειτουργία", ENERGY_NAME[p["energy"]]), ("Συλλέκτης", f'{num(p["area"])} m²' + (" (2×)" if p["n"] == 2 else "")),
                 ("Για", PEOPLE[p["cap"]]), ("Κλάση δοχείου", t["cls"])]
        if CONFIG["show_prices"]:
            specs.append(("Τιμή", eur(p["msrp"])))
        dl = "".join(f"<dt>{E(a)}</dt><dd>{E(b)}</dd>" for a, b in specs)
        cards += f'''<article class="pcard" id="{p["slug"]}" data-cap="{p["cap"]}">
  <span class="pcard__series">Σειρά {p["series"]} · {ENERGY_NAME[p["energy"]].split()[0]}</span>
  <h3><a href="{p["url"]}">{E(p["model"])}</a></h3>
  <p class="pcard__cap">Ηλιακός θερμοσίφωνας {p["cap"]} λίτρων</p>
  <dl class="spec">{dl}</dl>
  <a class="btn btn--ghost" href="{p["url"]}">Λεπτομέρειες</a>
</article>'''
    filters = '<button type="button" data-filter="all" aria-pressed="true">Όλα</button>' + "".join(
        f'<button type="button" data-filter="{c}" aria-pressed="false">{c} λίτρα</button>' for c in (130, 150, 220))
    body = f'''
<section class="page-head center">
  <div class="wrap">
    {eyebrow("Προϊόντα", True)}
    <h1 class="display">Ηλιακοί θερμοσίφωνες GLASS.</h1>
    <p class="lead">Δέκα μοντέλα σε 130, 150 και 220 λίτρα, διπλής (BV) ή τριπλής ενέργειας (BVR), με επιλεκτικούς συλλέκτες από 1,5 έως 4 m².</p>
  </div>
</section>
{lineup("section")}
<section class="section section--alt" id="montela" aria-labelledby="models-title">
  <div class="wrap">
    <div class="section__head center"><h2 class="headline" id="models-title">Όλα τα μοντέλα.</h2></div>
    <div class="filters" data-filters role="group" aria-label="Φίλτρο χωρητικότητας">{filters}</div>
    <p id="filter-status" class="visually-hidden" aria-live="polite"></p>
    <div class="grid-products">{cards}</div>
  </div>
</section>
{cta_band("Δεν ξέρετε ποιο να διαλέξετε;", "Ο οδηγός επιλογής σας προτείνει μοντέλο σε 10 δευτερόλεπτα — ή καλέστε μας.")}
'''
    page("/proionta/", "Ηλιακοί Θερμοσίφωνες GLASS 130, 150, 220 λίτρα | BAVARIA",
         "Όλα τα μοντέλα ηλιακών θερμοσιφώνων BAVARIA GLASS: 130, 150 και 220 λίτρα, διπλής (BV) και τριπλής ενέργειας (BVR), επιλεκτικοί συλλέκτες 1,5–4 m².",
         body, crumbs=[("/proionta/", "Προϊόντα")], active="/proionta/")


def build_model(p):
    c = CONFIG
    t = TANK[p["cap"]]
    rows = "".join(f"<tr><th scope=\"row\">{E(a)}</th><td>{E(b)}</td></tr>" for a, b in spec_rows(p))
    siblings = [q for q in PRODUCTS if q["cap"] == p["cap"]]
    var = "".join(
        f'<a class="variant" href="{q["url"]}"{" aria-current=\"page\"" if q is p else ""}><strong>{E(q["model"])}</strong>'
        f'<span>{ENERGY_NAME[q["energy"]]} · {num(q["area"])} m²</span></a>' for q in siblings)
    energy_word = "διπλής" if p["energy"] == 2 else "τριπλής"
    coll_txt = f'επιλεκτικό συλλέκτη {num(p["area"])} m²' if p["n"] == 1 else f'δύο επιλεκτικούς συλλέκτες, συνολικά {num(p["area"])} m²'
    lead = f'Ηλιακός θερμοσίφωνας {p["cap"]} λίτρων, {energy_word} ενέργειας, με {coll_txt}. Ιδανικός για {PEOPLE[p["cap"]]}.'
    price = (f'<p class="price">{eur(p["msrp"])}<small>Προτεινόμενη τιμή λιανικής με ΦΠΑ 24% · η εγκατάσταση με προσφορά</small></p>'
             if c["show_prices"] else "")
    lbl = f"energeiaki-etiketa-bavaria-{p['cap']}lt"
    schema = []
    if c["show_prices"]:
        schema.append({"@type": "Product", "name": f"BAVARIA {p['model']}", "brand": {"@type": "Brand", "name": "BAVARIA"},
                       "sku": "BAVARIA" + p["model"].replace(" ", ""), "description": lead,
                       "image": url(img_url("single", 800)), "url": url(p["url"]),
                       "offers": {"@type": "Offer", "price": str(p["msrp"]), "priceCurrency": "EUR",
                                  "availability": "https://schema.org/InStock", "seller": {"@id": url("/#organization")}}})
    body = f'''
<section class="mhead">
  <div class="wrap">
    {eyebrow(f'Σειρά {p["series"]} · {ENERGY_NAME[p["energy"]]}', True)}
    <h1 class="display">BAVARIA {E(p["model"])}</h1>
    <p class="lead">{E(lead)}</p>
    <ul class="badges">
      <li class="b-red">{p["cap"]} λίτρα</li><li>{num(p["area"])} m² συλλέκτης</li><li>Κλάση δοχείου {t["cls"]}</li><li>Εγγύηση {c["warranty_system_years"]} ετών</li>
    </ul>
    {price}
    <div class="actions actions--center">
      <a class="btn btn--primary" href="/epikoinonia/?model={quote(p["model"])}#forma">Ζητήστε προσφορά</a>
      <a class="link-more" href="{tel(c["phone"])}">Καλέστε {E(c["phone"])}</a>
    </div>
  </div>
  <figure class="hero__photo">{photo("roof", "(max-width: 1272px) 100vw, 1240px", eager=True)}<figcaption>Ενδεικτική εγκατάσταση BAVARIA</figcaption></figure>
</section>

<section class="section" aria-labelledby="specs-title">
  <div class="wrap">
    <div class="section__head"><h2 class="headline" id="specs-title">Τεχνικά χαρακτηριστικά.</h2></div>
    <div class="specs">
      <table class="spectable"><caption class="visually-hidden">Τεχνικά χαρακτηριστικά {E(p["model"])}</caption><tbody>{rows}</tbody></table>
      <aside class="label-card">
        <picture><source type="image/webp" srcset="/assets/img/{lbl}.webp"><img src="/assets/img/{lbl}.png" width="600" height="1200" loading="lazy" alt="Ενεργειακή ετικέτα δοχείου BAVARIA L {p["cap"]}: κλάση {t["cls"]}, απώλειες {t["loss"]} W, {p["cap"]} λίτρα"></picture>
        <p>Ενεργειακή ετικέτα δοχείου L {p["cap"]} κατά τον Κανονισμό (ΕΕ) 812/2013. <a href="/assets/img/{lbl}.png" download>Λήψη</a></p>
      </aside>
    </div>
  </div>
</section>

<section class="section section--alt" aria-labelledby="var-title">
  <div class="wrap">
    <div class="section__head"><h2 class="title" id="var-title">Άλλες εκδόσεις {p["cap"]} λίτρων</h2></div>
    <div class="variants">{var}</div>
    <p class="note mt-20">Με λίγο ήλιο τον χειμώνα ή αυξημένη κατανάλωση, προτιμήστε μεγαλύτερο συλλέκτη. Έχετε λέβητα; Οι εκδόσεις BVR αξιοποιούν και την κεντρική θέρμανση.</p>
  </div>
</section>
{cta_band(f"Θέλετε τον {p['model']};", "Πείτε μας πού θα τοποθετηθεί και σας στέλνουμε προσφορά με εγκατάσταση.")}
'''
    title = f"BAVARIA {p['model']} — Ηλιακός Θερμοσίφωνας {p['cap']}L {ENERGY_NAME[p['energy']]}"
    desc = f"{lead} Δοχείο GLASS κλάσης {t['cls']}, εγγύηση {c['warranty_system_years']} ετών. Κατασκευή στην Πάτρα."
    page(p["url"], title, desc, body, crumbs=[("/proionta/", "Προϊόντα"), (p["url"], p["model"])],
         active="/proionta/", schema=schema, images=[img_url("roof"), f"/assets/img/{lbl}.png"])


def build_guide():
    people = "".join(
        f'<label><input type="radio" name="people" value="{v}"{" checked" if v == 3 else ""}><span>{t}<small>{s}</small></span></label>'
        for v, t, s in [(1, "1", "άτομο"), (2, "2", "άτομα"), (3, "3", "άτομα"), (4, "4", "άτομα"), (5, "5", "άτομα"), (6, "6", "άτομα"), (7, "7+", "άτομα")])
    use = "".join(
        f'<label><input type="radio" name="use" value="{v}"{" checked" if v == "normal" else ""}><span>{t}<small>{s}</small></span></label>'
        for v, t, s in [("normal", "Κανονική", "ντους, κουζίνα"), ("high", "Αυξημένη", "συχνά μπάνια, πλυντήρια")])
    boiler = "".join(
        f'<label><input type="radio" name="boiler" value="{v}"{" checked" if v == "no" else ""}><span>{t}<small>{s}</small></span></label>'
        for v, t, s in [("no", "Όχι", "διπλής ενέργειας"), ("yes", "Ναι", "τριπλής ενέργειας")])
    data = json.dumps([{"m": p["model"], "u": p["url"], "c": p["cap"], "e": p["energy"], "a": p["area"]} for p in PRODUCTS], ensure_ascii=False)
    body = f'''
<section class="page-head center">
  <div class="wrap">
    {eyebrow("Οδηγός επιλογής", True)}
    <h1 class="display">Ποιο μοντέλο χρειάζεστε;</h1>
    <p class="lead">Τρεις ερωτήσεις και βλέπετε αμέσως ποιος ηλιακός θερμοσίφωνας BAVARIA ταιριάζει στο σπίτι σας.</p>
  </div>
</section>
<section class="section section--alt section--tight">
  <div class="wrap narrow">
    <form class="guide" data-guide data-products='{E(data)}' action="/proionta/" method="get" aria-describedby="guide-note">
      <fieldset><legend>1. Πόσα άτομα μένουν στο σπίτι;</legend><div class="seg seg--people">{people}</div></fieldset>
      <fieldset><legend>2. Πόσο ζεστό νερό χρησιμοποιείτε;</legend><div class="seg">{use}</div></fieldset>
      <fieldset><legend>3. Έχετε κεντρική θέρμανση (λέβητα) για να συνδεθεί;</legend><div class="seg">{boiler}</div></fieldset>
      <div class="result" aria-live="polite">
        <div class="result__cap" data-out="cap">150<small>λίτρα</small></div>
        <div>
          <h2 class="title" data-out="title">Σας προτείνουμε τον GLASS 150BV</h2>
          <p data-out="text">Για οικογένεια 3–4 ατόμων.</p>
          <div class="result__models" data-out="models"><a href="/proionta/glass-150bv/">GLASS 150BV</a></div>
          <div class="actions"><a class="btn btn--primary" data-out="link" href="/proionta/glass-150bv/">Δείτε το μοντέλο</a>
          <a class="link-more" data-out="quote" href="/epikoinonia/#forma">Ζητήστε προσφορά</a></div>
        </div>
      </div>
      <noscript><p><button class="btn btn--primary" type="submit">Δείτε τα μοντέλα</button></p></noscript>
    </form>
    <p id="guide-note" class="center note mt-20">Ο οδηγός δίνει γενική πρόταση. Η τελική επιλογή εξαρτάται και από τον προσανατολισμό, τη σκίαση και τη στέγη — σας βοηθάμε δωρεάν.</p>
  </div>
</section>
<section class="section">
  <div class="wrap narrow">
    <div class="prose prose--center">
      <h2>Πώς να διαλέξετε ηλιακό θερμοσίφωνα</h2>
      <h3>1. Χωρητικότητα</h3>
      <p>130 λίτρα για 1–2 άτομα, 150 λίτρα για 3–4 άτομα, 220 λίτρα για 5–6 άτομα. Με αυξημένη κατανάλωση, πηγαίνετε ένα μέγεθος πάνω ή σε μεγαλύτερο συλλέκτη.</p>
      <h3>2. Συλλέκτης</h3>
      <p>Μεγαλύτερη επιφάνεια συλλέκτη δίνει περισσότερο ζεστό νερό τις μέρες με λίγο ήλιο. Γι' αυτό υπάρχουν εκδόσεις με μεγαλύτερο συλλέκτη (π.χ. 130BV2 με 2 m² αντί για 1,5 m²).</p>
      <h3>3. Διπλής ή τριπλής ενέργειας</h3>
      <p>Διπλής (BV): ήλιος και ηλεκτρική αντίσταση. Τριπλής (BVR): επιπλέον σύνδεση με τον λέβητα της κεντρικής θέρμανσης, για ζεστό νερό τον χειμώνα χωρίς ρεύμα.</p>
      <h3>4. Τοποθέτηση</h3>
      <p>Σε ταράτσα ή κεραμοσκεπή. Ιδανικά οι συλλέκτες «βλέπουν» νότια, χωρίς σκιά από γειτονικά κτίρια ή δέντρα.</p>
    </div>
  </div>
</section>
{cta_band()}
'''
    page("/odigos-epilogis/", "Πόσα λίτρα ηλιακό θερμοσίφωνα χρειάζομαι; Οδηγός επιλογής | BAVARIA",
         "Βρείτε σε 10 δευτερόλεπτα ποιος ηλιακός θερμοσίφωνας σας ταιριάζει: 130, 150 ή 220 λίτρα, διπλής ή τριπλής ενέργειας, ανάλογα με τα άτομα και τη χρήση.",
         body, crumbs=[("/odigos-epilogis/", "Οδηγός επιλογής")], active="/odigos-epilogis/")


def build_warranty():
    c = CONFIG
    body = f'''
<section class="page-head center">
  <div class="wrap">
    {eyebrow("Εγγύηση & Service", True)}
    <h1 class="display">{c["warranty_system_years"]} χρόνια εγγύηση.<br><span class="grad">Γραπτή, από τον κατασκευαστή.</span></h1>
    <p class="lead">Κάθε ηλιακό σύστημα BAVARIA συνοδεύεται από έντυπη εγγύηση με σειριακό αριθμό.</p>
  </div>
</section>
<section class="section section--flush">
  <div class="wrap">
    <div class="wgrid">
      <div class="wcard reveal"><strong>{c["warranty_system_years"]}<small>χρόνια</small></strong><h3>Ηλιακό σύστημα</h3><p>Αντοχή, διάρκεια ζωής και καλή λειτουργία του ηλιακού συστήματος, από την ημερομηνία εγκατάστασης.</p></div>
      <div class="wcard reveal"><strong>{c["warranty_parts_years"]}<small>χρόνια</small></strong><h3>Εξαρτήματα</h3><p>Πλήρης κάλυψη για την αντικατάσταση τυχόν ελαττωματικών εξαρτημάτων.</p></div>
      <div class="wcard reveal"><strong>{c["warranty_electric_years"]}<small>χρόνος</small></strong><h3>Αντίσταση &amp; θερμοστάτης</h3><p>Καλή λειτουργία της ηλεκτρικής αντίστασης και του θερμοστάτη.</p></div>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="prose prose--center">
      <h2>Πώς ενεργοποιείται η εγγύηση</h2>
      <p>Συμπληρώστε το απόκομμα του εντύπου εγγύησης (στοιχεία, τύπος συστήματος, σειριακός αριθμός, ημερομηνία εγκατάστασης) και στείλτε το στην εταιρεία μας <strong>μέσα σε έναν μήνα</strong> από την εγκατάσταση. Η εγγύηση φέρει τη σφραγίδα και την υπογραφή μας.</p>
      <h2>Πότε δεν ισχύει η εγγύηση</h2>
      <ul>
        <li>Για ζημιές από βίαια φυσικά φαινόμενα (θεομηνίες, σεισμούς, πυρκαγιές κ.λπ.) ή από παρέμβαση τρίτων.</li>
        <li>Αν η εγκατάσταση δεν έγινε από το συνεργείο μας ή από εξειδικευμένο συνεργείο σύμφωνα με τις οδηγίες μας.</li>
        <li>Αν δεν έχει σταλεί το απόκομμα εγγύησης μέσα σε έναν μήνα από την εγκατάσταση.</li>
        <li>Αν το έντυπο δεν φέρει σφραγίδα και υπογραφή της εταιρείας μας.</li>
      </ul>
      <p class="note">Η εμπορική εγγύηση ισχύει επιπλέον και δεν περιορίζει τα δικαιώματα που σας δίνει ο νόμος ως καταναλωτή (νόμιμη εγγύηση, ν. 2251/1994 και ν. 4967/2022).</p>
      <h2 id="service">Service κάθε {c["service_every_years"]} χρόνια</h2>
      <p>Για την προστασία και τη μακροζωία του ηλιακού σας, προτείνουμε service κάθε {c["service_every_years"]} χρόνια. Ελέγχουμε την ανόδιο μαγνησίου, τις συνδέσεις, τη στεγανότητα και τη γενική κατάσταση του συστήματος.</p>
      <div class="actions"><a class="btn btn--primary" href="{tel(c["phone"])}">Κλείστε service · {E(c["phone"])}</a><a class="link-more" href="/epikoinonia/?model={quote("Εγκατάσταση / service")}#forma">Ή στείλτε μήνυμα</a></div>
    </div>
  </div>
</section>
{gallery()}
'''
    page("/eggyisi/", f"Εγγύηση {c['warranty_system_years']} Ετών & Service Ηλιακού Θερμοσίφωνα | BAVARIA",
         f"Εγγύηση {c['warranty_system_years']} ετών για ηλιακά συστήματα BAVARIA, κάλυψη εξαρτημάτων, όροι και service κάθε {c['service_every_years']} χρόνια στην Πάτρα.",
         body, crumbs=[("/eggyisi/", "Εγγύηση & Service")], active="/eggyisi/")


def build_about():
    c = CONFIG
    km_tile = (f'''<article class="tile tile--dark reveal">{icon("badge")}<h3>Solar Keymark</h3>
        <p>Οι επιλεκτικοί συλλέκτες μας φέρουν άδεια χρήσης Solar Keymark (Αρ. {E(c["keymark_no"])}, DQS Hellas) κατά EN 12975:2022 με δοκιμές ISO 9806:2013 — το ευρωπαϊκό σήμα ποιότητας για ηλιοθερμικά. Ισχύει έως 30/08/2027.</p>
        <p class="mt-20"><a class="link-more" href="{c["keymark_pdf"]}">Πιστοποιητικό (PDF)</a></p></article>'''
               if KEYMARK else "")
    body = f'''
<section class="page-head center">
  <div class="wrap">
    {eyebrow("Η εταιρεία", True)}
    <h1 class="display">Από το {c["founded"]}<br><span class="grad">στον ήλιο της Πάτρας.</span></h1>
    <p class="lead">Η BAVARIA είναι βιομηχανία παραγωγής ηλιακών θερμοσιφώνων υψηλής απόδοσης. Πάνω από {YEARS} χρόνια φτιάχνουμε στην Πάτρα συστήματα που ζεσταίνουν νερό σε σπίτια και επιχειρήσεις.</p>
  </div>
</section>
<figure class="hero__photo">{photo("install", "(max-width: 1272px) 100vw, 1240px", eager=True)}<figcaption>Το συνεργείο μας στη δουλειά</figcaption></figure>
<section class="section">
  <div class="wrap">
    <ol class="timeline">
      <li class="reveal"><strong>{c["founded"]}</strong>Ξεκινά η παραγωγή ηλιακών θερμοσιφώνων BAVARIA στην Πάτρα.</li>
      <li class="reveal"><strong>Βελβίτσι</strong>Το εργοστάσιό μας, με έλεγχο σε όλα τα στάδια της παραγωγής.</li>
      <li class="reveal"><strong>2 καταστήματα</strong>Στην Παντανάσσης 79 και στη Ν.Ε.Ο. Πατρών–Αθηνών 86, μαζί με το εργοστάσιο στο Βελβίτσι.</li>
      <li class="reveal"><strong>Σήμερα</strong>Δέκα μοντέλα GLASS, εγκατάσταση, service και συστήματα θέρμανσης–ψύξης.</li>
    </ol>
  </div>
</section>
<section class="section section--alt">
  <div class="wrap">
    <div class="bento">
      <article class="tile reveal">{icon("factory")}<h3>Τι κατασκευάζουμε</h3>
        <p>Ηλιακούς θερμοσίφωνες υψηλής απόδοσης από πιστοποιημένες πρώτες ύλες ορείχαλκου, σιδήρου, χαλκού και αλουμινίου, για θέρμανση νερού σε σπίτια και επαγγελματικούς χώρους.</p></article>
      <article class="tile reveal">{icon("wrench")}<h3>Τι άλλο κάνουμε</h3>
        <p>Πουλάμε και εγκαθιστούμε συστήματα θέρμανσης και ψύξης για οικιακούς και επαγγελματικούς χώρους — έναν υπεύθυνο για όλο το σύστημα.</p></article>
    </div>
  </div>
</section>
<section class="section" id="pistopoiiseis" aria-labelledby="cert-title">
  <div class="wrap">
    <div class="section__head center">
      {eyebrow("Πιστοποιήσεις", True)}
      <h2 class="headline" id="cert-title">Ποιότητα με χαρτιά.</h2>
      <p class="lead narrow">Κάθε μοντέλο συνοδεύεται από τα έγγραφα που ζητά η ευρωπαϊκή νομοθεσία.</p>
    </div>
    <div class="bento">
      <article class="tile tile--dark reveal">{icon("shield")}<h3>Δήλωση Συμμόρφωσης CE</h3>
        <p>Για καθένα από τα δέκα μοντέλα, σύμφωνα με το πρότυπο EN ISO 9806:2017 και την οδηγία οικολογικού σχεδιασμού 2009/125/ΕΚ.</p></article>
      <article class="tile tile--dark reveal">{icon("sun")}<h3>Ενεργειακή σήμανση</h3>
        <p>Ενεργειακή ετικέτα για κάθε δοχείο κατά τον Κανονισμό (ΕΕ) 812/2013: 130 λίτρα κλάση B, 150 λίτρα κλάση B, 220 λίτρα κλάση C.</p></article>
      {km_tile}
    </div>
  </div>
</section>
{cta_band("Ελάτε να γνωριστούμε.", "Επισκεφθείτε ένα από τα δύο καταστήματά μας στην Πάτρα, ή καλέστε μας.")}
'''
    page("/etaireia/", "Η Εταιρεία — Κατασκευαστής Ηλιακών από το 1985 | BAVARIA Πάτρα",
         "Η BAVARIA κατασκευάζει ηλιακούς θερμοσίφωνες στην Πάτρα από το 1985. Εργοστάσιο στο Βελβίτσι, Δήλωση Συμμόρφωσης CE και ενεργειακή σήμανση για κάθε μοντέλο.",
         body, crumbs=[("/etaireia/", "Εταιρεία")], active="/etaireia/", images=[img_url("install")])


def build_faq():
    items = faq_items()
    body = f'''
<section class="page-head center">
  <div class="wrap">
    {eyebrow("Συχνές ερωτήσεις", True)}
    <h1 class="display">Ρωτήστε μας ό,τι θέλετε.</h1>
    <p class="lead">Οι απαντήσεις στις πιο συχνές ερωτήσεις για τους ηλιακούς θερμοσίφωνες BAVARIA.</p>
  </div>
</section>
<section class="section section--tight"><div class="wrap"><div class="narrow"><div class="faq">{faq_html(items)}</div></div></div></section>
{cta_band("Δεν βρήκατε την απάντηση;", "Καλέστε μας ή στείλτε μήνυμα — απαντά ο ίδιος ο κατασκευαστής.")}
'''
    page("/syxnes-erotiseis/", "Συχνές Ερωτήσεις για Ηλιακούς Θερμοσίφωνες | BAVARIA",
         "Πόσα λίτρα χρειάζομαι; Τι σημαίνει BV και BVR; Πόσα χρόνια εγγύηση; Κάθε πότε service; Απαντήσεις από τον κατασκευαστή.",
         body, crumbs=[("/syxnes-erotiseis/", "Συχνές ερωτήσεις")], active="/syxnes-erotiseis/", schema=faq_schema(items))


def build_contact():
    c = CONFIG
    locs = ""
    for l in LOCATIONS:
        locs += f'''<article class="loc" id="{l["key"]}">
  <span class="loc__tag">{E(l["tag"])}</span>
  <h3>{E(l["street"])}</h3>
  <address>{E(l["zip"])} {E(l["city"])}</address>
  {(f'<p class="loc__phone"><a href="{tel(l["phone"])}">{E(l["phone"])}</a></p>' + hours_rows(l)) if l["store"] else '<p class="note">Χώρος παραγωγής. Για επίσκεψη κλείστε ραντεβού στο ' + E(c["phone"]) + '.</p>'}
  <div class="map" data-map-src="{E(l["embed"])}" data-map-title="Χάρτης: {E(l["name"])}">
    <div><button class="btn btn--dark" type="button">Εμφάνιση χάρτη</button>
    <p>Ο χάρτης φορτώνεται από την Google, η οποία μπορεί να χρησιμοποιήσει cookies. <a href="/politiki-cookies/">Περισσότερα</a></p></div>
  </div>
  <a class="link-more" href="{E(l["maps"])}" target="_blank" rel="noopener">Οδηγίες στο Google Maps</a>
</article>'''
    options = "".join(f"<option>{E(p['model'])}</option>" for p in PRODUCTS)
    body = f'''
<section class="page-head center">
  <div class="wrap">
    {eyebrow("Επικοινωνία", True)}
    <h1 class="display">Είμαστε εδώ για εσάς.</h1>
    <p class="lead">Καλέστε μας, στείλτε μήνυμα ή περάστε από την Πάτρα. Απαντάμε σε κάθε ερώτηση για μέγεθος, εγκατάσταση και τιμή.</p>
  </div>
</section>
<section class="section section--tight">
  <div class="wrap contact-grid">
    <div>
      <h2 class="title mb-18">Άμεση επικοινωνία</h2>
      <ul class="quick">
        <li><a href="{tel(c["phone"])}">{icon("phone", "")}<div><strong>{E(c["phone"])}</strong><span>Σταθερό</span></div></a></li>
        <li><a href="{tel(c["mobile"])}">{icon("mobile", "")}<div><strong>{E(c["mobile"])}</strong><span>Κινητό</span></div></a></li>
        <li><a href="mailto:{E(c["email"])}">{icon("mail", "")}<div><strong>{E(c["email"])}</strong><span>Email</span></div></a></li>
      </ul>
      <p class="note mt-20">Ωράριο καταστημάτων: Δευτέρα–Σάββατο πρωί, Τρίτη–Πέμπτη–Παρασκευή και απόγευμα 17:30–21:00. <a href="#where-title">Αναλυτικά ανά κατάστημα</a></p>
    </div>
    <div id="forma">
      <form class="form" data-mailform data-to="{E(c["email"])}" action="mailto:{E(c["email"])}" method="post" enctype="text/plain">
        <h2 class="title mb-6">Ζητήστε προσφορά</h2>
        <p class="note">Τα πεδία με * είναι υποχρεωτικά.</p>
        <div class="row">
          <div class="field"><label for="f-name">Ονοματεπώνυμο *</label><input id="f-name" name="name" type="text" autocomplete="name" required maxlength="100"></div>
          <div class="field"><label for="f-phone">Τηλέφωνο *</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required maxlength="30"></div>
        </div>
        <div class="row">
          <div class="field"><label for="f-model">Ενδιαφέρομαι για</label>
            <select id="f-model" name="model"><option value="">— Επιλέξτε —</option><option>130 λίτρα</option><option>150 λίτρα</option><option>220 λίτρα</option>{options}<option>Εγκατάσταση / service</option><option>Θέρμανση / ψύξη</option></select></div>
          <div class="field"><label for="f-area">Περιοχή</label><input id="f-area" name="area" type="text" maxlength="60" placeholder="π.χ. Πάτρα, Ρίο"></div>
        </div>
        <div class="field"><label for="f-msg">Μήνυμα</label><textarea id="f-msg" name="message" maxlength="2000" placeholder="π.χ. ταράτσα ή κεραμοσκεπή, πόσα άτομα, αν έχετε λέβητα"></textarea></div>
        <p class="form-note">Πατώντας «Συνέχεια στο email» ανοίγει η εφαρμογή email σας με το μήνυμα έτοιμο· εσείς το στέλνετε. Δεν αποθηκεύουμε τίποτα στον ιστότοπο. <a href="/politiki-aporritou/">Πολιτική απορρήτου</a></p>
        <button class="btn btn--primary" type="submit">Συνέχεια στο email</button>
      </form>
    </div>
  </div>
</section>
<section class="section section--alt" aria-labelledby="where-title">
  <div class="wrap">
    <div class="section__head center"><h2 class="headline" id="where-title">Δύο καταστήματα στην Πάτρα.</h2><p class="lead">Και το εργοστάσιό μας στο Βελβίτσι.</p></div>
    <div class="locs">{locs}</div>
  </div>
</section>
'''
    page("/epikoinonia/", "Επικοινωνία — Ηλιακοί Θερμοσίφωνες BAVARIA Πάτρα",
         f"Επικοινωνήστε με τη BAVARIA: τηλ. {c['phone']}, κινητό {c['mobile']}. Παντανάσσης 79, Ν.Ε.Ο. Πατρών–Αθηνών 86 και εργοστάσιο στο Βελβίτσι Πάτρας.",
         body, crumbs=[("/epikoinonia/", "Επικοινωνία")], active="/epikoinonia/")


def legal_page(path, title, h1, desc, content, crumb):
    body = f'''
<section class="page-head"><div class="wrap"><h1 class="headline">{E(h1)}</h1><p class="updated">Τελευταία ενημέρωση: {E(CONFIG["updated"])}</p></div></section>
<section class="section section--flush"><div class="wrap"><div class="prose">{content}</div></div></section>'''
    page(path, title, desc, body, crumbs=[(path, crumb)])


def controller_block():
    c = CONFIG
    return (f'<p><strong>{E(c["legal_name"])}</strong> (διακριτικός τίτλος «BAVARIA»)<br>Παντανάσσης 79, 26221 Πάτρα<br>'
            f'ΑΦΜ {E(c["afm"])} · ΔΟΥ {E(c["doy"])} · Αρ. ΓΕΜΗ {E(c["gemi"])}<br>'
            f'Τηλ. <a href="{tel(c["phone"])}">{E(c["phone"])}</a> · Email <a href="mailto:{E(c["email"])}">{E(c["email"])}</a></p>')


def build_legal():
    c = CONFIG
    privacy = f'''
<p>Εδώ εξηγούμε με απλά λόγια ποια προσωπικά δεδομένα επεξεργαζόμαστε, γιατί, για πόσο και ποια δικαιώματα έχετε, σύμφωνα με τον Γενικό Κανονισμό Προστασίας Δεδομένων (ΕΕ) 2016/679 («ΓΚΠΔ») και τον ν. 4624/2019.</p>
<h2>1. Υπεύθυνος επεξεργασίας</h2>
{controller_block()}
<h2>2. Τι επεξεργαζόμαστε και γιατί</h2>
<table>
<thead><tr><th>Πότε</th><th>Δεδομένα</th><th>Σκοπός</th><th>Νομική βάση</th></tr></thead>
<tbody>
<tr><td>Μας στέλνετε email (και μέσω της φόρμας «Ζητήστε προσφορά»)</td><td>Όσα γράφετε: όνομα, τηλέφωνο, email, περιοχή, μήνυμα</td><td>Απάντηση και προσφορά</td><td>Ενέργειες πριν από τη σύναψη σύμβασης κατόπιν αιτήματός σας (άρθρο 6 παρ. 1 β ΓΚΠΔ)</td></tr>
<tr><td>Μας τηλεφωνείτε</td><td>Αριθμός τηλεφώνου, όσα μας λέτε</td><td>Εξυπηρέτηση</td><td>Άρθρο 6 παρ. 1 β ΓΚΠΔ</td></tr>
<tr><td>Αγορά, εγκατάσταση, εγγύηση</td><td>Στοιχεία πελάτη, διεύθυνση εγκατάστασης, σειριακός αριθμός</td><td>Εκτέλεση σύμβασης, εγγύηση, φορολογικές υποχρεώσεις</td><td>Άρθρο 6 παρ. 1 β και γ ΓΚΠΔ</td></tr>
<tr><td>Επίσκεψη στον ιστότοπο</td><td>Τεχνικά δεδομένα σύνδεσης (π.χ. διεύθυνση IP) που καταγράφει ο πάροχος φιλοξενίας</td><td>Ασφάλεια και λειτουργία</td><td>Έννομο συμφέρον (άρθρο 6 παρ. 1 στ ΓΚΠΔ)</td></tr>
</tbody>
</table>
<p>Η φόρμα «Ζητήστε προσφορά» δεν στέλνει δεδομένα στον ιστότοπό μας: απλώς ετοιμάζει ένα email στη δική σας εφαρμογή, το οποίο στέλνετε εσείς. Δεν χρησιμοποιούμε τα στοιχεία σας για διαφήμιση, δεν τα πουλάμε και δεν κάνουμε κατάρτιση προφίλ ή αυτοματοποιημένες αποφάσεις.</p>
<h2>3. Πόσο τα κρατάμε</h2>
<ul>
<li>Μηνύματα και αιτήματα προσφοράς: έως 2 χρόνια από την τελευταία επικοινωνία, αν δεν ακολουθήσει αγορά.</li>
<li>Στοιχεία πελατών και εγγυήσεων: όσο διαρκεί η εγγύηση και όσο ορίζει η φορολογική νομοθεσία.</li>
</ul>
<h2>4. Ποιος τα βλέπει</h2>
<p>Μόνο εμείς. Χρησιμοποιούμε τρίτους παρόχους ως εκτελούντες την επεξεργασία: τον πάροχο φιλοξενίας του ιστοτόπου (DigitalOcean) και τον πάροχο ηλεκτρονικού ταχυδρομείου μας (Microsoft Outlook/Hotmail). Οι πάροχοι αυτοί μπορεί να επεξεργάζονται δεδομένα εκτός Ευρωπαϊκού Οικονομικού Χώρου, με τις εγγυήσεις του ΓΚΠΔ (απόφαση επάρκειας ΕΕ–ΗΠΑ ή τυποποιημένες συμβατικές ρήτρες). Δεδομένα δίνονται σε δημόσιες αρχές μόνο όταν το απαιτεί ο νόμος.</p>
<h2>5. Χάρτες Google</h2>
<p>Οι χάρτες στη σελίδα επικοινωνίας <strong>δεν φορτώνονται</strong> αν δεν πατήσετε «Εμφάνιση χάρτη». Αν τον ανοίξετε, η Google Ireland Ltd λαμβάνει τη διεύθυνση IP σας και μπορεί να χρησιμοποιήσει cookies, σύμφωνα με την <a href="https://policies.google.com/privacy?hl=el" target="_blank" rel="noopener">πολιτική απορρήτου της Google</a>.</p>
<h2>6. Cookies</h2>
<p>Ο ιστότοπός μας δεν χρησιμοποιεί cookies. Δείτε την <a href="/politiki-cookies/">πολιτική cookies</a>.</p>
<h2>7. Τα δικαιώματά σας</h2>
<p>Μπορείτε να ζητήσετε πρόσβαση, διόρθωση, διαγραφή, περιορισμό, φορητότητα ή να αντιταχθείτε σε επεξεργασία (άρθρα 15–21 ΓΚΠΔ), με email στο <a href="mailto:{E(c["email"])}">{E(c["email"])}</a>. Απαντάμε μέσα σε έναν μήνα.</p>
<p>Μπορείτε επίσης να υποβάλετε καταγγελία στην <a href="https://www.dpa.gr" target="_blank" rel="noopener">Αρχή Προστασίας Δεδομένων Προσωπικού Χαρακτήρα</a> (Κηφισίας 1–3, 115 23 Αθήνα).</p>
<h2>8. Ασφάλεια</h2>
<p>Ο ιστότοπος λειτουργεί αποκλειστικά με κρυπτογραφημένη σύνδεση (HTTPS) και δεν φορτώνει περιεχόμενο από τρίτους χωρίς την επιλογή σας.</p>
'''
    legal_page("/politiki-aporritou/", "Πολιτική Απορρήτου | BAVARIA", "Πολιτική απορρήτου",
               "Πώς η BAVARIA χειρίζεται τα προσωπικά σας δεδομένα σύμφωνα με τον ΓΚΠΔ.", privacy, "Πολιτική απορρήτου")
    cookies = '''
<p><strong>Ο ιστότοπός μας δεν χρησιμοποιεί cookies.</strong> Δεν έχουμε εργαλεία στατιστικών, διαφημίσεων ή παρακολούθησης και δεν αποθηκεύουμε τίποτα στη συσκευή σας. Γι' αυτό δεν θα δείτε αναδυόμενο παράθυρο για cookies.</p>
<p>Γραμματοσειρές, εικόνες και αρχεία φορτώνονται μόνο από τον δικό μας διακομιστή.</p>
<h2>Χάρτες Google</h2>
<p>Η μόνη εξαίρεση είναι οι χάρτες στη <a href="/epikoinonia/">σελίδα επικοινωνίας</a>, που δεν φορτώνονται αυτόματα. Αν πατήσετε «Εμφάνιση χάρτη», ο χάρτης φορτώνεται από την Google, η οποία μπορεί να τοποθετήσει δικά της cookies. Η επιλογή ισχύει μόνο για εκείνη την προβολή. Εναλλακτικά, ο σύνδεσμος «Οδηγίες στο Google Maps» ανοίγει σε νέα καρτέλα.</p>
<p>Περισσότερα στην <a href="https://policies.google.com/technologies/cookies?hl=el" target="_blank" rel="noopener">πολιτική cookies της Google</a> και στην <a href="/politiki-aporritou/">πολιτική απορρήτου</a> μας.</p>
'''
    legal_page("/politiki-cookies/", "Πολιτική Cookies | BAVARIA", "Πολιτική cookies",
               "Ο ιστότοπος της BAVARIA δεν χρησιμοποιεί cookies ούτε εργαλεία παρακολούθησης.", cookies, "Cookies")
    prices = ("<p>Οι τιμές είναι προτεινόμενες τιμές λιανικής του ηλιακού συστήματος, σε ευρώ, με ΦΠΑ 24%. "
              "Η εγκατάσταση και τυχόν επιπλέον υλικά τιμολογούνται με γραπτή προσφορά.</p>") if c["show_prices"] else ""
    terms = f'''
<h2>1. Ποιοι είμαστε</h2>
{controller_block()}
<h2>2. Χρήση του ιστοτόπου</h2>
<p>Ο ιστότοπος έχει ενημερωτικό χαρακτήρα και δεν είναι ηλεκτρονικό κατάστημα· οι πωλήσεις γίνονται με γραπτή προσφορά και σύμβαση.</p>
<h2>3. Πληροφορίες προϊόντων</h2>
<p>Τα τεχνικά στοιχεία προέρχονται από την τεχνική τεκμηρίωση, τις Δηλώσεις Συμμόρφωσης και τις ενεργειακές ετικέτες των προϊόντων μας και μπορεί να αλλάξουν λόγω εξέλιξης. Οι φωτογραφίες είναι πραγματικές εγκαταστάσεις BAVARIA και απεικονίζουν ενδεικτικά τη σειρά. Ο οδηγός επιλογής δίνει γενική πρόταση και δεν αντικαθιστά τη συμβουλή τεχνικού.</p>
{prices}
<h2>4. Εγγύηση</h2>
<p>Ισχύουν οι <a href="/eggyisi/">όροι εγγύησης</a> του εντύπου που συνοδεύει κάθε σύστημα, επιπλέον των δικαιωμάτων σας από τη νόμιμη εγγύηση (ν. 2251/1994, ν. 4967/2022).</p>
<h2>5. Πνευματική ιδιοκτησία</h2>
<p>Το σήμα BAVARIA®, το λογότυπο, τα κείμενα, οι φωτογραφίες και ο σχεδιασμός του ιστοτόπου προστατεύονται από τη νομοθεσία. Δεν επιτρέπεται η αναπαραγωγή τους χωρίς γραπτή άδεια.</p>
<h2>6. Ευθύνη και σύνδεσμοι</h2>
<p>Καταβάλλουμε κάθε προσπάθεια για τη σωστή λειτουργία του ιστοτόπου χωρίς να εγγυόμαστε ότι θα λειτουργεί πάντα χωρίς διακοπές. Δεν ευθυνόμαστε για το περιεχόμενο ιστοτόπων τρίτων στους οποίους παραπέμπουμε.</p>
<h2>7. Δίκαιο και επίλυση διαφορών</h2>
<p>Ισχύει το ελληνικό δίκαιο· αρμόδια τα δικαστήρια της Πάτρας, με την επιφύλαξη των δικαιωμάτων των καταναλωτών. Για εξωδικαστική επίλυση μπορείτε να απευθυνθείτε στον <a href="https://www.synigoroskatanaloti.gr" target="_blank" rel="noopener">Συνήγορο του Καταναλωτή</a>.</p>
'''
    legal_page("/oroi-xrisis/", "Όροι Χρήσης | BAVARIA", "Όροι χρήσης",
               "Όροι χρήσης του ιστοτόπου της BAVARIA Ηλιακοί Θερμοσίφωνες.", terms, "Όροι χρήσης")


def build_404():
    body = '''
<section class="page-head center page-head--tall">
  <div class="wrap">
    <span class="eyebrow c">Σφάλμα 404</span>
    <h1 class="display">Η σελίδα δεν βρέθηκε.</h1>
    <p class="lead">Ίσως άλλαξε διεύθυνση. Δοκιμάστε μία από τις παρακάτω.</p>
    <div class="actions actions--center mt-24">
      <a class="btn btn--primary" href="/">Αρχική</a><a class="link-more" href="/proionta/">Προϊόντα</a><a class="link-more" href="/epikoinonia/">Επικοινωνία</a>
    </div>
  </div>
</section>'''
    page("/404.html", "Η σελίδα δεν βρέθηκε | BAVARIA", "Η σελίδα δεν βρέθηκε.", body, noindex=True, out_name="404.html")


def build_meta_files():
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for p, imgs in PAGES:
        im = "".join(f"<image:image><image:loc>{url(i)}</image:loc></image:image>" for i in imgs)
        sm.append(f"  <url><loc>{url(p)}</loc><lastmod>{TODAY.isoformat()}</lastmod>{im}</url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {url('/sitemap.xml')}\n", encoding="utf-8")
    (OUT / "site.webmanifest").write_text(json.dumps({
        "name": "BAVARIA Ηλιακοί Θερμοσίφωνες", "short_name": "BAVARIA", "lang": "el",
        "icons": [{"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": "#ffffff", "background_color": "#ffffff", "display": "browser", "start_url": "/"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / ".well-known").mkdir(exist_ok=True)
    (OUT / ".well-known" / "security.txt").write_text(
        f"Contact: mailto:{CONFIG['email']}\nExpires: {YEAR + 1}-12-31T23:59:59.000Z\nPreferred-Languages: el, en\n"
        f"Canonical: {url('/.well-known/security.txt')}\n", encoding="utf-8")


if __name__ == "__main__":
    for f in ("contact.php", ".htaccess", "_headers"):
        (OUT / f).unlink(missing_ok=True)
    build_home(); build_products()
    for p in PRODUCTS:
        build_model(p)
    build_guide(); build_warranty(); build_about(); build_faq(); build_contact(); build_legal(); build_404()
    build_meta_files()
    print(f"Built {len(PAGES)} indexable pages into {OUT}")
    if not KEYMARK:
        print(f"⚠  Solar Keymark {CONFIG['keymark_no']} έληξε {CONFIG['keymark_valid_until']} — οι αναφορές Keymark είναι ΚΡΥΜΜΕΝΕΣ μέχρι να μπει νέα ημερομηνία λήξης.")
    if not CONFIG["show_prices"]:
        print("ℹ  Οι τιμές δεν εμφανίζονται (show_prices=False).")
