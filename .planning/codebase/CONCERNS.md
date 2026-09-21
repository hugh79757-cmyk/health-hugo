# Codebase Concerns

**Analysis Date:** 2026-09-21

## Tech Debt

### Ad Injection Logic — Fragile String Splitting
- **Issue:** `single.html` lines 42-78 splits rendered HTML (`.Content`) on `<h2` and `</p>` strings to inject AdSense ads
- **Files:** `layouts/_default/single.html`
- **Impact:** Breaks if Hugo/Goldmark output changes (e.g., heading anchor links, TOC injection, render hooks). No parser safety — relies on predictable tag structure
- **Fix approach:** Replace with Hugo's `.TableOfContents` for heading positions, or use shortcode markers (`{{% ad %}}`) at authoring time, or client-side JS post-render injection

### Hardcoded AdSense Publisher ID
- **Issue:** `params.toml` contains `adsense = "ca-pub-6677996696534146"` directly
- **Files:** `config/_default/params.toml` line 57
- **Impact:** Violates `adsense-publisher-governance` — must match domain family (informationhot.kr = 6677). Cannot be changed per environment; deploy to wrong domain = blank ads
- **Fix approach:** Inject via build pipeline/env var; validate against domain family at build time

### Theme Override Shadowing Without Documentation
- **Issue:** Project `layouts/partials/` files shadow theme files by exact path match with no record of what was overridden or why
- **Files:** `layouts/partials/extend-head.html`, `layouts/partials/cuap-spider-links.html`, `layouts/partials/adsense/*.html`, `layouts/_default/single.html`, `layouts/_default/_markup/render-link.html`
- **Impact:** Theme upgrades silently change behavior; no baseline for diffing
- **Fix approach:** Add header comment to each override explaining purpose and theme version baseline (see `cuap-spider-links.html` as good example)

### Duplicate Backup Files Polluting Content Directory
- **Issue:** 251 `.bak` / `.bak2` / `.bak.pre-regen-v4` files in `content/posts/`
- **Files:** `content/posts/*.bak*`
- **Impact:** Wasted disk space; confusion during content audits; git status noise
- **Fix approach:** `find content/posts -name "*.bak*" -delete` and add `*.bak*` to `.gitignore`

### Dual GA4 Tracking (Two Measurement IDs)
- **Issue:** `params.toml` has `googleAnalytics = "G-995DNX1KV8"` AND `hugo.toml` has `[services.googleAnalytics] ID = "G-G5KS0DE6HL"`
- **Files:** `config/_default/params.toml` line 1, `config/_default/hugo.toml` line 48
- **Impact:** Double pageviews in GA4; inflated metrics; wasted quota
- **Fix approach:** Remove one — keep either params.toml OR services.googleAnalytics, not both

### Same Slot ID for Top and In-Article Ads
- **Issue:** Both `topSlot` and `inArticleSlot` set to `"2195212287"` in `params.toml`
- **Files:** `config/_default/params.toml` lines 58-59
- **Impact:** AdSense reporting cannot distinguish top vs in-article performance; suboptimal yield optimization
- **Fix approach:** Create separate ad slots in AdSense console; update params.toml

## Known Bugs

### Content Splitting Breaks on Edge Cases
- **Symptoms:** Ad injection may produce malformed HTML if `.Content` has unexpected structure (e.g., nested tags, self-closing elements, no `</p>` before first `<h2>`)
- **Files:** `layouts/_default/single.html` lines 50-78
- **Trigger:** Posts with non-standard heading structures, short content, or custom shortcodes that output HTML
- **Workaround:** None — relies on predictable Hugo output
- **Fix approach:** Add defensive checks; fallback to no-ad if split fails; use parser-based approach

### Missing `</p>` After First Paragraph in Split Logic
- **Symptoms:** Line 56 outputs `{{ index $pParts 0 | safeHTML }}</p>` but if `$pParts[0]` already contains closing tag, produces duplicate `</p>`
- **Files:** `layouts/_default/single.html` line 56
- **Trigger:** Any post where first paragraph split produces already-closed HTML
- **Fix approach:** Check if `</p>` suffix exists before appending

## Security Considerations

### No Content Security Policy (CSP)
- **Risk:** XSS via injected scripts (adsbygoogle.js, gtag.js), inline styles/scripts in partials
- **Files:** `layouts/partials/extend-head.html`, `layouts/partials/adsense/*.html`, `layouts/_default/single.html`
- **Current mitigation:** None — no CSP header in Workers or meta tag
- **Recommendations:** Add CSP header via Workers `Response.headers.set("Content-Security-Policy", ...)` or `<meta http-equiv="Content-Security-Policy">`; allow `https://pagead2.googlesyndication.com`, `https://www.googletagmanager.com`, `'self'`, `'unsafe-inline'` (required for inline ad scripts)

