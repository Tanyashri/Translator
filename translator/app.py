# English to Kannada Translator Flask Application
# This app translates English text to Kannada and generates audio

from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from gtts import gTTS
import os
from pathlib import Path

# Initialize Flask app
app = Flask(__name__)

# Set up paths for audio files
AUDIO_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# Initialize Google Translator
translator = Translator()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """
    API endpoint to translate English to Kannada
    Expects JSON: {"text": "english text here"}
    Returns JSON: {"kannada": "ಕನ್ನಡ text", "audio_url": "/static/output.mp3"}
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        english_text = data.get('text', '').strip()
        
        # Validate input
        if not english_text:
            return jsonify({
                'error': 'Please enter English text to translate',
                'success': False
            }), 400
        
        # Limit text length for audio generation
        if len(english_text) > 500:
            return jsonify({
                'error': 'Text is too long. Maximum 500 characters allowed.',
                'success': False
            }), 400
        
        # Translate text using Google Translate
        # googletrans returns a Translated object with .text attribute
        translated = translator.translate(english_text, src='en', dest='kn')
        kannada_text = translated.text
        
        # Generate Kannada audio using gTTS
        audio_file_path = os.path.join(AUDIO_FOLDER, 'output.mp3')
        try:
            tts = gTTS(text=kannada_text, lang='kn', slow=False)
            tts.save(audio_file_path)
        except Exception as audio_error:
            print(f"Audio generation warning: {audio_error}")
            # Continue without audio if generation fails
        
        # Return successful response
        return jsonify({
            'success': True,
            'english': english_text,
            'kannada': kannada_text,
            'audio_url': '/static/output.mp3'
        }), 200
    
    except Exception as e:
        # Handle any translation errors
        print(f"Translation error: {str(e)}")
        return jsonify({
            'error': f'Translation failed: {str(e)}',
            'success': False
        }), 500

@app.route('/api/translate-batch', methods=['POST'])
def translate_batch():
    """
    API endpoint for batch translation
    Expects JSON: {"texts": ["text1", "text2", ...]}
    Returns JSON: {"translations": [{"english": "text1", "kannada": "ಕನ್ನಡ1"}, ...]}
    """
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        # Validate input
        if not texts or not isinstance(texts, list):
            return jsonify({
                'error': 'Please provide a list of texts',
                'success': False
            }), 400
        
        # Translate each text
        translations = []
        for text in texts:
            if text.strip():
                translated = translator.translate(text, src='en', dest='kn')
                translations.append({
                    'english': text,
                    'kannada': translated.text
                })
        
        return jsonify({
            'success': True,
            'translations': translations
        }), 200
    
    except Exception as e:
        print(f"Batch translation error: {str(e)}")
        return jsonify({
            'error': f'Batch translation failed: {str(e)}',
            'success': False
        }), 500

@app.route('/api/voice-translate', methods=['POST'])
def voice_translate():
    """
    API endpoint for voice translation with both English and Kannada audio
    Expects JSON: {"text": "english text here"}
    Returns JSON with Kannada translation, English audio, and Kannada audio
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        english_text = data.get('text', '').strip()
        
        # Validate input
        if not english_text:
            return jsonify({
                'error': 'Please enter English text to translate',
                'success': False
            }), 400
        
        # Limit text length
        if len(english_text) > 500:
            return jsonify({
                'error': 'Text is too long. Maximum 500 characters allowed.',
                'success': False
            }), 400
        
        # Translate to Kannada
        translated = translator.translate(english_text, src='en', dest='kn')
        kannada_text = translated.text
        
        # Generate English audio
        english_audio_path = os.path.join(AUDIO_FOLDER, 'english_audio.mp3')
        try:
            tts_english = gTTS(text=english_text, lang='en', slow=False)
            tts_english.save(english_audio_path)
        except Exception as audio_error:
            print(f"English audio generation warning: {audio_error}")
        
        # Generate Kannada audio
        kannada_audio_path = os.path.join(AUDIO_FOLDER, 'kannada_audio.mp3')
        try:
            tts_kannada = gTTS(text=kannada_text, lang='kn', slow=False)
            tts_kannada.save(kannada_audio_path)
        except Exception as audio_error:
            print(f"Kannada audio generation warning: {audio_error}")
        
        # Return successful response with both audios
        return jsonify({
            'success': True,
            'english': english_text,
            'kannada': kannada_text,
            'english_audio_url': '/static/english_audio.mp3',
            'kannada_audio_url': '/static/kannada_audio.mp3'
        }), 200
    
    except Exception as e:
        # Handle any translation errors
        print(f"Voice translation error: {str(e)}")
        return jsonify({
            'error': f'Voice translation failed: {str(e)}',
            'success': False
        }), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Run the Flask app
if __name__ == '__main__':
    print("=" * 60)
    print("English to Kannada Translator")
    print("=" * 60)
    print("Server running at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    app.run(debug=True, host='localhost', port=5001)
