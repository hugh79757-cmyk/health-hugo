# Coding Conventions

**Analysis Date:** 2026-09-21

## Naming Patterns

**Files:**
- Content (Markdown): `kebab-case-korean-or-english.md` — e.g., `마그네슘-고르는-법-2026년-최신-가이드.md`, `bcaa-recommend-nyuteulikoseuteu-bcaa-powder.md`
- Hugo templates: `kebab-case.html` — standard Hugo convention (`single.html`, `render-link.html`, `top.html`, `in-article.html`)
- Partials: `kebab-case.html` in `partials/` subdirectories by feature (e.g., `partials/adsense/top.html`)
- Config: `kebab-case.toml` — `hugo.toml`, `params.toml`, `markup.toml`, `languages.ko.toml`
- Workers: `camelCase.js` — `src/index.js`
- CSS: `kebab-case.css` — `custom.css`, `funnel-card.css`

**Directories:**
- Hugo standard names: `_default`, `_markup`, `partials`, `posts`
- Config environment: `_default`
- Feature-based: `adsense` (under `partials/`)

**Frontmatter Keys:**
- Standard Hugo: `title`, `date`, `draft`, `tags`, `categories`, `series`
- Custom CUAP params: `cuap_cross_links`, `cuap_funnel`, `showHero`, `heroStyle`, `showBreadcrumbs`, `showAuthor`, `showAuthorBottom`, `showComments`

**CSS Classes:**
- BEM-like for custom components: `.cross-sell-card`, `.cross-sell-card__title`, `.cross-sell-card__links`, `.cross-sell-card__link`
- Funnel card: `.funnel-card`, `.funnel-card-inner`, `.funnel-card-thumb`, `.funnel-card-body`, `.funnel-card-label`, `.funnel-card-title`, `.funnel-card-cta`
- Utility prefixes: `.ad-` for ad containers (`.ad-top`, `.ad-inarticle`, `.ad-leaderboard`, `.ad-mobile-sticky`)
- CTA button: `.btn-price-check`
- Dark mode: `html.dark` selector prefix (not `.dark` class on elements)

**Hugo Template Variables:**
- Scratch variables: `$`-prefixed (`$heroStyle`, `$content`, `$wordCount`, `$section`, `$isHighValue`, `$maxAds`, `$h2parts`, `$pParts`)
- Parameter access: `.Params.<key>` or `site.Params.<key>` with `| default` fallbacks
- Conditional checks: `.Params.showHero | default (site.Params.article.showHero | default false)`

## Code Style

**Formatting:**
- **Hugo templates**: 2-space indentation, inline `{{ }}` delimiters, no trailing spaces
- **CSS**: 2-space indentation, semicolon-terminated declarations, grouped by component with comment headers (`/* ── Component Name ── */`)
- **TOML**: 2-space indentation, inline tables for simple objects (`[advertisement]` section), arrays in brackets
- **JavaScript (Workers)**: 2-space indentation, `async/await`, `const`/`let`, ES modules syntax

**Linting:**
- No formal linter configured for Hugo templates, CSS, or Workers JS
- Hugo validates templates at build time (fail-fast)
- Goldmark markdown renderer with `unsafe = true` allows raw HTML in content
- No markdownlint, stylelint, or ESLint configs detected

## Import Organization

**Hugo Template Partials:**
- Referenced via `{{ partial "<path>" . }}` or `{{ partial "<path>" (dict ...) }}`
- Path relative to `layouts/partials/` — e.g., `adsense/top.html`, `series/series.html`, `cuap-spider-links.html`
- No explicit import statements; Hugo resolves by convention

**CSS:**
- Theme manages Tailwind imports via `/Users/twinssn/Projects/shared-themes/blowfish/`
- Custom CSS in `assets/css/custom.css` and `assets/css/extended/funnel-card.css` loaded via theme's asset pipeline
- No `@import` statements in custom CSS files

**Workers (src/index.js):**
- No imports — minimal single-file entry point using only `env.ASSETS` binding

**Path Aliases:**
- `themesDir = "/Users/twinssn/Projects/shared-themes"` in `hugo.toml` and `config/_default/hugo.toml` points to shared Blowfish theme
- Theme partials overridden by project `layouts/partials/` with same path (shadowing)

## Error Handling

**Patterns:**
- **Build-time**: Hugo template errors cause build failure — visible in CLI output
- **Missing partials**: `warnf` used for optional partials (e.g., comments partial in `single.html` line 99) — warns but continues
- **Runtime (Workers)**: `try/catch` in `src/index.js` catches fetch errors, returns 404 Response
- **Client-side**: None (static HTML, no JS error boundaries)
- **Ad injection**: No error handling for malformed HTML splitting — relies on predictable Hugo output

**AdSense Loading:**
- Uses `(adsbygoogle = window.adsbygoogle || []).push({})` pattern in each ad partial
- No async/defer on inline scripts — executes immediately after `<ins>` element

## Logging

**Framework:** None configured
- **Hugo build**: Logs to stdout/stderr during `hugo --gc --minify`
- **Workers**: No logging in `src/index.js` (static asset serving only)
- **Cloudflare**: Access via `wrangler tail` or dashboard for deployed Workers

## Comments

