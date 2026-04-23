"""
SEO Optimizer Module
Automated SEO auditing, keyword research, and content optimization using Claude AI.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class KeywordData:
    keyword: str
    search_volume: int = 0
    difficulty: str = "medium"
    intent: str = "informational"
    current_rank: Optional[int] = None
    target_rank: int = 10
    priority: str = "medium"


@dataclass
class SEOAuditResult:
    url: str
    score: int = 0
    issues: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    meta_analysis: Dict = field(default_factory=dict)
    content_analysis: Dict = field(default_factory=dict)
    technical_issues: List[Dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SEOOptimizer:
    """AI-powered SEO optimization and auditing engine."""

    def __init__(self, claude_client, db_service=None, config=None):
        self.claude = claude_client
        self.db = db_service
        self.config = config or {}
        self.container_name = "seo_data"

    async def research_keywords(self, topic: str, count: int = 20) -> List[Dict]:
        """Use Claude to generate keyword research for a topic."""
        prompt = f"""You are an expert SEO specialist. Perform keyword research for the topic: "{topic}"

Company context:
- Industry: {self.config.get('industry', 'Technology')}
- Target audience: {self.config.get('target_audience', 'Business professionals')}

Generate exactly {count} keywords in this JSON format:
{{
    "keywords": [
        {{
            "keyword": "exact keyword phrase",
            "estimated_monthly_volume": 1000,
            "difficulty": "low|medium|high",
            "search_intent": "informational|navigational|transactional|commercial",
            "content_type": "blog|landing_page|product_page|guide",
            "priority": "high|medium|low",
            "notes": "brief strategic note"
        }}
    ],
    "topic_clusters": [
        {{
            "pillar": "main topic",
            "cluster_keywords": ["kw1", "kw2", "kw3"]
        }}
    ],
    "content_gaps": ["gap1", "gap2"]
}}

Focus on a mix of:
- High-volume head terms (2-3)
- Medium-volume mid-tail (8-10)  
- Low-competition long-tail keywords (7-10)
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=3000)
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            result = json.loads(json_match.group()) if json_match else {"keywords": [], "topic_clusters": [], "content_gaps": []}

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"keywords_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                "type": "keyword_research",
                "topic": topic,
                "data": result,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"Generated {len(result.get('keywords', []))} keywords for topic: {topic}")
        return result

    async def audit_page_seo(self, url: str, page_content: str = "", meta_title: str = "", meta_description: str = "") -> SEOAuditResult:
        """Perform an AI-powered SEO audit on a page."""
        prompt = f"""You are a senior SEO auditor. Analyze this page and provide a detailed SEO audit.

URL: {url}
Meta Title: {meta_title or 'Not provided'}
Meta Description: {meta_description or 'Not provided'}
Page Content (first 2000 chars): {page_content[:2000] if page_content else 'Not provided'}

Provide your audit as JSON:
{{
    "overall_score": 75,
    "meta_analysis": {{
        "title_score": 80,
        "title_length": 55,
        "title_issues": ["issue1"],
        "description_score": 70,
        "description_length": 145,
        "description_issues": ["issue1"]
    }},
    "content_analysis": {{
        "readability_score": 75,
        "keyword_density": "appropriate|too_low|too_high",
        "heading_structure": "good|needs_improvement|poor",
        "content_length": "sufficient|too_short|too_long",
        "content_issues": ["issue1"]
    }},
    "technical_issues": [
        {{
            "severity": "high|medium|low",
            "issue": "description",
            "fix": "how to fix"
        }}
    ],
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2"
    ],
    "quick_wins": ["quick win 1", "quick win 2"]
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2500)
        try:
            audit_data = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            audit_data = json.loads(json_match.group()) if json_match else {}

        result = SEOAuditResult(
            url=url,
            score=audit_data.get("overall_score", 0),
            issues=[i for i in audit_data.get("technical_issues", [])],
            recommendations=audit_data.get("recommendations", []),
            meta_analysis=audit_data.get("meta_analysis", {}),
            content_analysis=audit_data.get("content_analysis", {}),
            technical_issues=audit_data.get("technical_issues", [])
        )

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"audit_{url.replace('/', '_').replace(':', '')}_{datetime.now().strftime('%Y%m%d%H%M')}",
                "type": "seo_audit",
                "url": url,
                "data": asdict(result),
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"SEO audit complete for {url} — Score: {result.score}/100")
        return result

    async def optimize_content_for_seo(self, content: str, target_keyword: str, secondary_keywords: List[str] = None) -> Dict:
        """Optimize existing content for better SEO performance."""
        secondary = ", ".join(secondary_keywords) if secondary_keywords else "none specified"

        prompt = f"""You are an expert SEO content optimizer. Optimize the following content for the target keyword.

Target Keyword: {target_keyword}
Secondary Keywords: {secondary}
Content to optimize:
---
{content[:4000]}
---

