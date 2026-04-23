"""
Social Media Manager Module
Automated multi-platform social media content creation, scheduling, and posting.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class SocialPost:
    platform: str
    content: str
    hashtags: List[str] = field(default_factory=list)
    media_urls: List[str] = field(default_factory=list)
    scheduled_time: Optional[str] = None
    status: str = "draft"
    post_id: Optional[str] = None
    engagement: Dict = field(default_factory=dict)


class SocialMediaManager:
    """AI-powered social media management across multiple platforms."""

    PLATFORMS = ["twitter", "linkedin", "facebook", "instagram"]

    PLATFORM_LIMITS = {
        "twitter": {"max_chars": 280, "hashtags": 3, "best_times": ["09:00", "12:00", "17:00"]},
        "linkedin": {"max_chars": 3000, "hashtags": 5, "best_times": ["08:00", "10:00", "12:00"]},
        "facebook": {"max_chars": 63206, "hashtags": 3, "best_times": ["09:00", "13:00", "16:00"]},
        "instagram": {"max_chars": 2200, "hashtags": 20, "best_times": ["11:00", "14:00", "19:00"]},
    }

    def __init__(self, claude_client, db_service=None, storage_service=None, config=None):
        self.claude = claude_client
        self.db = db_service
        self.storage = storage_service
        self.config = config or {}
        self.container_name = "social_media"

    async def generate_posts_from_content(
        self,
        source_content: str,
        platforms: List[str] = None,
        num_variations: int = 3,
        content_type: str = "promotional"
    ) -> Dict[str, List[SocialPost]]:
        """Generate platform-specific social media posts from source content."""
        platforms = platforms or self.PLATFORMS

        prompt = f"""You are an expert social media marketer. Create engaging social media posts from this content.

Source Content:
---
{source_content[:3000]}
---

Company: {self.config.get('company_name', 'Our Company')}
Brand Voice: {self.config.get('brand_voice', 'Professional and engaging')}
Content Type: {content_type}

Generate {num_variations} variations for each platform: {', '.join(platforms)}

Platform constraints:
- Twitter/X: Max 280 chars, 2-3 hashtags, punchy and concise
- LinkedIn: Professional tone, 1-3 paragraphs, 3-5 hashtags, can include bullet points
- Facebook: Conversational, can be longer, 2-3 hashtags, encourage engagement
- Instagram: Visual-first caption, storytelling approach, up to 20 relevant hashtags

