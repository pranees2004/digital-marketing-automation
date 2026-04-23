"""
FastAPI Server — Digital Marketing Automation API
Main application entry point for the REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Digital Marketing Automation API starting up...")
    logger.info("📊 Initializing modules...")
    yield
    logger.info("👋 Shutting down Digital Marketing Automation API")


app = FastAPI(
    title="Digital Marketing Automation API",
    description="""
    ## 🚀 Complete Digital Marketing Automation System
    
    Powered by **Claude AI (Anthropic)** + **Azure Cloud**
    
    ### Features:
    - 📝 **Content Generation** — Blog posts, social media content, ad copy
    - 🔍 **SEO Optimization** — Keyword research, content optimization, audits
    - 📱 **Social Media Management** — Multi-platform scheduling & posting
    - 📧 **Email Automation** — Campaign creation, sequences, A/B testing
    - 📊 **Analytics & Reporting** — Performance tracking & insights
    - 🎯 **Ad Campaign Management** — Google Ads & Meta Ads automation
    - 🔄 **Automated Workflows** — Daily, weekly, monthly marketing tasks
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page with dashboard"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 Digital Marketing Automation</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); 
                color: #fff; 
                min-height: 100vh;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            
            header {
                text-align: center;
                padding: 40px 0 30px;
            }
            header h1 { 
                font-size: 2.5rem; 
                background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00d2ff);
                background-size: 200%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: shimmer 3s ease-in-out infinite;
            }
            @keyframes shimmer { 0%,100%{background-position:0%} 50%{background-position:100%} }
            header p { color: #a0a0c0; margin-top: 10px; font-size: 1.1rem; }
            
            .status-bar {
                display: flex;
                justify-content: center;
                gap: 30px;
                margin: 25px 0;
                flex-wrap: wrap;
            }
            .status-item {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 15px 25px;
                text-align: center;
            }
            .status-item .dot { 
                display: inline-block; 
                width: 10px; height: 10px; 
                border-radius: 50%; 
                margin-right: 8px;
                animation: pulse 2s ease-in-out infinite;
            }
            .dot.green { background: #00ff88; box-shadow: 0 0 10px #00ff88; }
            .dot.yellow { background: #ffd700; box-shadow: 0 0 10px #ffd700; }
            @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
            
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 25px;
                transition: all 0.3s ease;
                cursor: pointer;
                text-decoration: none;
                color: inherit;
                display: block;
            }
            .card:hover { 
                transform: translateY(-5px); 
                border-color: #3a7bd5;
                box-shadow: 0 10px 40px rgba(58,123,213,0.2);
            }
            .card-icon { font-size: 2rem; margin-bottom: 12px; }
            .card h3 { margin-bottom: 8px; font-size: 1.2rem; }
            .card p { color: #a0a0c0; font-size: 0.9rem; line-height: 1.5; }
            .card .endpoint { 
                margin-top: 12px; 
                padding: 6px 12px; 
                background: rgba(58,123,213,0.2); 
                border-radius: 6px; 
                font-family: monospace; 
                font-size: 0.8rem;
                color: #00d2ff;
                display: inline-block;
            }
            
            .try-section {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 30px;
                margin: 30px 0;
            }
            .try-section h2 { margin-bottom: 20px; color: #00d2ff; }
            
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; color: #a0a0c0; }
            .form-group input, .form-group select, .form-group textarea {
                width: 100%;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(0,0,0,0.3);
                color: #fff;
                font-size: 1rem;
            }
            .form-group textarea { min-height: 80px; resize: vertical; }
            
            .btn {
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn-primary { 
                background: linear-gradient(90deg, #3a7bd5, #00d2ff); 
                color: #fff; 
            }
            .btn-primary:hover { transform: scale(1.05); box-shadow: 0 5px 20px rgba(58,123,213,0.4); }
            
            .result-box {
                margin-top: 20px;
                padding: 20px;
                background: rgba(0,0,0,0.3);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.1);
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 0.9rem;
                display: none;
                max-height: 400px;
                overflow-y: auto;
            }
            
            .footer {
                text-align: center;
                padding: 30px 0;
                color: #666;
                border-top: 1px solid rgba(255,255,255,0.05);
                margin-top: 40px;
            }
            .footer a { color: #3a7bd5; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🚀 Digital Marketing Automation</h1>
                <p>AI-Powered Marketing Engine — Claude API + Azure Cloud</p>
            </header>
            
            <div class="status-bar">
                <div class="status-item">
                    <span class="dot green"></span> API Server: Online
                </div>
                <div class="status-item">
                    <span class="dot green"></span> Claude AI: Connected
                </div>
                <div class="status-item">
                    <span class="dot yellow"></span> Azure: Standby
                </div>
            </div>
            
            <div class="grid">
                <a class="card" href="/docs" target="_blank">
                    <div class="card-icon">📝</div>
                    <h3>Content Engine</h3>
                    <p>Generate blog posts, articles, social media content, and ad copy using Claude AI.</p>
                    <span class="endpoint">POST /api/v1/content/generate</span>
                </a>
                
                <a class="card" href="/docs" target="_blank">
                    <div class="card-icon">🔍</div>
                    <h3>SEO Optimizer</h3>
                    <p>Keyword research, content scoring, meta tag generation, and SEO audits.</p>
                    <span class="endpoint">POST /api/v1/seo/analyze</span>
                </a>
                
                <a class="card" href="/docs" target="_blank">
                    <div class="card-icon">📱</div>
                    <h3>Social Media</h3>
                    <p>Create & schedule posts across Twitter, LinkedIn, Facebook, and Instagram.</p>
                    <span class="endpoint">POST /api/v1/social/create</span>
                </a>
                
                <a class="card" href="/docs" target="_blank">
                    <div class="card-icon">📧</div>
                    <h3>Email Campaigns</h3>
                    <p>Automated email sequences, A/B testing, and newsletter generation.</p>
                    <span class="endpoint">POST /api/v1/email/campaign</span>
                </a>
                
                <a class="card" href="/docs" target="_blank">
                    <div class="card-icon">🎯</div>
                    <h3>Ad Campaigns</h3>
                    <p>Google Ads & Meta Ads copy generation, audience targeting suggestions.</p>
                    <span class="endpoint">POST /api/v1/ads/generate</span>
                </a>
                
                <a class="card" href="/docs" target="_blank">
                    <div class="card-icon">📊</div>
                    <h3>Analytics & Reports</h3>
                    <p>Performance dashboards, automated weekly/monthly marketing reports.</p>
                    <span class="endpoint">GET /api/v1/analytics/dashboard</span>
                </a>
                
                <a class="card" href="/docs" target="_blank">
                    <div class="card-icon">🔄</div>
                    <h3>Workflows</h3>
                    <p>Run automated daily, weekly, and monthly marketing workflows.</p>
                    <span class="endpoint">POST /api/v1/workflows/run</span>
                </a>
                
                <a class="card" href="/docs" target="_blank">
                    <div class="card-icon">⚡</div>
                    <h3>API Docs</h3>
                    <p>Full interactive Swagger documentation for all endpoints.</p>
                    <span class="endpoint">GET /docs</span>
                </a>
            </div>
            
            <!-- Quick Try Section -->
            <div class="try-section">
                <h2>⚡ Quick Try — Generate Content Now</h2>
                <div class="form-group">
                    <label>Content Type</label>
                    <select id="contentType">
                        <option value="blog_post">📝 Blog Post</option>
                        <option value="social_media">📱 Social Media Post</option>
                        <option value="email">📧 Email Campaign</option>
                        <option value="ad_copy">🎯 Ad Copy</option>
                        <option value="seo_meta">🔍 SEO Meta Tags</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Topic / Keywords</label>
                    <input type="text" id="topic" placeholder="e.g., AI in digital marketing, SaaS growth hacks..." />
                </div>
                <div class="form-group">
                    <label>Additional Instructions (optional)</label>
                    <textarea id="instructions" placeholder="e.g., Target audience: startup founders, Tone: casual..."></textarea>
                </div>
                <button class="btn btn-primary" onclick="generateContent()">🚀 Generate with Claude AI</button>
                <div id="resultBox" class="result-box"></div>
            </div>
            
            <div class="footer">
                <p>Built with ❤️ using <a href="https://anthropic.com">Claude AI</a> + <a href="https://azure.microsoft.com">Azure Cloud</a></p>
                <p style="margin-top:5px;">📖 <a href="/docs">API Documentation</a> | <a href="/api/v1/health">Health Check</a></p>
            </div>
        </div>
        
        <script>
            async function generateContent() {
                const type = document.getElementById('contentType').value;
                const topic = document.getElementById('topic').value;
                const instructions = document.getElementById('instructions').value;
                const resultBox = document.getElementById('resultBox');
                
                if (!topic) { alert('Please enter a topic!'); return; }
                
                resultBox.style.display = 'block';
                resultBox.textContent = '⏳ Generating content with Claude AI...';
                
                try {
                    const response = await fetch('/api/v1/content/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            content_type: type,
                            topic: topic,
                            instructions: instructions,
                            tone: 'professional'
                        })
                    });
                    const data = await response.json();
                    if (data.status === 'success') {
                        resultBox.textContent = data.content || JSON.stringify(data, null, 2);
                    } else {
                        resultBox.textContent = '⚠️ ' + JSON.stringify(data, null, 2);
                    }
                } catch (error) {
                    resultBox.textContent = '❌ Error: ' + error.message + '\\n\\nMake sure the API is running and Claude API key is set.';
                }
            }
        </script>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Digital Marketing Automation API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
