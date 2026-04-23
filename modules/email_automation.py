"""
Email Automation Module
AI-powered email campaign creation, sequence management, and performance tracking.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class EmailTemplate:
    name: str
    subject: str
    body_html: str
    body_text: str
    category: str = "marketing"
    tags: List[str] = field(default_factory=list)


@dataclass
class EmailCampaign:
    campaign_id: str
    name: str
    subject: str
    body_html: str
    recipients_count: int = 0
    status: str = "draft"
    scheduled_at: Optional[str] = None
    sent_at: Optional[str] = None
    metrics: Dict = field(default_factory=dict)


class EmailAutomation:
    """AI-powered email marketing automation engine."""

    def __init__(self, claude_client, db_service=None, email_service=None, config=None):
        self.claude = claude_client
        self.db = db_service
        self.email_service = email_service
        self.config = config or {}
        self.container_name = "email_campaigns"

    async def generate_email_campaign(
        self,
        campaign_goal: str,
        audience_segment: str,
        key_message: str,
        email_type: str = "promotional",
        num_variations: int = 2
    ) -> Dict:
        """Generate a complete email campaign with subject lines, body, and CTAs."""
        prompt = f"""You are an expert email marketer. Create a high-converting email campaign.

Campaign Goal: {campaign_goal}
Audience Segment: {audience_segment}
Key Message: {key_message}
Email Type: {email_type}
Company: {self.config.get('company_name', 'Our Company')}
Brand Voice: {self.config.get('brand_voice', 'Professional')}

