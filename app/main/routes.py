from flask import render_template, request, jsonify
from app.main import bp
from app.utils.text_transformers import TextTransformer


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/transform', methods=['POST'])
def transform_text():
    data = request.get_json()
    if not data or 'text' not in data or 'transformation' not in data:
        return jsonify({'error': 'Missing text or transformation type'}), 400
    
    text = data['text']
    transformation = data['transformation']
    
    transformer = TextTransformer()
    
    try:
        result = transformer.transform(text, transformation)
        return jsonify({
            'success': True,
            'original_text': text,
            'transformed_text': result,
            'transformation': transformation
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400