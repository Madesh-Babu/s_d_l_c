from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register global error handlers for consistent JSON responses."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle all HTTP-related errors."""
        response = e.get_response()
        response.data = jsonify({
            "error": {
                "type": e.__class__.__name__,
                "message": e.description,
                "status_code": e.code
            }
        }).data
        response.content_type = "application/json"
        return response, e.code

    @app.errorhandler(Exception)
    def handle_general_exception(e):
        """Handle non-HTTP exceptions (e.g., ValueError, DB errors)."""
        return jsonify({
            "error": {
                "type": e.__class__.__name__,
                "message": str(e),
                "status_code": 500
            }
        }), 500

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            "error": {
                "type": "NotFound",
                "message": "The requested resource could not be found.",
                "status_code": 404
            }
        }), 404

    @app.errorhandler(403)
    def handle_forbidden(e):
        return jsonify({
            "error": {
                "type": "Forbidden",
                "message": "Access forbidden: insufficient permissions.",
                "status_code": 403
            }
        }), 403

    @app.errorhandler(401)
    def handle_unauthorized(e):
        return jsonify({
            "error": {
                "type": "Unauthorized",
                "message": "You are not authorized to access this resource.",
                "status_code": 401
            }
        }), 401

    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({
            "error": {
                "type": "BadRequest",
                "message": "The request was invalid or cannot be served.",
                "status_code": 400
            }
        }), 400
