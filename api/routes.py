"""
API Routes — All REST endpoints for the Digital Marketing Automation System
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import sys
import os
import json
import asyncio
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────

class ContentRequest(BaseModel):
    content_type: str = Field(default="blog_post", description="blog_post | social_media | email | ad_copy | seo_meta | landing_page")
    topic: str = Field(..., description="Main topic or subject")
    keywords: List[str] = Field(default=[], description="Target SEO keywords")
    tone: str = Field(default="professional", description="Content tone")
    word_count: int = Field(default=1500, description="Target word count (for blog posts)")
    platform: str = Field(default="", description="Target platform for social/ads")
    instructions: str = Field(default="", description="Additional instructions")


class SEORequest(BaseModel):
    url: str = Field(default="", description="URL to audit")
    content: str = Field(default="", description="Content to analyze")
    target_keyword: str = Field(default="", description="Primary keyword")
    secondary_keywords: List[str] = Field(default=[], description="Secondary keywords")
    action: str = Field(default="audit", description="audit | optimize | keywords | meta_tags | content_brief")


class SocialMediaRequest(BaseModel):
    action: str = Field(default="generate", description="generate | calendar | repurpose | campaign | hashtags")
    content: str = Field(default="", description="Source content to repurpose or topic")
    platforms: List[str] = Field(default=["twitter", "linkedin", "instagram", "facebook"])
    num_variations: int = Field(default=3, description="Number of variations per platform")
    content_type: str = Field(default="educational", description="promotional | educational | entertaining | storytelling")
    weeks: int = Field(default=4, description="Calendar duration in weeks")
    campaign_name: str = Field(default="", description="Campaign name (for campaign action)")
    objective: str = Field(default="", description="Campaign objective")


class EmailRequest(BaseModel):
    action: str = Field(default="campaign", description="campaign | sequence | newsletter | subject_lines")
    campaign_type: str = Field(default="welcome", description="welcome | nurture | sales | re_engagement | abandoned_cart")
    subject_topic: str = Field(default="", description="Email topic or offer")
    audience_segment: str = Field(default="all_subscribers", description="Target audience segment")
    num_emails: int = Field(default=5, description="Number of emails in sequence")


class AdRequest(BaseModel):
    platform: str = Field(default="google", description="google | facebook | linkedin | twitter")
    product: str = Field(default="", description="Product or service name")
    objective: str = Field(default="conversions", description="Campaign objective")
    audience: str = Field(default="", description="Target audience description")
    num_variants: int = Field(default=5, description="Number of ad copy variations")
    budget: float = Field(default=1000.0, description="Campaign budget")


class WorkflowRequest(BaseModel):
    workflow_type: str = Field(default="daily", description="daily | weekly | monthly")


class AnalyticsRequest(BaseModel):
    channel: str = Field(default="all", description="all | seo | social | email | ads")
    period: str = Field(default="7d", description="1d | 7d | 30d | 90d")
    metrics: List[str] = Field(default=[], description="Specific metrics to retrieve")


class APIResponse(BaseModel):
    status: str = "success"
    message: str = ""
    data: Any = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ─────────────────────────────────────────────
# HELPER — INITIALIZE MODULES
# ─────────────────────────────────────────────

def _get_claude_client():
    """Initialize Claude client with error handling."""
    try:
        from core.claude_client import ClaudeMarketingAI
        return ClaudeMarketingAI()
    except Exception as e:
        logger.warning(f"Claude client init failed (running in mock mode): {e}")
        return None


def _get_mock_response(content_type: str, topic: str) -> dict:
    """Generate mock response when Claude API is not configured."""
    return {
        "status": "success",
        "mode": "mock",
        "message": "Running in MOCK MODE — Set CLAUDE_API_KEY in .env to enable AI generation",
        "content_type": content_type,
        "topic": topic,
        "sample_output": {
            "title": f"AI-Generated: {topic}",
            "content": f"This is a mock {content_type} about '{topic}'. Configure your Claude API key to get real AI-generated content.",
            "meta_description": f"Discover insights about {topic} in this comprehensive guide.",
            "tags": ["marketing", "automation", topic.lower().replace(" ", "-")],
        }
    }


# ─────────────────────────────────────────────
# HEALTH & STATUS
# ─────────────────────────────────────────────

@router.get("/health", response_model=APIResponse)
async def health_check():
    """System health check — shows status of all services."""
    claude_status = "connected" if os.getenv("CLAUDE_API_KEY") else "not_configured"
    azure_status = "connected" if os.getenv("AZURE_COSMOS_ENDPOINT") else "not_configured"

    return APIResponse(
        status="success",
        message="Digital Marketing Automation API is running",
        data={
            "version": "1.0.0",
            "services": {
                "api": "online",
                "claude_ai": claude_status,
                "azure_cosmos": azure_status,
                "azure_storage": "connected" if os.getenv("AZURE_STORAGE_CONNECTION") else "not_configured",
            },
            "available_endpoints": {
                "content": "/api/v1/content/generate",
                "seo": "/api/v1/seo/analyze",
                "social": "/api/v1/social/create",
                "email": "/api/v1/email/campaign",
                "ads": "/api/v1/ads/generate",
                "workflows": "/api/v1/workflows/run",
                "analytics": "/api/v1/analytics/dashboard",
            },
            "docs": "/docs",
        }
    )


# ─────────────────────────────────────────────
# CONTENT GENERATION ENDPOINTS
# ─────────────────────────────────────────────

@router.post("/content/generate", response_model=APIResponse)
async def generate_content(request: ContentRequest):
    """
    🖊️ Generate marketing content using Claude AI.

    Supported types:
    - `blog_post` — Full SEO-optimized blog article
    - `social_media` — Platform-specific social posts
    - `email` — Email campaign copy
    - `ad_copy` — Ad copy for Google/Meta/LinkedIn
    - `seo_meta` — Meta titles and descriptions
    - `landing_page` — Landing page copy
    """
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(
                status="success",
                message="Mock mode — Claude API key not set",
                data=_get_mock_response(request.content_type, request.topic)
            )

        if request.content_type == "blog_post":
            result = client.generate_blog_post(
                topic=request.topic,
                keywords=request.keywords or [request.topic],
                word_count=request.word_count,
                tone=request.tone,
            )
        elif request.content_type == "social_media":
            platforms = [request.platform] if request.platform else ["twitter", "linkedin", "instagram"]
            result = client.generate_social_posts(
                topic=request.topic,
                platforms=platforms,
                campaign_goal="engagement",
                num_variants=3,
            )
        elif request.content_type == "email":
            result = client.generate_email_campaign(
                campaign_type="promotional",
                subject_topic=request.topic,
                audience_segment="general",
                num_emails=3,
            )
        elif request.content_type == "ad_copy":
            platform = request.platform or "google"
            result = client.generate_ad_copy(
                platform=platform,
                product=request.topic,
                objective="conversions",
                audience=request.instructions or "business professionals",
            )
        elif request.content_type == "landing_page":
            from modules.content_engine import ContentEngine
            engine = ContentEngine(ai_client=client)
            result = engine.generate_landing_page(
                product_name=request.topic,
                product_description=request.instructions or request.topic,
            )
        else:
            result = client.generate_blog_post(
                topic=request.topic,
                keywords=request.keywords or [request.topic],
            )

        return APIResponse(
            status="success",
            message=f"Generated {request.content_type} content for: {request.topic}",
            data=result
        )

    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/repurpose", response_model=APIResponse)
async def repurpose_content(
    content: str = Body(..., description="Original content to repurpose"),
    source_format: str = Body(default="blog_post", description="Original content format"),
):
    """♻️ Repurpose content into multiple formats (blog → social, email, video script, etc.)."""
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("repurpose", "content"))

        from modules.content_engine import ContentEngine
        engine = ContentEngine(ai_client=client)
        result = engine.repurpose_content(content, source_format)

        return APIResponse(status="success", message="Content repurposed successfully", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/ideas", response_model=APIResponse)
async def generate_content_ideas(
    niche: str = Body(..., description="Content niche/industry"),
    count: int = Body(default=10, description="Number of ideas"),
):
    """💡 Generate blog post ideas and content calendar suggestions."""
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("ideas", niche))

        from modules.content_engine import ContentEngine
        engine = ContentEngine(ai_client=client)
        result = engine.generate_blog_ideas(niche, count)

        return APIResponse(status="success", message=f"Generated {count} content ideas", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# SEO ENDPOINTS
# ─────────────────────────────────────────────

@router.post("/seo/analyze", response_model=APIResponse)
async def seo_analyze(request: SEORequest):
    """
    🔍 SEO analysis and optimization.

    Actions:
    - `audit` — Full SEO audit of a URL
    - `optimize` — Optimize content for a target keyword
    - `keywords` — Keyword research for a topic
    - `meta_tags` — Generate optimized meta tags
    - `content_brief` — Generate SEO content brief
    """
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("seo", request.target_keyword or request.url))

        from modules.seo_optimizer import SEOOptimizer
        seo = SEOOptimizer(claude_client=client)

        if request.action == "audit":
            result = await seo.audit_page_seo(
                url=request.url,
                page_content=request.content,
            )
            result = result.__dict__ if hasattr(result, '__dict__') else result
        elif request.action == "optimize":
            result = await seo.optimize_content_for_seo(
                content=request.content,
                target_keyword=request.target_keyword,
                secondary_keywords=request.secondary_keywords,
            )
        elif request.action == "keywords":
            result = await seo.research_keywords(
                topic=request.target_keyword or request.content[:100],
                count=20,
            )
        elif request.action == "meta_tags":
            result = await seo.generate_meta_tags(
                page_content=request.content,
                target_keyword=request.target_keyword,
            )
        elif request.action == "content_brief":
            result = await seo.generate_content_brief(
                keyword=request.target_keyword,
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown SEO action: {request.action}")

        return APIResponse(
            status="success",
            message=f"SEO {request.action} completed",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SEO analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# SOCIAL MEDIA ENDPOINTS
# ─────────────────────────────────────────────

@router.post("/social/create", response_model=APIResponse)
async def social_media_create(request: SocialMediaRequest):
    """
    📱 Social media content creation and management.

    Actions:
    - `generate` — Generate posts from a topic/content
    - `calendar` — Create a multi-week content calendar
    - `repurpose` — Repurpose blog content into social posts
    - `campaign` — Design a full social media campaign
    - `hashtags` — Generate hashtag strategy
    """
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("social", request.content))

        from modules.social_media_manager import SocialMediaManager
        social = SocialMediaManager(claude_client=client)

        if request.action == "generate":
            result = await social.generate_posts_from_content(
                source_content=request.content,
                platforms=request.platforms,
                num_variations=request.num_variations,
                content_type=request.content_type,
            )
            # Convert SocialPost dataclasses to dicts for JSON serialization
            result = {k: [p.__dict__ if hasattr(p, '__dict__') else p for p in v] for k, v in result.items()}
        elif request.action == "calendar":
            result = await social.generate_content_calendar(
                weeks=request.weeks,
                posts_per_week=5,
            )
        elif request.action == "repurpose":
            result = await social.repurpose_blog_to_social(
                blog_title=request.content[:100],
                blog_content=request.content,
            )
        elif request.action == "campaign":
            result = await social.create_campaign(
                campaign_name=request.campaign_name or "AI Campaign",
                objective=request.objective or "brand awareness",
                platforms=request.platforms,
            )
        elif request.action == "hashtags":
            platform = request.platforms[0] if request.platforms else "instagram"
            result = await social.generate_hashtag_strategy(
                topic=request.content,
                platform=platform,
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown social action: {request.action}")

        return APIResponse(
            status="success",
            message=f"Social media {request.action} completed",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Social media action failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# EMAIL MARKETING ENDPOINTS
# ─────────────────────────────────────────────

@router.post("/email/campaign", response_model=APIResponse)
async def email_campaign(request: EmailRequest):
    """
    📧 Email marketing automation.

    Actions:
    - `campaign` — Generate a full email campaign sequence
    - `sequence` — Create an automation sequence
    - `newsletter` — Generate newsletter content
    - `subject_lines` — Generate A/B test subject lines
    """
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("email", request.subject_topic))

        if request.action == "campaign":
            result = client.generate_email_campaign(
                campaign_type=request.campaign_type,
                subject_topic=request.subject_topic,
                audience_segment=request.audience_segment,
                num_emails=request.num_emails,
            )
        elif request.action == "sequence":
            from modules.content_engine import ContentEngine
            engine = ContentEngine(ai_client=client)
            result = engine.generate_email_sequence(
                sequence_type=request.campaign_type,
                num_emails=request.num_emails,
                product=request.subject_topic,
            )
        elif request.action == "subject_lines":
            prompt = f"""Generate 10 A/B test email subject lines for: {request.subject_topic}