Provide the optimized version as JSON:
{{
    "optimized_title": "SEO-optimized title (50-60 chars)",
    "optimized_meta_description": "Compelling meta description (150-160 chars)",
    "optimized_content": "The full optimized content with proper heading structure, keyword placement, internal linking suggestions marked as [INTERNAL_LINK: anchor text -> suggested page], and improved readability",
    "changes_made": [
        "Description of change 1",
        "Description of change 2"
    ],
    "keyword_placement": {{
        "title": true,
        "first_paragraph": true,
        "headings": ["H2 containing keyword"],
        "body_count": 5,
        "meta_description": true
    }},
    "suggested_schema_markup": "Article|FAQ|HowTo|Product",
    "internal_link_suggestions": [
        {{"anchor_text": "text", "suggested_target": "/page-slug"}}
    ],
    "estimated_improvement": "Brief prediction of ranking improvement"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=4000)
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            result = json.loads(json_match.group()) if json_match else {"error": "Failed to parse optimization"}

        logger.info(f"Content optimized for keyword: {target_keyword}")
        return result

    async def generate_meta_tags(self, page_content: str, target_keyword: str) -> Dict:
        """Generate optimized meta title and description."""
        prompt = f"""Generate 3 variations of SEO-optimized meta tags for this content.

Target Keyword: {target_keyword}
Content summary: {page_content[:1500]}

Return JSON:
{{
    "variations": [
        {{
            "meta_title": "Title here (50-60 chars)",
            "meta_description": "Description here (150-160 chars)",
            "title_length": 55,
            "description_length": 155
        }}
    ],
    "recommended_variation": 1,
    "reasoning": "Why this variation is best"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=1500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"variations": [], "error": "Parse failed"}

    async def generate_schema_markup(self, page_type: str, page_data: Dict) -> str:
        """Generate JSON-LD schema markup for a page."""
        prompt = f"""Generate valid JSON-LD schema markup for a {page_type} page.

Page data:
{json.dumps(page_data, indent=2)}

Return ONLY the complete JSON-LD script tag, properly formatted. 
Include all relevant schema.org properties for maximum rich snippet potential."""

        response = await self.claude.generate(prompt, max_tokens=2000)
        return response

    async def analyze_competitors(self, competitor_urls: List[str], target_keyword: str) -> Dict:
        """Analyze competitor pages for a target keyword."""
        prompt = f"""You are a competitive SEO analyst. Analyze these competitor URLs for the keyword "{target_keyword}":

Competitors:
{chr(10).join(f'- {url}' for url in competitor_urls)}

Provide competitive analysis as JSON:
{{
    "keyword": "{target_keyword}",
    "competitor_analysis": [
        {{
            "url": "competitor url",
            "estimated_strengths": ["strength1", "strength2"],
            "estimated_weaknesses": ["weakness1"],
            "content_approach": "brief description"
        }}
    ],
    "content_gap_opportunities": ["opportunity1", "opportunity2"],
    "recommended_strategy": "How to outrank these competitors",
    "minimum_content_length": 2000,
    "recommended_content_format": "guide|listicle|comparison|case_study",
    "backlink_strategy": "Suggested approach to build authority"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse competitor analysis"}

    async def generate_content_brief(self, keyword: str, content_type: str = "blog") -> Dict:
        """Generate a comprehensive content brief for writers."""
        prompt = f"""Create a detailed SEO content brief for a {content_type} targeting the keyword: "{keyword}"

Company: {self.config.get('company_name', 'Our Company')}
Industry: {self.config.get('industry', 'Technology')}
Audience: {self.config.get('target_audience', 'Business professionals')}

Return as JSON:
{{
    "title_suggestions": ["title1", "title2", "title3"],
    "target_keyword": "{keyword}",
    "secondary_keywords": ["kw1", "kw2", "kw3", "kw4", "kw5"],
    "search_intent": "informational|transactional|commercial",
    "recommended_word_count": 2000,
    "content_outline": [
        {{
            "heading": "H2 heading",
            "subheadings": ["H3 sub1", "H3 sub2"],
            "key_points": ["point1", "point2"],
            "target_word_count": 300
        }}
    ],
    "required_elements": ["element1", "element2"],
    "internal_links": ["suggested internal link targets"],
    "external_reference_topics": ["topic1", "topic2"],
    "cta_suggestions": ["cta1", "cta2"],
    "featured_snippet_opportunity": true,
    "featured_snippet_format": "paragraph|list|table",
    "tone_guidelines": "Specific tone instructions",
    "dos_and_donts": {{
        "dos": ["do1", "do2"],
        "donts": ["dont1", "dont2"]
    }}
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=3000)
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            result = json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"brief_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                "type": "content_brief",
                "keyword": keyword,
                "data": result,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        return result

    async def track_keyword_rankings(self, keywords: List[str]) -> Dict:
        """Track and log keyword ranking positions (placeholder for real API integration)."""
        # In production, integrate with Google Search Console API or SEMrush/Ahrefs API
        tracking_data = {
            "tracked_at": datetime.now(timezone.utc).isoformat(),
            "keywords": []
        }
        for kw in keywords:
            tracking_data["keywords"].append({
                "keyword": kw,
                "status": "tracking_configured",
                "note": "Connect Google Search Console API for real ranking data"
            })

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"rankings_{datetime.now().strftime('%Y%m%d')}",
                "type": "keyword_rankings",
                "data": tracking_data,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        return tracking_data

    async def full_seo_audit(self, urls: List[str]) -> Dict:
        """Run a comprehensive SEO audit across multiple pages."""
        results = {
            "audit_date": datetime.now(timezone.utc).isoformat(),
            "total_pages": len(urls),
            "page_audits": [],
            "summary": {}
        }

        for url in urls:
            audit = await self.audit_page_seo(url)
            results["page_audits"].append(asdict(audit))

        scores = [a["score"] for a in results["page_audits"]]
        results["summary"] = {
            "average_score": sum(scores) / len(scores) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "total_issues": sum(len(a["issues"]) for a in results["page_audits"]),
            "critical_issues": sum(
                1 for a in results["page_audits"]
                for i in a.get("technical_issues", [])
                if i.get("severity") == "high"
            )
        }

        logger.info(f"Full SEO audit complete — {len(urls)} pages, avg score: {results['summary']['average_score']:.0f}")
        return results