### Goldmark `unsafe = true` Allows Raw HTML in Markdown
- **Risk:** Content authors (or compromised pipeline) can inject arbitrary HTML/JS in posts
- **Files:** `config/_default/markup.toml` (referenced in STACK.md)
- **Current mitigation:** Trusted content pipeline only
- **Recommendations:** Set `unsafe = false` if raw HTML not needed; or sanitize at publish pipeline

### No Subresource Integrity (SRI) for External Scripts
- **Risk:** Compromised CDN (Google AdSense, GA4) serves malicious code
- **Files:** `layouts/partials/adsense/*.html`, `layouts/partials/extend-head.html`
- **Current mitigation:** None
- **Recommendations:** Add `integrity` and `crossorigin="anonymous"` to `<script src="...">` tags; use SRI hashes from trusted sources

### AdSense Publisher ID Exposed in Repo
- **Risk:** Publisher ID visible in git history — could be used for ad fraud on other domains
- **Files:** `config/_default/params.toml`, `static/ads.txt`
- **Current mitigation:** Domain-locked in AdSense console
- **Recommendations:** Move to build-time env var injection; keep `ads.txt` as-is (required for verification)

## Performance Bottlenecks

### Large Committed Build Artifacts
- **Problem:** `public/` (86 MB) and `resources/_gen/` (14 MB) committed to repo
- **Files:** `public/`, `resources/_gen/`
- **Cause:** Required for Workers Assets binding but bloats repo clone size
- **Improvement path:** Use `.gitignore` for these dirs and generate in CI/CD; or use Cloudflare Pages direct Git integration (builds on CF side)

### Inline Ad Script Duplication
- **Problem:** Each ad partial (`top.html`, `in-article.html`) includes `<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>`
- **Files:** `layouts/partials/adsense/top.html` line 9, `layouts/partials/adsense/in-article.html` line 9
- **Cause:** AdSense docs show per-slot push pattern
- **Improvement path:** Move to single script in `extend-head.html` or footer; use `adsbygoogle.pauseAdRequests=1` / `adsbygoogle.resumeAdRequests()` for control

### No Image Optimization Pipeline
- **Problem:** Feature images and thumbnails served at original resolution; no WebP/AVIF conversion, no responsive sizes
- **Files:** `content/posts/*/feature*.jpg`, `static/img/`
- **Cause:** Hugo image processing not configured; theme handles but no custom config
- **Improvement path:** Configure `markup.toml` image processing; use `resources.GetMatch` with `Resize`/`Fill`; add Cloudflare Polish/Image Resizing

### 251 Backup Files in Content Directory
- **Problem:** ~251 `.bak*` files increase build time (Hugo processes all files in `content/`)
- **Files:** `content/posts/*.bak*`
- **Improvement path:** Delete backups; add `*.bak*` to `.gitignore`

## Fragile Areas

### Ad Injection Logic in `single.html`
- **Files:** `layouts/_default/single.html` lines 42-78
- **Why fragile:** String manipulation on rendered HTML; depends on exact `<h2` and `</p>` output; breaks if theme changes heading rendering, adds anchor links, or modifies paragraph wrapping
- **Safe modification:** Test with various content structures (no H2s, many H2s, short content, long content); add `{{ warnf }}` for unexpected split results
- **Test coverage:** None — zero tests in repo

### External Theme Dependency
- **Files:** `hugo.toml` line 1 (`themesDir = "/Users/twinssn/Projects/shared-themes"`), `config/_default/hugo.toml` line 44
- **Why fragile:** Theme updates outside this repo; breaking changes in partials, CSS classes, or template structure affect all blogs simultaneously; no version pinning
- **Safe modification:** Audit theme diffs before upgrading; document override baselines; consider vendoring theme
- **Test coverage:** None

### Cross-Blog Links Depend on External Pipeline
- **Files:** `layouts/partials/cuap-spider-links.html`, post frontmatter `cuap_cross_links`, `cuap_funnel`
- **Why fragile:** Links injected at publish time by external pipeline (not in this repo); if pipeline fails or data malformed, fallback to `related.html` may show irrelevant posts
- **Safe modification:** Validate frontmatter structure at build time; add schema validation
- **Test coverage:** None

### Content Splitting Depends on Hugo Output Format
- **Files:** `layouts/_default/single.html` lines 50-78
- **Why fragile:** Goldmark/HTML renderer version changes, render hooks, or theme partials can alter tag structure (`<h2 id="...">` vs `<h2>`, `<p>` wrapping differences)
- **Safe modification:** Pin Hugo version in CI; test build after Hugo upgrades
- **Test coverage:** None

## Scaling Limits

### Single Workers Entry Point — No Routing/Middleware
- **Current capacity:** Serves static assets only via `env.ASSETS.fetch()`
- **Limit:** Cannot handle dynamic routes, API endpoints, auth, redirects, or edge logic
- **Scaling path:** Add Workers modules under `src/`; use `itty-router` or Hono for routing; add middleware for headers, caching, auth