Generate {num_variations} email variations as JSON:
{{
    "campaign_name": "Campaign name",
    "goal": "{campaign_goal}",
    "audience": "{audience_segment}",
    "variations": [
        {{
            "variation_id": "A",
            "subject_line": "Compelling subject line (40-60 chars)",
            "preview_text": "Preview text that shows in inbox (80-100 chars)",
            "body_html": "Full HTML email body with inline styles. Use tables for layout. Include header, hero section, body content, CTA button, and footer. Use placeholder images as [IMAGE: description].",
            "body_text": "Plain text version of the email",
            "cta_text": "Button text",
            "cta_url": "https://yourcompany.com/landing-page",
            "personalization_tokens": ["first_name", "company_name"],
            "estimated_open_rate": "25%",
            "rationale": "Why this variation should work"
        }}
    ],
    "subject_line_alternatives": [
        "Alternative subject 1",
        "Alternative subject 2",
        "Alternative subject 3"
    ],
    "send_time_recommendation": "Tuesday 10:00 AM",
    "send_time_reasoning": "Why this time",
    "ab_test_plan": {{
        "test_element": "subject_line",
        "sample_size": "20%",
        "winner_criteria": "open_rate",
        "duration_hours": 4
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
                "id": f"campaign_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": "email_campaign",
                "data": campaign,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"Generated email campaign: {campaign.get('campaign_name', 'Unknown')}")
        return campaign

    async def generate_drip_sequence(
        self,
        sequence_name: str,
        trigger: str,
        num_emails: int = 5,
        days_span: int = 14,
        goal: str = "nurture"
    ) -> Dict:
        """Generate a complete automated drip email sequence."""
        prompt = f"""Create a {num_emails}-email drip sequence over {days_span} days.

Sequence Name: {sequence_name}
Trigger: {trigger}
Goal: {goal}
Company: {self.config.get('company_name', 'Our Company')}
Product/Service: {self.config.get('key_products', 'Our solution')}
Audience: {self.config.get('target_audience', 'Business professionals')}

Return as JSON:
{{
    "sequence_name": "{sequence_name}",
    "trigger": "{trigger}",
    "goal": "{goal}",
    "total_emails": {num_emails},
    "emails": [
        {{
            "email_number": 1,
            "send_delay_days": 0,
            "send_time": "10:00 AM",
            "purpose": "Welcome / First value delivery",
            "subject_line": "Subject line",
            "preview_text": "Preview text",
            "body_text": "Complete email body in plain text format with clear sections",
            "cta_text": "CTA button text",
            "cta_url": "/link",
            "conditional_logic": "Send to all / Only if opened previous / Only if clicked",
            "key_elements": ["social proof", "value proposition"]
        }}
    ],
    "exit_conditions": [
        "Subscriber purchases product",
        "Subscriber unsubscribes"
    ],
    "branch_logic": [
        {{
            "condition": "If email 2 not opened within 48 hours",
            "action": "Send re-engagement variant of email 2"
        }}
    ],
    "sequence_kpis": {{
        "target_open_rate": "35%",
        "target_click_rate": "5%",
        "target_conversion_rate": "2%"
    }},
    "optimization_notes": "Tips for improving sequence over time"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=4096)
        try:
            sequence = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            sequence = json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"sequence_{sequence_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                "type": "drip_sequence",
                "data": sequence,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"Generated drip sequence: {sequence_name} ({num_emails} emails)")
        return sequence

    async def generate_newsletter(
        self,
        topics: List[str],
        newsletter_name: str = "Weekly Digest",
        tone: str = "informative"
    ) -> Dict:
        """Generate a newsletter from a list of topics."""
        prompt = f"""Create a compelling newsletter.

Newsletter Name: {newsletter_name}
Tone: {tone}
Company: {self.config.get('company_name', 'Our Company')}
Topics to cover:
{chr(10).join(f'- {t}' for t in topics)}

Return as JSON:
{{
    "newsletter_name": "{newsletter_name}",
    "subject_line": "Subject line",
    "preview_text": "Preview text",
    "sections": [
        {{
            "section_title": "Section heading",
            "content": "Section content (2-3 paragraphs)",
            "cta_text": "Read more",
            "cta_url": "/link"
        }}
    ],
    "intro_text": "Opening paragraph",
    "closing_text": "Sign-off paragraph",
    "social_sharing_text": "Text for social sharing",
    "plain_text_version": "Complete plain text version"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=3500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

    async def optimize_subject_lines(self, subject_lines: List[str], audience: str = "") -> Dict:
        """Analyze and optimize email subject lines."""
        prompt = f"""You are an email marketing expert. Analyze and optimize these subject lines.

Audience: {audience or self.config.get('target_audience', 'Business professionals')}
Industry: {self.config.get('industry', 'Technology')}

Subject lines to analyze:
{chr(10).join(f'{i+1}. {s}' for i, s in enumerate(subject_lines))}

Return as JSON:
{{
    "analysis": [
        {{
            "original": "Original subject line",
            "score": 75,
            "strengths": ["strength1"],
            "weaknesses": ["weakness1"],
            "optimized_version": "Improved subject line",
            "optimized_score": 88,
            "reasoning": "Why the optimized version is better"
        }}
    ],
    "best_practices_applied": ["practice1", "practice2"],
    "general_tips": ["tip1", "tip2"],
    "power_words_suggested": ["word1", "word2"],
    "recommended_winner": 1
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Parse failed"}

    async def generate_segmentation_strategy(self, subscriber_data_summary: str) -> Dict:
        """Generate email list segmentation strategy."""
        prompt = f"""Create an email list segmentation strategy.

Company: {self.config.get('company_name', 'Our Company')}
Industry: {self.config.get('industry', 'Technology')}
Subscriber Data Summary: {subscriber_data_summary}

Return as JSON:
{{
    "segments": [
        {{
            "segment_name": "Segment Name",
            "criteria": "How to identify these subscribers",
            "estimated_percentage": "20%",
            "content_strategy": "What content to send them",
            "frequency": "How often to email",
            "sample_subject_lines": ["subject1", "subject2"],
            "automation_triggers": ["trigger1"]
        }}
    ],
    "lifecycle_stages": [
        {{
            "stage": "New Subscriber",
            "email_approach": "Welcome series",
            "transition_trigger": "Clicks 3+ emails"
        }}
    ],
    "re_engagement_plan": {{
        "inactive_definition": "No opens in 90 days",
        "strategy": "Re-engagement approach",
        "sunset_policy": "When to remove from list"
    }}
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Parse failed"}

    async def analyze_email_performance(self, campaign_metrics: List[Dict]) -> Dict:
        """Analyze email campaign performance and generate recommendations."""
        prompt = f"""Analyze these email campaign metrics and provide actionable insights.

Campaign Metrics:
{json.dumps(campaign_metrics[:15], indent=2)}

Industry: {self.config.get('industry', 'Technology')}

Return as JSON:
{{
    "summary": {{
        "campaigns_analyzed": 0,
        "avg_open_rate": "0%",
        "avg_click_rate": "0%",
        "avg_unsubscribe_rate": "0%",
        "trend": "improving|stable|declining",
        "industry_benchmark_comparison": "above|at|below average"
    }},
    "top_performers": [
        {{
            "campaign_name": "name",
            "key_metric": "45% open rate",
            "success_factor": "Why it worked"
        }}
    ],
    "improvement_areas": [
        {{
            "area": "Subject lines",
            "current_performance": "22% open rate",
            "target": "30% open rate",
            "action_items": ["action1", "action2"]
        }}
    ],
    "recommendations": [
        "Specific recommendation 1",
        "Specific recommendation 2"
    ],
    "next_month_focus": "Key area to focus on"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Parse failed"}

    async def send_campaign(self, campaign: EmailCampaign, recipients: List[Dict]) -> Dict:
        """Send an email campaign through Azure Communication Services."""
        if not self.email_service:
            logger.warning("Email service not configured. Returning preview only.")
            return {
                "status": "preview_only",
                "campaign_id": campaign.campaign_id,
                "recipients_count": len(recipients),
                "message": "Email service not configured. Connect Azure Communication Services to send."
            }

        results = {"sent": 0, "failed": 0, "errors": []}
        for recipient in recipients:
            try:
                await self.email_service.send_email(
                    to_address=recipient.get("email"),
                    subject=campaign.subject,
                    html_content=campaign.body_html,
                    sender_address=self.config.get("sender_address", "marketing@yourcompany.com")
                )
                results["sent"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"email": recipient.get("email", "unknown"), "error": str(e)})

        results["total"] = len(recipients)
        results["success_rate"] = f"{(results['sent'] / len(recipients) * 100):.1f}%" if recipients else "0%"

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"send_log_{campaign.campaign_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": "send_log",
                "campaign_id": campaign.campaign_id,
                "results": results,
                "sent_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"Campaign sent: {results['sent']}/{results['total']} emails delivered")
        return results
