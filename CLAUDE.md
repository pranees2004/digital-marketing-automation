# CLAUDE.md — Project Documentation for AI Assistants

## Project Overview

**Digital Marketing Automation System** — A complete AI-powered marketing platform that automates content creation, SEO optimization, social media management, email campaigns, ad copy generation, analytics, and reporting.

**Tech Stack:** Python 3.11+ | FastAPI | Claude API (Anthropic) | Azure Cloud Services | Redis

---

## Repository Structure

```
digital-marketing-automation/
│
├── main.py                        # CLI entry point (api / daily / weekly / monthly / scheduler)
├── requirements.txt               # All pip dependencies
├── Dockerfile                     # Docker image definition
├── docker-compose.yml             # Docker Compose (api + scheduler services)
├── .env.sample                    # Annotated sample environment file — copy to .env
├── CLAUDE.md                      # This documentation file
│
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, responsive frontend (/), v1 router + onboarding endpoints
│   └── routes.py                  # All /api/v1/* REST endpoints
│
├── core/
│   ├── __init__.py
│   ├── claude_client.py           # ClaudeMarketingAI — central AI engine (alias: ClaudeClient)
│   └── azure_services.py          # Cosmos DB, Blob Storage, Azure Email wrappers
│
├── modules/
│   ├── __init__.py                # Re-exports all module classes
│   ├── content_engine.py          # Blog posts, landing pages, ad copy, email copy
│   ├── seo_optimizer.py           # Keyword research, SEO audits, meta tags, content briefs
│   ├── social_media_manager.py    # Multi-platform post generation, calendars, campaigns
│   ├── email_automation.py        # Email sequences, drip campaigns, A/B testing
│   ├── ad_campaign_manager.py     # Google Ads, Meta Ads campaign creation & optimisation
│   ├── analytics_engine.py        # Performance data collection & AI analysis
│   └── reporting.py               # Automated report generation (daily/weekly/monthly)
│
├── workflows/
│   ├── __init__.py
│   ├── daily_workflow.py          # Runs at 8:00 AM — social posts, analytics, emails
│   ├── weekly_workflow.py         # Runs Mondays 9:00 AM — content, SEO, performance
│   └── monthly_workflow.py        # Runs 1st of month — full reports, strategy review
│
└── config/
    ├── __init__.py
    └── settings.py                # Pydantic AppConfig loaded from environment variables
```

---

## Key Design Patterns

1. **AI-First Architecture** — Every module uses `ClaudeMarketingAI` as its brain. All content generation, analysis, and decision-making flows through the Claude API.

2. **Mock Mode** — When `CLAUDE_API_KEY` is not set (or is the placeholder value), the system runs in mock mode returning sample data. This lets you develop and test locally with zero API costs.

3. **Modular Design** — Each marketing function (SEO, social, email, etc.) is an independent module class. Modules can be used standalone or orchestrated via workflows.

4. **Async-Ready** — All module methods and workflow orchestration are `async` / awaitable for concurrent execution under FastAPI's event loop.

5. **JSON-Structured AI Outputs** — All Claude prompts request structured JSON responses. The `_call_claude_json()` / `generate()` helpers handle markdown code-block stripping and parse errors.

6. **Backward-Compatible Aliases** — `ClaudeClient` and `MarketingAIClient` are aliases for `ClaudeMarketingAI` for compatibility with all modules.

---

## API Endpoints Quick Reference

### Frontend (Responsive Dashboard)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/`                                       | Responsive dashboard (onboarding + social scheduling) |
| GET  | `/health`                                 | App health status |
| POST | `/api/v1/frontend/company-profile`        | Save company profile + get AI marketing strategy |
| GET  | `/api/v1/frontend/company-profile`        | Get saved company profile |
| POST | `/api/v1/frontend/social/connect`         | Connect a social platform account |
| GET  | `/api/v1/frontend/social/connections`     | List connected platforms |
| POST | `/api/v1/frontend/social/schedule`        | Schedule a social post |
| GET  | `/api/v1/frontend/social/scheduled`       | List scheduled posts |

### v1 REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/v1/health`                    | Health check + service status |
| POST | `/api/v1/content/generate`          | Generate blog posts, social posts, emails, ads |
| POST | `/api/v1/content/repurpose`         | Repurpose content into multiple formats |
| POST | `/api/v1/content/ideas`             | Generate content ideas |
| POST | `/api/v1/seo/analyze`               | SEO audit, keyword research, optimization |
| POST | `/api/v1/social/create`             | Social media post generation & calendars |
| POST | `/api/v1/email/campaign`            | Email campaign & sequence generation |
| POST | `/api/v1/ads/generate`              | Ad copy generation |
| POST | `/api/v1/ads/strategy`              | Campaign strategy with budget allocation |
| GET  | `/api/v1/analytics/dashboard`       | Marketing analytics dashboard |
| POST | `/api/v1/analytics/report`          | AI-generated performance report |
| POST | `/api/v1/workflows/run`             | Execute daily/weekly/monthly workflow |
| GET  | `/api/v1/workflows/status`          | Workflow schedule and status |
| POST | `/api/v1/strategy/content-calendar` | Monthly content calendar |
| POST | `/api/v1/strategy/campaign`         | Full campaign strategy |
| GET  | `/docs`                             | Swagger UI |
| GET  | `/redoc`                            | ReDoc documentation |

---

## Configuration (`config/settings.py`)

