"""
Reporting Engine Module
Generates comprehensive marketing reports (weekly, monthly, quarterly).
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ReportingEngine:
    """AI-powered marketing report generation."""

    def __init__(self, claude_client, db_service=None, storage_service=None, config=None):
        self.claude = claude_client
        self.db = db_service
        self.storage = storage_service
        self.config = config or {}
        self.container_name = "reports"

    async def generate_weekly_report(self, week_data: Dict) -> Dict:
        """Generate a weekly marketing performance report."""
        prompt = f"""Generate a concise weekly marketing report.

Company: {self.config.get('company_name', 'Our Company')}
Week Data:
{json.dumps(week_data, indent=2)[:3000]}

Return as JSON:
{{
    "report_type": "weekly",
    "report_title": "Weekly Marketing Report — [Date Range]",
    "generated_at": "{datetime.now(timezone.utc).isoformat()}",
    "executive_summary": "3-4 sentence summary of the week",
    "highlights": [
        {{"highlight": "Positive achievement", "metric": "Specific number/percentage"}}
    ],
    "challenges": [
        {{"challenge": "Issue encountered", "impact": "How it affected results", "action": "What we're doing about it"}}
    ],
    "channel_performance": {{
        "seo": {{"summary": "Brief overview", "key_metric": "value", "trend": "up|down|stable"}},
        "paid": {{"summary": "Brief overview", "key_metric": "value", "trend": "up|down|stable"}},
        "social": {{"summary": "Brief overview", "key_metric": "value", "trend": "up|down|stable"}},
        "email": {{"summary": "Brief overview", "key_metric": "value", "trend": "up|down|stable"}}
    }},
    "content_published": [
        {{"title": "Content title", "type": "blog|social|email", "performance": "Good|Average|Below expectations"}}
    ],
    "next_week_priorities": [
        {{"priority": 1, "task": "What to focus on", "owner": "Team/person"}}
    ],
    "budget_status": {{
        "spent_this_week": 0,
        "monthly_budget_remaining": 0,
        "on_track": true
    }}
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=3000)
        try:
            report = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            report = json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"weekly_report_{datetime.now().strftime('%Y%m%d')}",
                "type": "weekly_report",
                "data": report,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info("Weekly report generated")
        return report

    async def generate_monthly_report(self, month_data: Dict) -> Dict:
        """Generate a comprehensive monthly marketing report."""
        prompt = f"""Generate a detailed monthly marketing report.

Company: {self.config.get('company_name', 'Our Company')}
Industry: {self.config.get('industry', 'Technology')}
Month Data:
{json.dumps(month_data, indent=2)[:4000]}

Return as JSON:
{{
    "report_type": "monthly",
    "report_title": "Monthly Marketing Report — [Month Year]",
    "generated_at": "{datetime.now(timezone.utc).isoformat()}",
    "executive_summary": "5-6 sentence comprehensive summary",
    "kpi_dashboard": {{
        "total_traffic": {{"value": 0, "change": "+10%", "target": 50000, "on_track": true}},
        "total_leads": {{"value": 0, "change": "+5%", "target": 500, "on_track": true}},
        "total_conversions": {{"value": 0, "change": "+8%", "target": 50, "on_track": false}},
        "revenue": {{"value": 0, "change": "+12%", "target": 100000, "on_track": true}},
        "total_spend": {{"value": 0, "budget": 10000, "utilization": "80%"}},
        "overall_roi": {{"value": "350%", "change": "+15%"}}
    }},
    "channel_deep_dive": {{
        "seo": {{
            "traffic": 0,
            "organic_keywords_ranked": 0,
            "top_pages": ["page1", "page2"],
            "wins": ["win1"],
            "issues": ["issue1"],
            "next_month_focus": "Focus area"
        }},
        "paid_advertising": {{
            "spend": 0,
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "roas": 0,
            "top_campaigns": ["campaign1"],
            "optimization_actions": ["action1"]
        }},
        "social_media": {{
            "followers_gained": 0,
            "total_engagement": 0,
            "top_posts": ["post1"],
            "platform_breakdown": {{}},
            "content_performance": "analysis"
        }},
        "email_marketing": {{
            "emails_sent": 0,
            "avg_open_rate": "0%",
            "avg_click_rate": "0%",
            "unsubscribes": 0,
            "revenue_attributed": 0,
            "top_campaign": "campaign name"
        }}
    }},
    "content_performance": {{
        "pieces_published": 0,
        "top_performing": [
            {{"title": "Content title", "type": "blog", "views": 0, "conversions": 0}}
        ],
        "content_gaps_identified": ["gap1"]
    }},
    "competitor_landscape": "Brief competitive overview and any notable moves",
    "wins_of_the_month": [
        {{"win": "Achievement description", "impact": "Business impact"}}
    ],
    "lessons_learned": [
        {{"lesson": "What we learned", "application": "How we'll apply it"}}
    ],
    "next_month_plan": {{
        "goals": ["goal1", "goal2"],
        "key_initiatives": [
            {{"initiative": "Description", "channel": "channel", "expected_impact": "Expected result"}}
        ],
        "budget_allocation": {{
            "seo": 0, "paid": 0, "social": 0, "email": 0, "content": 0
        }}
    }},
    "risks_and_mitigations": [
        {{"risk": "Identified risk", "likelihood": "high|medium|low", "mitigation": "Plan to address"}}
    ]
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=4096)
        try:
            report = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            report = json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

        if self.db:
            await self.db.upsert_item(self.container_name, {
                "id": f"monthly_report_{datetime.now().strftime('%Y%m')}",
                "type": "monthly_report",
                "data": report,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info("Monthly report generated")
        return report

    async def generate_campaign_report(self, campaign_name: str, campaign_data: Dict) -> Dict:
        """Generate a report for a specific campaign."""
        prompt = f"""Generate a campaign performance report.

Campaign: {campaign_name}
Company: {self.config.get('company_name', 'Our Company')}
Campaign Data:
{json.dumps(campaign_data, indent=2)[:3000]}

Return as JSON:
{{
    "report_type": "campaign",
    "campaign_name": "{campaign_name}",
    "generated_at": "{datetime.now(timezone.utc).isoformat()}",
    "summary": "Campaign performance summary",
    "status": "active|completed|paused",
    "duration": "Start date to end date",
    "goals_vs_actuals": [
        {{"goal": "Goal description", "target": "Target value", "actual": "Actual value", "met": true}}
    ],
    "key_metrics": {{
        "impressions": 0,
        "reach": 0,
        "clicks": 0,
        "ctr": "0%",
        "conversions": 0,
        "conversion_rate": "0%",
        "cost": 0,
        "cpc": 0,
        "cpa": 0,
        "roas": 0,
        "revenue": 0
    }},
    "audience_insights": {{
        "top_demographics": "Who responded best",
        "top_locations": "Best performing regions",
        "top_devices": "Device breakdown"
    }},
    "creative_performance": [
        {{"creative": "Creative name/ID", "ctr": "0%", "conversions": 0, "verdict": "winner|loser|average"}}
    ],
    "what_worked": ["Success factor 1"],
    "what_didnt_work": ["Failure factor 1"],
    "recommendations": ["Recommendation for future campaigns"],
    "repeat_recommendation": "Should this campaign be repeated? How?"
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=3000)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {"error": "Parse failed"}

    async def generate_executive_dashboard(self, all_data: Dict) -> Dict:
        """Generate a C-level executive marketing dashboard summary."""
        prompt = f"""Create a C-level executive marketing dashboard summary. Keep it high-level and business-focused.

Company: {self.config.get('company_name', 'Our Company')}
All Marketing Data:
{json.dumps(all_data, indent=2)[:3000]}

Return as JSON:
{{
    "dashboard_title": "Marketing Performance Dashboard",
    "period": "Current period",
    "generated_at": "{datetime.now(timezone.utc).isoformat()}",
    "headline_metric": {{
        "label": "Revenue from Marketing",
        "value": "$0",
        "change": "+10% vs last period"
    }},
    "top_kpis": [
        {{"label": "KPI Name", "value": "Value", "trend": "up|down|stable", "status": "green|yellow|red"}}
    ],
    "marketing_roi": "Overall ROI figure",
    "pipeline_contribution": "Marketing's contribution to sales pipeline",
    "channel_summary": [
        {{"channel": "Channel name", "spend": 0, "revenue": 0, "roi": "0%", "status": "green|yellow|red"}}
    ],
    "three_things_to_know": [
        "Most important insight 1",
        "Most important insight 2",
        "Most important insight 3"
    ],
    "decisions_needed": [
        {{"decision": "What needs to be decided", "options": ["Option A", "Option B"], "recommendation": "Recommended option"}}
    ]
}}
Return ONLY valid JSON."""

        response = await self.claude.generate(prompt, max_tokens=2500)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Parse failed"}
