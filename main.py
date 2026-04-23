#!/usr/bin/env python3
"""
Digital Marketing Automation System — Main Entry Point

Usage:
    python main.py                  # Start the API server (default)
    python main.py --mode api       # Start the API server
    python main.py --mode daily     # Run daily workflow once
    python main.py --mode weekly    # Run weekly workflow once
    python main.py --mode monthly   # Run monthly workflow once
    python main.py --mode scheduler # Start the background scheduler (cron-like)
"""

import argparse
import asyncio
import logging
import os
import sys
import signal

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


def start_api_server():
    """Start the FastAPI server with Uvicorn."""
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "False").lower() == "true"

    logger.info(f"🚀 Starting Digital Marketing Automation API")
    logger.info(f"📡 Server: http://{host}:{port}")
    logger.info(f"📖 Docs:   http://{host}:{port}/docs")
    logger.info(f"🔄 Reload: {'ON' if reload else 'OFF'}")
    logger.info(f"──────────────────────────────────────────")

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


async def run_workflow(workflow_type: str):
    """Run a specific workflow once."""
    logger.info(f"🔄 Running {workflow_type} workflow...")

    if workflow_type == "daily":
        from workflows.daily_workflow import DailyWorkflow
        workflow = DailyWorkflow()
        result = await workflow.run()
    elif workflow_type == "weekly":
        from workflows.weekly_workflow import WeeklyWorkflow
        workflow = WeeklyWorkflow()
        result = await workflow.run()
    elif workflow_type == "monthly":
        from workflows.monthly_workflow import MonthlyWorkflow
        workflow = MonthlyWorkflow()
        result = await workflow.run()
    else:
        logger.error(f"Unknown workflow type: {workflow_type}")
        return

    logger.info(f"✅ Workflow completed: {result.get('summary', 'done')}")
    return result


def start_scheduler():
    """Start a background scheduler that runs workflows on a schedule."""
    try:
        import schedule
        import time
    except ImportError:
        logger.error("Install 'schedule' package: pip install schedule")
        return

    logger.info("⏰ Starting background scheduler...")
    logger.info("   Daily workflow:   Every day at 08:00")
    logger.info("   Weekly workflow:  Every Monday at 09:00")
    logger.info("   Monthly workflow: 1st of month at 10:00")

    def run_async(coro):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(coro)
        finally:
            loop.close()

    schedule.every().day.at("08:00").do(lambda: run_async(run_workflow("daily")))
    schedule.every().monday.at("09:00").do(lambda: run_async(run_workflow("weekly")))

    # Monthly — check daily if it's the 1st
    def monthly_check():
        from datetime import datetime
        if datetime.now().day == 1:
            run_async(run_workflow("monthly"))

    schedule.every().day.at("10:00").do(monthly_check)

    # Graceful shutdown
    running = True

    def shutdown(signum, frame):
        nonlocal running
        logger.info("🛑 Shutting down scheduler...")
        running = False

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while running:
        schedule.run_pending()
        time.sleep(60)

    logger.info("👋 Scheduler stopped.")


def print_banner():
    """Print startup banner."""
    banner = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   🚀 DIGITAL MARKETING AUTOMATION SYSTEM             ║
║                                                       ║
║   Powered by Claude AI + Azure Cloud                  ║
║                                                       ║
║   Modules:                                            ║
║   📝 Content Engine    — AI blog posts & copy         ║
║   🔍 SEO Optimizer     — Keywords & audits            ║
║   📱 Social Manager    — Multi-platform posting       ║
║   📧 Email Automation  — Campaigns & sequences        ║
║   🎯 Ad Manager        — Google & Meta ads            ║
║   📊 Analytics Engine  — Performance tracking         ║
║   📋 Report Generator  — Automated reports            ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    parser = argparse.ArgumentParser(description="Digital Marketing Automation System")
    parser.add_argument(
        "--mode",
        choices=["api", "daily", "weekly", "monthly", "scheduler"],
        default="api",
        help="Run mode (default: api)",
    )
    parser.add_argument("--port", type=int, default=None, help="API server port (overrides PORT env)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    if args.port:
        os.environ["PORT"] = str(args.port)
    if args.debug:
        os.environ["DEBUG"] = "True"
        logging.getLogger().setLevel(logging.DEBUG)

    print_banner()

    # Check for Claude API key
    if not os.getenv("CLAUDE_API_KEY"):
        logger.warning("⚠️  CLAUDE_API_KEY not set — running in MOCK MODE")
        logger.warning("   Set it in .env file for real AI-powered features")
    else:
        logger.info("✅ Claude API key detected")

    # Check for Azure
    if os.getenv("AZURE_COSMOS_ENDPOINT"):
        logger.info("✅ Azure Cosmos DB configured")
    else:
        logger.info("ℹ️  Azure not configured — using local storage")

    if args.mode == "api":
        start_api_server()
    elif args.mode == "scheduler":
        start_scheduler()
    else:
        asyncio.run(run_workflow(args.mode))


if __name__ == "__main__":
    main()
