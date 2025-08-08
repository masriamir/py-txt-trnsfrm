from flask import render_template, request, jsonify
from app.main import bp
from app.utils.text_transformers import TextTransformer
from app.logging_config import get_logger

logger = get_logger(__name__)


@bp.route('/')
def index():
    logger.info("Index page requested")
    return render_template('index.html')


@bp.route('/transform', methods=['POST'])
def transform_text():
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
