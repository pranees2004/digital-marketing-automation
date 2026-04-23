"""
Ad Campaign Manager Module
AI-powered paid advertising campaign creation and optimization for Google Ads and Meta Ads.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class AdCreative:
    headline: str
    description: str
    cta: str
    image_description: str = ""
    platform: str = "google"
    ad_type: str = "search"
    landing_page: str = ""


class AdCampaignManager:
    """AI-powered paid advertising campaign management."""

    def __init__(self, claude_client, db_service=None, config=None):
        self.claude = claude_client
        self.db = db_service
        self.config = config or {}
        self.container_name = "ad_campaigns"

    async def create_google_search_campaign(
        self,
        product_service: str,
        target_keywords: List[str],
        daily_budget: float,
        landing_page: str = "",
        goal: str = "conversions"
    ) -> Dict:
        """Generate a complete Google Search Ads campaign structure."""
        prompt = f"""You are a Google Ads expert. Create a complete search campaign structure.

Product/Service: {product_service}
Target Keywords: {', '.join(target_keywords)}
Daily Budget: ${daily_budget}
Landing Page: {landing_page or 'https://yourcompany.com/landing'}
Campaign Goal: {goal}
Company: {self.config.get('company_name', 'Our Company')}

Return as JSON:
{{
    "campaign_name": "Campaign name",
    "campaign_type": "Search",
    "goal": "{goal}",
    "daily_budget": {daily_budget},
    "bidding_strategy": "Maximize Conversions|Target CPA|Target ROAS|Manual CPC",
    "target_cpa": 25.00,
    "ad_groups": [
        {{
            "ad_group_name": "Ad Group Name",
            "theme": "Theme description",
            "keywords": [
                {{"keyword": "keyword phrase", "match_type": "exact|phrase|broad", "estimated_cpc": 2.50}}
            ],
            "negative_keywords": ["negative kw1", "negative kw2"],
            "ads": [
                {{
                    "headline_1": "30 chars max",
                    "headline_2": "30 chars max",
                    "headline_3": "30 chars max",
                    "description_1": "90 chars max",
                    "description_2": "90 chars max",
                    "display_url_path_1": "path1",
                    "display_url_path_2": "path2",
                    "final_url": "{landing_page or 'https://yourcompany.com/landing'}"
                }}
            ],
            "responsive_search_ad": {{
                "headlines": ["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8"],
                "descriptions": ["d1", "d2", "d3", "d4"],
                "pin_suggestions": "Any headline/description pinning"
            }}
        }}
    ],
    "campaign_negative_keywords": ["free", "cheap", "diy"],
    "extensions": {{
        "sitelinks": [
            {{"text": "Link text", "url": "/page", "description": "Sitelink desc"}}
        ],
        "callouts": ["Callout 1", "Callout 2", "Callout 3"],
        "structured_snippets": {{
            "header": "Services|Types|Features",
            "values": ["value1", "value2", "value3"]
        }},
        "call_extension": "+1-XXX-XXX-XXXX"
    }},
    "audience_targeting": {{
        "demographics": "Age, gender targeting",
        "in_market_audiences": ["audience1"],
        "custom_audiences": "Custom audience suggestions"
    }},
    "optimization_tips": [
        "Tip 1",
        "Tip 2"
    ],
    "expected_metrics": {{
        "estimated_impressions_daily": 1000,
        "estimated_clicks_daily": 50,
        "estimated_ctr": "5%",
        "estimated_conversions_daily": 5
    }}
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=4096)
        try:
            campaign = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            campaign = json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"google_campaign_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": "google_search_campaign",
                "data": campaign,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"Google Search campaign created: {campaign.get('campaign_name', 'Unknown')}")
        return campaign

    async def create_meta_ad_campaign(
        self,
        product_service: str,
        objective: str = "conversions",
        daily_budget: float = 50.0,
        target_audience_description: str = "",
        platforms: List[str] = None
    ) -> Dict:
        """Generate a complete Meta (Facebook/Instagram) ad campaign."""
        platforms = platforms or ["facebook", "instagram"]

        prompt = f"""You are a Meta Ads expert. Create a complete Facebook/Instagram ad campaign.

Product/Service: {product_service}
Objective: {objective}
Daily Budget: ${daily_budget}
Target Audience: {target_audience_description or self.config.get('target_audience', 'Business professionals')}
Placement: {', '.join(platforms)}
Company: {self.config.get('company_name', 'Our Company')}

Return as JSON:
{{
    "campaign_name": "Campaign name",
    "objective": "{objective}",
    "daily_budget": {daily_budget},
    "ad_sets": [
        {{
            "ad_set_name": "Ad Set Name",
            "audience": {{
                "age_min": 25,
                "age_max": 55,
                "gender": "all",
                "locations": ["United States"],
                "interests": ["interest1", "interest2"],
                "behaviors": ["behavior1"],
                "custom_audiences": "Suggestion for custom audience",
                "lookalike_suggestion": "1% lookalike of customers"
            }},
            "placements": {{
                "automatic": false,
                "manual": ["Facebook Feed", "Instagram Feed", "Instagram Stories", "Facebook Reels"]
            }},
            "optimization_goal": "conversions|landing_page_views|link_clicks",
            "bid_strategy": "lowest_cost|cost_cap|bid_cap",
            "ads": [
                {{
                    "ad_name": "Ad Name",
                    "format": "single_image|carousel|video",
                    "primary_text": "Main ad copy (125 chars recommended)",
                    "headline": "Headline text (40 chars)",
                    "description": "Link description (30 chars)",
                    "cta_button": "Learn More|Sign Up|Shop Now|Get Offer",
                    "image_description": "Detailed description of the image to create",
                    "landing_page": "https://yourcompany.com/offer"
                }}
            ]
        }}
    ],
    "carousel_ads": [
        {{
            "name": "Carousel Ad Name",
            "cards": [
                {{
                    "headline": "Card headline",
                    "description": "Card description",
                    "image_description": "Image description",
                    "link": "/page"
                }}
            ]
        }}
    ],
    "retargeting_strategy": {{
        "website_visitors": "Retarget last 30 day visitors",
        "engaged_users": "Retarget social media engaged users",
        "email_list": "Upload customer email list"
    }},
    "ab_test_plan": {{
        "variable": "creative|audience|placement",
        "variations": 3,
        "budget_split": "equal",
        "duration_days": 7
    }},
    "estimated_results": {{
        "daily_reach": 5000,
        "daily_clicks": 100,
        "estimated_cpc": 0.50,
        "estimated_cpm": 10.00
    }}
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=4096)
        try:
            campaign = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            campaign = json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"meta_campaign_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": "meta_ad_campaign",
                "data": campaign,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"Meta ad campaign created: {campaign.get('campaign_name', 'Unknown')}")
        return campaign

    async def generate_ad_copy_variations(
        self,
        product: str,
        platform: str = "google",
        num_variations: int = 5,
        tone: str = "professional"
    ) -> Dict:
        """Generate multiple ad copy variations for A/B testing."""
        prompt = f"""Generate {num_variations} ad copy variations for {platform} ads.