All settings are loaded from environment variables via Pydantic models with sensible defaults.

| Class | Env Prefix | Key Variables |
|-------|-----------|---------------|
| `ClaudeConfig` | `CLAUDE_` | `API_KEY`, `MODEL`, `MAX_TOKENS` |
| `AzureConfig` | `AZURE_` | `COSMOS_ENDPOINT/KEY/DATABASE`, `STORAGE_CONNECTION`, `KEYVAULT_URL`, `COMMUNICATION_CONNECTION` |
| `SocialMediaConfig` | `TWITTER_`, `META_`, `LINKEDIN_` | Platform API keys and tokens |
| `CompanyProfile` | `COMPANY_`, `TARGET_`, `BRAND_` | Name, industry, website, audience, brand voice, UVP |
| `EmailConfig` | `EMAIL_` | `SENDER_ADDRESS`, `REPLY_TO` |
| `GoogleConfig` | `GOOGLE_` | Analytics property, Ads customer ID, Search Console site |

Global singleton: `from config.settings import config`

---

## Running the Project

```bash
# 1. Copy and edit environment variables
cp .env.sample .env
# → edit .env with your API keys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the API server (default port 8000)
python main.py

# 4. Open your browser
# Dashboard: http://localhost:8000
# Swagger:   http://localhost:8000/docs

# Run with a custom port
python main.py --port 3000

# Enable hot-reload (development)
python main.py --debug

# Run a single workflow manually
python main.py --mode daily
python main.py --mode weekly
python main.py --mode monthly

# Start the cron-like background scheduler
python main.py --mode scheduler

# Docker (API + scheduler)
docker-compose up -d
```

---

## Module Usage Examples

```python
from config.settings import config
from core.claude_client import ClaudeMarketingAI
from modules.content_engine import ContentEngine
from modules.seo_optimizer import SEOOptimizer
from modules.social_media_manager import SocialMediaManager

client = ClaudeMarketingAI()   # mock mode if CLAUDE_API_KEY not set

# Generate a blog post
engine = ContentEngine(ai_client=client)
post = engine.generate_blog_post(
    topic="AI-powered marketing automation",
    keywords=["ai marketing", "automation", "content generation"],
)

# Keyword research
seo = SEOOptimizer(claude_client=client)
import asyncio
keywords = asyncio.run(seo.research_keywords("marketing automation", count=10))

# Generate social posts
social = SocialMediaManager(claude_client=client)
posts = asyncio.run(social.generate_posts_from_content(
    source_content="We just launched our AI marketing suite!",
    platforms=["instagram", "linkedin", "twitter"],
))
```

---

## Component Health Check

Run this to verify all components import and the API boots cleanly:

```bash
python - <<'PY'
import sys

checks = [
    'config.settings', 'core.claude_client', 'core.azure_services',
    'modules.content_engine', 'modules.seo_optimizer', 'modules.social_media_manager',
    'modules.email_automation', 'modules.ad_campaign_manager',
    'modules.analytics_engine', 'modules.reporting', 'modules',
    'workflows.daily_workflow', 'workflows.weekly_workflow', 'workflows.monthly_workflow',
    'api.routes', 'api.main',
]

results = {}
for mod in checks:
    try:
        __import__(mod)
        results[mod] = 'ok'
    except Exception as e:
        results[mod] = f'ERROR: {e}'

ok = [k for k,v in results.items() if v == 'ok']
fail = {k:v for k,v in results.items() if v != 'ok'}
print(f'\n=== {len(ok)}/{len(results)} components OK, {len(fail)} failed ===')
for k in ok:   print(f'  ✅ {k}')
for k,v in fail.items(): print(f'  ❌ {k}: {v}')
sys.exit(1 if fail else 0)
PY
```

Expected output (all 16 components):

```
=== 16/16 components OK, 0 failed ===
  ✅ config.settings
  ✅ core.claude_client
  ✅ core.azure_services
  ✅ modules.content_engine
  ✅ modules.seo_optimizer
  ✅ modules.social_media_manager
  ✅ modules.email_automation
  ✅ modules.ad_campaign_manager
  ✅ modules.analytics_engine
  ✅ modules.reporting
  ✅ modules
  ✅ workflows.daily_workflow
  ✅ workflows.weekly_workflow
  ✅ workflows.monthly_workflow
  ✅ api.routes
  ✅ api.main
```

---

## Adding a New Module

1. Create `modules/your_module.py` with a class that accepts `claude_client` in `__init__`
2. Export it from `modules/__init__.py`
3. Add relevant endpoints in `api/routes.py`
4. Integrate into workflows (`workflows/daily_workflow.py` or weekly/monthly)
5. Add any new config fields to `config/settings.py` and `.env.sample`

---

## Notes for AI Assistants

- `ClaudeMarketingAI` in `core/claude_client.py` is the central AI engine with aliases `ClaudeClient` and `MarketingAIClient`.
- `ClaudeMarketingAI.generate(prompt, ...)` is the async-compatible public method — use this instead of `_call_claude_json()` in new code.
- All modules gracefully handle `None` claude_client — they fall back to mock data.
- The responsive frontend at `/` supports company onboarding (profile + strategy) and social post scheduling (connect platforms → schedule posts).
- Workflows are designed to run independently or be orchestrated via the scheduler.
- In-memory demo storage in `api/main.py` is protected by `asyncio.Lock`; replace with a database for production.
- The `.env.sample` file contains annotated placeholders for every supported configuration variable.
