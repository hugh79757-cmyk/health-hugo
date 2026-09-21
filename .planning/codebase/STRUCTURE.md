# Codebase Structure

**Analysis Date:** 2026-09-21

## Directory Layout

```
health-hugo/
├── .planning/              # GSD planning artifacts (codebase maps, phase docs)
├── .wrangler/              # Wrangler local dev state (ignored)
├── archetypes/             # Hugo content scaffolding templates
├── assets/                 # Hugo asset pipeline sources (images, SCSS - currently empty)
├── config/                 # Hugo configuration (per-environment)
│   └── _default/           # Default environment config
│       ├── hugo.toml       # Main site config
│       ├── params.toml     # Site parameters (theme, ads, GA, etc.)
│       ├── markup.toml     # Markdown processing config
│       └── languages.ko.toml  # Korean language config
├── content/                # Blog post content (Markdown + frontmatter)
│   └── posts/              # All blog posts (~60+ files)
├── data/                   # Hugo data files (JSON/TOML/YAML - currently empty)
├── i18n/                   # Internationalization strings (currently empty)
├── layouts/                # Template overrides (shadows theme partials)
│   ├── _default/
│   │   ├── single.html          # Main post template (custom ad injection)
│   │   └── _markup/
│   │       └── render-link.html # Custom link render hook
│   └── partials/
│       ├── extend-head.html     # Head injections (GA4, Twitter, mobile CSS)
│       ├── cuap-spider-links.html  # Cross-blog nav fallback
│       ├── related.html         # Default related posts
│       └── adsense/
│           ├── top.html         # Top-of-article leaderboard
│           └── in-article.html  # In-content fluid ad
├── public/                   # Hugo build output (generated, committed)
├── resources/                # Hugo resource cache (generated, committed)
│   └── _gen/
│       ├── images/           # Processed images
│       └── assets/           # Processed assets
├── src/                      # Cloudflare Workers source
│   └── index.js              # Workers entry point (asset serving)
├── static/                   # Static files copied to public/
│   ├── ads.txt               # AdSense authorization
│   ├── favicon*.png/ico      # Favicons
│   ├── img/background.svg    # Default background
│   ├── robots.txt            # Crawler rules
│   └── site.webmanifest      # PWA manifest
├── themes/                   # Local theme mount (empty — uses themesDir)
├── .gitignore
├── .gitmodules
├── hugo.toml                 # Root config (themesDir only)
├── hugo.yaml.bak             # Backup config
└── wrangler.toml             # Cloudflare Workers/Pages deploy config
```

## Directory Purposes