Product/Service: {product}
Tone: {tone}
Company: {self.config.get('company_name', 'Our Company')}
USP: {self.config.get('unique_value_proposition', 'Leading solution in the market')}

Return as JSON:
{{
    "variations": [
        {{
            "variation_id": "V1",
            "headline": "Headline text",
            "description": "Ad description",
            "cta": "Call to action",
            "emotional_trigger": "urgency|curiosity|fear_of_missing_out|social_proof|benefit",
            "estimated_effectiveness": "high|medium|low",
            "best_for": "cold_audience|warm_audience|retargeting"
        }}
    ],
    "testing_priority": ["V1", "V3", "V2"],
    "testing_rationale": "Why to test in this order"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Parse failed"}

    async def optimize_campaign(self, campaign_data: Dict, performance_metrics: Dict) -> Dict:
        """Analyze campaign performance and suggest optimizations."""
        prompt = f"""You are a paid advertising optimization expert. Analyze this campaign and suggest improvements.

Campaign Data:
{json.dumps(campaign_data, indent=2)[:2000]}

Performance Metrics:
{json.dumps(performance_metrics, indent=2)[:2000]}

Return as JSON:
{{
    "performance_assessment": {{
        "overall_rating": "excellent|good|needs_improvement|poor",
        "roas": "Return on ad spend",
        "vs_benchmark": "above|at|below industry average"
    }},
    "immediate_actions": [
        {{
            "action": "Specific action to take",
            "expected_impact": "high|medium|low",
            "area": "bidding|targeting|creative|budget",
            "details": "Step by step instructions"
        }}
    ],
    "budget_recommendations": {{
        "current_daily": 0,
        "recommended_daily": 0,
        "reallocation": "How to redistribute budget across ad sets"
    }},
    "creative_recommendations": [
        "Creative recommendation 1"
    ],
    "audience_recommendations": [
        "Audience recommendation 1"
    ],
    "keywords_to_add": ["keyword1"],
    "keywords_to_pause": ["keyword1"],
    "projected_improvement": "Expected improvement with changes"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=3000)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Parse failed"}

    async def generate_landing_page_copy(self, product: str, ad_campaign_context: str = "") -> Dict:
        """Generate landing page copy that aligns with ad campaigns."""
        prompt = f"""Create high-converting landing page copy for a paid ad campaign.

Product/Service: {product}
Ad Campaign Context: {ad_campaign_context or 'General product promotion'}
Company: {self.config.get('company_name', 'Our Company')}
Target Audience: {self.config.get('target_audience', 'Business professionals')}

Return as JSON:
{{
    "headline": "Main headline (10 words max)",
    "subheadline": "Supporting subheadline",
    "hero_section": {{
        "text": "Hero section body copy",
        "cta_text": "Primary CTA button text",
        "trust_badges": ["badge1", "badge2"]
    }},
    "problem_section": {{
        "heading": "Section heading",
        "pain_points": ["pain1", "pain2", "pain3"]
    }},
    "solution_section": {{
        "heading": "Section heading",
        "benefits": [
            {{"benefit": "Benefit title", "description": "Benefit description"}}
        ]
    }},
    "social_proof": {{
        "testimonial_templates": [
            {{"quote": "Testimonial text", "attribution": "Name, Title, Company"}}
        ],
        "stats": ["100+ companies trust us", "4.9/5 rating"]
    }},
    "faq_section": [
        {{"question": "FAQ question", "answer": "FAQ answer"}}
    ],
    "final_cta": {{
        "heading": "Final CTA section heading",
        "text": "Urgency-driven copy",
        "button_text": "CTA button text"
    }},
    "seo_meta": {{
        "title": "Page title",
        "description": "Meta description"
    }},
    "message_match_score": "How well this matches typical ad copy (high/medium/low)"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=3500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

    async def calculate_budget_allocation(self, total_monthly_budget: float, goals: Dict) -> Dict:
        """AI-powered budget allocation across advertising channels."""
        prompt = f"""You are a media buying expert. Allocate this advertising budget optimally.

Total Monthly Budget: ${total_monthly_budget}
Business Goals: {json.dumps(goals)}
Industry: {self.config.get('industry', 'Technology')}
Target Audience: {self.config.get('target_audience', 'Business professionals')}

Return as JSON:
{{
    "total_budget": {total_monthly_budget},
    "allocation": [
        {{
            "channel": "Google Search Ads",
            "budget": 0,
            "percentage": "0%",
            "rationale": "Why this allocation",
            "expected_results": {{
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "estimated_cpa": 0
            }}
        }}
    ],
    "testing_budget": {{
        "amount": 0,
        "percentage": "10%",
        "suggested_tests": ["test1", "test2"]
    }},
    "scaling_plan": {{
        "month_2_budget": 0,
        "month_3_budget": 0,
        "scaling_criteria": "When to increase budget"
    }},
    "risk_assessment": "Budget risk analysis"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Parse failed"}
