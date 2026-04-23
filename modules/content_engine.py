"""
Content Engine — AI-powered blog posts, articles, landing pages, ad copy
Uses Claude API for all content generation
"""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ContentEngine:
    """Generates all types of marketing content using Claude AI."""

    def __init__(self, ai_client, azure_services=None, company_profile=None):
        self.ai = ai_client
        self.azure = azure_services
        self.company = company_profile or {}

    def _get_brand_context(self) -> str:
        """Build brand context string for prompts."""
        if isinstance(self.company, dict):
            name = self.company.get("name", "Our Company")
            industry = self.company.get("industry", "")
            audience = self.company.get("target_audience", "")
            voice = self.company.get("brand_voice", "")
            uvp = self.company.get("unique_value_proposition", "")
        else:
            name = getattr(self.company, "name", "Our Company")
            industry = getattr(self.company, "industry", "")
            audience = getattr(self.company, "target_audience", "")
            voice = getattr(self.company, "brand_voice", "")
            uvp = getattr(self.company, "unique_value_proposition", "")

        return f"""
BRAND CONTEXT:
- Company: {name}
- Industry: {industry}
- Target Audience: {audience}
- Brand Voice: {voice}
- Value Proposition: {uvp}
""".strip()

    # ==================== BLOG CONTENT ====================

    def generate_blog_post(
        self,
        topic: str,
        keywords: List[str] = None,
        word_count: int = 1500,
        tone: str = "professional",
        include_meta: bool = True,
    ) -> Dict:
        """Generate a complete SEO-optimized blog post."""
        keywords_str = ", ".join(keywords) if keywords else "relevant industry terms"

        prompt = f"""
{self._get_brand_context()}

Write a complete, SEO-optimized blog post with the following specifications:

TOPIC: {topic}
TARGET KEYWORDS: {keywords_str}
WORD COUNT: ~{word_count} words
TONE: {tone}

REQUIREMENTS:
1. Compelling headline (H1) with primary keyword
2. Meta description (155 characters max)
3. Introduction with hook (first 100 words must be engaging)
4. 4-6 H2 subheadings with keyword variations
5. Bullet points and numbered lists where appropriate
6. Internal linking suggestions (mark as [INTERNAL LINK: topic])
7. Call-to-action at the end
8. FAQ section with 3-5 questions (for featured snippets)

OUTPUT FORMAT (JSON):
{{
    "title": "...",
    "meta_description": "...",
    "slug": "...",
    "keywords": ["primary", "secondary1", "secondary2"],
    "estimated_read_time": "X min",
    "content_html": "<article>...</article>",
    "content_markdown": "...",
    "faq": [{{"question": "...", "answer": "..."}}],
    "internal_link_suggestions": ["topic1", "topic2"],
    "social_snippets": {{
        "twitter": "...",
        "linkedin": "...",
        "facebook": "..."
    }}
}}
"""
        response = self.ai.generate(prompt, max_tokens=8000, temperature=0.7)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {
                "title": topic,
                "content_markdown": response,
                "raw_response": True,
            }

        result["generated_at"] = datetime.now(timezone.utc).isoformat()
        result["topic"] = topic
        result["content_type"] = "blog_post"

        # Save to database
        if self.azure:
            self.azure.cosmos.save_document("content", result)

        return result

    def generate_blog_ideas(self, niche: str, count: int = 10, months_ahead: int = 3) -> List[Dict]:
        """Generate a content calendar of blog ideas."""
        prompt = f"""
{self._get_brand_context()}

Generate {count} blog post ideas for the next {months_ahead} months in the "{niche}" niche.

For each idea provide:
1. Title (SEO optimized)
2. Primary keyword
3. Search intent (informational/commercial/transactional/navigational)
4. Estimated search volume (low/medium/high)
5. Difficulty (easy/medium/hard)
6. Suggested publish date
7. Content angle / unique hook
8. Target word count

OUTPUT FORMAT (JSON array):
[
    {{
        "title": "...",
        "primary_keyword": "...",
        "search_intent": "...",
        "estimated_volume": "...",
        "difficulty": "...",
        "suggested_date": "YYYY-MM-DD",
        "content_angle": "...",
        "word_count": 1500
    }}
]
"""
        response = self.ai.generate(prompt, max_tokens=4000)

        try:
            ideas = json.loads(response)
        except json.JSONDecodeError:
            ideas = [{"raw_response": response}]

        return ideas

    # ==================== LANDING PAGES ====================

    def generate_landing_page(
        self,
        product_name: str,
        product_description: str,
        target_action: str = "Sign up for free trial",
        style: str = "modern",
    ) -> Dict:
        """Generate landing page copy."""
        prompt = f"""
{self._get_brand_context()}

Create high-converting landing page copy for:

PRODUCT: {product_name}
DESCRIPTION: {product_description}
TARGET ACTION (CTA): {target_action}
STYLE: {style}

Include these sections:
1. Hero Section — Headline + subheadline + primary CTA
2. Problem Statement — Pain points (3-4)
3. Solution — How product solves the problems
4. Features — 4-6 key features with benefits
5. Social Proof — Placeholder testimonial templates
6. Pricing (if applicable) — Suggested structure
7. FAQ — 4-5 common objections answered
8. Final CTA — Urgency-driven closing

OUTPUT FORMAT (JSON):
{{
    "hero": {{
        "headline": "...",
        "subheadline": "...",
        "cta_text": "...",
        "supporting_text": "..."
    }},
    "problem_section": {{
        "headline": "...",
        "pain_points": ["...", "...", "..."]
    }},
    "solution_section": {{
        "headline": "...",
        "description": "..."
    }},
    "features": [
        {{"title": "...", "description": "...", "icon_suggestion": "..."}}
    ],
    "testimonials_template": [
        {{"quote": "...", "name": "[Name]", "role": "[Role]"}}
    ],
    "faq": [{{"question": "...", "answer": "..."}}],
    "final_cta": {{
        "headline": "...",
        "cta_text": "...",
        "urgency_text": "..."
    }},
    "meta": {{
        "title": "...",
        "description": "..."
    }}
}}
"""
        response = self.ai.generate(prompt, max_tokens=6000)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {"raw_response": response}

        result["content_type"] = "landing_page"
        result["product_name"] = product_name

        if self.azure:
            self.azure.cosmos.save_document("content", result)

        return result

    # ==================== AD COPY ====================

    def generate_ad_copy(
        self,
        product: str,
        platform: str = "google",
        campaign_goal: str = "conversions",
        variations: int = 5,
    ) -> List[Dict]:
        """Generate ad copy variations for different platforms."""
        platform_specs = {
            "google": {
                "headlines": "up to 30 characters each, need 15 headlines",
                "descriptions": "up to 90 characters each, need 4 descriptions",
            },
            "facebook": {
                "primary_text": "up to 125 characters (recommended)",
                "headline": "up to 40 characters",
                "description": "up to 30 characters",
            },
            "linkedin": {
                "intro_text": "up to 150 characters",
                "headline": "up to 70 characters",
            },
            "twitter": {
                "tweet_text": "up to 280 characters",
                "card_title": "up to 70 characters",
            },
        }

        specs = platform_specs.get(platform, platform_specs["google"])

        prompt = f"""
{self._get_brand_context()}

Create {variations} ad copy variations for:

PRODUCT/SERVICE: {product}
PLATFORM: {platform}
CAMPAIGN GOAL: {campaign_goal}
AD SPECS: {json.dumps(specs)}

For each variation:
1. Follow the platform's character limits STRICTLY
2. Include a clear CTA
3. Use power words and emotional triggers
4. A/B test different angles (benefit, feature, social proof, urgency, curiosity)

OUTPUT FORMAT (JSON):
{{
    "platform": "{platform}",
    "variations": [
        {{
            "variation_name": "Benefit-focused",
            "copy": {{...platform-specific fields...}},
            "angle": "...",
            "expected_ctr": "low/medium/high"
        }}
    ]
}}
"""
        response = self.ai.generate(prompt, max_tokens=4000)

        try:
            result = json.loads(response)
            return result.get("variations", [result])
        except json.JSONDecodeError:
            return [{"raw_response": response}]

    # ==================== EMAIL COPY ====================

    def generate_email_sequence(
        self,
        sequence_type: str = "welcome",
        num_emails: int = 5,
        product: str = "",
    ) -> List[Dict]:
        """Generate an email sequence (welcome, nurture, sales, re-engagement)."""
        prompt = f"""
{self._get_brand_context()}

Create a {num_emails}-email {sequence_type} sequence for:
PRODUCT/CONTEXT: {product or 'general company engagement'}

For each email provide:
1. Subject line (and 2 A/B test alternatives)
2. Preview text
3. Email body (HTML-friendly)
4. CTA text and link placeholder
5. Send timing (e.g., "Day 0", "Day 2", "Day 5")
6. Goal of this specific email

SEQUENCE TYPES CONTEXT:
- welcome: Onboard new subscribers, build trust, deliver value
- nurture: Educate and build relationship over time
- sales: Drive conversions with increasing urgency
- re-engagement: Win back inactive subscribers
- abandoned_cart: Recover abandoned purchases

OUTPUT FORMAT (JSON):
{{
    "sequence_type": "{sequence_type}",
    "emails": [
        {{
            "email_number": 1,
            "send_timing": "Day 0",
            "goal": "...",
            "subject_line": "...",
            "subject_alternatives": ["...", "..."],
            "preview_text": "...",
            "body_html": "...",
            "cta_text": "...",
            "cta_url_placeholder": "..."
        }}
    ]
}}
"""
        response = self.ai.generate(prompt, max_tokens=8000)

        try:
            result = json.loads(response)
            return result.get("emails", [result])
        except json.JSONDecodeError:
            return [{"raw_response": response}]

    # ==================== SOCIAL MEDIA CONTENT ====================

    def generate_social_posts(
        self,
        topic: str,
        platforms: List[str] = None,
        num_posts: int = 5,
        content_type: str = "educational",
    ) -> Dict:
        """Generate social media posts for multiple platforms."""
        platforms = platforms or ["twitter", "linkedin", "instagram", "facebook"]

        prompt = f"""
{self._get_brand_context()}

Create {num_posts} social media posts about "{topic}" for these platforms: {', '.join(platforms)}

CONTENT TYPE: {content_type} (educational/promotional/entertaining/behind-the-scenes/user-generated)

For each platform, follow these rules:
- Twitter/X: Max 280 chars, use hashtags (2-3), conversational
- LinkedIn: Professional tone, 150-300 words, storytelling, use line breaks
- Instagram: Caption + hashtags (20-30), use emojis, strong hook in first line
- Facebook: Engaging question or story, 100-200 words, community-focused

OUTPUT FORMAT (JSON):
{{
    "topic": "{topic}",
    "posts": {{
        "twitter": [
            {{"text": "...", "hashtags": ["...", "..."], "best_time": "...", "media_suggestion": "..."}}
        ],
        "linkedin": [
            {{"text": "...", "hashtags": ["...", "..."], "best_time": "...", "media_suggestion": "..."}}
        ],
        "instagram": [
            {{"caption": "...", "hashtags": ["..."], "best_time": "...", "media_suggestion": "...", "reel_idea": "..."}}
        ],
        "facebook": [
            {{"text": "...", "best_time": "...", "media_suggestion": "...", "engagement_question": "..."}}
        ]
    }}
}}
"""
        response = self.ai.generate(prompt, max_tokens=6000)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {"raw_response": response}

        result["content_type"] = "social_posts"

        if self.azure:
            self.azure.cosmos.save_document("social_posts", result)

        return result

    # ==================== CONTENT REPURPOSING ====================

    def repurpose_content(self, original_content: str, original_format: str = "blog_post") -> Dict:
        """Repurpose one piece of content into multiple formats."""
        prompt = f"""
{self._get_brand_context()}

Repurpose the following {original_format} into multiple content formats:

ORIGINAL CONTENT:
{original_content[:3000]}

Create ALL of the following from this content:
1. Twitter thread (5-7 tweets)
2. LinkedIn article summary post
3. Instagram carousel outline (8-10 slides)
4. Email newsletter snippet
5. YouTube video script outline
6. Podcast talking points
7. Infographic text outline
8. Quote graphics (3-5 shareable quotes)

OUTPUT FORMAT (JSON):
{{
    "twitter_thread": ["tweet1", "tweet2", ...],
    "linkedin_post": "...",
    "instagram_carousel": [{{"slide_number": 1, "text": "...", "visual_suggestion": "..."}}],
    "email_snippet": {{"subject": "...", "body": "..."}},
    "youtube_outline": {{"title": "...", "sections": [...]}},
    "podcast_points": ["point1", "point2", ...],
    "infographic_outline": {{"title": "...", "sections": [...]}},
    "quote_graphics": ["quote1", "quote2", ...]
}}
"""
        response = self.ai.generate(prompt, max_tokens=6000)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}

    # ==================== CONTENT OPTIMIZATION ====================

    def optimize_content(self, content: str, optimization_type: str = "seo") -> Dict:
        """Optimize existing content for SEO, readability, or conversions."""
        prompt = f"""
{self._get_brand_context()}

Analyze and optimize the following content for {optimization_type}:

CONTENT:
{content[:4000]}

OPTIMIZATION TYPE: {optimization_type}

Provide:
1. Overall score (1-100)
2. Specific issues found
3. Optimized version of the content
4. List of changes made and why
5. Additional recommendations

OUTPUT FORMAT (JSON):
{{
    "score": 75,
    "issues": [
        {{"type": "...", "severity": "high/medium/low", "description": "...", "location": "..."}}
    ],
    "optimized_content": "...",
    "changes_made": ["change1", "change2"],
    "recommendations": ["rec1", "rec2"],
    "keyword_suggestions": ["kw1", "kw2"]
}}
"""
        response = self.ai.generate(prompt, max_tokens=6000)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}
