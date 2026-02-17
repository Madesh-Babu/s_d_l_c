# !/usr/bin/env python3
"""
Inventory Management API - Application Entry Point

This file serves as the main entry point for running the Flask application.
It initializes and starts the Inventory Management API server.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.api import create_app
from src.core.config import settings
from src.core.logging import get_logger


def main():
    """Main function to run the Flask application."""

    # Initialize logger
    logger = get_logger(__name__)

    try:
        # Create Flask application
        app = create_app()

        # Get configuration
        config_name = os.getenv("FLASK_ENV", "development")
        host = os.getenv("FLASK_HOST", "127.0.0.1")
        port = int(os.getenv("FLASK_PORT", 5000))
        debug = app.config.get("DEBUG", False)

        # Log application startup
        logger.info(
            "Starting Inventory Management API",
            environment=settings.ENVIRONMENT,
            host=host,
            port=port,
            debug=debug,
            config_name=config_name,
        )

        # Print startup information
        print("=" * 60)
        print("🚀 INVENTORY MANAGEMENT API")
        print("=" * 60)
        print(f"📍 Environment: {settings.ENVIRONMENT}")
        print(f"🌐 Server: http://{host}:{port}")
        print(f"🔧 Debug Mode: {debug}")
        print(f"📚 API Documentation: http://{host}:{port}/health")
        print(f"🔐 Auth Bypass: {settings.feature_toggles.BYPASS_AUTH}")
        print("=" * 60)
        print("🎯 Available Endpoints:")
        print("  • GET  /           - Home")
        print("  • GET  /health     - Health Check")
        print("  • POST /auth/register - User Registration")
        print("  • POST /auth/login    - User Login")
        print("  • POST /auth/dev-login - Development Bypass")
        print("  • GET  /auth/users    - Get All Users")
        print("  • GET  /products/     - Get All Products")
        print("  • GET  /categories/   - Get All Categories")
        print("=" * 60)
        print("🛠️  Press CTRL+C to stop the server")
        print("=" * 60)

        # Run the Flask application
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,  # Enable auto-reload in development
        )

    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        print("\n🛑 Application stopped by user")

    except Exception as e:
        logger.error("Failed to start application", error=str(e), exc_info=True)
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
