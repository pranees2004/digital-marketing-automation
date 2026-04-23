"""
Analytics Engine — Collects, processes, and analyzes marketing data
across all channels using Claude AI for insights.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class ChannelMetrics:
    """Metrics for a single marketing channel"""
    channel: str
    date: str
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    revenue: float = 0.0
    sessions: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    new_users: int = 0
    returning_users: int = 0

    @property
    def ctr(self) -> float:
        return (self.clicks / self.impressions * 100) if self.impressions > 0 else 0.0

    @property
    def conversion_rate(self) -> float:
        return (self.conversions / self.clicks * 100) if self.clicks > 0 else 0.0

    @property
    def cpc(self) -> float:
        return (self.spend / self.clicks) if self.clicks > 0 else 0.0

    @property
    def roas(self) -> float:
        return (self.revenue / self.spend) if self.spend > 0 else 0.0

    @property
    def cpa(self) -> float:
        return (self.spend / self.conversions) if self.conversions > 0 else 0.0

    def to_dict(self) -> Dict:
        d = asdict(self)
        d.update({
            "ctr": round(self.ctr, 2),
            "conversion_rate": round(self.conversion_rate, 2),
            "cpc": round(self.cpc, 2),
            "roas": round(self.roas, 2),
            "cpa": round(self.cpa, 2),
        })
        return d


@dataclass
class WebsiteAnalytics:
    """Overall website analytics"""
    date: str
    total_sessions: int = 0
    unique_visitors: int = 0
    page_views: int = 0
    avg_session_duration: float = 0.0
    bounce_rate: float = 0.0
    top_pages: List[Dict] = field(default_factory=list)
    top_referrers: List[Dict] = field(default_factory=list)
    device_breakdown: Dict[str, int] = field(default_factory=dict)
    geo_breakdown: Dict[str, int] = field(default_factory=dict)
    conversion_events: List[Dict] = field(default_factory=list)


@dataclass
class CompetitorData:
    """Competitor analysis data"""
    competitor_name: str
    domain: str
    estimated_traffic: int = 0
    domain_authority: int = 0
    backlinks: int = 0
    top_keywords: List[str] = field(default_factory=list)
    social_followers: Dict[str, int] = field(default_factory=dict)
    recent_content: List[str] = field(default_factory=list)


class AnalyticsEngine:
    """
    Central analytics engine that:
    1. Collects metrics from all channels
    2. Stores historical data in Azure Cosmos DB
    3. Uses Claude AI to analyze trends and generate insights
    4. Provides recommendations for optimization
    """

    def __init__(self, claude_client=None, db_service=None, config=None):
        self.claude = claude_client
        self.db = db_service
        self.config = config
        self.container_name = "analytics"
        self._mock_mode = claude_client is None
        logger.info(f"AnalyticsEngine initialized (mock_mode={self._mock_mode})")

    # ===== DATA COLLECTION =====

    async def collect_google_analytics(self, days: int = 7) -> WebsiteAnalytics:
        """Collect data from Google Analytics 4"""
        logger.info(f"Collecting Google Analytics data for last {days} days")

        if self._mock_mode:
            return self._mock_ga_data(days)

        # In production, use google-analytics-data library:
        # from google.analytics.data_v1beta import BetaAnalyticsDataClient
        # client = BetaAnalyticsDataClient()
        # request = RunReportRequest(
        #     property=f"properties/{property_id}",
        #     dimensions=[Dimension(name="date")],
        #     metrics=[
        #         Metric(name="sessions"),
        #         Metric(name="totalUsers"),
        #         Metric(name="screenPageViews"),
        #         Metric(name="bounceRate"),
        #     ],
        #     date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        # )
        # response = client.run_report(request)
        return self._mock_ga_data(days)

    async def collect_channel_metrics(
        self, channel: str, days: int = 7
    ) -> List[ChannelMetrics]:
        """Collect metrics for a specific marketing channel"""
        logger.info(f"Collecting {channel} metrics for last {days} days")

        collectors = {
            "google_ads": self._collect_google_ads,
            "meta_ads": self._collect_meta_ads,
            "email": self._collect_email_metrics,
            "social_organic": self._collect_social_organic,
            "seo": self._collect_seo_metrics,
        }

        collector = collectors.get(channel, self._collect_generic_metrics)
        return await collector(days)

    async def collect_all_channels(self, days: int = 7) -> Dict[str, List[ChannelMetrics]]:
        """Collect metrics from all channels"""
        channels = ["google_ads", "meta_ads", "email", "social_organic", "seo"]
        results = {}

        for channel in channels:
            try:
                results[channel] = await self.collect_channel_metrics(channel, days)
                logger.info(f"✅ Collected {channel} metrics: {len(results[channel])} records")
            except Exception as e:
                logger.error(f"❌ Failed to collect {channel} metrics: {e}")
                results[channel] = []

        return results

    # ===== AI-POWERED ANALYSIS =====

    async def analyze_performance(self, days: int = 7) -> Dict[str, Any]:
        """Use Claude to analyze overall marketing performance"""
        logger.info("Running AI-powered performance analysis")

        all_metrics = await self.collect_all_channels(days)
        ga_data = await self.collect_google_analytics(days)

        # Prepare data summary for Claude
        summary = self._prepare_data_summary(all_metrics, ga_data)

        if self._mock_mode:
            return self._mock_ai_analysis(summary)

        prompt = f"""You are a senior digital marketing analyst. Analyze the following marketing