Return as JSON:
{{
    "posts": {{
        "twitter": [
            {{
                "content": "Tweet text without hashtags",
                "hashtags": ["hashtag1", "hashtag2"],
                "suggested_media": "Description of ideal image/video",
                "cta_type": "link_click|engagement|awareness",
                "best_time": "09:00"
            }}
        ],
        "linkedin": [...],
        "facebook": [...],
        "instagram": [...]
    }},
    "content_theme": "The overarching theme",
    "campaign_hashtag": "A branded hashtag suggestion"
}}
Only include platforms requested. Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=4000)
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            result = json.loads(json_match.group()) if json_match else {"posts": {}}

        all_posts = {}
        for platform in platforms:
            platform_posts = result.get("posts", {}).get(platform, [])
            all_posts[platform] = [
                SocialPost(
                    platform=platform,
                    content=p.get("content", ""),
                    hashtags=p.get("hashtags", []),
                    scheduled_time=p.get("best_time"),
                    status="draft"
                )
                for p in platform_posts
            ]

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"posts_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": "generated_posts",
                "platforms": platforms,
                "posts": {k: [asdict(p) for p in v] for k, v in all_posts.items()},
                "source_content_preview": source_content[:200],
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        total = sum(len(v) for v in all_posts.values())
        logger.info(f"Generated {total} social media posts across {len(platforms)} platforms")
        return all_posts

    async def generate_content_calendar(self, weeks: int = 4, posts_per_week: int = 5, themes: List[str] = None) -> Dict:
        """Generate a full social media content calendar."""
        themes_str = ", ".join(themes) if themes else "industry trends, product features, tips & tutorials, customer stories, company culture"

        prompt = f"""Create a {weeks}-week social media content calendar.

Company: {self.config.get('company_name', 'Our Company')}
Industry: {self.config.get('industry', 'Technology')}
Audience: {self.config.get('target_audience', 'Business professionals')}
Brand Voice: {self.config.get('brand_voice', 'Professional')}

Posts per week: {posts_per_week}
Content themes to rotate: {themes_str}
Platforms: Twitter, LinkedIn, Facebook, Instagram

Return as JSON:
{{
    "calendar": [
        {{
            "week": 1,
            "theme": "Main theme for the week",
            "posts": [
                {{
                    "day": "Monday",
                    "date_offset_days": 0,
                    "platform": "linkedin",
                    "content_type": "thought_leadership|tip|promotion|story|question|poll",
                    "topic": "Specific topic",
                    "draft_content": "Draft post content",
                    "hashtags": ["tag1", "tag2"],
                    "media_suggestion": "Image/video description",
                    "best_post_time": "10:00",
                    "goal": "engagement|traffic|awareness|leads"
                }}
            ]
        }}
    ],
    "strategy_notes": "Overall strategy explanation",
    "kpis_to_track": ["kpi1", "kpi2"]
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=4096)
        try:
            calendar = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            calendar = json.loads(json_match.group()) if json_match else {"calendar": []}

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"calendar_{datetime.now().strftime('%Y%m%d')}",
                "type": "content_calendar",
                "weeks": weeks,
                "data": calendar,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"Generated {weeks}-week content calendar")
        return calendar

    async def repurpose_blog_to_social(self, blog_title: str, blog_content: str, blog_url: str = "") -> Dict:
        """Repurpose a single blog post into multiple social media posts."""
        prompt = f"""Repurpose this blog post into a week's worth of social media content.

Blog Title: {blog_title}
Blog URL: {blog_url or 'https://example.com/blog'}
Blog Content:
---
{blog_content[:3000]}
---

