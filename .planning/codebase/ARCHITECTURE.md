<!-- refreshed: 2026-09-21 -->
# Architecture

**Analysis Date:** 2026-09-21

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                      Hugo Static Site                        │
├──────────────────────┬──────────────────────┬────────────────┤
│   Content Layer      │   Template Layer     │  Asset Layer   │
│  `content/posts/`   │  `layouts/`          │  `static/`     │
│  `archetypes/`      │  `config/_default/`  │  `assets/`     │
└──────────┬───────────┴──────────┬───────────┴───────┬────────┘
           │                      │                   │
           ▼                      ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Hugo Build Engine (Go)                          │
│  - Processes Markdown → HTML                                 │
│  - Applies templates & partials                              │
│  - Generates `public/` output                                │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloudflare Workers (via Wrangler)               │
│  `src/index.js` → Workers Assets Binding                    │
│  Serves `public/` as static assets                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Hugo Configuration | Site config, params, markup, taxonomies | `config/_default/hugo.toml`, `config/_default/params.toml`, `config/_default/markup.toml`, `config/_default/languages.ko.toml` |
| Theme (Blowfish) | Base layouts, partials, shortcodes, styling | `/Users/twinssn/Projects/shared-themes/blowfish/` |
| Content | Blog posts in Markdown with frontmatter | `content/posts/*.md` |
| Custom Layouts | Overrides for single post, render-link, partials | `layouts/_default/single.html`, `layouts/_default/_markup/render-link.html`, `layouts/partials/*` |
| Ads Integration | AdSense top-slot & in-article injection | `layouts/partials/adsense/top.html`, `layouts/partials/adsense/in-article.html` |
| Cross-blog Navigation | CUAP spider links & fallback related posts | `layouts/partials/cuap-spider-links.html`, `layouts/partials/related.html` |
| Extended Head | GA4, Twitter card, mobile ad CSS fixes | `layouts/partials/extend-head.html` |
| Workers Entry | Cloudflare Workers asset serving | `src/index.js` |
| Deployment Config | Wrangler Pages/Workers config | `wrangler.toml` |
| Static Assets | Favicons, robots.txt, ads.txt, background image | `static/` |
| Archetypes | Post scaffolding template | `archetypes/default.md` |

## Pattern Overview

**Overall:** Hugo static site generator with Cloudflare Workers/Pages deployment using shared theme override pattern.

**Key Characteristics:**
- **Theme inheritance**: Uses `blowfish` theme from shared location (`themesDir = "/Users/twinssn/Projects/shared-themes"`), overrides only necessary partials/layouts
- **Content-first**: Posts authored as Markdown with frontmatter in `content/posts/`
- **Partial override pattern**: Project-level `layouts/partials/` shadows theme partials
- **Ad injection logic**: Custom in-article ad placement via Hugo template logic in `single.html` (splits content by `<h2>` and `</p>`)
- **Cross-blog entity linking**: CUAP spider links injected at publish time; fallback to Hugo's built-in related content

## Layers

**Content Layer:**
- Purpose: Author-facing blog post source files
- Location: `content/posts/`
- Contains: Markdown files with frontmatter (title, date, draft, tags, categories, custom params like `cuap_cross_links`, `cuap_funnel`)
- Depends on: Archetypes for scaffolding
- Used by: Hugo build engine

**Template Layer:**
- Purpose: HTML generation, presentation logic
- Location: `layouts/`, `config/_default/`
- Contains: 
  - `layouts/_default/single.html` — Main post template with custom ad injection logic
  - `layouts/_default/_markup/render-link.html` — Custom link rendering (CTA button for "최저가 확인하기")
  - `layouts/partials/extend-head.html` — Head injections (GA4, Twitter card, mobile ad CSS)
  - `layouts/partials/adsense/*.html` — AdSense slot partials
  - `layouts/partials/cuap-spider-links.html` — Cross-blog navigation fallback
  - `layouts/partials/related.html` — Default related posts
  - Config files for Hugo behavior
- Depends on: Blowfish theme partials (fallback), site params
- Used by: Hugo build engine

**Asset Layer:**
- Purpose: Static files served as-is
- Location: `static/`, `assets/`
- Contains: Favicons, `ads.txt`, `robots.txt`, `site.webmanifest`, background SVG
- Depends on: None
- Used by: Hugo (copied to `public/`), Cloudflare Workers Assets

**Build/Deploy Layer:**
- Purpose: Production build and deployment
- Location: `src/index.js`, `wrangler.toml`, `hugo.toml` (root)
- Contains: Workers entry point, Wrangler config, themesDir pointer
- Depends on: `public/` output from Hugo build
- Used by: `wrangler deploy`, Cloudflare Workers runtime

## Data Flow

### Primary Request Path (Static Site Generation)

