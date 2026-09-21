# Testing Patterns

**Analysis Date:** 2026-09-21

## Test Framework

**Runner:**
- Not detected in this repository
- No `jest.config.*`, `vitest.config.*`, `playwright.config.*`, or similar test configuration files
- No `package.json` in project root (theme has one at `/Users/twinssn/Projects/shared-themes/blowfish/package.json` but it's for Tailwind/build tooling only)

**Assertion Library:**
- None

**Run Commands:**
```bash
# No test commands available
# Hugo build serves as de facto validation:
HUGO_THEMESDIR=/Users/twinssn/Projects/shared-themes hugo --gc --minify

# Deploy validation:
env -u CLOUDFLARE_API_TOKEN wrangler deploy --config wrangler.toml --dry-run
```

## Test File Organization

**Location:**
- No test files detected anywhere in repository
- No `tests/`, `__tests__/`, `spec/`, or `*.test.*` / `*.spec.*` files

**Naming:**
- Not applicable

**Structure:**
- Not applicable

## Test Structure

**Suite Organization:**
- Not applicable

**Patterns:**
- No setup/teardown/assertion patterns exist

## Mocking

**Framework:**
- None

**Patterns:**
- Not applicable

**What to Mock:**
- Not applicable

**What NOT to Mock:**
- Not applicable

## Fixtures and Factories

**Test Data:**
- Not applicable

**Location:**
- Not applicable

## Coverage

**Requirements:**
- None enforced
- No coverage tooling configured

**View Coverage:**
```bash
# Not available
```

## Test Types

**Unit Tests:**
- Not implemented
- Would apply to: Hugo template logic (ad injection, cross-link rendering), Workers fetch handler

**Integration Tests:**
- Not implemented
- Would apply to: Full Hugo build → Workers deploy → live site verification

**E2E Tests:**
- Not implemented
- No Playwright, Cypress, or similar configured
- Manual verification via browser after deploy

## Common Patterns

**Async Testing:**
- Not applicable

**Error Testing:**
- Not applicable

## Validation Approaches (Current Practice)

Since no formal testing framework exists, the project relies on these validation methods:

### 1. Hugo Build Validation (Primary)
```bash
HUGO_THEMESDIR=/Users/twinssn/Projects/shared-themes hugo --gc --minify
```
- Catches: Template syntax errors, missing partials, frontmatter parsing errors, markdown rendering issues
- Runs: Locally before deploy, manually

### 2. Wrangler Dry-Run Deploy
```bash
env -u CLOUDFLARE_API_TOKEN wrangler deploy --config wrangler.toml --dry-run
```
- Catches: Workers config errors, asset binding issues, size limits
- Runs: Before actual deploy

### 3. Live Site Verification (Post-Deploy)
- Manual browser check of:
  - Homepage loads
  - Sample post renders correctly
  - AdSense slots render (not blank)
  - Cross-blog links appear (if `cuap_cross_links` present)
  - Mobile layout (ad overflow, sticky ad)
  - Dark mode toggle
  - GA4/tracking scripts present

### 4. Content Quality Checks (External Pipeline)
- `mc-content-quality` skill provides audit scripts for:
  - Prompt leak detection
  - Unresolved markers
  - CTA block validation
  - Feature image URL validation
  - Image existence
  - HTML tag residue
  - Hugo build success
- Run via external pipeline, not in this repo

### 5. AdSense Governance Validation
- `adsense-publisher-governance` skill validates:
  - Publisher ID matches domain family (`ca-pub-6677996696534146` for `*.informationhot.kr`)
  - `adsbygoogle.js` client matches all `data-ad-client` slots
  - `ads.txt` authorizes correct publisher ID
- Run manually or via pipeline

## Recommended Test Additions (If Testing Were Added)

### Unit Test Candidates
1. **Ad injection logic** (`single.html` lines 42-78)
   - Input: Various HTML content structures (with/without H2s, varying word counts, different sections)
   - Output: Correct ad placement positions
   - Tool: Custom Hugo template test harness or JS port of splitting logic

2. **Cross-blog link fallback** (`cuap-spider-links.html`)
   - Input: Page with/without `cuap_cross_links`, `cuap_funnel`
   - Output: Correct partial rendered

3. **Render-link hook** (`render-link.html`)
   - Input: Links with text "최저가 확인하기"
   - Output: Button with `rel="nofollow sponsored"`, correct classes

4. **Workers fetch handler** (`src/index.js`)
   - Input: Various request paths
   - Output: Correct asset response or 404

### Integration Test Candidates
1. **Full build → deploy → smoke test**
   - Build site, deploy to preview, verify key pages return 200

2. **AdSense slot rendering**
   - Deployed page contains correct `data-ad-client` and `data-ad-slot` values

3. **Mobile CSS**
   - Viewport < 768px: ad containers constrained, unfilled ads hidden

### E2E Test Candidates
1. **User journey**: Homepage → post → ad click tracking → cross-blog navigation
2. **Dark mode**: Toggle persists, all custom components adapt

## Gaps and Risks

| Area | Risk | Mitigation |
|------|------|------------|
| Ad injection logic | Fragile string splitting on HTML tags | Manual review of output; consider shortcode-based markers |
| AdSense ID governance | Wrong publisher ID → blank ads (revenue loss) | `adsense-publisher-governance` skill audit before deploy |
| Theme upgrades | Overridden partials break silently | Document each override with theme version baseline |
| Mobile ad overflow | Ads break layout on mobile | CSS guards in `extend-head.html` + custom.css |
| No automated validation | Regressions caught only manually | Add Hugo build to CI; add preview deploy checks |

## Running Validations Locally

```bash
# 1. Full build (validates templates, content, config)
HUGO_THEMESDIR=/Users/twinssn/Projects/shared-themes hugo --gc --minify

# 2. Check for common issues in generated HTML
# - Verify ad slots present
grep -r "data-ad-client" public/
# - Verify GA4
grep -r "gtag" public/
# - Verify no template errors in output
grep -r "ERROR\|WARN" public/ 2>/dev/null || echo "No errors in output"

# 3. Deploy dry-run
env -u CLOUDFLARE_API_TOKEN wrangler deploy --config wrangler.toml --dry-run

# 4. AdSense governance check (if skill available)
# adsense-publisher-governance validate --domain health.informationhot.kr
```

---

*Testing analysis: 2026-09-21*