Create a repurposing plan as JSON:
{{
    "repurpose_plan": [
        {{
            "day": 1,
            "platform": "linkedin",
            "angle": "Key takeaway thread",
            "content": "Full post text",
            "hashtags": ["tag1"],
            "media_type": "text|image|carousel|video_script",
            "media_description": "What visual to create"
        }}
    ],
    "twitter_thread": [
        "Tweet 1 (hook)",
        "Tweet 2 (key point)",
        "Tweet 3 (value)",
        "Tweet 4 (CTA with link)"
    ],
    "instagram_carousel_slides": [
        {{
            "slide": 1,
            "text": "Slide text",
            "design_notes": "Design direction"
        }}
    ],
    "linkedin_article_summary": "A LinkedIn article version summary",
    "total_pieces": 10
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=4000)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

    async def generate_engagement_responses(self, comments: List[Dict], context: str = "") -> List[Dict]:
        """Generate AI responses for social media comments/messages."""
        prompt = f"""You are a social media community manager for {self.config.get('company_name', 'our company')}.
Brand voice: {self.config.get('brand_voice', 'Professional and friendly')}

Generate thoughtful responses to these comments:
{json.dumps(comments, indent=2)}

Context: {context or 'General social media engagement'}

Return as JSON:
{{
    "responses": [
        {{
            "original_comment": "The comment text",
            "response": "Your crafted response",
            "tone": "friendly|professional|empathetic|enthusiastic",
            "action_needed": "none|escalate_to_support|flag_for_review"
        }}
    ]
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2000)
        try:
            result = json.loads(response)
            return result.get("responses", [])
        except json.JSONDecodeError:
            return []

    async def analyze_post_performance(self, posts_data: List[Dict]) -> Dict:
        """Analyze social media post performance and provide recommendations."""
        prompt = f"""Analyze these social media post performance metrics and provide insights.

Post Performance Data:
{json.dumps(posts_data[:20], indent=2)}

Return as JSON:
{{
    "summary": {{
        "total_posts_analyzed": 0,
        "avg_engagement_rate": "0%",
        "top_performing_platform": "platform",
        "best_content_type": "type",
        "best_posting_time": "time"
    }},
    "top_posts": [
        {{
            "post_preview": "first 50 chars",
            "platform": "platform",
            "why_it_worked": "explanation"
        }}
    ],
    "underperforming_posts": [
        {{
            "post_preview": "first 50 chars",
            "platform": "platform",
            "improvement_suggestion": "suggestion"
        }}
    ],
    "recommendations": [
        "Actionable recommendation 1",
        "Actionable recommendation 2"
    ],
    "content_mix_suggestion": {{
        "educational": "30%",
        "promotional": "20%",
        "engagement": "25%",
        "storytelling": "25%"
    }}
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse analysis"}

    async def generate_hashtag_strategy(self, topic: str, platform: str = "instagram") -> Dict:
        """Generate an optimized hashtag strategy for a topic."""
        limit = self.PLATFORM_LIMITS.get(platform, {}).get("hashtags", 10)

        prompt = f"""Create an optimized hashtag strategy for the topic "{topic}" on {platform}.

Company industry: {self.config.get('industry', 'Technology')}

Return as JSON:
{{
    "primary_hashtags": ["3-5 high-volume hashtags"],
    "secondary_hashtags": ["5-10 medium-volume niche hashtags"],
    "branded_hashtags": ["1-2 branded hashtags"],
    "trending_suggestions": ["2-3 currently relevant hashtags"],
    "hashtag_sets": [
        {{
            "name": "Set A - Broad Reach",
            "hashtags": ["tag1", "tag2"],
            "use_case": "When targeting broad audience"
        }},
        {{
            "name": "Set B - Niche Focus",
            "hashtags": ["tag1", "tag2"],
            "use_case": "When targeting specific segment"
        }}
    ],
    "avoid_hashtags": ["overused or spammy hashtags to avoid"],
    "max_recommended": {limit}
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=1500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Parse failed"}

    async def create_campaign(self, campaign_name: str, objective: str, duration_days: int = 30, platforms: List[str] = None) -> Dict:
        """Create a full social media campaign plan."""
        platforms = platforms or self.PLATFORMS

        prompt = f"""Design a complete social media campaign.

Campaign Name: {campaign_name}
Objective: {objective}
Duration: {duration_days} days
Platforms: {', '.join(platforms)}
Company: {self.config.get('company_name', 'Our Company')}
Audience: {self.config.get('target_audience', 'Business professionals')}

Return as JSON:
{{
    "campaign_name": "{campaign_name}",
    "objective": "{objective}",
    "duration_days": {duration_days},
    "strategy": "Overall campaign strategy description",
    "phases": [
        {{
            "phase": "Teaser/Launch/Sustain/Close",
            "days": "1-7",
            "focus": "Phase focus",
            "post_frequency": "2x daily",
            "content_types": ["type1", "type2"],
            "sample_posts": [
                {{
                    "platform": "linkedin",
                    "content": "Sample post",
                    "media": "Media description"
                }}
            ]
        }}
    ],
    "hashtag_strategy": {{
        "campaign_hashtag": "#CampaignTag",
        "supporting_hashtags": ["tag1", "tag2"]
    }},
    "kpis": [
        {{"metric": "Engagement Rate", "target": "5%"}},
        {{"metric": "Reach", "target": "50,000"}}
    ],
    "budget_suggestion": {{
        "organic": "Strategy for organic reach",
        "paid_boost": "Suggested posts to boost and budget"
    }},
    "influencer_collab": "Suggested influencer collaboration approach"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=4000)
        try:
            campaign = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            campaign = json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"campaign_{campaign_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                "type": "campaign",
                "data": campaign,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"Campaign created: {campaign_name}")
        return campaign
