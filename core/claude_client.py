"""
Claude AI Client — The Brain of the Marketing Automation System

Handles all AI-powered content generation, analysis, and decision-making
through the Anthropic Claude API.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, List, Any
from anthropic import Anthropic
from config.settings import config

logger = logging.getLogger(__name__)


class ClaudeMarketingAI:
    """
    Central AI engine that powers all marketing automation tasks.
    Uses Claude API for content generation, SEO analysis, ad copy,
    email writing, social media posts, and strategic recommendations.
    """

    def __init__(self):
        self.client = Anthropic(api_key=config.claude.api_key)
        self.model = config.claude.model
        self.max_tokens = config.claude.max_tokens
        self.company = config.company

        # System prompt that gives Claude full context about the company
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build a comprehensive system prompt with company context."""
        return f"""You are an expert digital marketing AI assistant for {self.company.name}.

COMPANY CONTEXT:
- Company: {self.company.name}
- Industry: {self.company.industry}
- Website: {self.company.website}
- Target Audience: {self.company.target_audience}
- Brand Voice: {self.company.brand_voice}
- Unique Value Proposition: {self.company.unique_value_proposition}

RULES:
1. Always maintain the brand voice described above.
2. All content must be original, engaging, and optimized for the target audience.
3. Follow current digital marketing best practices.
4. Include relevant CTAs where appropriate.
5. Optimize for SEO when creating written content.
6. Be data-driven in your recommendations.
7. Output structured JSON when requested.
"""

    def _call_claude(
        self,
        prompt: str,
        system_override: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Make a call to Claude API with error handling."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature,
                system=system_override or self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}")
            raise

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        system_override: Optional[str] = None,
    ) -> str:
        """Async compatibility method for modules that await .generate()."""
        return await asyncio.to_thread(
            self._call_claude,
            prompt,
            system_override,
            temperature,
            max_tokens,
        )

    def _call_claude_json(
        self,
        prompt: str,
        system_override: Optional[str] = None,
        temperature: float = 0.5,
    ) -> Dict[str, Any]:
        """Call Claude and parse the response as JSON."""
        json_prompt = f"""{prompt}

IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, no code blocks.
Just the raw JSON object."""

        response = self._call_claude(json_prompt, system_override, temperature)

        # Clean response — strip markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            return {"error": "Failed to parse response", "raw": response}

    # ─────────────────────────────────────────────
    # CONTENT GENERATION
    # ─────────────────────────────────────────────

    def generate_blog_post(
        self,
        topic: str,
        keywords: List[str],
        word_count: int = 1500,
        tone: Optional[str] = None,
    ) -> Dict[str, str]:
        """Generate a full SEO-optimized blog post."""
        prompt = f"""Write a comprehensive, SEO-optimized blog post on the following topic:

TOPIC: {topic}
TARGET KEYWORDS: {', '.join(keywords)}
WORD COUNT: approximately {word_count} words
TONE: {tone or self.company.brand_voice}

Requirements:
- Engaging title with primary keyword
- Meta description (under 160 characters)
- Use H2 and H3 subheadings with keywords naturally included
- Include an introduction hook, body sections, and strong conclusion
- Add a clear CTA at the end
- Naturally incorporate keywords (don't keyword stuff)
- Write for humans first, search engines second

Return as JSON with keys: "title", "meta_description", "content", "tags", "slug"
"""
        return self._call_claude_json(prompt)

    def generate_social_posts(
        self,
        topic: str,
        platforms: List[str],
        campaign_goal: str = "engagement",
        num_variants: int = 3,
    ) -> Dict[str, List[Dict]]:
        """Generate platform-specific social media posts."""
        prompt = f"""Create {num_variants} social media post variants for each platform.

TOPIC: {topic}
PLATFORMS: {', '.join(platforms)}
CAMPAIGN GOAL: {campaign_goal}

Requirements per platform:
- Twitter/X: Max 280 characters, punchy, include hashtags
- LinkedIn: Professional tone, 150-300 words, thought leadership style
- Instagram: Visual-first caption, storytelling, relevant hashtags (up to 30)
- Facebook: Conversational, 100-250 words, encourage comments

Return as JSON:
{{
    "platform_name": [
        {{
            "content": "post text",
            "hashtags": ["tag1", "tag2"],
            "cta": "call to action",
            "best_posting_time": "suggested time",
            "content_type": "text/image/video/carousel"
        }}
    ]
}}
"""
        return self._call_claude_json(prompt)

    def generate_email_campaign(
        self,
        campaign_type: str,
        subject_topic: str,
        audience_segment: str,
        num_emails: int = 3,
    ) -> Dict[str, Any]:
        """Generate a complete email campaign sequence."""
        prompt = f"""Create a {num_emails}-email campaign sequence.

CAMPAIGN TYPE: {campaign_type}
TOPIC/OFFER: {subject_topic}
AUDIENCE SEGMENT: {audience_segment}
BRAND: {self.company.name}

For each email provide:
1. Subject line (and 2 A/B test variants)
2. Preview text
3. Email body (HTML-ready with personalization tokens like {{{{first_name}}}})
4. CTA button text and link placeholder
5. Send timing (delay from previous email)

Return as JSON:
{{
    "campaign_name": "name",
    "sequence": [
        {{
            "email_number": 1,
            "subject_lines": ["main", "variant_a", "variant_b"],
            "preview_text": "text",
            "body_html": "html content",
            "cta_text": "text",
            "cta_link": "placeholder",
            "send_delay_hours": 0
        }}
    ]
}}
"""
        return self._call_claude_json(prompt, max_tokens=8000)

    def generate_ad_copy(
        self,
        platform: str,
        product: str,
        objective: str,
        audience: str,
        num_variants: int = 5,
    ) -> Dict[str, Any]:
        """Generate ad copy variants for paid campaigns."""
        prompt = f"""Create {num_variants} ad copy variants.

PLATFORM: {platform}
PRODUCT/SERVICE: {product}
OBJECTIVE: {objective}
TARGET AUDIENCE: {audience}
BRAND: {self.company.name}

Platform-specific requirements:
- Google Ads: Headlines (30 chars each, provide 15), Descriptions (90 chars each, provide 4)
- Meta Ads: Primary text, headline, description, CTA
- LinkedIn Ads: Intro text, headline, description

Return as JSON:
{{
    "platform": "{platform}",
    "variants": [
        {{
            "variant_id": 1,
            "headlines": [],
            "descriptions": [],
            "primary_text": "",
            "cta": "",
            "estimated_appeal": "high/medium/low"
        }}
    ]
}}
"""
        return self._call_claude_json(prompt)

    # ─────────────────────────────────────────────
    # SEO & ANALYSIS
    # ─────────────────────────────────────────────

    def analyze_keywords(
        self,
        seed_keywords: List[str],
        intent: str = "mixed",
    ) -> Dict[str, Any]:
        """Generate keyword research and clustering from seed keywords."""
        prompt = f"""Perform comprehensive keyword research and analysis.

SEED KEYWORDS: {', '.join(seed_keywords)}
SEARCH INTENT FOCUS: {intent}
INDUSTRY: {self.company.industry}
TARGET AUDIENCE: {self.company.target_audience}

Provide:
1. Expanded keyword list (50+ keywords) grouped by topic cluster
2. Search intent classification for each (informational, commercial, transactional, navigational)
3. Estimated difficulty (low/medium/high)
4. Content type recommendation for each cluster
5. Priority ranking

Return as JSON:
{{
    "clusters": [
        {{
            "cluster_name": "name",
            "pillar_keyword": "main keyword",
            "keywords": [
                {{
                    "keyword": "term",
                    "intent": "informational",
                    "difficulty": "medium",
                    "priority": 1,
                    "content_recommendation": "blog post"
                }}
            ]
        }}
    ],
    "content_plan": [
        {{
            "title": "suggested article title",
            "target_keyword": "primary keyword",
            "supporting_keywords": ["kw1", "kw2"],
            "content_type": "blog/landing-page/guide",
            "priority": 1
        }}
    ]
}}
"""
        return self._call_claude_json(prompt, max_tokens=8000)

    def audit_seo_content(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Audit existing content for SEO optimization opportunities."""
        prompt = f"""Perform a detailed SEO audit of the following content.

TARGET KEYWORD: {target_keyword}
CONTENT:
{content[:3000]}

Analyze and score (0-100) on:
1. Keyword optimization (density, placement, LSI keywords)
2. Title tag and meta description effectiveness
3. Header structure (H1, H2, H3 usage)
4. Content quality (depth, uniqueness, readability)
5. Internal/external linking opportunities
6. Content length adequacy
7. User intent alignment

Return as JSON:
{{
    "overall_score": 75,
    "scores": {{
        "keyword_optimization": 80,
        "title_meta": 70,
        "header_structure": 65,
        "content_quality": 85,
        "linking": 50,
        "content_length": 75,
        "intent_alignment": 80
    }},
    "issues": ["issue 1", "issue 2"],
    "recommendations": ["rec 1", "rec 2"],
    "optimized_title": "suggested title",
    "optimized_meta": "suggested meta description",
    "missing_keywords": ["kw1", "kw2"],
    "suggested_sections": ["section to add"]
}}
"""
        return self._call_claude_json(prompt)

    # ─────────────────────────────────────────────
    # ANALYTICS & INSIGHTS
    # ─────────────────────────────────────────────

    def analyze_performance_data(
        self, data: Dict[str, Any], channel: str
    ) -> Dict[str, Any]:
        """Analyze marketing performance data and provide actionable insights."""
        prompt = f"""Analyze the following {channel} marketing performance data and provide actionable insights.

DATA:
{json.dumps(data, indent=2)}

Provide:
1. Key performance summary
2. Trends identified (positive and negative)
3. Anomalies or concerns
4. Top 5 actionable recommendations ranked by expected impact
5. Predicted next period performance
6. Budget reallocation suggestions (if applicable)

Return as JSON:
{{
    "summary": "brief overview",
    "kpi_highlights": {{"metric": "value"}},
    "trends": [
        {{"trend": "description", "direction": "up/down/stable", "significance": "high/medium/low"}}
    ],
    "anomalies": ["anomaly 1"],
    "recommendations": [
        {{"action": "what to do", "expected_impact": "high/medium/low", "effort": "low/medium/high", "timeline": "immediate/this_week/this_month"}}
    ],
    "predictions": {{"metric": "predicted_value"}},
    "budget_suggestions": {{"channel": "suggested_change"}}
}}
"""
        return self._call_claude_json(prompt)

    def generate_marketing_report(
        self,
        period: str,
        data: Dict[str, Any],
        channels: List[str],
    ) -> Dict[str, Any]:
        """Generate a comprehensive marketing report."""
        prompt = f"""Generate a comprehensive {period} marketing report.

COMPANY: {self.company.name}
CHANNELS COVERED: {', '.join(channels)}
PERFORMANCE DATA:
{json.dumps(data, indent=2)}

Create a complete report with:
1. Executive summary (3-4 sentences)
2. Channel-by-channel performance breakdown
3. Key wins and challenges
4. ROI analysis
5. Competitor landscape observations
6. Next period goals and action items
7. Budget recommendations

Return as JSON:
{{
    "report_title": "title",
    "period": "{period}",
    "executive_summary": "summary text",
    "channels": {{
        "channel_name": {{
            "performance_summary": "text",
            "key_metrics": {{}},
            "wins": [],
            "challenges": [],
            "recommendations": []
        }}
    }},
    "overall_roi": "calculated ROI",
    "top_wins": [],
    "top_challenges": [],
    "action_items": [
        {{"item": "description", "owner": "team/role", "deadline": "timeframe", "priority": "high/medium/low"}}
    ],
    "budget_recommendations": {{}}
}}
"""
        return self._call_claude_json(prompt, max_tokens=8000)

    # ─────────────────────────────────────────────
    # STRATEGY & PLANNING
    # ─────────────────────────────────────────────

    def create_content_calendar(
        self,
        month: str,
        channels: List[str],
        themes: List[str],
        posts_per_week: int = 5,
    ) -> Dict[str, Any]:
        """Generate a full month content calendar."""
        prompt = f"""Create a detailed content calendar for {month}.

COMPANY: {self.company.name}
CHANNELS: {', '.join(channels)}
THEMES/TOPICS: {', '.join(themes)}
FREQUENCY: {posts_per_week} posts per week per channel
TARGET AUDIENCE: {self.company.target_audience}

For each entry include:
- Date and day of week
- Platform
- Content type (post, story, reel, blog, email, etc.)
- Topic/headline
- Brief content description
- Hashtags (if social)
- Content pillar category
- CTA

Return as JSON:
{{
    "month": "{month}",
    "calendar": [
        {{
            "week": 1,
            "entries": [
                {{
                    "date": "YYYY-MM-DD",
                    "day": "Monday",
                    "platform": "platform",
                    "content_type": "type",
                    "title": "headline",
                    "description": "brief description",
                    "hashtags": [],
                    "content_pillar": "category",
                    "cta": "call to action",
                    "status": "planned"
                }}
            ]
        }}
    ]
}}
"""
        return self._call_claude_json(prompt, max_tokens=8000)

    def suggest_campaign_strategy(
        self,
        goal: str,
        budget: float,
        timeline: str,
        current_metrics: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Get AI-powered campaign strategy recommendations."""
        prompt = f"""Design a comprehensive marketing campaign strategy.

COMPANY: {self.company.name}
INDUSTRY: {self.company.industry}
GOAL: {goal}
BUDGET: ${budget:,.2f}
TIMELINE: {timeline}
TARGET AUDIENCE: {self.company.target_audience}
CURRENT METRICS: {json.dumps(current_metrics) if current_metrics else 'Not provided'}

Create a detailed strategy including:
1. Campaign concept and messaging framework
2. Channel mix with budget allocation percentages
3. Content requirements for each channel
4. Timeline with milestones
5. KPIs and targets
6. A/B testing plan
7. Risk mitigation strategies

Return as JSON:
{{
    "campaign_name": "suggested name",
    "concept": "campaign concept description",
    "messaging_framework": {{
        "primary_message": "",
        "supporting_messages": [],
        "tagline": ""
    }},
    "channel_strategy": [
        {{
            "channel": "name",
            "budget_percentage": 30,
            "budget_amount": 3000,
            "tactics": [],
            "content_needed": [],
            "kpis": {{}}
        }}
    ],
    "timeline": [
        {{"phase": "name", "duration": "2 weeks", "activities": []}}
    ],
    "testing_plan": [
        {{"test": "what to test", "hypothesis": "expected outcome", "metric": "measurement"}}
    ],
    "projected_results": {{}},
    "risks": [
        {{"risk": "description", "mitigation": "how to handle"}}
    ]
        }}
"""
        return self._call_claude_json(prompt, max_tokens=8000)


# Backward-compatible aliases used across modules.
ClaudeClient = ClaudeMarketingAI
MarketingAIClient = ClaudeMarketingAI