Target audience: {request.audience_segment}
Return as JSON: {{"subject_lines": [{{"line": "subject", "angle": "benefit|curiosity|urgency|social_proof", "predicted_open_rate": "high|medium|low"}}]}}
Return ONLY valid JSON."""
            response = client._call_claude_json(prompt)
            result = response
        else:
            result = client.generate_email_campaign(
                campaign_type=request.campaign_type,
                subject_topic=request.subject_topic,
                audience_segment=request.audience_segment,
            )

        return APIResponse(
            status="success",
            message=f"Email {request.action} generated",
            data=result
        )
    except Exception as e:
        logger.error(f"Email campaign generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# AD CAMPAIGN ENDPOINTS
# ─────────────────────────────────────────────

@router.post("/ads/generate", response_model=APIResponse)
async def generate_ads(request: AdRequest):
    """
    🎯 Generate ad copy and campaign strategies.

    Supports: Google Ads, Meta (Facebook/Instagram), LinkedIn Ads, Twitter Ads
    """
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("ads", request.product))

        result = client.generate_ad_copy(
            platform=request.platform,
            product=request.product,
            objective=request.objective,
            audience=request.audience or "business professionals",
            num_variants=request.num_variants,
        )

        return APIResponse(
            status="success",
            message=f"Generated {request.num_variants} ad variations for {request.platform}",
            data=result
        )
    except Exception as e:
        logger.error(f"Ad generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ads/strategy", response_model=APIResponse)
async def ad_strategy(
    product: str = Body(...),
    budget: float = Body(default=5000.0),
    goal: str = Body(default="conversions"),
    timeline: str = Body(default="30 days"),
):
    """📊 Generate a complete ad campaign strategy with budget allocation."""
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("ad_strategy", product))

        result = client.suggest_campaign_strategy(
            goal=goal,
            budget=budget,
            timeline=timeline,
        )

        return APIResponse(status="success", message="Campaign strategy generated", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# ANALYTICS & REPORTING
# ─────────────────────────────────────────────

@router.get("/analytics/dashboard", response_model=APIResponse)
async def analytics_dashboard(
    period: str = Query(default="7d", description="Time period: 1d, 7d, 30d, 90d"),
    channel: str = Query(default="all", description="Channel filter"),
):
    """📊 Get marketing analytics dashboard data."""
    # Mock analytics data — in production, pull from GA4, social APIs, etc.
    dashboard_data = {
        "period": period,
        "channel": channel,
        "overview": {
            "total_sessions": 45230,
            "total_leads": 892,
            "total_conversions": 156,
            "total_revenue": 48750.00,
            "conversion_rate": "3.45%",
            "cost_per_lead": 12.50,
            "roas": 4.2,
        },
        "channels": {
            "organic_search": {
                "sessions": 18500,
                "leads": 420,
                "conversion_rate": "2.27%",
                "top_pages": ["/blog/marketing-automation", "/pricing", "/features"],
                "trend": "up",
                "change": "+12.5%",
            },
            "social_media": {
                "sessions": 8200,
                "leads": 185,
                "engagement_rate": "4.8%",
                "top_platform": "LinkedIn",
                "trend": "up",
                "change": "+8.3%",
            },
            "email": {
                "sessions": 6800,
                "leads": 152,
                "open_rate": "24.5%",
                "click_rate": "3.8%",
                "trend": "stable",
                "change": "+1.2%",
            },
            "paid_ads": {
                "sessions": 11730,
                "leads": 135,
                "spend": 4250.00,
                "cpc": 0.36,
                "roas": 3.8,
                "trend": "up",
                "change": "+15.0%",
            },
        },
        "top_content": [
            {"title": "10 Marketing Automation Tips", "views": 3200, "conversions": 45},
            {"title": "Email Marketing Guide 2025", "views": 2800, "conversions": 38},
            {"title": "SEO Strategy for Startups", "views": 2100, "conversions": 28},
        ],
        "alerts": [
            {"type": "positive", "message": "Organic traffic up 12.5% this week"},
            {"type": "info", "message": "Email open rates stabilized at 24.5%"},
            {"type": "warning", "message": "Ad CPC increased 8% — review targeting"},
        ],
    }

    return APIResponse(
        status="success",
        message=f"Analytics dashboard for {period}",
        data=dashboard_data
    )


@router.post("/analytics/report", response_model=APIResponse)
async def generate_report(
    period: str = Body(default="weekly", description="daily | weekly | monthly"),
    channels: List[str] = Body(default=["all"]),
):
    """📋 Generate an AI-powered marketing performance report."""
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("report", period))

        # Mock performance data — in production, pull from real sources
        mock_data = {
            "organic_search": {"sessions": 18500, "conversions": 85, "revenue": 21250},
            "social_media": {"impressions": 125000, "engagement": 6200, "clicks": 3400},
            "email": {"sent": 15000, "opened": 3675, "clicked": 570},
            "paid_ads": {"spend": 4250, "clicks": 11730, "conversions": 156},
        }

        result = client.generate_marketing_report(
            period=period,
            data=mock_data,
            channels=channels if "all" not in channels else ["organic_search", "social_media", "email", "paid_ads"],
        )

        return APIResponse(status="success", message=f"{period} report generated", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# WORKFLOW ENDPOINTS
# ─────────────────────────────────────────────

@router.post("/workflows/run", response_model=APIResponse)
async def run_workflow(request: WorkflowRequest):
    """
    🔄 Run automated marketing workflows.

    Types:
    - `daily` — Social posting, analytics collection, email triggers
    - `weekly` — Content creation, performance analysis, SEO check
    - `monthly` — Full reporting, strategy review, competitor analysis
    """
    try:
        if request.workflow_type == "daily":
            from workflows.daily_workflow import DailyWorkflow
            workflow = DailyWorkflow()
            result = await workflow.run()
        elif request.workflow_type == "weekly":
            from workflows.weekly_workflow import WeeklyWorkflow
            workflow = WeeklyWorkflow()
            result = await workflow.run()
        elif request.workflow_type == "monthly":
            from workflows.monthly_workflow import MonthlyWorkflow
            workflow = MonthlyWorkflow()
            result = await workflow.run()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown workflow: {request.workflow_type}")

        return APIResponse(
            status="success",
            message=f"{request.workflow_type} workflow completed",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/status", response_model=APIResponse)
async def workflow_status():
    """📋 Get status of all configured workflows."""
    return APIResponse(
        status="success",
        message="Workflow status",
        data={
            "workflows": {
                "daily": {
                    "schedule": "Every day at 8:00 AM",
                    "last_run": "2025-04-23T08:00:00Z",
                    "status": "idle",
                    "tasks": ["analytics_collection", "social_posting", "email_triggers", "ad_monitoring", "seo_check", "daily_report"],
                },
                "weekly": {
                    "schedule": "Every Monday at 9:00 AM",
                    "last_run": "2025-04-21T09:00:00Z",
                    "status": "idle",
                    "tasks": ["content_creation", "performance_analysis", "seo_audit", "competitor_check", "weekly_report"],
                },
                "monthly": {
                    "schedule": "1st of every month at 10:00 AM",
                    "last_run": "2025-04-01T10:00:00Z",
                    "status": "idle",
                    "tasks": ["full_reporting", "strategy_review", "budget_analysis", "content_audit", "quarterly_planning"],
                },
            }
        }
    )


# ─────────────────────────────────────────────
# STRATEGY & PLANNING
# ─────────────────────────────────────────────

@router.post("/strategy/content-calendar", response_model=APIResponse)
async def content_calendar(
    month: str = Body(default="May 2025"),
    channels: List[str] = Body(default=["blog", "twitter", "linkedin", "email"]),
    themes: List[str] = Body(default=["industry trends", "product updates", "tips & tutorials"]),
    posts_per_week: int = Body(default=5),
):
    """📅 Generate a full content calendar for a month."""
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("calendar", month))

        result = client.create_content_calendar(
            month=month,
            channels=channels,
            themes=themes,
            posts_per_week=posts_per_week,
        )

        return APIResponse(status="success", message=f"Content calendar for {month} created", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy/campaign", response_model=APIResponse)
async def campaign_strategy(
    goal: str = Body(..., description="Campaign goal"),
    budget: float = Body(default=5000.0),
    timeline: str = Body(default="30 days"),
):
    """🎯 Generate a complete marketing campaign strategy."""
    try:
        client = _get_claude_client()
        if not client:
            return APIResponse(status="success", message="Mock mode", data=_get_mock_response("strategy", goal))

        result = client.suggest_campaign_strategy(
            goal=goal,
            budget=budget,
            timeline=timeline,
        )

        return APIResponse(status="success", message="Campaign strategy generated", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
