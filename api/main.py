"""
FastAPI Application — Digital Marketing Automation System
Main entry point for the REST API server.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from config.settings import config
from core.claude_client import ClaudeClient
from modules.content_engine import ContentEngine
from modules.seo_optimizer import SEOOptimizer
from modules.social_media_manager import SocialMediaManager
from modules.email_automation import EmailAutomation
from modules.ad_campaign_manager import AdCampaignManager
from modules.analytics_engine import AnalyticsEngine
from modules.reporting import ReportGenerator
from workflows.daily_workflow import DailyWorkflow
from workflows.weekly_workflow import WeeklyWorkflow
from workflows.monthly_workflow import MonthlyWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ===== Initialize Services =====
claude = None
try:
    if config.claude.api_key and config.claude.api_key != "sk-ant-your-api-key-here":
        claude = ClaudeClient(config.claude)
        logger.info("✅ Claude AI client initialized")
    else:
        logger.warning("⚠️ Claude API key not set — running in MOCK MODE")
except Exception as e:
    logger.warning(f"⚠️ Claude client init failed: {e} — running in MOCK MODE")

# Initialize all modules
content_engine = ContentEngine(claude_client=claude, config=config)
seo_optimizer = SEOOptimizer(claude_client=claude, config=config)
social_manager = SocialMediaManager(claude_client=claude, config=config)
email_automation = EmailAutomation(claude_client=claude, config=config)
ad_manager = AdCampaignManager(claude_client=claude, config=config)
analytics_engine = AnalyticsEngine(claude_client=claude, config=config)
report_generator = ReportGenerator(
    claude_client=claude, analytics_engine=analytics_engine, config=config
)

# Initialize workflows
daily_workflow = DailyWorkflow(
    claude_client=claude,
    content_engine=content_engine,
    social_manager=social_manager,
    email_automation=email_automation,
    ad_manager=ad_manager,
    analytics_engine=analytics_engine,
    report_generator=report_generator,
    config=config,
)

weekly_workflow = WeeklyWorkflow(
    claude_client=claude,
    content_engine=content_engine,
    social_manager=social_manager,
    email_automation=email_automation,
    ad_manager=ad_manager,
    analytics_engine=analytics_engine,
    report_generator=report_generator,
    seo_optimizer=seo_optimizer,
    config=config,
)

monthly_workflow = MonthlyWorkflow(
    claude_client=claude,
    content_engine=content_engine,
    social_manager=social_manager,
    email_automation=email_automation,
    ad_manager=ad_manager,
    analytics_engine=analytics_engine,
    report_generator=report_generator,
    seo_optimizer=seo_optimizer,
    config=config,
)


# ===== FastAPI App =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Digital Marketing Automation API starting up...")
    logger.info(f"   Company: {config.company.name}")
    logger.info(f"   Industry: {config.company.industry}")
    logger.info(f"   Mock Mode: {claude is None}")
    yield
    logger.info("👋 Digital Marketing Automation API shutting down...")


app = FastAPI(
    title="Digital Marketing Automation API",
    description="Complete marketing automation system powered by Claude AI + Azure",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== HEALTH & INFO =====
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint — shows system dashboard"""
    mode = "🟢 LIVE (Claude AI Connected)" if claude else "🟡 MOCK MODE (No API Key)"
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Digital Marketing Automation</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ font-size: 36px; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }}
        .subtitle {{ color: #94a3b8; font-size: 16px; margin-bottom: 32px; }}
        .mode {{ padding: 12px 20px; border-radius: 8px; margin-bottom: 32px; font-weight: 600;
            background: {'#065f46' if claude else '#78350f'}; border: 1px solid {'#10b981' if claude else '#f59e0b'}; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; transition: all 0.2s; }}
        .card:hover {{ border-color: #667eea; transform: translateY(-2px); }}
        .card h3 {{ color: #667eea; margin-bottom: 8px; font-size: 18px; }}
        .card p {{ color: #94a3b8; font-size: 14px; margin-bottom: 16px; line-height: 1.5; }}
        .endpoints {{ font-family: monospace; font-size: 13px; }}
        .endpoints a {{ color: #a78bfa; text-decoration: none; display: block; padding: 4px 0; }}
        .endpoints a:hover {{ color: #c4b5fd; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-right: 4px; }}
        .get {{ background: #064e3b; color: #6ee7b7; }}
        .post {{ background: #1e3a5f; color: #7dd3fc; }}
        footer {{ text-align: center; margin-top: 48px; color: #475569; font-size: 13px; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 Digital Marketing Automation</h1>
    <p class="subtitle">Powered by Claude AI + Azure — Complete Marketing on Autopilot</p>
    <div class="mode">{mode}</div>

    <div class="grid">
        <div class="card">
            <h3>📝 Content Engine</h3>
            <p>AI-powered blog posts, social content, ad copy, and more</p>
            <div class="endpoints">
                <a href="/docs#/Content"><span class="badge post">POST</span> /api/content/blog</a>
                <a href="/docs#/Content"><span class="badge post">POST</span> /api/content/social</a>
                <a href="/docs#/Content"><span class="badge post">POST</span> /api/content/email</a>
                <a href="/docs#/Content"><span class="badge post">POST</span> /api/content/ad-copy</a>
            </div>
        </div>

        <div class="card">
            <h3>🔍 SEO Optimizer</h3>
            <p>Keyword research, site audits, and optimization recommendations</p>
            <div class="endpoints">
                <a href="/docs#/SEO"><span class="badge post">POST</span> /api/seo/keywords</a>
                <a href="/docs#/SEO"><span class="badge post">POST</span> /api/seo/audit</a>
                <a href="/docs#/SEO"><span class="badge post">POST</span> /api/seo/optimize</a>
            </div>
        </div>

        <div class="card">
            <h3>📱 Social Media</h3>
            <p>Multi-platform post generation, scheduling, and analytics</p>
            <div class="endpoints">
                <a href="/docs#/Social"><span class="badge post">POST</span> /api/social/generate</a>
                <a href="/docs#/Social"><span class="badge get">GET</span> /api/social/calendar</a>
            </div>
        </div>

        <div class="card">
            <h3>📧 Email Marketing</h3>
            <p>Campaign creation, sequences, and performance tracking</p>
            <div class="endpoints">
                <a href="/docs#/Email"><span class="badge post">POST</span> /api/email/campaign</a>
                <a href="/docs#/Email"><span class="badge post">POST</span> /api/email/sequence</a>
            </div>
        </div>

        <div class="card">
            <h3>💰 Ad Campaigns</h3>
            <p>Ad copy generation, budget optimization, and performance</p>
            <div class="endpoints">
                <a href="/docs#/Ads"><span class="badge post">POST</span> /api/ads/generate</a>
                <a href="/docs#/Ads"><span class="badge get">GET</span> /api/ads/performance</a>
            </div>
        </div>

        <div class="card">
            <h3>📊 Analytics & Reports</h3>
            <p>AI-powered analytics, insights, and automated reporting</p>
            <div class="endpoints">
                <a href="/docs#/Analytics"><span class="badge get">GET</span> /api/analytics/dashboard</a>
                <a href="/docs#/Analytics"><span class="badge get">GET</span> /api/analytics/performance</a>
                <a href="/api/reports/daily"><span class="badge get">GET</span> /api/reports/daily</a>
                <a href="/api/reports/weekly"><span class="badge get">GET</span> /api/reports/weekly</a>
            </div>
        </div>

        <div class="card">
            <h3>⚡ Workflows</h3>
            <p>Run automated daily, weekly, and monthly marketing workflows</p>
            <div class="endpoints">
                <a href="/docs#/Workflows"><span class="badge post">POST</span> /api/workflows/daily</a>
                <a href="/docs#/Workflows"><span class="badge post">POST</span> /api/workflows/weekly</a>
                <a href="/docs#/Workflows"><span class="badge post">POST</span> /api/workflows/monthly</a>
            </div>
        </div>

        <div class="card">
            <h3>📚 API Documentation</h3>
            <p>Interactive Swagger UI with all endpoints</p>
            <div class="endpoints">
                <a href="/docs"><span class="badge get">GET</span> /docs — Swagger UI</a>
                <a href="/redoc"><span class="badge get">GET</span> /redoc — ReDoc</a>
                <a href="/openapi.json"><span class="badge get">GET</span> /openapi.json</a>
            </div>
        </div>
    </div>

    <footer>
        <p>Digital Marketing Automation System v1.0.0 | {config.company.name} | {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </footer>
</div>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "live" if claude else "mock",
        "company": config.company.name,
        "version": "1.0.0",
    }


# ===== CONTENT ENDPOINTS =====
@app.post("/api/content/blog", tags=["Content"])
async def generate_blog_post(topic: str, keywords: str = "", tone: str = "professional"):
    """Generate a complete SEO-optimized blog post"""
    try:
        result = await content_engine.generate_blog_post(
            topic=topic,
            keywords=keywords.split(",") if keywords else [],
            tone=tone,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/content/social", tags=["Content"])
async def generate_social_post(
    topic: str, platform: str = "linkedin", post_type: str = "educational"
):
    """Generate a social media post for a specific platform"""
    try:
        result = await content_engine.generate_social_post(
            topic=topic, platform=platform, post_type=post_type
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/content/email", tags=["Content"])
async def generate_email(
    subject_topic: str, email_type: str = "newsletter", audience: str = "subscribers"
):
    """Generate email content"""
    try:
        result = await content_engine.generate_email_content(
            topic=subject_topic, email_type=email_type, audience=audience
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/content/ad-copy", tags=["Content"])
async def generate_ad_copy(
    product: str, platform: str = "google", campaign_goal: str = "conversions"
):
    """Generate ad copy for paid campaigns"""
    try:
        result = await content_engine.generate_ad_copy(
            product=product, platform=platform, goal=campaign_goal
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== SEO ENDPOINTS =====
@app.post("/api/seo/keywords", tags=["SEO"])
async def keyword_research(seed_keyword: str, count: int = 10):
    """AI-powered keyword research"""
    try:
        result = await seo_optimizer.keyword_research(seed_keyword=seed_keyword, count=count)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seo/audit", tags=["SEO"])
async def seo_audit(url: str = ""):
    """Run SEO audit on a URL"""
    try:
        target_url = url or config.company.website_url
        result = await seo_optimizer.site_audit(url=target_url)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seo/optimize", tags=["SEO"])
async def optimize_content(content: str, target_keyword: str):
    """Get SEO optimization suggestions for content"""
    try:
        result = await seo_optimizer.optimize_content(content=content, keyword=target_keyword)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== SOCIAL MEDIA ENDPOINTS =====
@app.post("/api/social/generate", tags=["Social"])
async def generate_social_content(
    topic: str, platforms: str = "linkedin,twitter,instagram"
):
    """Generate social media content for multiple platforms"""
    try:
        platform_list = [p.strip() for p in platforms.split(",")]
        results = {}
        for platform in platform_list:
            results[platform] = await content_engine.generate_social_post(
                topic=topic, platform=platform
            )
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/social/calendar", tags=["Social"])
async def get_social_calendar():
    """Get the social media content calendar"""
    try:
        calendar = await social_manager.get_content_calendar()
        return {"status": "success", "data": calendar}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== EMAIL ENDPOINTS =====
@app.post("/api/email/campaign", tags=["Email"])
async def create_email_campaign(
    name: str, subject: str, content_topic: str, audience: str = "all"
):
    """Create an email campaign"""
    try:
        result = await email_automation.create_campaign(
            name=name, subject=subject, topic=content_topic, audience=audience
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/sequence", tags=["Email"])
async def create_email_sequence(
    name: str, trigger: str = "signup", emails_count: int = 5
):
    """Create an automated email sequence"""
    try:
        result = await email_automation.create_sequence(
            name=name, trigger=trigger, count=emails_count
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ADS ENDPOINTS =====
@app.post("/api/ads/generate", tags=["Ads"])
async def generate_ad_campaign(
    product: str, platform: str = "google", budget: float = 100.0, goal: str = "conversions"
):
    """Generate a complete ad campaign"""
    try:
        result = await ad_manager.create_campaign(
            product=product, platform=platform, budget=budget, goal=goal
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ads/performance", tags=["Ads"])
async def get_ad_performance():
    """Get ad campaign performance metrics"""
    try:
        result = await ad_manager.get_performance()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ANALYTICS ENDPOINTS =====
@app.get("/api/analytics/dashboard", tags=["Analytics"])
async def get_dashboard():
    """Get marketing dashboard data"""
    try:
        data = await analytics_engine.get_dashboard_data()
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/performance", tags=["Analytics"])
async def get_performance(days: int = 7):
    """Get AI-powered performance analysis"""
    try:
        analysis = await analytics_engine.analyze_performance(days)
        return {"status": "success", "data": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/trends", tags=["Analytics"])
async def get_trends(days: int = 30):
    """Get trend analysis"""
    try:
        trends = await analytics_engine.analyze_trends(days)
        return {"status": "success", "data": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/funnel", tags=["Analytics"])
async def get_funnel():
    """Get funnel analysis"""
    try:
        funnel = await analytics_engine.funnel_analysis()
        return {"status": "success", "data": funnel}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== REPORT ENDPOINTS =====
@app.get("/api/reports/daily", tags=["Reports"])
async def get_daily_report(format: str = "json"):
    """Generate daily marketing report"""
    try:
        report = await report_generator.daily_report()
        if format == "html":
            html = report_generator.to_html(report)
            return HTMLResponse(content=html)
        elif format == "markdown":
            md = report_generator.to_markdown(report)
            return {"status": "success", "format": "markdown", "data": md}
        return {"status": "success", "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/weekly", tags=["Reports"])
async def get_weekly_report(format: str = "json"):
    """Generate weekly marketing report"""
    try:
        report = await report_generator.weekly_report()
        if format == "html":
            html = report_generator.to_html(report)
            return HTMLResponse(content=html)
        return {"status": "success", "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/monthly", tags=["Reports"])
async def get_monthly_report(format: str = "json"):
    """Generate monthly marketing report"""
    try:
        report = await report_generator.monthly_report()
        if format == "html":
            html = report_generator.to_html(report)
            return HTMLResponse(content=html)
        return {"status": "success", "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== WORKFLOW ENDPOINTS =====
@app.post("/api/workflows/daily", tags=["Workflows"])
async def run_daily_workflow():
    """Run the daily marketing automation workflow"""
    try:
        result = await daily_workflow.run()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflows/weekly", tags=["Workflows"])
async def run_weekly_workflow():
    """Run the weekly marketing automation workflow"""
    try:
        result = await weekly_workflow.run()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflows/monthly", tags=["Workflows"])
async def run_monthly_workflow():
    """Run the monthly marketing automation workflow"""
    try:
        result = await monthly_workflow.run()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== RUN SERVER =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