### No Incremental Static Regeneration (ISR)
- **Current capacity:** Full rebuild on every content change
- **Limit:** Build time scales with post count (~60 posts now; 1000+ would be slow)
- **Scaling path:** Migrate to Cloudflare Pages with on-demand builders or use Hugo's `--renderToMemory` + Workers KV for partial rebuilds

### Content Directory Growth
- **Current capacity:** ~60 posts + 251 backup files
- **Limit:** Hugo build time increases linearly; git operations slow down
- **Scaling path:** Archive old posts to separate repo; use Hugo's `cascade` for bulk frontmatter; clean backup files

## Dependencies at Risk

### External Blowfish Theme at Shared Location
- **Package:** `/Users/twinssn/Projects/shared-themes/blowfish`
- **Risk:** Single point of failure for 36+ blogs; theme updates affect all; no version lock in this repo
- **Impact:** Breaking change in theme = all blogs break simultaneously
- **Migration plan:** Vendor theme into each repo (copy to `themes/blowfish/`) or use Git submodule with pinned commit

### AdSense Publisher ID Hardcoded
- **Package:** `config/_default/params.toml`
- **Risk:** Domain family coupling — cannot deploy to different domain without code change
- **Impact:** Deploy to `rotcha.kr` domain with `informationhot.kr` publisher ID = blank ads
- **Migration plan:** Build-time injection via env var; validate domain→publisher mapping

### Cloudflare Workers Compatibility Date
- **Package:** `wrangler.toml` line 2 (`compatibility_date = "2025-07-31"`)
- **Risk:** Old compatibility date misses new Workers features, security patches
- **Impact:** Cannot use newer APIs (Workflows, Pipelines, newer KV/D1 bindings)
- **Migration plan:** Update to current date (`2026-09-21`) after testing

## Missing Critical Features

### No Automated Testing
- **What's missing:** Unit tests for template logic, integration tests for build/deploy, visual regression tests
- **Blocks:** Confidence in refactors; CI/CD pipeline adoption; safe theme upgrades
- **Files:** Entire repo — no `*_test.*`, no test config

### No CI/CD Pipeline
- **What's missing:** GitHub Actions / GitLab CI for build, test, deploy
- **Blocks:** Automated deploy on push; preview deployments; rollback capability
- **Files:** No `.github/workflows/`, no CI config

### No Link Checking
- **What's missing:** Broken link detection (internal + external)
- **Blocks:** SEO health; user experience; ad quality (landing page errors)
- **Files:** None

### No Markdown Linting
- **What's missing:** `markdownlint` or similar for frontmatter consistency, heading hierarchy, link format
- **Blocks:** Content quality at scale; automated frontmatter validation
- **Files:** None

### No Image Optimization
- **What's missing:** Automatic WebP/AVIF conversion, responsive sizes, lazy-loading config
- **Blocks:** Core Web Vitals (LCP, CLS); bandwidth costs; mobile UX
- **Files:** None

### No Security Headers (CSP, HSTS, X-Frame-Options, etc.)
- **What's missing:** Security headers in Workers response
- **Blocks:** XSS protection; clickjacking prevention; MIME sniffing prevention
- **Files:** `src/index.js`

### No Automated Sitemap/Robots Management
- **What's missing:** Dynamic `robots.txt`, sitemap pinging to search engines
- **Blocks:** Faster indexing; crawl budget optimization
- **Files:** Static `static/robots.txt` only

## Test Coverage Gaps

### Zero Tests in Repository
- **What's not tested:** All template logic (ad injection, cross-blog links, render hooks), build process, deploy process, Workers routing
- **Files:** Entire repo
- **Risk:** Any change can break production silently
- **Priority:** High — add at minimum: Hugo build test in CI, template syntax validation, ad injection logic test with sample content

### No Unit Tests for Ad Injection Logic
- **What's not tested:** The complex string-splitting logic in `single.html` lines 42-78
- **Files:** `layouts/_default/single.html`
- **Risk:** Edge cases (no H2s, 1 H2, 3 H2s, short content, malformed HTML) untested
- **Priority:** High — this is the most complex and revenue-critical logic

### No Integration Tests for Cross-Blog Navigation
- **What's not tested:** `cuap-spider-links.html` fallback chain, frontmatter param handling
- **Files:** `layouts/partials/cuap-spider-links.html`, `layouts/partials/related.html`
- **Risk:** Broken cross-blog links; fallback shows irrelevant posts
- **Priority:** Medium

### No Visual Regression Tests
- **What's not tested:** Ad rendering, mobile layout, dark mode, funnel/cross-sell cards
- **Files:** `assets/css/custom.css`, `assets/css/extended/funnel-card.css`, ad partials
- **Risk:** CSS regressions on theme upgrade; ad layout shifts (CLS)
- **Priority:** Medium

---

*Concerns audit: 2026-09-21*