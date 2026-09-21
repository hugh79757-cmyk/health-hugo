# Technology Stack

**Analysis Date:** 2026-09-21

## Languages

**Primary:**
- **Go 1.16+** - Hugo static site generator (`/Users/twinssn/Projects/shared-themes/blowfish/go.mod`)
- **JavaScript/TypeScript** - Cloudflare Workers entry point (`src/index.js`)

**Secondary:**
- **HTML/CSS** - Hugo templates and custom styles (`layouts/`, `assets/css/`)
- **Markdown** - Content files (`content/posts/`)

## Runtime

**Environment:**
- **Hugo** (Go-based SSG) - Build-time rendering
- **Cloudflare Workers** - Runtime for edge deployment (`src/index.js` serves static assets)

**Package Manager:**
- **npm** (Node.js) - For theme dependencies
- Lockfile: `package-lock.json` present in theme (`/Users/twinssn/Projects/shared-themes/blowfish/package-lock.json`)

## Frameworks

**Core:**
- **Hugo** - Static site generator (extended version for SCSS/Tailwind)
- **Blowfish Theme v2.104.0** - Hugo theme (`/Users/twinssn/Projects/shared-themes/blowfish/theme.toml`, `package.json`)
- **Tailwind CSS v4.3.2** - Utility-first CSS framework (`/Users/twinssn/Projects/shared-themes/blowfish/tailwind.config.js`)

**Testing:**
- Not detected in this repository

**Build/Dev:**
- **Hugo** - `hugo --gc --minify` for production builds
- **@tailwindcss/cli v4.3.2** - Tailwind CSS compilation (replaces PostCSS)
- **wrangler** - Cloudflare Workers/Pages CLI for deployment
- **vendor-copy** - Copies vendor JS/CSS to theme assets

## Key Dependencies

**Critical (Theme - `/Users/twinssn/Projects/shared-themes/blowfish/package.json`):**
- `@tailwindcss/cli@^4.3.2` - Tailwind CSS v4 compiler
- `@tailwindcss/typography@^0.5.20` - Prose/typography plugin
- `tailwindcss@^4.3.2` - Core Tailwind CSS
- `chart.js@^4.5.1` - Chart rendering
- `mermaid@^11.16.0` - Diagram rendering
- `katex@^0.17.0` - Math formula rendering
- `fuse.js@~7.4.2` - Fuzzy search
- `typeit@^8.8.7` - Typing animation
- `lite-youtube-embed@^0.3.4` - Lazy YouTube embeds
- `medium-zoom@^1.1.0` - Image zoom
- `packery@^3.0.0` - Masonry layouts
- `tw-elements@2.0.0` - Tailwind UI components

**Infrastructure:**
- **Cloudflare Workers/Pages** - Hosting and edge deployment (`wrangler.toml`, `src/index.js`)
- **Cloudflare Assets binding** - Static asset serving via Workers

## Configuration

**Environment:**
- **Hugo config**: `hugo.toml` (root, minimal), `config/_default/` (modular config)
- **Theme config**: `themesDir = "/Users/twinssn/Projects/shared-themes"` in both root `hugo.toml` and `config/_default/hugo.toml`
- **Wrangler config**: `wrangler.toml` (Workers/Pages deployment)
- **Tailwind config**: `/Users/twinssn/Projects/shared-themes/blowfish/tailwind.config.js`

**Key configs:**
- `config/_default/hugo.toml` - Base URL, language, taxonomies, related content, GA4 service
- `config/_default/params.toml` - Theme params, AdSense IDs, colors, article/list settings
- `config/_default/languages.ko.toml` - Korean language specifics
- `config/_default/markup.toml` - Markup processing (Goldmark unsafe=true)

**Build:**
```bash
# Hugo build (with external themes dir)
HUGO_THEMESDIR=/Users/twinssn/Projects/shared-themes hugo --gc --minify

# Tailwind build (in theme)
npm run build  # NODE_ENV=production npx @tailwindcss/cli ...

# Deploy
env -u CLOUDFLARE_API_TOKEN wrangler deploy --config wrangler.toml
```

## Platform Requirements

**Development:**
- Go 1.16+ (for Hugo)
- Node.js 18+ (for Tailwind CLI, npm deps)
- Hugo extended (for Tailwind/SCSS)
- wrangler CLI

**Production:**
- **Deployment target**: Cloudflare Pages (Workers + Assets)
- **Worker script**: `src/index.js` - serves `env.ASSETS` (static files from `./public`)
- **wrangler.toml**: `assets.directory = "./public"`, `not_found_handling = "404-page"`, `html_handling = "auto-trailing-slash"`
- **Domain**: `health.informationhot.kr` (configured in `config/_default/hugo.toml` baseURL)

---

*Stack analysis: 2026-09-21*