**When to Comment:**
- File headers for custom partials explaining purpose and context (e.g., `cuap-spider-links.html` lines 1-3)
- Complex template logic sections (e.g., `single.html` ad injection logic lines 42-78 with inline comments)
- CSS component sections with `/* ── Component Name ── */` headers
- No JSDoc/TSDoc (no TypeScript, minimal JS)

**JSDoc/TSDoc:**
- Not applicable — no TypeScript, only 10-line Workers entry point

## Function Design

**Hugo Templates (not functions per se):**
- **Size**: Templates kept focused — `single.html` is largest at 111 lines with ad injection logic
- **Parameters**: Pass context via `.` (current page) or `dict` for multiple values
- **Return Values**: HTML output directly; no explicit returns
- **Reusability**: Partials for repeated chunks (adsense, series, sharing, cross-links)

**Workers (src/index.js):**
- Single `fetch` handler — minimal, stateless, no helper functions needed

## Module Design

**Exports:**
- Hugo: No module system — templates resolved by file path convention
- Workers: Default export of `{ fetch }` handler object

**Barrel Files:**
- Not used

**Theme Override Pattern:**
- Project `layouts/` shadows theme files by exact path match
- Document each override with header comment explaining purpose and theme version baseline (see `cuap-spider-links.html` as example)
- Anti-pattern: Shadowing without documentation (see ARCHITECTURE.md anti-patterns section)

## CSS Conventions

**Tailwind Integration:**
- Theme uses Tailwind v4 via `@tailwindcss/cli`
- Custom CSS extends rather than replaces — uses `@media` for responsive, `html.dark` for dark mode
- Component styles defined in `custom.css` and `extended/funnel-card.css`
- Utility classes preferred in templates (`mt-5`, `max-w-prose`, `flex`, `prose`, `dark:prose-invert`)

**Dark Mode:**
- `html.dark` selector on `<html>` element (Blowfish default)
- All custom components provide `html.dark` variants
- Ad containers force white background in dark mode (`.dark ins.adsbygoogle`, `html.dark ins.adsbygoogle`)

**Responsive:**
- Mobile-first via `@media (max-width: 767px)` and `@media (max-width: 640px)` breakpoints
- `.desktop-only` / `.mobile-only` utility classes for visibility toggling
- Ad containers have `overflow: hidden`, `max-width: 100%` for mobile safety

**Ad-Specific CSS:**
- `.ad-inarticle`, `.ad-top`, `.ad-leaderboard`, `.ad-mobile-sticky` container classes
- `ins` elements forced `display: block !important`, `width: 100% !important`
- Unfilled ads hidden via `ins.adsbygoogle[data-ad-status="unfilled"] { display: none !important }`

## Ad Injection Conventions

**Placement Logic (single.html):**
- Top ad: Before H1, after breadcrumbs (`adsense/top.html`)
- In-article ads: Split `.Content` on `<h2` and `</p>` strings
  - After first `</p>` of intro → ad #1
  - Before H2 #2 → ad #2 (if wordCount ≥ 800 or high-value section)
  - Before H2 #4 → ad #3 (if maxAds = 3)
  - Fallback (no H2s): After first `</p>` → single in-article ad
- Slot IDs from `site.Params.advertisement` in `params.toml`

**AdSense Publisher ID Governance:**
- Must match domain family per `adsense-publisher-governance` skill
- `health.informationhot.kr` → `ca-pub-6677996696534146` (informationhot.kr family)
- Hardcoded in `params.toml` — anti-pattern per ARCHITECTURE.md (should be env-injected)

## Cross-Blog Entity Linking (CUAP)

**Frontmatter Params:**
- `cuap_cross_links`: Array of cross-blog related posts (injected at publish time)
- `cuap_funnel`: Funnel header data for landing→course navigation

**Fallback Chain:**
1. If `cuap_cross_links` or `cuap_funnel` present → render `cuap-spider-links.html` (passes `.Content` through)
2. Else → render `related.html` (Hugo's built-in `.Site.RegularPages.Related`)

**CSS Components:**
- Cross-sell cards: `.cross-sell-card` with `__title`, `__links`, `__link` BEM elements
- Funnel header: `.funnel-header` with `__label`, `__links`, `__link`
- Funnel card: `.funnel-card` with `-bridge` variant, responsive down to 640px

## Deployment Conventions

**Hugo Build:**
```bash
HUGO_THEMESDIR=/Users/twinssn/Projects/shared-themes hugo --gc --minify
```

**Wrangler Deploy (CRITICAL):**
```bash
env -u CLOUDFLARE_API_TOKEN wrangler deploy --config wrangler.toml
```
- `CLOUDFLARE_API_TOKEN` MUST be unset to use OAuth profile (`hugh79757` / `default`)
- Otherwise auth error code 10000 occurs

**Output:**
- `public/` committed to repo (required for Workers Assets binding)
- `resources/_gen/` committed (build performance cache)

## Architectural Constraints Affecting Conventions

- **No client-side JS framework** — all logic in Hugo templates or static CSS
- **External theme dependency** — overrides must track theme changes; document baselines
- **Static-first** — no dynamic data fetching, no API routes in Workers
- **AdSense domain coupling** — publisher ID locked to domain family; cannot change per environment
- **Content splitting fragility** — string-based HTML manipulation in templates; avoid modifying output tags that injection logic depends on (`<h2`, `</p>`)

---

*Convention analysis: 2026-09-21*