performance data and provide actionable insights.

COMPANY: {self.config.company.name if self.config else 'Company'}
INDUSTRY: {self.config.company.industry if self.config else 'Technology'}
PERIOD: Last {days} days

DATA:
{json.dumps(summary, indent=2)}

Provide your analysis in this JSON format:
{{
    "overall_health_score": 0-100,
    "executive_summary": "2-3 sentence overview",
    "channel_performance": [
        {{
            "channel": "channel_name",
            "score": 0-100,
            "trend": "up|down|stable",
            "key_metric": "most important metric and value",
            "insight": "what the data tells us"
        }}
    ],
    "top_wins": ["win 1", "win 2", "win 3"],
    "top_concerns": ["concern 1", "concern 2", "concern 3"],
    "recommendations": [
        {{
            "priority": "high|medium|low",
            "channel": "channel_name",
            "action": "specific action to take",
            "expected_impact": "what improvement to expect",
            "effort": "low|medium|high"
        }}
    ],
    "budget_reallocation": {{
        "suggestion": "where to move budget",
        "reasoning": "why"
    }},
    "next_week_focus": ["focus area 1", "focus area 2", "focus area 3"]
}}"""

        response = await self.claude.generate(
            prompt=prompt,
            system="You are an expert marketing data analyst. Return ONLY valid JSON.",
            temperature=0.3,
            max_tokens=3000,
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_analysis": response, "parse_error": True}

    async def analyze_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze long-term trends across channels"""
        all_metrics = await self.collect_all_channels(days)

        trend_data = {}
        for channel, metrics_list in all_metrics.items():
            if len(metrics_list) < 2:
                continue

            first_half = metrics_list[: len(metrics_list) // 2]
            second_half = metrics_list[len(metrics_list) // 2:]

            first_avg_ctr = (
                sum(m.ctr for m in first_half) / len(first_half) if first_half else 0
            )
            second_avg_ctr = (
                sum(m.ctr for m in second_half) / len(second_half) if second_half else 0
            )

            first_avg_conv = (
                sum(m.conversion_rate for m in first_half) / len(first_half)
                if first_half
                else 0
            )
            second_avg_conv = (
                sum(m.conversion_rate for m in second_half) / len(second_half)
                if second_half
                else 0
            )

            trend_data[channel] = {
                "ctr_trend": "up" if second_avg_ctr > first_avg_ctr else "down",
                "ctr_change_pct": round(
                    ((second_avg_ctr - first_avg_ctr) / first_avg_ctr * 100)
                    if first_avg_ctr > 0
                    else 0,
                    2,
                ),
                "conversion_trend": "up" if second_avg_conv > first_avg_conv else "down",
                "conversion_change_pct": round(
                    ((second_avg_conv - first_avg_conv) / first_avg_conv * 100)
                    if first_avg_conv > 0
                    else 0,
                    2,
                ),
                "total_spend": sum(m.spend for m in metrics_list),
                "total_revenue": sum(m.revenue for m in metrics_list),
                "total_conversions": sum(m.conversions for m in metrics_list),
            }

        return {
            "period_days": days,
            "analysis_date": datetime.now().isoformat(),
            "channel_trends": trend_data,
        }

    async def competitor_analysis(self, competitors: List[str] = None) -> Dict[str, Any]:
        """AI-powered competitor analysis"""
        if not competitors and self.config:
            competitors = self.config.company.competitors

        if not competitors:
            competitors = ["competitor1.com", "competitor2.com"]

        if self._mock_mode:
            return {
                "competitors": [
                    {
                        "name": comp,
                        "estimated_traffic": 50000,
                        "domain_authority": 45,
                        "top_keywords": ["keyword1", "keyword2"],
                        "strengths": ["Strong content marketing", "Active social presence"],
                        "weaknesses": ["Poor mobile UX", "Slow page speed"],
                    }
                    for comp in competitors
                ],
                "our_advantages": ["Better product", "Stronger brand voice"],
                "opportunities": ["Target their weak keywords", "Improve content frequency"],
            }

        prompt = f"""Analyze these competitors for {self.config.company.name} in the
{self.config.company.industry} industry:

Competitors: {', '.join(competitors)}
Our website: {self.config.company.website_url}

Provide competitive analysis in JSON format with:
- Each competitor's strengths and weaknesses
- Our competitive advantages
- Market opportunities
- Recommended counter-strategies"""

        response = await self.claude.generate(prompt=prompt, temperature=0.4)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_analysis": response}

    # ===== FUNNEL ANALYSIS =====

    async def funnel_analysis(self) -> Dict[str, Any]:
        """Analyze the full marketing funnel"""
        ga_data = await self.collect_google_analytics(30)

        funnel = {
            "awareness": {
                "impressions": 150000,
                "reach": 95000,
                "brand_searches": 2500,
            },
            "interest": {
                "website_visits": ga_data.total_sessions,
                "page_views": ga_data.page_views,
                "avg_time_on_site": ga_data.avg_session_duration,
                "bounce_rate": ga_data.bounce_rate,
            },
            "consideration": {
                "return_visitors": ga_data.unique_visitors * 0.3,
                "content_downloads": 450,
                "email_signups": 280,
                "demo_requests": 85,
            },
            "conversion": {
                "trials_started": 45,
                "purchases": 22,
                "conversion_rate": 1.2,
                "avg_order_value": 299.00,
            },
            "retention": {
                "repeat_customers": 15,
                "churn_rate": 5.2,
                "nps_score": 42,
                "ltv": 1450.00,
            },
        }

        # Calculate drop-off rates
        stages = list(funnel.keys())
        stage_values = [
            150000,
            ga_data.total_sessions,
            int(ga_data.unique_visitors * 0.3),
            22,
            15,
        ]

        drop_offs = []
        for i in range(len(stage_values) - 1):
            drop_off = round(
                (1 - stage_values[i + 1] / stage_values[i]) * 100, 1
            ) if stage_values[i] > 0 else 0
            drop_offs.append({
                "from": stages[i],
                "to": stages[i + 1],
                "drop_off_pct": drop_off,
            })

        return {
            "funnel_data": funnel,
            "drop_offs": drop_offs,
            "biggest_leak": max(drop_offs, key=lambda x: x["drop_off_pct"]),
            "analysis_date": datetime.now().isoformat(),
        }

    # ===== DATA STORAGE =====

    async def store_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Store metrics in Azure Cosmos DB"""
        if self.db is None:
            logger.info("No DB connection — metrics logged but not stored")
            return True

        try:
            doc = {
                "id": f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "daily_metrics",
                "timestamp": datetime.now().isoformat(),
                "data": metrics,
            }
            await self.db.create_document(self.container_name, doc)
            return True
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            return False

    async def get_historical_metrics(self, days: int = 30) -> List[Dict]:
        """Retrieve historical metrics from database"""
        if self.db is None:
            return self._mock_historical_data(days)

        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            query = f"SELECT * FROM c WHERE c.type = 'daily_metrics' AND c.timestamp >= '{start_date}' ORDER BY c.timestamp DESC"
            return await self.db.query_documents(self.container_name, query)
        except Exception as e:
            logger.error(f"Failed to get historical metrics: {e}")
            return []

    # ===== KPI DASHBOARD DATA =====

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all data needed for a marketing dashboard"""
        today = datetime.now().strftime("%Y-%m-%d")

        return {
            "date": today,
            "kpis": {
                "total_website_visits": 12450,
                "total_leads": 342,
                "total_conversions": 28,
                "total_revenue": 8372.00,
                "total_spend": 3200.00,
                "overall_roas": 2.62,
                "email_subscribers": 4850,
                "social_followers": 12300,
            },
            "kpi_changes": {
                "website_visits_change": 12.5,
                "leads_change": 8.3,
                "conversions_change": -2.1,
                "revenue_change": 15.7,
                "spend_change": 5.0,
            },
            "channel_breakdown": {
                "seo": {"traffic_pct": 42, "leads_pct": 35, "revenue_pct": 38},
                "paid_search": {"traffic_pct": 25, "leads_pct": 30, "revenue_pct": 32},
                "social": {"traffic_pct": 18, "leads_pct": 15, "revenue_pct": 12},
                "email": {"traffic_pct": 10, "leads_pct": 15, "revenue_pct": 14},
                "direct": {"traffic_pct": 5, "leads_pct": 5, "revenue_pct": 4},
            },
            "alerts": [
                {"level": "warning", "message": "Bounce rate increased 5% this week"},
                {"level": "info", "message": "Email open rate above industry avg"},
                {"level": "success", "message": "Organic traffic up 12% MoM"},
            ],
        }

    # ===== PRIVATE: DATA COLLECTORS =====

    async def _collect_google_ads(self, days: int) -> List[ChannelMetrics]:
        return [
            ChannelMetrics(
                channel="google_ads",
                date=(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                impressions=8500 + (i * 100),
                clicks=340 + (i * 10),
                conversions=12 + (i % 3),
                spend=125.50 + (i * 5),
                revenue=450.00 + (i * 20),
            )
            for i in range(days)
        ]

    async def _collect_meta_ads(self, days: int) -> List[ChannelMetrics]:
        return [
            ChannelMetrics(
                channel="meta_ads",
                date=(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                impressions=12000 + (i * 200),
                clicks=480 + (i * 15),
                conversions=8 + (i % 4),
                spend=95.00 + (i * 3),
                revenue=320.00 + (i * 15),
            )
            for i in range(days)
        ]

    async def _collect_email_metrics(self, days: int) -> List[ChannelMetrics]:
        return [
            ChannelMetrics(
                channel="email",
                date=(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                impressions=5000,
                clicks=750 + (i * 20),
                conversions=15 + (i % 5),
                spend=0.0,
                revenue=280.00 + (i * 10),
            )
            for i in range(days)
        ]

    async def _collect_social_organic(self, days: int) -> List[ChannelMetrics]:
        return [
            ChannelMetrics(
                channel="social_organic",
                date=(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                impressions=20000 + (i * 500),
                clicks=600 + (i * 20),
                conversions=5 + (i % 2),
                spend=0.0,
                revenue=150.00 + (i * 8),
            )
            for i in range(days)
        ]

    async def _collect_seo_metrics(self, days: int) -> List[ChannelMetrics]:
        return [
            ChannelMetrics(
                channel="seo",
                date=(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                impressions=45000 + (i * 1000),
                clicks=2200 + (i * 50),
                conversions=18 + (i % 6),
                spend=0.0,
                revenue=520.00 + (i * 25),
                sessions=2200 + (i * 50),
                bounce_rate=42.5 - (i * 0.2),
            )
            for i in range(days)
        ]

    async def _collect_generic_metrics(self, days: int) -> List[ChannelMetrics]:
        return [
            ChannelMetrics(
                channel="unknown",
                date=(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                impressions=1000,
                clicks=50,
                conversions=2,
            )
            for i in range(days)
        ]

    # ===== PRIVATE: MOCK DATA =====

    def _mock_ga_data(self, days: int) -> WebsiteAnalytics:
        return WebsiteAnalytics(
            date=datetime.now().strftime("%Y-%m-%d"),
            total_sessions=12450,
            unique_visitors=8920,
            page_views=34500,
            avg_session_duration=185.5,
            bounce_rate=45.2,
            top_pages=[
                {"page": "/", "views": 5400},
                {"page": "/blog", "views": 3200},
                {"page": "/pricing", "views": 2100},
                {"page": "/features", "views": 1800},
                {"page": "/contact", "views": 950},
            ],
            top_referrers=[
                {"source": "google", "sessions": 5200},
                {"source": "direct", "sessions": 2800},
                {"source": "linkedin.com", "sessions": 1200},
                {"source": "twitter.com", "sessions": 800},
            ],
            device_breakdown={"desktop": 55, "mobile": 38, "tablet": 7},
            geo_breakdown={"US": 45, "UK": 15, "India": 12, "Canada": 8, "Other": 20},
        )

    def _mock_ai_analysis(self, summary: Dict) -> Dict:
        return {
            "overall_health_score": 72,
            "executive_summary": "Marketing performance is solid with strong SEO growth. Paid channels need optimization — CPA is above target. Email remains highest-ROI channel.",
            "channel_performance": [
                {
                    "channel": "SEO",
                    "score": 85,
                    "trend": "up",
                    "key_metric": "Organic traffic +12% MoM",
                    "insight": "Content strategy is working. Blog posts driving 60% of organic traffic.",
                },
                {
                    "channel": "Google Ads",
                    "score": 68,
                    "trend": "stable",
                    "key_metric": "ROAS 3.2x",
                    "insight": "Decent returns but CPC rising. Need to refine keyword targeting.",
                },
                {
                    "channel": "Social Media",
                    "score": 60,
                    "trend": "up",
                    "key_metric": "Engagement rate 4.2%",
                    "insight": "LinkedIn outperforming other platforms. Double down on LinkedIn content.",
                },
                {
                    "channel": "Email",
                    "score": 88,
                    "trend": "up",
                    "key_metric": "Open rate 28%, CTR 4.5%",
                    "insight": "Highest ROI channel. Segmentation strategy is effective.",
                },
            ],
            "top_wins": [
                "Organic traffic grew 12% month-over-month",
                "Email list grew by 280 subscribers",
                "Blog post 'Ultimate Guide' ranked #3 for target keyword",
            ],
            "top_concerns": [
                "Google Ads CPC increased 15%",
                "Social media reach declining on Facebook",
                "Landing page conversion rate dropped to 2.1%",
            ],
            "recommendations": [
                {
                    "priority": "high",
                    "channel": "Google Ads",
                    "action": "Pause low-performing keywords and reallocate budget to top converters",
                    "expected_impact": "Reduce CPA by 20%",
                    "effort": "low",
                },
                {
                    "priority": "high",
                    "channel": "Website",
                    "action": "A/B test landing page headline and CTA button",
                    "expected_impact": "Increase conversion rate by 0.5-1%",
                    "effort": "medium",
                },
                {
                    "priority": "medium",
                    "channel": "Content",
                    "action": "Publish 2 more long-form guides targeting high-volume keywords",
                    "expected_impact": "20% more organic traffic in 60 days",
                    "effort": "high",
                },
            ],
            "next_week_focus": [
                "Optimize Google Ads campaigns",
                "Launch landing page A/B test",
                "Send segmented email campaign to warm leads",
            ],
        }

    def _prepare_data_summary(
        self, all_metrics: Dict[str, List[ChannelMetrics]], ga_data: WebsiteAnalytics
    ) -> Dict:
        summary = {
            "website": {
                "sessions": ga_data.total_sessions,
                "unique_visitors": ga_data.unique_visitors,
                "page_views": ga_data.page_views,
                "bounce_rate": ga_data.bounce_rate,
                "top_pages": ga_data.top_pages[:5],
            },
            "channels": {},
        }

        for channel, metrics_list in all_metrics.items():
            if not metrics_list:
                continue
            summary["channels"][channel] = {
                "total_impressions": sum(m.impressions for m in metrics_list),
                "total_clicks": sum(m.clicks for m in metrics_list),
                "total_conversions": sum(m.conversions for m in metrics_list),
                "total_spend": round(sum(m.spend for m in metrics_list), 2),
                "total_revenue": round(sum(m.revenue for m in metrics_list), 2),
                "avg_ctr": round(
                    sum(m.ctr for m in metrics_list) / len(metrics_list), 2
                ),
                "avg_conversion_rate": round(
                    sum(m.conversion_rate for m in metrics_list) / len(metrics_list), 2
                ),
            }

        return summary

    def _mock_historical_data(self, days: int) -> List[Dict]:
        data = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            data.append({
                "date": date,
                "sessions": 400 + (i * 10),
                "conversions": 8 + (i % 5),
                "revenue": 280 + (i * 12),
            })
        return data
