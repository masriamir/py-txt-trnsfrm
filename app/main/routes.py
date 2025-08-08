"""Main application routes module.

This module contains the primary Flask routes for the text transformation web
application, including the main page and the text transformation API endpoint.
"""
from flask import jsonify, render_template, request

from app.logging_config import get_logger
from app.main import bp
from app.utils.text_transformers import TextTransformer

logger = get_logger(__name__)


@bp.route('/')
def index():
    """Render the main application page.

    Serves the main HTML page containing the text transformation interface.
    Logs the page request for monitoring purposes.

    Returns:
        str: Rendered HTML template for the main page.
    """
    logger.info("Index page requested")
    return render_template('index.html')


@bp.route('/transform', methods=['POST'])
def transform_text():
    """Handle text transformation requests via JSON API.

    Processes POST requests containing text and transformation type,
    applies the requested transformation, and returns the result as JSON.
    Validates input data and provides detailed error messages for invalid requests.

    Expected JSON payload:
        {
            "text": "Text to transform",
            "transformation": "transformation_type"
        }

    Returns:
        tuple: JSON response and HTTP status code. Success responses include:
            - success: True
            - original_text: Input text
            - transformed_text: Transformed result
            - transformation: Applied transformation type

        Error responses include:
            - error: Error description

    Raises:
        400: If request data is invalid or transformation fails.
    """
    logger.info("Text transformation request received")

    data = request.get_json()
    if not data or 'text' not in data or 'transformation' not in data:
        logger.warning("Invalid transformation request - missing text or transformation type")
        return jsonify({'error': 'Missing text or transformation type'}), 400

    text = data['text']
    transformation = data['transformation']

    # Log the request details (truncate text if too long for readability)
    text_preview = text[:100] + "..." if len(text) > 100 else text
    logger.info(f"Transformation request - Type: '{transformation}', Text: '{text_preview}'")
    logger.debug(f"Full text length: {len(text)} characters")

    transformer = TextTransformer()

    try:
        result = transformer.transform(text, transformation)
        logger.info(f"Transformation '{transformation}' completed successfully")
        logger.debug(f"Result length: {len(result)} characters")

        return jsonify({
            'success': True,
            'original_text': text,
            'transformed_text': result,
            'transformation': transformation
        })
    except ValueError as e:
        logger.error(f"Transformation failed - Type: '{transformation}', Error: {str(e)}")
        return jsonify({'error': str(e)}), 400
