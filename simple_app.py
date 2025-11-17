from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import io
import re
import sys
import os

# Create Flask app
app = Flask(__name__)

# Configure CORS properly for Vercel
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# Disable debug mode for production
app.config['DEBUG'] = False

# API Keys (you should set these as environment variables in Vercel)
GEMINI_API_KEYS = [
    os.environ.get('GEMINI_API_KEY_1', 'AIzaSyDvo1FDQbtVtLxpGk1E40_xE0wv3xtpuys'),
    os.environ.get('GEMINI_API_KEY_2', 'AIzaSyAJl7pwh_Hj5fmRFtQl6T14ZkiTzdrautQ'),
    os.environ.get('GEMINI_API_KEY_3', 'AIzaSyCxmGRVK9KFE8kHdxH6ON63lw9BtjxhV5M')
]

# API URLs
GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def make_gemini_request(url, body, api_keys):
    """Make request to Gemini API with fallback across multiple keys"""
    headers = {"Content-Type": "application/json"}

    for i, api_key in enumerate(api_keys):
        if not api_key:
            continue

        try:
            response = requests.post(
                f"{url}?key={api_key}",
                headers=headers,
                json=body,
                timeout=30
            )

            if response.status_code == 200:
                return response.json(), None
            else:
                continue

        except Exception as e:
            continue

    return None, "All API keys failed"

def clean_arabic_text(text):
    """Clean Arabic text from unwanted English explanations"""
    if not text:
        return ""

    english_patterns = [
        r"Berikut teks Arab.*?:",
        r"There are some.*?differences.*?\.",
        r"I have corrected.*?\.",
        r"The most significant difference.*?\.",
        r"based on my understanding.*?\.",
        r"common Arabic spelling.*?\.",
        r"where the OCR.*?\.",
        r"Here is the.*?:",
        r"The Arabic text.*?:",
        r"OCR misinterprets.*?\.",
        r"Some minor.*?transcription\.",
        r"[A-Za-z].*?spelling\.",
        r".*?significant difference.*?\.",
        r".*?understanding.*?context.*?\.",
        r"\n\n[A-Za-z].*",
        r"[A-Za-z]{3,}.*?Arabic.*?\.",
    ]

    cleaned_text = text
    for pattern in english_patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.DOTALL)

    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
    cleaned_text = re.sub(r'\s{3,}', ' ', cleaned_text)

    return cleaned_text.strip()

# Routes
@app.route('/')
def root():
    return jsonify({
        'message': 'Arabic Text Analyzer API',
        'status': 'running',
        'version': '1.0',
        'endpoints': {
            'ocr': '/ocr - Extract Arabic text from images (POST)',
            'analyze_arabic': '/analyze_arabic - Analyze Arabic text for errors (POST)',
            'health': '/health - Health check (GET)'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Arabic Text Analyzer API is running',
        'api_keys_count': len([k for k in GEMINI_API_KEYS if k])
    })

@app.route('/ocr', methods=['POST'])
def ocr_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided', 'success': False}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file', 'success': False}), 400

        # Read image file
        image_data = file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

        body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "استخرج النص العربي من هذه الصورة بدقة. أريد النص العربي فقط بدون أي تفسير أو تعليق إضافي."
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 2048,
            }
        }

        result, error = make_gemini_request(GEMINI_VISION_URL, body, GEMINI_API_KEYS)

        if result and 'candidates' in result and len(result['candidates']) > 0:
            extracted_text = result['candidates'][0]['content']['parts'][0]['text']
            cleaned_text = clean_arabic_text(extracted_text)

            return jsonify({
                'text': cleaned_text,
                'success': True,
                'raw_text': extracted_text
            })
        else:
            return jsonify({
                'error': error or 'Failed to extract text from image',
                'success': False
            }), 500

    except Exception as e:
        return jsonify({
            'error': f'Error processing image: {str(e)}',
            'success': False
        }), 500

@app.route('/analyze_arabic', methods=['POST'])
def analyze_arabic():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided', 'success': False}), 400

        arabic_text = data.get('text', '')

        if not arabic_text.strip():
            return jsonify({'error': 'No text provided', 'success': False}), 400

        prompt = f"""
قم بتصحيح الأخطاء في النص التالي:

**1. أخطاء النحو:**
اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
الخطأ_النحوي1 -> التصحيح_النحوي1

**2. أخطاء الصرف:**
اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
الخطأ_الصرفي1 -> التصحيح_الصرفي1

**3. أخطاء الإملاء:**
اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
الخطأ_الإملائي1 -> التصحيح_الإملائي1

**4. أخطاء التركيب:**
اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
الخطأ_التركيبي1 -> التصحيح_التركيبي1

**النص المُصحح كاملاً:**
اكتب النص كاملاً بعد التصحيح

**النص المراد تصحيحه:**
{arabic_text}

ملاحظة: إذا لم توجد أخطاء في أي قسم، اكتب "لا توجد أخطاء" تحت ذلك القسم.
"""

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4096,
            }
        }

        result, error = make_gemini_request(GEMINI_TEXT_URL, body, GEMINI_API_KEYS)

        if result and 'candidates' in result and len(result['candidates']) > 0:
            analysis_text = result['candidates'][0]['content']['parts'][0]['text']

            return jsonify({
                'success': True,
                'analysis': analysis_text.strip(),
                'raw_response': analysis_text
            })
        else:
            return jsonify({
                'error': error or 'Failed to analyze text',
                'success': False
            }), 500

    except Exception as e:
        return jsonify({
            'error': f'Error analyzing text: {str(e)}',
            'success': False
        }), 500

# Vercel serverless function handler
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == '__main__':
    print("Starting Arabic Text Analyzer API...")
    print(f"Using {len([k for k in GEMINI_API_KEYS if k])} API keys for fallback")
    print("Available endpoints:")
    print("   - POST /ocr - Extract Arabic text from images")
    print("   - POST /analyze_arabic - Detailed Arabic text analysis")
    print("   - GET /health - Health check")
    print(f"Server running on http://localhost:5000")

    app.run(debug=False, port=5000, host='0.0.0.0')