# CLAUDE.md — Project Documentation for AI Assistants

## Project Overview
**Digital Marketing Automation System** — A complete AI-powered marketing platform that automates content creation, SEO optimization, social media management, email campaigns, ad copy generation, analytics, and reporting.

**Tech Stack:** Python 3.11+ | FastAPI | Claude API (Anthropic) | Azure Cloud Services | Redis

---

## Architecture

```
main.py (entry point)
│
├── api/
│   ├── main.py          → FastAPI app + landing page dashboard
│   └── routes.py        → All REST endpoints
│
├── core/
│   ├── claude_client.py → ClaudeMarketingAI — central AI engine
│   └── azure_services.py→ Cosmos DB, Blob Storage, Email services
│
├── modules/
│   ├── content_engine.py       → Blog posts, landing pages, ad copy, email copy
│   ├── seo_optimizer.py        → Keyword research, SEO audits, meta tags
│   ├── social_media_manager.py → Multi-platform post generation & calendars
│   ├── email_automation.py     → Email sequences, campaigns, A/B testing
│   ├── ad_campaign_manager.py  → Google/Meta/LinkedIn ad management
│   ├── analytics_engine.py     → Performance data collection & analysis
│   └── reporting.py            → Automated report generation
│
├── workflows/
│   ├── daily_workflow.py   → Runs at 8:00 AM — social posts, analytics, emails
│   ├── weekly_workflow.py  → Runs Mondays 9:00 AM — content, SEO, performance
│   └── monthly_workflow.py → Runs 1st of month — full reports, strategy review
│
└── config/
    └── settings.py         → Pydantic configuration from environment variables
```

---

## Key Design Patterns

1. **AI-First Architecture**: Every module uses `ClaudeMarketingAI` as its brain. All content generation, analysis, and decision-making flows through Claude API.

2. **Mock Mode**: When `CLAUDE_API_KEY` is not set, the system runs in mock mode returning sample data. This allows development and testing without API costs.

3. **Modular Design**: Each marketing function (SEO, social, email, etc.) is an independent module that can be used standalone or orchestrated via workflows.

4. **Async-Ready**: Workflow orchestration and module methods are async-compatible for concurrent execution.

5. **JSON-Structured AI Outputs**: All Claude prompts request JSON responses for reliable parsing and API delivery.

---

## API Endpoints Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page dashboard |
| GET | `/docs` | Swagger API documentation |
| GET | `/api/v1/health` | Health check + service status |
| POST | `/api/v1/content/generate` | Generate blog posts, social posts, emails, ads |
| POST | `/api/v1/content/repurpose` | Repurpose content into multiple formats |
| POST | `/api/v1/content/ideas` | Generate content ideas |
| POST | `/api/v1/seo/analyze` | SEO audit, keyword research, optimization |
| POST | `/api/v1/social/create` | Social media post generation & calendars |
| POST | `/api/v1/email/campaign` | Email campaign & sequence generation |
| POST | `/api/v1/ads/generate` | Ad copy generation |
| POST | `/api/v1/ads/strategy` | Campaign strategy with budget allocation |
| GET | `/api/v1/analytics/dashboard` | Marketing analytics dashboard |
| POST | `/api/v1/analytics/report` | AI-generated performance report |
| POST | `/api/v1/workflows/run` | Execute daily/weekly/monthly workflow |
| GET | `/api/v1/workflows/status` | Workflow schedule and status |
| POST | `/api/v1/strategy/content-calendar` | Monthly content calendar |
| POST | `/api/v1/strategy/campaign` | Full campaign strategy |

---

## Configuration

All config is loaded from environment variables via `config/settings.py` using Pydantic models:

- **ClaudeConfig**: API key, model name, max_tokens, temperature
- **AzureConfig**: Cosmos DB, Blob Storage, Key Vault, Communication Services
- **SocialMediaConfig**: Twitter, Meta, LinkedIn API credentials
- **CompanyProfile**: Name, industry, audience, brand voice, products
- **EmailConfig**: Sender address, reply-to
- **GoogleConfig**: Analytics, Ads, Search Console

---

## Running the Project

```bash
# API server (default)
python main.py

# With specific port
python main.py --port 3000

# Debug mode
python main.py --debug

# Run a single workflow
python main.py --mode daily
python main.py --mode weekly
python main.py --mode monthly

# Background scheduler (cron-like)
python main.py --mode scheduler

# Docker
docker-compose up -d
```

---

## Adding a New Module

1. Create `modules/your_module.py` with a class that accepts `claude_client` in `__init__`
2. Add relevant endpoints in `api/routes.py`
3. Integrate into workflows in `workflows/daily_workflow.py` (or weekly/monthly)
4. Add any new config fields to `config/settings.py`

---

## Important Notes for AI Assistants

- The `ClaudeMarketingAI` class in `core/claude_client.py` is the central AI engine. All modules delegate to it.
- The `_call_claude_json()` method handles JSON parsing with fallback cleanup for markdown code blocks.
- The system prompt in `claude_client.py` includes full company context for brand-consistent outputs.
- All modules work in mock mode without external dependencies for local development.
- The FastAPI landing page at `/` has a built-in "Quick Try" form for testing content generation directly.
- Workflows are designed to run independently or be orchestrated via the scheduler.
