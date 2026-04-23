"""
Reporting Module — Generates comprehensive marketing reports
using Claude AI for narrative insights and analysis.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates marketing reports:
    - Daily performance snapshots
    - Weekly summaries with trends
    - Monthly comprehensive reports
    - Custom campaign reports
    - Executive dashboards
    """

    def __init__(self, claude_client=None, analytics_engine=None, db_service=None, config=None):
        self.claude = claude_client
        self.analytics = analytics_engine
        self.db = db_service
        self.config = config
        self._mock_mode = claude_client is None
        logger.info(f"ReportGenerator initialized (mock_mode={self._mock_mode})")

    # ===== REPORT GENERATORS =====

    async def daily_report(self) -> Dict[str, Any]:
        """Generate daily performance snapshot"""
        logger.info("Generating daily report...")

        dashboard = await self.analytics.get_dashboard_data() if self.analytics else self._mock_dashboard()

        report = {
            "report_type": "daily",
            "generated_at": datetime.now().isoformat(),
            "period": datetime.now().strftime("%Y-%m-%d"),
            "company": self.config.company.name if self.config else "Company",
            "kpis": dashboard.get("kpis", {}),
            "kpi_changes": dashboard.get("kpi_changes", {}),
            "channel_breakdown": dashboard.get("channel_breakdown", {}),
            "alerts": dashboard.get("alerts", []),
        }

        # Generate AI narrative
        narrative = await self._generate_narrative(report, "daily")
        report["narrative"] = narrative

        return report

    async def weekly_report(self) -> Dict[str, Any]:
        """Generate weekly summary report with trends"""
        logger.info("Generating weekly report...")

        analysis = {}
        trends = {}
        funnel = {}

        if self.analytics:
            analysis = await self.analytics.analyze_performance(7)
            trends = await self.analytics.analyze_trends(14)
            funnel = await self.analytics.funnel_analysis()
        else:
            analysis = self._mock_analysis()
            trends = self._mock_trends()
            funnel = self._mock_funnel()

        report = {
            "report_type": "weekly",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "end": datetime.now().strftime("%Y-%m-%d"),
            },
            "company": self.config.company.name if self.config else "Company",
            "performance_analysis": analysis,
            "trends": trends,
            "funnel_analysis": funnel,
            "content_performance": await self._get_content_performance(),
            "social_performance": await self._get_social_performance(),
            "email_performance": await self._get_email_performance(),
            "paid_performance": await self._get_paid_performance(),
        }

        narrative = await self._generate_narrative(report, "weekly")
        report["executive_summary"] = narrative

        return report

    async def monthly_report(self) -> Dict[str, Any]:
        """Generate comprehensive monthly report"""
        logger.info("Generating monthly report...")

        analysis = {}
        trends = {}
        funnel = {}
        competitors = {}

        if self.analytics:
            analysis = await self.analytics.analyze_performance(30)
            trends = await self.analytics.analyze_trends(30)
            funnel = await self.analytics.funnel_analysis()
            competitors = await self.analytics.competitor_analysis()
        else:
            analysis = self._mock_analysis()
            trends = self._mock_trends()
            funnel = self._mock_funnel()
            competitors = self._mock_competitor_data()

        report = {
            "report_type": "monthly",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "month": datetime.now().strftime("%B %Y"),
                "start": datetime.now().replace(day=1).strftime("%Y-%m-%d"),
                "end": datetime.now().strftime("%Y-%m-%d"),
            },
            "company": self.config.company.name if self.config else "Company",
            "performance_analysis": analysis,
            "trends": trends,
            "funnel_analysis": funnel,
            "competitor_analysis": competitors,
            "budget_analysis": await self._get_budget_analysis(),
            "content_performance": await self._get_content_performance(),
            "seo_performance": await self._get_seo_performance(),
            "social_performance": await self._get_social_performance(),
            "email_performance": await self._get_email_performance(),
            "paid_performance": await self._get_paid_performance(),
            "goals_tracking": await self._get_goals_tracking(),
            "next_month_plan": await self._generate_next_month_plan(),
        }

        narrative = await self._generate_narrative(report, "monthly")
        report["executive_summary"] = narrative

        return report

    async def campaign_report(self, campaign_id: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Generate report for a specific campaign"""
        logger.info(f"Generating campaign report: {campaign_id}")

        if campaign_data is None:
            campaign_data = {
                "id": campaign_id,
                "name": f"Campaign {campaign_id}",
                "channel": "multi-channel",
                "start_date": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "budget": 5000.00,
                "spend": 4250.00,
                "impressions": 125000,
                "clicks": 5400,
                "conversions": 185,
                "revenue": 12800.00,
            }

        metrics = {
            "ctr": round(campaign_data["clicks"] / campaign_data["impressions"] * 100, 2) if campaign_data.get("impressions") else 0,
            "conversion_rate": round(campaign_data["conversions"] / campaign_data["clicks"] * 100, 2) if campaign_data.get("clicks") else 0,
            "cpc": round(campaign_data["spend"] / campaign_data["clicks"], 2) if campaign_data.get("clicks") else 0,
            "cpa": round(campaign_data["spend"] / campaign_data["conversions"], 2) if campaign_data.get("conversions") else 0,
            "roas": round(campaign_data["revenue"] / campaign_data["spend"], 2) if campaign_data.get("spend") else 0,
            "budget_utilization": round(campaign_data["spend"] / campaign_data["budget"] * 100, 1) if campaign_data.get("budget") else 0,
        }

        report = {
            "report_type": "campaign",
            "generated_at": datetime.now().isoformat(),
            "campaign": campaign_data,
            "calculated_metrics": metrics,
        }

        narrative = await self._generate_narrative(report, "campaign")
        report["analysis"] = narrative

        return report

    # ===== FORMAT CONVERTERS =====

    def to_html(self, report: Dict[str, Any]) -> str:
        """Convert report to HTML format"""
        report_type = report.get("report_type", "general")
        company = report.get("company", "Company")
        generated = report.get("generated_at", datetime.now().isoformat())

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{company} - {report_type.title()} Marketing Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px; margin-bottom: 24px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
        .header p {{ opacity: 0.9; font-size: 14px; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .card h2 {{ color: #667eea; margin-bottom: 16px; font-size: 20px; border-bottom: 2px solid #f0f0f0; padding-bottom: 8px; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }}
        .kpi-box {{ background: #f8f9ff; border-radius: 8px; padding: 16px; text-align: center; }}
        .kpi-box .value {{ font-size: 28px; font-weight: 700; color: #667eea; }}
        .kpi-box .label {{ font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; }}
        .kpi-box .change {{ font-size: 13px; margin-top: 4px; }}
        .change.up {{ color: #22c55e; }}
        .change.down {{ color: #ef4444; }}
        .alert {{ padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; font-size: 14px; }}
        .alert.warning {{ background: #fff7ed; border-left: 4px solid #f59e0b; }}
        .alert.info {{ background: #eff6ff; border-left: 4px solid #3b82f6; }}
        .alert.success {{ background: #f0fdf4; border-left: 4px solid #22c55e; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #f0f0f0; font-size: 14px; }}
        th {{ background: #f8f9ff; font-weight: 600; color: #555; }}
        .narrative {{ background: #fefce8; border-radius: 8px; padding: 20px; font-style: italic; line-height: 1.8; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 32px; padding: 16px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📊 {company} — {report_type.title()} Marketing Report</h1>
        <p>Generated: {generated[:19].replace('T', ' ')}</p>
    </div>
"""

        # KPIs
        kpis = report.get("kpis", {})
        changes = report.get("kpi_changes", {})
        if kpis:
            html += '<div class="card"><h2>📈 Key Performance Indicators</h2><div class="kpi-grid">'
            kpi_display = [
                ("Website Visits", kpis.get("total_website_visits", 0), changes.get("website_visits_change", 0)),
                ("Leads", kpis.get("total_leads", 0), changes.get("leads_change", 0)),
                ("Conversions", kpis.get("total_conversions", 0), changes.get("conversions_change", 0)),
                ("Revenue", f"${kpis.get('total_revenue', 0):,.2f}", changes.get("revenue_change", 0)),
                ("Ad Spend", f"${kpis.get('total_spend', 0):,.2f}", changes.get("spend_change", 0)),
                ("ROAS", f"{kpis.get('overall_roas', 0)}x", None),
            ]
            for label, value, change in kpi_display:
                change_html = ""
                if change is not None:
                    cls = "up" if change >= 0 else "down"
                    arrow = "↑" if change >= 0 else "↓"
                    change_html = f'<div class="change {cls}">{arrow} {abs(change)}%</div>'
                html += f'<div class="kpi-box"><div class="label">{label}</div><div class="value">{value}</div>{change_html}</div>'
            html += "</div></div>"

        # Alerts
        alerts = report.get("alerts", [])
        if alerts:
            html += '<div class="card"><h2>🔔 Alerts</h2>'
            for alert in alerts:
                level = alert.get("level", "info")
                msg = alert.get("message", "")
                html += f'<div class="alert {level}">{msg}</div>'
            html += "</div>"

        # Narrative
        narrative = report.get("narrative") or report.get("executive_summary", "")
        if narrative:
            html += f'<div class="card"><h2>🤖 AI Analysis</h2><div class="narrative">{narrative}</div></div>'

        # Performance analysis
        perf = report.get("performance_analysis", {})
        channel_perf = perf.get("channel_performance", [])
        if channel_perf:
            html += '<div class="card"><h2>📊 Channel Performance</h2><table><tr><th>Channel</th><th>Score</th><th>Trend</th><th>Key Metric</th><th>Insight</th></tr>'
            for ch in channel_perf:
                trend_icon = {"up": "📈", "down": "📉", "stable": "➡️"}.get(ch.get("trend", ""), "")
                html += f"<tr><td><strong>{ch.get('channel', '')}</strong></td><td>{ch.get('score', '')}/100</td><td>{trend_icon} {ch.get('trend', '')}</td><td>{ch.get('key_metric', '')}</td><td>{ch.get('insight', '')}</td></tr>"
            html += "</table></div>"

        # Recommendations
        recs = perf.get("recommendations", [])
        if recs:
            html += '<div class="card"><h2>💡 Recommendations</h2><table><tr><th>Priority</th><th>Channel</th><th>Action</th><th>Impact</th><th>Effort</th></tr>'
            for rec in recs:
                priority_colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}
                color = priority_colors.get(rec.get("priority", ""), "#888")
                html += f"<tr><td><span style='color:{color};font-weight:700;'>{rec.get('priority', '').upper()}</span></td><td>{rec.get('channel', '')}</td><td>{rec.get('action', '')}</td><td>{rec.get('expected_impact', '')}</td><td>{rec.get('effort', '')}</td></tr>"
            html += "</table></div>"

        html += f"""
    <div class="footer">
        <p>Generated by Digital Marketing Automation System | Powered by Claude AI + Azure</p>
        <p>{company} &copy; {datetime.now().year}</p>
    </div>
</div>
</body>
</html>"""

        return html

    def to_json(self, report: Dict[str, Any]) -> str:
        """Convert report to JSON string"""
        return json.dumps(report, indent=2, default=str)

    def to_markdown(self, report: Dict[str, Any]) -> str:
        """Convert report to Markdown format"""
        report_type = report.get("report_type", "general")
        company = report.get("company", "Company")

        md = f"# {company} — {report_type.title()} Marketing Report\n\n"
        md += f"**Generated:** {report.get('generated_at', '')[:19]}\n\n"

        # KPIs
        kpis = report.get("kpis", {})
        if kpis:
            md += "## 📈 Key Performance Indicators\n\n"
            md += "| Metric | Value |\n|--------|-------|\n"
            for key, value in kpis.items():
                label = key.replace("_", " ").title()
                md += f"| {label} | {value} |\n"
            md += "\n"

        # Narrative
        narrative = report.get("narrative") or report.get("executive_summary", "")
        if narrative:
            md += f"## 🤖 AI Analysis\n\n{narrative}\n\n"

        # Alerts
        alerts = report.get("alerts", [])
        if alerts:
            md += "## 🔔 Alerts\n\n"
            for alert in alerts:
                icon = {"warning": "⚠️", "info": "ℹ️", "success": "✅"}.get(alert.get("level"), "")
                md += f"- {icon} {alert.get('message', '')}\n"
            md += "\n"

        return md

    # ===== AI NARRATIVE GENERATION =====

    async def _generate_narrative(self, report: Dict, report_type: str) -> str:
        """Use Claude to generate a narrative summary"""
        if self._mock_mode:
            return self._mock_narrative(report_type)

        prompt = f"""You are a senior marketing analyst writing a {report_type} report for
{self.config.company.name if self.config else 'the company'}.

Based on this data, write a concise executive summary (3-5 sentences) that:
1. Highlights the most important performance trends
2. Calls out wins and concerns
3. Recommends immediate actions

DATA:
{json.dumps(report, indent=2, default=str)[:3000]}

Write in professional but accessible tone. Be specific with numbers."""

        return await self.claude.generate(prompt=prompt, temperature=0.4, max_tokens=500)

    async def _generate_next_month_plan(self) -> Dict[str, Any]:
        """Generate AI-powered plan for next month"""
        return {
            "goals": [
                "Increase organic traffic by 10%",
                "Reduce Google Ads CPA by 15%",
                "Grow email list by 500 subscribers",
                "Launch 2 new content campaigns",
            ],
            "key_initiatives": [
                {"initiative": "SEO content push — publish 8 long-form articles", "owner": "Content Team"},
                {"initiative": "Landing page A/B tests — test 3 variants", "owner": "CRO Team"},
                {"initiative": "Email nurture sequence revamp", "owner": "Email Team"},
                {"initiative": "LinkedIn thought leadership campaign", "owner": "Social Team"},
            ],
            "budget_allocation": {
                "google_ads": 40,
                "meta_ads": 25,
                "content_creation": 20,
                "tools_and_software": 10,
                "influencer_partnerships": 5,
            },
        }

    # ===== PRIVATE: DATA FETCHERS =====

    async def _get_content_performance(self) -> Dict:
        return {
            "posts_published": 6,
            "total_views": 8400,
            "avg_time_on_page": "4:32",
            "top_post": {"title": "Ultimate Guide to Digital Marketing", "views": 2300, "shares": 145},
            "content_score": 78,
        }

    async def _get_social_performance(self) -> Dict:
        return {
            "total_posts": 28,
            "total_reach": 45000,
            "total_engagement": 3200,
            "engagement_rate": 4.2,
            "follower_growth": 320,
            "top_platform": "LinkedIn",
            "top_post": {"platform": "LinkedIn", "engagement": 580, "type": "carousel"},
        }

    async def _get_email_performance(self) -> Dict:
        return {
            "campaigns_sent": 4,
            "total_sent": 19200,
            "avg_open_rate": 28.5,
            "avg_click_rate": 4.2,
            "unsubscribe_rate": 0.3,
            "list_growth": 280,
            "top_campaign": {"subject": "5 Marketing Trends for 2025", "open_rate": 35.2, "click_rate": 6.1},
        }

    async def _get_paid_performance(self) -> Dict:
        return {
            "total_spend": 3200.00,
            "total_impressions": 185000,
            "total_clicks": 7200,
            "total_conversions": 245,
            "overall_ctr": 3.89,
            "overall_cpc": 0.44,
            "overall_cpa": 13.06,
            "overall_roas": 3.2,
        }

    async def _get_seo_performance(self) -> Dict:
        return {
            "organic_sessions": 5200,
            "organic_growth_pct": 12.3,
            "keywords_ranking": 342,
            "keywords_top_10": 48,
            "keywords_top_3": 12,
            "backlinks_gained": 35,
            "domain_authority": 38,
            "top_keyword": {"keyword": "digital marketing automation", "position": 3, "volume": 2400},
        }

    async def _get_budget_analysis(self) -> Dict:
        return {
            "total_budget": 5000.00,
            "total_spent": 4250.00,
            "utilization_pct": 85.0,
            "by_channel": {
                "google_ads": {"budget": 2000, "spent": 1800, "roi": 3.2},
                "meta_ads": {"budget": 1500, "spent": 1350, "roi": 2.8},
                "content": {"budget": 1000, "spent": 800, "roi": 4.5},
                "tools": {"budget": 500, "spent": 300, "roi": None},
            },
            "recommendation": "Shift 10% of Meta budget to Content — higher ROI",
        }

    async def _get_goals_tracking(self) -> Dict:
        return {
            "goals": [
                {"goal": "10,000 monthly website visits", "target": 10000, "actual": 12450, "status": "achieved", "pct": 124.5},
                {"goal": "300 new leads", "target": 300, "actual": 342, "status": "achieved", "pct": 114.0},
                {"goal": "50 conversions", "target": 50, "actual": 28, "status": "behind", "pct": 56.0},
                {"goal": "$15,000 revenue", "target": 15000, "actual": 8372, "status": "behind", "pct": 55.8},
                {"goal": "5,000 email subscribers", "target": 5000, "actual": 4850, "status": "on_track", "pct": 97.0},
            ]
        }

    # ===== MOCK DATA =====

    def _mock_dashboard(self) -> Dict:
        return {
            "kpis": {
                "total_website_visits": 12450,
                "total_leads": 342,
                "total_conversions": 28,
                "total_revenue": 8372.00,
                "total_spend": 3200.00,
                "overall_roas": 2.62,
            },
            "kpi_changes": {
                "website_visits_change": 12.5,
                "leads_change": 8.3,
                "conversions_change": -2.1,
                "revenue_change": 15.7,
            },
            "alerts": [
                {"level": "warning", "message": "Bounce rate increased 5% this week"},
                {"level": "success", "message": "Organic traffic up 12% MoM"},
            ],
        }

    def _mock_analysis(self) -> Dict:
        return {"overall_health_score": 72, "channel_performance": [], "recommendations": []}

    def _mock_trends(self) -> Dict:
        return {"period_days": 14, "channel_trends": {}}

    def _mock_funnel(self) -> Dict:
        return {"funnel_data": {}, "drop_offs": []}

    def _mock_competitor_data(self) -> Dict:
        return {"competitors": [], "our_advantages": [], "opportunities": []}

    def _mock_narrative(self, report_type: str) -> str:
        narratives = {
            "daily": "Today's performance is tracking well. Website visits are up 8% compared to yesterday with 12,450 sessions. Organic traffic continues its upward trend, contributing 42% of total visits. One area of concern is the conversion rate, which dipped slightly to 2.1%. Recommend reviewing the checkout flow for friction points.",
            "weekly": "This week showed strong overall growth with organic traffic up 12% MoM. The email channel continues to be the highest-ROI performer with a 28.5% open rate. Google Ads ROAS held steady at 3.2x, though CPC increased 15% — worth monitoring. LinkedIn organic content saw a 25% engagement boost after switching to carousel format. Priority for next week: optimize landing pages and launch the new email nurture sequence.",
            "monthly": "This month delivered mixed results. Top-of-funnel metrics are strong — website traffic grew 15% and we added 280 email subscribers. However, bottom-of-funnel conversion is lagging behind targets (56% of goal). The biggest opportunity is improving the consideration-to-conversion stage of our funnel, where we're seeing a 74% drop-off. Content marketing ROI was the standout performer at 4.5x, suggesting we should increase investment here. Recommendation: reallocate 10% of paid budget to content creation and CRO initiatives.",
            "campaign": "The campaign delivered solid awareness metrics with 125K impressions and a 4.3% CTR. Conversion rate of 3.4% is above the industry benchmark of 2.5%. ROAS of 3.0x indicates profitability. The best-performing ad creative was the video variant, driving 60% of all conversions. Consider scaling the budget by 20% while maintaining the winning creative strategy.",
        }
        return narratives.get(report_type, narratives["daily"])
