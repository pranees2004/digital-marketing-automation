"""
FastAPI Application — Digital Marketing Automation System
Stable app entrypoint with responsive frontend and v1 API router integration.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator

from api.routes import router as v1_router
from config.settings import config
from core.claude_client import ClaudeMarketingAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

claude: Optional[ClaudeMarketingAI] = None
try:
    if config.claude.api_key and config.claude.api_key != "sk-ant-your-api-key-here":
        claude = ClaudeMarketingAI()
        logger.info("✅ Claude AI client initialized")
    else:
        logger.warning("⚠️ Claude API key not set — running in MOCK MODE")
except Exception as exc:
    logger.warning(f"⚠️ Claude client init failed: {exc} — running in MOCK MODE")

# Non-persistent demo storage (resets on restart); use a database in production.
company_profiles: List[Dict[str, Any]] = []
social_connections: List[Dict[str, Any]] = []
scheduled_posts: List[Dict[str, Any]] = []
store_lock = asyncio.Lock()


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
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


class CompanyOnboardingRequest(BaseModel):
    company_name: str = Field(..., min_length=2)
    website: str = Field(default="")
    description: str = Field(..., min_length=10)
    industry: str = Field(default="Technology")
    target_audience: str = Field(default="B2B professionals")


class SocialConnectionRequest(BaseModel):
    platform: Literal["instagram", "facebook", "linkedin", "twitter"]
    account_name: str = Field(..., min_length=2)


class ScheduledPostRequest(BaseModel):
    platform: Literal["instagram", "facebook", "linkedin", "twitter"]
    content: str = Field(..., min_length=10)
    scheduled_for: datetime

    @field_validator("scheduled_for")
    @classmethod
    def ensure_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("scheduled_for must include timezone information")
        return value


@app.get("/", response_class=HTMLResponse)
async def root():
    mode = "🟢 LIVE (Claude AI Connected)" if claude else "🟡 MOCK MODE (No API Key)"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Digital Marketing Automation</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: Inter, Segoe UI, Arial, sans-serif; background: #0b1220; color: #e2e8f0; }}
    .container {{ max-width: 1120px; margin: 0 auto; padding: 20px; }}
    h1 {{ font-size: clamp(1.7rem, 4vw, 2.6rem); margin-bottom: 8px; }}
    .subtitle {{ color: #94a3b8; margin-bottom: 16px; }}
    .mode {{ padding: 10px 14px; border-radius: 8px; margin-bottom: 16px; font-weight: 600;
      background: {'#065f46' if claude else '#78350f'}; border: 1px solid {'#10b981' if claude else '#f59e0b'}; }}
    .grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}
    .card {{ background: #111827; border: 1px solid #334155; border-radius: 12px; padding: 16px; }}
    .card h2 {{ font-size: 1.1rem; margin-bottom: 12px; color: #a78bfa; }}
    label {{ display: block; margin: 8px 0 6px; color: #cbd5e1; font-size: 0.9rem; }}
    input, textarea, select, button {{
      width: 100%; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #f8fafc;
      padding: 10px; font-size: 0.95rem;
    }}
    textarea {{ min-height: 110px; resize: vertical; }}
    button {{ background: #4f46e5; border: none; cursor: pointer; font-weight: 600; margin-top: 12px; }}
    button:hover {{ background: #4338ca; }}
    .row {{ display: grid; gap: 10px; grid-template-columns: 1fr 1fr; }}
    .result {{ margin-top: 12px; padding: 12px; background: #0f172a; border-radius: 8px; border: 1px solid #334155; white-space: pre-wrap; font-size: 0.9rem; }}
    .list {{ margin-top: 8px; font-size: 0.9rem; color: #cbd5e1; }}
    .list li {{ margin: 4px 0 4px 18px; }}
    @media (max-width: 640px) {{ .row {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🚀 Digital Marketing Automation</h1>
    <p class="subtitle">AI marketing setup + social integration + scheduled posting from one responsive dashboard.</p>
    <div class="mode">{mode}</div>
    <div class="grid">
      <section class="card">
        <h2>Company Onboarding</h2>
        <form id="companyForm">
          <label>Company Name</label>
          <input id="company_name" required />
          <label>Website Link</label>
          <input id="website" placeholder="https://example.com" />
          <label>Company Description</label>
          <textarea id="description" required></textarea>
          <div class="row">
            <div>
              <label>Industry</label>
              <input id="industry" value="Technology" />
            </div>
            <div>
              <label>Target Audience</label>
              <input id="target_audience" value="B2B professionals" />
            </div>
          </div>
          <button type="submit">Generate Marketing Starter Plan</button>
        </form>
        <div id="companyResult" class="result" style="display:none;"></div>
      </section>

      <section class="card">
        <h2>Connect Social Platforms</h2>
        <form id="connectForm">
          <label>Platform</label>
          <select id="platform">
            <option>instagram</option>
            <option>facebook</option>
            <option>linkedin</option>
            <option>twitter</option>
          </select>
          <label>Account Name</label>
          <input id="account_name" placeholder="@yourbrand" required />
          <button type="submit">Connect Platform</button>
        </form>
        <ul id="connections" class="list"></ul>
      </section>

      <section class="card">
        <h2>Schedule Social Post</h2>
        <form id="scheduleForm">
          <label>Platform</label>
          <select id="schedule_platform">
            <option>instagram</option>
            <option>facebook</option>
            <option>linkedin</option>
            <option>twitter</option>
          </select>
          <label>Post Content</label>
          <textarea id="post_content" required></textarea>
          <label for="scheduled_for">Scheduled Date & Time</label>
          <input id="scheduled_for" type="datetime-local" required />
          <p style="margin-top:6px;color:#94a3b8;font-size:.8rem;">Your local time is converted to UTC for scheduling.</p>
          <button type="submit">Schedule Post</button>
        </form>
        <ul id="scheduledPosts" class="list"></ul>
      </section>
    </div>
  </div>
  <script>
    const show = (id, text) => {{
      const el = document.getElementById(id);
      el.style.display = 'block';
      el.textContent = typeof text === 'string' ? text : JSON.stringify(text, null, 2);
    }};

    async function refreshConnections() {{
      const res = await fetch('/api/v1/frontend/social/connections');
      const data = await res.json();
      const list = document.getElementById('connections');
      list.innerHTML = '';
      (data.data || []).forEach(c => {{
        const li = document.createElement('li');
        li.textContent = `${{c.platform}} → ${{c.account_name}} (${{c.status}})`;
        list.appendChild(li);
      }});
    }}

    async function refreshScheduledPosts() {{
      const res = await fetch('/api/v1/frontend/social/scheduled');
      const data = await res.json();
      const list = document.getElementById('scheduledPosts');
      list.innerHTML = '';
      (data.data || []).forEach(p => {{
        const li = document.createElement('li');
        li.textContent = `${{p.platform}} | ${{new Date(p.scheduled_for).toLocaleString()}} | ${{p.content.slice(0, 80)}}...`;
        list.appendChild(li);
      }});
    }}

    document.getElementById('companyForm').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const payload = {{
        company_name: document.getElementById('company_name').value,
        website: document.getElementById('website').value,
        description: document.getElementById('description').value,
        industry: document.getElementById('industry').value,
        target_audience: document.getElementById('target_audience').value
      }};
      const res = await fetch('/api/v1/frontend/company-profile', {{
        method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(payload)
      }});
      show('companyResult', await res.json());
    }});

    document.getElementById('connectForm').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const payload = {{
        platform: document.getElementById('platform').value,
        account_name: document.getElementById('account_name').value
      }};
      await fetch('/api/v1/frontend/social/connect', {{
        method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(payload)
      }});
      await refreshConnections();
    }});

    document.getElementById('scheduleForm').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const payload = {{
        platform: document.getElementById('schedule_platform').value,
        content: document.getElementById('post_content').value,
        scheduled_for: new Date(document.getElementById('scheduled_for').value).toISOString()
      }};
      const res = await fetch('/api/v1/frontend/social/schedule', {{
        method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(payload)
      }});
      const data = await res.json();
      if (data.status === 'success') {{
        await refreshScheduledPosts();
      }} else {{
        alert(data.detail || 'Failed to schedule post');
      }}
    }});

    refreshConnections();
    refreshScheduledPosts();
  </script>
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
        "version": "1.1.0",
    }


@app.post("/api/v1/frontend/company-profile")
async def create_company_profile(request: CompanyOnboardingRequest):
    recommendation_source = "fallback"
    recommendations = {
        "positioning": f"Position {request.company_name} as a trusted {request.industry.lower()} leader.",
        "seo_focus": ["solution keywords", "comparison keywords", "problem-intent long-tail keywords"],
        "social_focus": ["educational posts", "customer stories", "short-form authority content"],
        "email_focus": ["welcome sequence", "nurture drip", "offer conversion campaign"],
    }

    if claude:
        prompt = f"""Create a concise digital marketing starter strategy.
