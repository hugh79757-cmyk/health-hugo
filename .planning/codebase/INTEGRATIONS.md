# External Integrations

**Analysis Date:** 2026-09-21

## APIs & External Services

**Advertising (AdSense):**
- **Google AdSense** - Display advertising
  - Publisher ID: `ca-pub-6677996696534146` (informationhot.kr family)
  - Slots: `topSlot = "2195212287"`, `inArticleSlot = "2195212287"`
  - Implementation: `layouts/partials/adsense/top.html`, `layouts/partials/adsense/in-article.html`
  - Loader: Injected via partials using `adsbygoogle.js` push pattern
  - Ads.txt: `static/ads.txt` - `google.com, pub-6677996696534146, DIRECT, f08c47fec0942fa0`

**Analytics:**
- **Google Analytics 4 (GA4)** - Web analytics
  - Measurement IDs: `G-995DNX1KV8` (params.toml), `G-G5KS0DE6HL` (hugo.toml services.googleAnalytics)
  - Implementation: `layouts/partials/extend-head.html` (gtag.js async load)
  - Config: `config/_default/hugo.toml` `[services.googleAnalytics]`

**Social/Meta:**
- **Twitter/X Cards** - Social sharing preview
  - Implementation: `layouts/partials/extend-head.html` (`twitter:card = summary_large_image`)

## Data Storage

**Databases:**
- None (static site - no database)

**File Storage:**
- **Cloudflare R2 / Workers Assets** - Static asset hosting
  - Assets served via `env.ASSETS.fetch()` in `src/index.js`
  - Build output: `./public` directory (configured in `wrangler.toml`)

**Caching:**
- **Cloudflare CDN** - Edge caching via Workers/Pages
- **Browser caching** - Standard HTTP caching headers

## Authentication & Identity

**Auth Provider:**
- None (public content site, no authentication required)

## Monitoring & Observability

**Error Tracking:**
- None configured

**Logs:**
- **Cloudflare Workers logs** - Via wrangler tail / dashboard
- **Build logs** - Hugo build output
- **Access logs** - Cloudflare Analytics

## CI/CD & Deployment

**Hosting:**
- **Cloudflare Pages** (Workers + Assets mode)
  - Project name: `health-hugo` (from `wrangler.toml`)
  - Compatibility date: `2025-07-31`

**CI Pipeline:**
- Not detected in repository (no `.github/workflows/`, no CI config)
- Manual deployment via wrangler CLI

**Deployment Commands:**
```bash
# Build
HUGO_THEMESDIR=/Users/twinssn/Projects/shared-themes hugo --gc --minify

# Deploy (MUST unset CLOUDFLARE_API_TOKEN to use OAuth profile)
env -u CLOUDFLARE_API_TOKEN wrangler deploy --config wrangler.toml
```

## Environment Configuration

**Required env vars (for deployment):**
- Cloudflare OAuth authentication (via `wrangler login` / profile)
- **Critical**: `CLOUDFLARE_API_TOKEN` must be **unset** during deploy to use OAuth profile (`hugh79757` / `default`)

**Secrets location:**
- Cloudflare dashboard (account-level OAuth tokens)
- Local `~/.wrangler/config/default.toml` (OAuth profile config)
- **NOT in repo** - no `.env` files committed

**Local config files:**
- `.wrangler/cache/` - Cached account/pages info (gitignored)
- `wrangler.toml` - Project config (committed)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None (static site)

## Cross-Blog Integration (CUAP Pipeline)

**Entity Linking:**
- **cuap-spider-links** partial (`layouts/partials/cuap-spider-links.html`)
- Cross-blog navigation via frontmatter:
  - `cuap_cross_links` - Related posts across blogs
  - `cuap_funnel` - Funnel header links (landing → course)
- Injected at publish time via pipeline (not in this repo)

**AdSense Governance:**
- Domain family: `*.informationhot.kr` → Publisher ID `ca-pub-6677996696534146`
- Enforced via `adsense-publisher-governance` skill
- Mismatch causes blank ads (AdSense rejects slots for wrong domain)

---

*Integration audit: 2026-09-21*