"""
Logging Tests

This module contains comprehensive tests for the logging system
including structured logging, log levels, and middleware.
"""

import pytest
import json
import logging
from unittest.mock import Mock, patch, MagicMock
from src.core.logging import (
    get_logger,
    setup_logging,
    LoggingMiddleware,
    log_user_action,
    log_api_error,
)


class TestLoggingSetup:
    """Test logging setup and configuration."""

    def test_setup_logging_default(self):
        """Test setup_logging with default parameters."""
        with patch("src.core.logging.logging.basicConfig") as mock_config:
            setup_logging()

            mock_config.assert_called_once()
            call_args = mock_config.call_args
            assert call_args[1]["level"] == logging.INFO
            assert "format" in call_args[1]

    def test_setup_logging_with_level(self):
        """Test setup_logging with custom log level."""
        with patch("src.core.logging.logging.basicConfig") as mock_config:
            setup_logging(log_level="DEBUG")

            call_args = mock_config.call_args
            assert call_args[1]["level"] == logging.DEBUG

    def test_setup_logging_with_environment(self):
        """Test setup_logging with environment parameter."""
        with patch("src.core.logging.logging.basicConfig") as mock_config:
            setup_logging(environment="production")

            mock_config.assert_called_once()
            # Production should use WARNING level by default
            call_args = mock_config.call_args
            assert call_args[1]["level"] == logging.WARNING

    def test_setup_logging_file_output(self, tmp_path):
        """Test setup_logging with file output."""
        log_file = tmp_path / "test.log"

        with patch("src.core.logging.logging.FileHandler") as mock_handler:
            setup_logging(log_file_path=str(log_file))

            mock_handler.assert_called_once_with(str(log_file))

    def test_setup_logging_colored_output(self):
        """Test setup_logging with colored output."""
        with patch("src.core.logging.coloredlogs.install") as mock_colored:
            setup_logging(use_colors=True)

            mock_colored.assert_called_once()


class TestGetLogger:
    """Test logger creation and retrieval."""

    def test_get_logger_basic(self):
        """Test basic logger creation."""
        logger = get_logger("test_module")

        assert logger is not None
        assert logger.name == "test_module"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_singleton(self):
        """Test that get_logger returns same instance for same name."""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")

        assert logger1 is logger2

    def test_get_logger_different_names(self):
        """Test that get_logger returns different instances for different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"

    def test_get_logger_with_handlers(self):
        """Test logger has appropriate handlers."""
        logger = get_logger("test_module")

        # Should have at least one handler
        assert len(logger.handlers) > 0


class TestStructuredLogging:
    """Test structured logging functionality."""

    def test_structured_log_format(self, caplog):
        """Test that logs have structured format."""
        logger = get_logger("test_structured")

        with patch("src.core.logging.json.dumps") as mock_json:
            mock_json.return_value = '{"test": "data"}'

            logger.info("Test message", user_id=123, action="test")

            # Verify JSON serialization was called
            mock_json.assert_called()

    def test_log_with_extra_fields(self, caplog):
        """Test logging with extra fields."""
        logger = get_logger("test_extra")

        logger.info("Test message", user_id=123, action="login", ip_address="127.0.0.1")

        # Check that log record has extra fields
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.user_id == 123
        assert record.action == "login"
        assert record.ip_address == "127.0.0.1"

    def test_log_levels(self):
        """Test different log levels."""
        logger = get_logger("test_levels")

        with patch.object(logger, "_log") as mock_log:
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")

            # Should have called _log for each level
            assert mock_log.call_count == 5

    def test_log_exception_handling(self):
        """Test logging exception information."""
        logger = get_logger("test_exception")

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            with patch.object(logger, "error") as mock_error:
                logger.exception("Exception occurred")

                mock_error.assert_called_once()
                # Should include exception info
                call_args = mock_error.call_args
                assert "exc_info" in call_args[1]


class TestLoggingMiddleware:
    """Test logging middleware functionality."""

    def test_middleware_initialization(self, app):
        """Test middleware initialization."""
        middleware = LoggingMiddleware(app)

        assert middleware.app is app

    def test_middleware_request_logging(self, app):
        """Test that middleware logs requests."""
        middleware = LoggingMiddleware(app)

        # Mock request and logger
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.path = "/test"
        mock_request.remote_addr = "127.0.0.1"
        mock_request.headers = {"User-Agent": "test-agent"}

        with patch("src.core.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Simulate request processing
            with app.test_request_context("/test"):
                middleware.before_request()

                # Should have logged the request
                mock_logger.info.assert_called()
                call_args = mock_logger.info.call_args
                assert "method" in call_args[1]
                assert call_args[1]["method"] == "GET"

    def test_middleware_response_logging(self, app):
        """Test that middleware logs responses."""
        middleware = LoggingMiddleware(app)

        with patch("src.core.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Simulate response
            response = Mock()
            response.status_code = 200

            with app.test_request_context("/test"):
                middleware.after_request(response)

                # Should have logged the response
                mock_logger.info.assert_called()
                call_args = mock_logger.info.call_args
                assert "status_code" in call_args[1]
                assert call_args[1]["status_code"] == 200


class TestUtilityFunctions:
    """Test logging utility functions."""

    def test_log_user_action(self):
        """Test log_user_action utility function."""
        with patch("src.core.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_user_action("user_login", user_id=123, details={"ip": "127.0.0.1"})

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[0][0] == "user_login"
            assert call_args[1]["user_id"] == 123
            assert call_args[1]["action"] == "user_login"

    def test_log_api_error(self):
        """Test log_api_error utility function."""
        with patch("src.core.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_api_error(
                "validation_failed",
                endpoint="/auth/login",
                error="Invalid email",
                user_id=123,
            )

            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert call_args[0][0] == "validation_failed"
            assert call_args[1]["endpoint"] == "/auth/login"
            assert call_args[1]["error"] == "Invalid email"

    def test_log_user_action_without_details(self):
        """Test log_user_action without details parameter."""
        with patch("src.core.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_user_action("user_logout", user_id=123)

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[1]["action"] == "user_logout"
            assert "details" not in call_args[1]

    def test_log_api_error_without_user(self):
        """Test log_api_error without user_id."""
        with patch("src.core.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_api_error(
                "server_error", endpoint="/api/test", error="Internal server error"
            )

            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert call_args[1]["endpoint"] == "/api/test"
            assert "user_id" not in call_args[1]


class TestLoggingIntegration:
    """Test logging integration with application."""

    def test_logging_with_flask_app(self, app):
        """Test logging integration with Flask app."""
        with app.app_context():
            logger = get_logger("flask_test")

            # Should be able to log without errors
            logger.info("Test message in app context")

            # Should have app context available
            assert logger is not None

    def test_logging_performance(self):
        """Test logging performance doesn't impact application."""
        logger = get_logger("performance_test")

        import time

        start_time = time.time()

        # Log multiple messages
        for i in range(100):
            logger.info(f"Message {i}", iteration=i)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly (less than 1 second for 100 messages)
        assert duration < 1.0

    def test_logging_thread_safety(self):
        """Test that logging is thread-safe."""
        import threading
        import time

        logger = get_logger("thread_test")
        results = []

        def log_messages(thread_id):
            for i in range(10):
                logger.info(f"Thread {thread_id} message {i}")
            results.append(thread_id)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_messages, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All threads should complete successfully
        assert len(results) == 5