Company: {request.company_name}
Website: {request.website}
Description: {request.description}
Industry: {request.industry}
Audience: {request.target_audience}

Return JSON with keys: positioning, seo_focus, social_focus, email_focus."""
        try:
            raw_recommendations = await claude.generate(
                f"{prompt}\nRespond with valid JSON only."
            )
            recommendations = json.loads(raw_recommendations)
            recommendation_source = "ai"
        except json.JSONDecodeError as exc:
            logger.warning(f"AI response parsing failed, returning fallback plan: {exc}")
        except Exception as exc:
            logger.warning(f"AI recommendations failed, returning fallback plan: {exc}")

    profile = {
        "company_name": request.company_name,
        "website": request.website,
        "description": request.description,
        "industry": request.industry,
        "target_audience": request.target_audience,
        "recommendations": recommendations,
        "recommendation_source": recommendation_source,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    async with store_lock:
        company_profiles.append(profile)
    return {"status": "success", "message": "Company profile captured and strategy generated", "data": profile}


@app.get("/api/v1/frontend/company-profile")
async def get_company_profile():
    async with store_lock:
        if not company_profiles:
            return {"status": "success", "data": None}
        return {"status": "success", "data": company_profiles[-1]}


@app.post("/api/v1/frontend/social/connect")
async def connect_social_platform(request: SocialConnectionRequest):
    connection = {
        "platform": request.platform,
        "account_name": request.account_name,
        "status": "connected",
        "connected_at": datetime.now(timezone.utc).isoformat(),
    }
    async with store_lock:
        social_connections.append(connection)
    return {"status": "success", "message": f"{request.platform} connected", "data": connection}


@app.get("/api/v1/frontend/social/connections")
async def list_social_connections():
    async with store_lock:
        return {"status": "success", "data": list(social_connections)}


@app.post("/api/v1/frontend/social/schedule")
async def schedule_social_post(request: ScheduledPostRequest):
    scheduled_for_utc = request.scheduled_for.astimezone(timezone.utc)
    now_utc = datetime.now(timezone.utc)
    if scheduled_for_utc < now_utc:
        raise HTTPException(status_code=400, detail="scheduled_for must be a future date/time")

    async with store_lock:
        platform_connected = any(
            connection["platform"] == request.platform and connection["status"] == "connected"
            for connection in social_connections
        )
    if not platform_connected:
        raise HTTPException(
            status_code=400,
            detail=f"{request.platform} is not connected. Connect it first.",
        )

    scheduled_post = {
        "platform": request.platform,
        "content": request.content,
        "scheduled_for": scheduled_for_utc.isoformat(),
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    async with store_lock:
        scheduled_posts.append(scheduled_post)
    return {"status": "success", "message": "Post scheduled successfully", "data": scheduled_post}


@app.get("/api/v1/frontend/social/scheduled")
async def list_scheduled_posts():
    async with store_lock:
        posts = sorted(scheduled_posts, key=lambda p: p["scheduled_for"])
    return {"status": "success", "data": posts}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