1. **Content Authoring** — Writer creates/edits `content/posts/*.md` with frontmatter
2. **Hugo Build** — `hugo --gc --minify` processes:
   - Parses Markdown + frontmatter
   - Applies `layouts/_default/single.html` (overrides theme's `single.html`)
   - Injects AdSense partials via template logic (splits content at `<h2>` and `</p>`)
   - Renders `cuap-spider-links.html` → falls back to `related.html` if no cross-link data
   - Applies `render-link.html` for special link styling
   - Includes `extend-head.html` in `<head>`
   - Outputs to `public/`
3. **Workers Deploy** — `env -u CLOUDFLARE_API_TOKEN wrangler deploy --config wrangler.toml` uploads `public/` to Cloudflare Workers Assets

### Content Processing Flow (single.html)

```
Post Markdown (.Content)
    │
    ├─► Hero partial (conditional)
    │
    ├─► Header: breadcrumbs, H1, meta, author
    │       │
    │       └─► adsense/top.html (before H1)
    │
    ├─► Body: series/series.html
    │       │
    │       ├─► Content splitting logic:
    │       │     $h2parts := split .Content "<h2"
    │       │     If multiple H2s:
    │       │       - After 1st </p> of intro → in-article ad #1
    │       │       - Before H2 #2 → in-article ad #2 (if wordCount≥800 or high-value section)
    │       │       - Before H2 #4 → in-article ad #3 (if maxAds=3)
    │       │     Else (no H2s):
    │       │       - After 1st </p> → in-article ad
    │       │
    │       └─► adsense/in-article.html (injected at calculated positions)
    │
    ├─► series/series-closed.html
    ├─► sharing-links.html
    ├─► cuap-spider-links.html → (fallback) related.html
    │
    └─► Footer: pagination, comments (disabled)
```

### Cross-Blog Navigation Flow

```
Post params (cuap_cross_links, cuap_funnel)
    │
    ├─► Present? → Render cuap-spider-links.html (passes .Content through)
    │
    └─► Absent? → Render related.html (Hugo's .Site.RegularPages.Related)
```

**State Management:**
- No client-side state (static HTML)
- Build-time state: Hugo Scratch (`$.Scratch.Set "scope" "single"`), template variables
- Cross-blog links injected at publish time by external pipeline (not in this repo)

## Key Abstractions

**Ad Injection Logic:**
- Purpose: Automatically place AdSense ads within article content at semantic boundaries
- Examples: `layouts/_default/single.html` lines 42-78
- Pattern: String splitting on HTML tags (`<h2`, `</p>`) with conditional insertion based on word count and section

**CUAP Spider Links:**
- Purpose: Cross-blog entity linking (shortcode/nearby-card/funnel-card)
- Examples: `layouts/partials/cuap-spider-links.html`, post params `cuap_cross_links`, `cuap_funnel`
- Pattern: Fallback chain — cross-blog data → same-blog related posts

**Custom Link Rendering:**
- Purpose: Convert "최저가 확인하기" links to styled CTA buttons with `rel="nofollow sponsored"`
- Examples: `layouts/_default/_markup/render-link.html`
- Pattern: Hugo markup render hook

**Mobile Ad CSS Fix:**
- Purpose: Prevent ad overflow on mobile, hide unfilled ad slots
- Examples: `layouts/partials/extend-head.html` lines 8-26
- Pattern: Injected `<style>` in `<head>` via partial

## Entry Points

**Hugo Build:**
- Location: CLI command `hugo --gc --minify` (uses `hugo.toml` root for themesDir, `config/_default/` for config)
- Triggers: Manual build, CI/CD pipeline
- Responsibilities: Full static site generation to `public/`

**Cloudflare Workers:**
- Location: `src/index.js`
- Triggers: HTTP request to `health.informationhot.kr` (via Workers route)
- Responsibilities: Serve static assets from `public/` via `env.ASSETS.fetch()`

**Content Creation:**
- Location: `archetypes/default.md`
- Triggers: `hugo new posts/<slug>.md`
- Responsibilities: Scaffold new post with date, draft=true, title from filename

## Architectural Constraints

- **Threading:** Single-threaded Hugo build; Workers runtime is single-threaded per isolate
- **Global state:** None in Workers (`src/index.js` is stateless); Hugo uses template-level Scratch
- **Circular imports:** None detected (Hugo template inheritance is acyclic)
- **Theme coupling:** Project layouts override theme partials by name — theme updates may require override updates
- **AdSense coupling:** Publisher ID hardcoded in `config/_default/params.toml` (ca-pub-6677996696534146 — informationhot.kr family). Must match domain family per adsense-publisher-governance rules.
- **External theme dependency:** `themesDir` points to shared location outside repo — theme changes affect all blogs using it

## Anti-Patterns

### Content Splitting via String Manipulation

**What happens:** `single.html` splits `.Content` (rendered HTML) on `<h2` and `</p>` strings to inject ads
**Why it's wrong:** Fragile to HTML output changes; breaks if markup render hooks change heading/tags; no parser safety
**Do this instead:** Use Hugo's `.TableOfContents` or custom shortcode for ad placement markers, or client-side JS injection post-render

### Hardcoded AdSense Publisher ID

**What happens:** `params.toml` contains `adsense = "ca-pub-6677996696534146"` directly
**Why it's wrong:** Violates adsense-publisher-governance — must match domain family (informationhot.kr = 6677, rotcha.kr = 8772, aikorea24.kr = 5938). Cannot be changed per environment.
**Do this instead:** Use environment-specific config or inject via build pipeline; validate against domain family

### Theme Override Shadowing Without Documentation

**What happens:** Project `layouts/partials/` files shadow theme files with same name/path
**Why it's wrong:** Theme upgrades silently change behavior; no record of what was overridden or why
**Do this instead:** Document each override with comment header explaining purpose and theme version baseline

## Error Handling

**Strategy:** Fail-fast at build time; runtime serves static assets only

**Patterns:**
- Hugo template errors → build failure (visible in CI/logs)
- Missing partials → Hugo warns (`warnf`) but continues (e.g., comments partial)
- Workers fetch error → 404 response (line 7 in `src/index.js`)
- No client-side error boundaries (static HTML)

## Cross-Cutting Concerns

**Logging:** None in Workers (static serving); Hugo logs to stdout during build

**Validation:** 
- Frontmatter validated by Hugo at build time
- Markdown linting not configured
- Link checking not configured

**Authentication:** None (public blog)

**Analytics:** GA4 via `extend-head.html` (Measurement ID: 532414941) + site param `googleAnalytics = "G-995DNX1KV8"` (dual tracking)

---

*Architecture analysis: 2026-09-21*