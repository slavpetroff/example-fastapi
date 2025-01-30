from time import time

from fastapi.responses import ORJSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from api import get_logger


class ErrorLoggingMiddleware:
    logger = get_logger(__qualname__)

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            # Pass through for non-HTTP requests
            await self.app(scope, receive, send)
            return

        # Log the request details
        method = scope["method"]
        path = scope["path"]
        start_time = time()
        self.logger.info(f"Received request: {method} {path}")

        # Intercept the response to log its details
        response_status = 500  # Default to 500 in case of unhandled exceptions

        async def send_wrapper(message):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            await send(message)

        try:
            # Call the next application
            await self.app(scope, receive, send_wrapper)

        except Exception as e:
            # Log exception details
            self.logger.exception(
                f"Exception occurred during request: {method} {path}",
            )
            # Return a JSON response with error details
            error_response = ORJSONResponse(
                {"error": "Internal Server Error", "detail": str(e)},
                status_code=500,
            )
            await error_response(scope, receive, send)
            return
        finally:
            # Log the response status and duration
            duration = time() - start_time
            logger_function = self.logger.info

            if response_status >= 500:
                logger_function = self.logger.exception

            if response_status >= 400:
                logger_function = self.logger.warning

            logger_function(
                f"Response: {response_status} {method}"
                f" {path} completed in {duration:.2f} seconds",
            )
