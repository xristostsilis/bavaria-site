# bavaria.com.gr

Στατικό website για DigitalOcean App Platform. Χωρίς server, χωρίς βάση, χωρίς cookies.

## Δομή
- `public/` — το έτοιμο site (αυτό σερβίρει το DigitalOcean)
- `tools/build.py` — φτιάχνει όλες τις σελίδες από τα στοιχεία στην αρχή του αρχείου
- `.do/app.yaml` — ρυθμίσεις DigitalOcean (static site, domain, www → bavaria.com.gr, 301 από παλιά URLs)

## Αλλαγή στοιχείων
1. Ανοίξτε `tools/build.py` → `CONFIG` / `PRODUCTS`.
2. `python3 tools/build.py`
3. `git commit` + `git push` → το DigitalOcean ανεβάζει αυτόματα.

Σημαντικές ρυθμίσεις στο `CONFIG`:
- `keymark_valid_until`: λήξη Solar Keymark (τώρα 30/08/2027). Στην ανανέωση: νέα ημερομηνία + νέο PDF στο `public/assets/docs/`. Αν λήξει, οι αναφορές κρύβονται αυτόματα.
- `show_prices`: προτεινόμενες τιμές λιανικής (με ΦΠΑ) — ενεργό. Τιμές στο `PRODUCTS` (msrp).

## DigitalOcean
Στο App Platform: Settings → App Spec → επικόλληση του `.do/app.yaml` (ή `doctl apps update <APP_ID> --spec .do/app.yaml`).
Στο DNS: `bavaria.com.gr` και `www.bavaria.com.gr` να δείχνουν στο app (ο DigitalOcean δείχνει τις εγγραφές).

## Μετά το ανέβασμα
- Google Search Console → υποβολή `https://bavaria.com.gr/sitemap.xml`.
- Google Business Profile για έδρα, υποκατάστημα, εργοστάσιο, με ίδια στοιχεία με το site και τις νέες φωτογραφίες.