**`.planning/`:**
- Purpose: GSD (Getting Shit Done) planning artifacts
- Contains: Codebase maps (ARCHITECTURE.md, STRUCTURE.md, STACK.md, INTEGRATIONS.md), phase plans, requirements
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`

**`archetypes/`:**
- Purpose: Content scaffolding templates for `hugo new`
- Contains: `default.md` — minimal frontmatter template
- Key files: `archetypes/default.md`

**`assets/`:**
- Purpose: Source assets for Hugo's asset pipeline (images, SCSS, JS)
- Contains: Currently empty — all static assets in `static/`

**`config/_default/`:**
- Purpose: Hugo site configuration for default environment
- Contains: 4 config files (hugo, params, markup, languages)
- Key files: All `.toml` files in this directory

**`content/posts/`:**
- Purpose: Blog post source files
- Contains: 60+ Markdown files with frontmatter (title, date, draft, tags, categories, custom params: `cuap_cross_links`, `cuap_funnel`, `showHero`, `heroStyle`, etc.)
- Key files: All `*.md` files in this directory

**`layouts/`:**
- Purpose: Template overrides that shadow the Blowfish theme
- Contains: 
  - `_default/single.html` — Main post layout with custom ad injection logic
  - `_default/_markup/render-link.html` — Markdown render hook for CTA links
  - `partials/extend-head.html` — `<head>` injections
  - `partials/cuap-spider-links.html` — Cross-blog navigation
  - `partials/related.html` — Fallback related posts
  - `partials/adsense/*.html` — AdSense slot partials
- Key files: All files listed above

**`public/`:**
- Purpose: Hugo build output (static HTML, CSS, JS, assets)
- Contains: Full generated site (~600+ files)
- Generated: Yes (by `hugo --gc --minify`)
- Committed: Yes (for Workers Assets deployment)

**`resources/_gen/`:**
- Purpose: Hugo resource cache (image processing, asset fingerprinting)
- Contains: Processed images, fingerprinted assets
- Generated: Yes
- Committed: Yes (speeds up builds)

**`src/`:**
- Purpose: Cloudflare Workers application code
- Contains: `index.js` — minimal asset fetcher
- Key files: `src/index.js`

**`static/`:**
- Purpose: Static files copied verbatim to `public/`
- Contains: Favicons, `ads.txt`, `robots.txt`, `site.webmanifest`, background image
- Key files: All files listed in Directory Layout

**`themes/`:**
- Purpose: Local theme directory (unused — `themesDir` points to shared location)
- Contains: Empty

## Key File Locations

**Entry Points:**
- `hugo.toml` (root): themesDir pointer for Hugo CLI
- `config/_default/hugo.toml`: Main Hugo configuration
- `src/index.js`: Cloudflare Workers entry point
- `wrangler.toml`: Deployment configuration

**Configuration:**
- `config/_default/params.toml`: Site params (theme, colors, ads, GA, article/list/taxonomy settings)
- `config/_default/markup.toml`: Markdown processing (goldmark, highlight, table of contents)
- `config/_default/languages.ko.toml`: Korean language strings

**Core Logic:**
- `layouts/_default/single.html`: Post rendering + ad injection logic
- `layouts/partials/extend-head.html`: Analytics, social, mobile CSS fixes
- `layouts/partials/adsense/*.html`: AdSense ad slots
- `layouts/partials/cuap-spider-links.html`: Cross-blog entity linking
- `layouts/_default/_markup/render-link.html`: CTA link styling

**Testing:**
- No test files detected in this repository

## Naming Conventions

**Files:**
- Content: `kebab-case-korean-or-english.md` (e.g., `마그네슘-고르는-법-2026년-최신-가이드.md`, `bcaa-recommend-nyuteulikoseuteu-bcaa-powder.md`)
- Templates: `kebab-case.html` (Hugo standard)
- Partials: `kebab-case.html` in `partials/` subdirectories
- Config: `kebab-case.toml`
- Workers: `camelCase.js`

**Directories:**
- Hugo standard: `_default`, `_markup`, `partials`, `posts`
- Config: `_default` (environment name)
- Custom: `adsense` (feature-based)

**Frontmatter Keys:**
- Standard: `title`, `date`, `draft`, `tags`, `categories`, `series`
- Custom: `cuap_cross_links`, `cuap_funnel`, `showHero`, `heroStyle`, `showBreadcrumbs`, `showAuthor`, `showAuthorBottom`, `showComments`

## Where to Add New Code

**New Blog Post:**
- Primary code: `content/posts/<slug>.md` (use `hugo new posts/<slug>.md`)
- Frontmatter: Follow archetype + add CUAP params as needed

**New Template Override:**
- Identify theme partial to override in `/Users/twinssn/Projects/shared-themes/blowfish/layouts/partials/`
- Create matching path under `layouts/partials/`
- Document purpose in file header comment

**New Partial/Component:**
- Implementation: `layouts/partials/<feature>/<name>.html`
- Include in templates via `{{ partial "<feature>/<name>.html" . }}`

**New AdSense Slot:**
- Add partial: `layouts/partials/adsense/<slot-name>.html`
- Reference in `params.toml` under `[advertisement]`
- Include in `single.html` at desired position

**New Static Asset:**
- Place in `static/` (copied to `public/` on build)
- Reference via absolute path from site root (e.g., `/img/logo.png`)

**Workers Logic:**
- Modify `src/index.js` for custom routing, headers, or middleware
- For complex Workers, add modules under `src/` and import in `index.js`

**Configuration Changes:**
- Site-wide: `config/_default/hugo.toml` or `params.toml`
- Markdown processing: `config/_default/markup.toml`
- Language strings: `config/_default/languages.ko.toml`

## Special Directories

**`public/`:**
- Purpose: Hugo build output — deployed to Cloudflare Workers Assets
- Generated: Yes (`hugo --gc --minify`)
- Committed: Yes (required for Workers Assets binding)

**`resources/_gen/`:**
- Purpose: Hugo resource cache (image processing, asset fingerprinting)
- Generated: Yes
- Committed: Yes (build performance)

**`.wrangler/`:**
- Purpose: Wrangler local development state (D1, KV, R2 local persistence)
- Generated: Yes (by `wrangler dev`)
- Committed: No (in `.gitignore`)

**`themes/`:**
- Purpose: Local theme mount point (unused)
- Generated: No
- Committed: No (empty, but tracked)

---

*Structure analysis: 2026-09-21*