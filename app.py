# awal
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from PIL import Image
# import requests
# import base64
# import json
# import io
# import re

# from flask import jsonify
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# # 🔑 Multiple API Keys for fallback - ganti dengan API keys milikmu
# GEMINI_API_KEYS = [
#     # pakai yang no 1 
#             "AIzaSyAHzRxPzIov7LZDs47QnhwHvwPEfNFWfV4",

#     "AIzaSyDvo1FDQbtVtLxpGk1E40_xE0wv3xtpuys", 
#     "AIzaSyD6XObCpKK03BVP0SshWm4KV_noh-HCjCo", 
#     "AIzaSyCxmGRVK9KFE8kHdxH6ON63lw9BtjxhV5M"
# ]

# # Ganti di kode Anda:
# GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
# GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
# def encode_image_to_base64(image):
#     """Convert PIL Image to base64 string"""
#     buffered = io.BytesIO()
#     # Convert to RGB if image has transparency (RGBA)
#     if image.mode in ('RGBA', 'LA'):
#         background = Image.new('RGB', image.size, (255, 255, 255))
#         background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
#         image = background
#     image.save(buffered, format="JPEG", quality=85)
#     return base64.b64encode(buffered.getvalue()).decode('utf-8')

# def clean_arabic_text(text):
#     """Clean Arabic text from unwanted English explanations"""
#     if not text:
#         return ""
    
#     # Remove common English phrases that appear in OCR results
#     english_patterns = [
#         r"Berikut teks Arab.*?:",
#         r"There are some.*?differences.*?\.",
#         r"I have corrected.*?\.",
#         r"The most significant difference.*?\.",
#         r"based on my understanding.*?\.",
#         r"common Arabic spelling.*?\.",
#         r"where the OCR.*?\.",
#         r"Here is the.*?:",
#         r"The Arabic text.*?:",
#         r"OCR misinterprets.*?\.",
#         r"Some minor.*?transcription\.",
#         r"[A-Za-z].*?spelling\.",
#         r".*?significant difference.*?\.",
#         r".*?understanding.*?context.*?\.",
#         r"\n\n[A-Za-z].*",  # Remove paragraph starting with English
#         r"[A-Za-z]{3,}.*?Arabic.*?\.",  # Remove English sentences mentioning Arabic
#     ]
    
#     cleaned_text = text
#     for pattern in english_patterns:
#         cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    
#     # Remove excessive whitespace and newlines
#     cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
#     cleaned_text = re.sub(r'\s{3,}', ' ', cleaned_text)
    
#     return cleaned_text.strip()

# def make_gemini_request(url, body, api_keys):
#     """Make request to Gemini API with fallback across multiple keys"""
#     headers = {"Content-Type": "application/json"}
    
#     for i, api_key in enumerate(api_keys):
#         try:
#             response = requests.post(
#                 f"{url}?key={api_key}",
#                 headers=headers,
#                 json=body,
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 return response.json(), None
#             else:
#                 print(f"[!] API key {i+1} failed with status {response.status_code}: {response.text[:100]}...")
#                 continue
                
#         except Exception as e:
#             print(f"[!] API key {i+1} failed with error: {str(e)}")
#             continue
    
#     return None, "All API keys failed"

# # ========== 1️⃣ Enhanced OCR Endpoint ==========
# @app.route('/ocr', methods=['POST'])
# def ocr_image():
#     try:
#         if 'image' not in request.files:
#             return jsonify({'error': 'No image file provided', 'success': False}), 400

#         file = request.files['image']
#         if file.filename == '':
#             return jsonify({'error': 'No selected file', 'success': False}), 400

#         # Open and process image
#         image = Image.open(file.stream)
        
#         # Convert image to base64
#         base64_image = encode_image_to_base64(image)
        
#         # Improved prompt to avoid English explanations
#         body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {
#                             "text": "استخرج النص العربي من هذه الصورة بدقة. أريد النص العربي فقط بدون أي تفسير أو تعليق إضافي."
#                         },
#                         {
#                             "inline_data": {
#                                 "mime_type": "image/jpeg",
#                                 "data": base64_image
#                             }
#                         }
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.1,
#                 "maxOutputTokens": 2048,
#             }
#         }
        
#         # Make request with fallback API keys
#         result, error = make_gemini_request(GEMINI_VISION_URL, body, GEMINI_API_KEYS)
        
#         if result and 'candidates' in result and len(result['candidates']) > 0:
#             extracted_text = result['candidates'][0]['content']['parts'][0]['text']
            
#             # Clean the extracted text
#             cleaned_text = clean_arabic_text(extracted_text)
            
#             return jsonify({
#                 'text': cleaned_text,
#                 'success': True,
#                 'raw_text': extracted_text  # Include raw text for debugging
#             })
#         else:
#             return jsonify({
#                 'error': error or 'Failed to extract text from image',
#                 'success': False
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'error': f'Error processing image: {str(e)}',
#             'success': False
#         }), 500


# # ========== 2️⃣ Enhanced Arabic Analysis ==========
# @app.route('/analyze_arabic', methods=['POST'])
# def analyze_arabic():
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'No JSON data provided', 'success': False}), 400
            
#         arabic_text = data.get('text', '')

#         if not arabic_text.strip():
#             return jsonify({'error': 'No text provided', 'success': False}), 400

#         # Use the same detailed prompt as the Colab version
#         prompt = f"""
# قم بتصحيح الأخطاء في النص التالي:

# **1. أخطاء النحو:**
# اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
# الخطأ_النحوي1 -> التصحيح_النحوي1
# الخطأ_النحوي2 -> التصحيح_النحوي2

# **2. أخطاء الصرف:**
# اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
# الخطأ_الصرفي1 -> التصحيح_الصرفي1
# الخطأ_الصرفي2 -> التصحيح_الصرفي2

# **3. أخطاء الإملاء:**
# اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
# الخطأ_الإملائي1 -> التصحيح_الإملائي1
# الخطأ_الإملائي2 -> التصحيح_الإملائي2

# **4. أخطاء التركيب:**
# اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
# الخطأ_التركيبي1 -> التصحيح_التركيبي1
# الخطأ_التركيبي2 -> التصحيح_التركيبي2

# **النص المُصحح كاملاً:**
# اكتب النص كاملاً بعد التصحيح

# **النص المراد تصحيحه:**
# {arabic_text}

# ملاحظة: إذا لم توجد أخطاء في أي قسم، اكتب "لا توجد أخطاء" تحت ذلك القسم.
# """

#         body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.3,
#                 "maxOutputTokens": 4096,
#             }
#         }

#         result, error = make_gemini_request(GEMINI_TEXT_URL, body, GEMINI_API_KEYS)
        
#         if result and 'candidates' in result and len(result['candidates']) > 0:
#             analysis_text = result['candidates'][0]['content']['parts'][0]['text']
            
#             return jsonify({
#                 'success': True,
#                 'analysis': analysis_text.strip(),
#                 'raw_response': analysis_text
#             })
#         else:
#             return jsonify({
#                 'error': error or 'Failed to analyze text',
#                 'success': False
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'error': f'Error analyzing text: {str(e)}',
#             'success': False
#         }), 500


# # ========== 3️⃣ Combined OCR + Analysis Endpoint ==========
# @app.route('/ocr_and_analyze', methods=['POST'])
# def ocr_and_analyze():
#     """Combined OCR and Analysis like the Colab version"""
#     try:
#         if 'image' not in request.files:
#             return jsonify({'error': 'No image file provided', 'success': False}), 400

#         file = request.files['image']
#         if file.filename == '':
#             return jsonify({'error': 'No selected file', 'success': False}), 400

#         # Step 1: OCR
#         print("Performing OCR with Gemini...")
#         image = Image.open(file.stream)
#         base64_image = encode_image_to_base64(image)
        
#         ocr_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {
#                             "text": "استخرج النص العربي من هذه الصورة بدقة. أريد النص العربي فقط بدون أي تفسير أو تعليق إضافي."
#                         },
#                         {
#                             "inline_data": {
#                                 "mime_type": "image/jpeg",
#                                 "data": base64_image
#                             }
#                         }
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.1,
#                 "maxOutputTokens": 2048,
#             }
#         }
        
#         ocr_result, ocr_error = make_gemini_request(GEMINI_VISION_URL, ocr_body, GEMINI_API_KEYS)
        
#         if not ocr_result or 'candidates' not in ocr_result or len(ocr_result['candidates']) == 0:
#             return jsonify({
#                 'error': f'OCR failed: {ocr_error}',
#                 'success': False
#             }), 500
            
#         extracted_text = ocr_result['candidates'][0]['content']['parts'][0]['text']
#         cleaned_extracted_text = clean_arabic_text(extracted_text)
        
#         print("Performing Language Analysis...")
        
#         # Step 2: Analysis using the same prompt as Colab
#         analysis_prompt = f"""
# قم بتصحيح الأخطاء في النص التالي:

# **1. أخطاء النحو:**
# اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
# الخطأ_النحوي1 -> التصحيح_النحوي1
# الخطأ_النحوي2 -> التصحيح_النحوي2

# **2. أخطاء الصرف:**
# اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
# الخطأ_الصرفي1 -> التصحيح_الصرفي1
# الخطأ_الصرفي2 -> التصحيح_الصرفي2

# **3. أخطاء الإملاء:**
# اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
# الخطأ_الإملائي1 -> التصحيح_الإملائي1
# الخطأ_الإملائي2 -> التصحيح_الإملائي2

# **4. أخطاء التركيب:**
# اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
# الخطأ_التركيبي1 -> التصحيح_التركيبي1
# الخطأ_التركيبي2 -> التصحيح_التركيبي2

# **النص المُصحح كاملاً:**
# اكتب النص كاملاً بعد التصحيح

# **النص المراد تصحيحه:**
# {cleaned_extracted_text}

# ملاحظة: إذا لم توجد أخطاء في أي قسم، اكتب "لا توجد أخطاء" تحت ذلك القسم.
# """

#         analysis_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": analysis_prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.3,
#                 "maxOutputTokens": 4096,
#             }
#         }
        
#         analysis_result, analysis_error = make_gemini_request(GEMINI_TEXT_URL, analysis_body, GEMINI_API_KEYS)
        
#         if not analysis_result or 'candidates' not in analysis_result or len(analysis_result['candidates']) == 0:
#             return jsonify({
#                 'success': True,
#                 'extracted_text': cleaned_extracted_text,
#                 'analysis': f'Analysis failed: {analysis_error}',
#                 'error_in_analysis': True
#             })
            
#         analysis_text = analysis_result['candidates'][0]['content']['parts'][0]['text']
        
#         return jsonify({
#             'success': True,
#             'extracted_text': cleaned_extracted_text,
#             'analysis': analysis_text.strip(),
#             'message': 'OCR and analysis completed successfully',
#             'raw_extracted_text': extracted_text  # Include for debugging
#         })
        
#     except Exception as e:
#         return jsonify({
#             'error': f'Error in OCR and analysis: {str(e)}',
#             'success': False
#         }), 500


# # ========== 4️⃣ Generate Arabic Text ==========
# @app.route('/generate_arabic', methods=['POST'])
# def generate_arabic():
#     try:
#         data = request.json
#         if not data:
#             data = {}
            
#         prompt = data.get('prompt', 'اكتب لي نصا عربيا قصيرا')

#         body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.7,
#                 "maxOutputTokens": 1024,
#             }
#         }

#         result, error = make_gemini_request(GEMINI_TEXT_URL, body, GEMINI_API_KEYS)
        
#         if result and 'candidates' in result and len(result['candidates']) > 0:
#             generated_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
#             return jsonify({
#                 'success': True,
#                 'generated_text': generated_text
#             })
#         else:
#             return jsonify({
#                 'error': error or 'Failed to generate text',
#                 'success': False
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'error': f'Error generating text: {str(e)}',
#             'success': False
#         }), 500


# # ========== 5️⃣ Generate + Analyze Combined ==========
# @app.route('/generate_and_analyze', methods=['POST'])
# def generate_and_analyze():
#     try:
#         data = request.json
#         if not data:
#             data = {}
            
#         prompt = data.get('prompt', 'اكتب لي نصا عربيا قصيرا')

#         # Step 1: Generate text
#         generate_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.7,
#                 "maxOutputTokens": 1024,
#             }
#         }

#         gen_result, gen_error = make_gemini_request(GEMINI_TEXT_URL, generate_body, GEMINI_API_KEYS)
        
#         if not gen_result or 'candidates' not in gen_result or len(gen_result['candidates']) == 0:
#             return jsonify({
#                 'error': f'Text generation failed: {gen_error}',
#                 'success': False
#             }), 500

#         generated_text = gen_result['candidates'][0]['content']['parts'][0]['text'].strip()

#         # Step 2: Analyze the generated text
#         analysis_prompt = f"""
# قم بتصحيح الأخطاء في النص التالي:

# **1. أخطاء النحو:**
# اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
# الخطأ_النحوي1 -> التصحيح_النحوي1
# الخطأ_النحوي2 -> التصحيح_النحوي2

# **2. أخطاء الصرف:**
# اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
# الخطأ_الصرفي1 -> التصحيح_الصرفي1
# الخطأ_الصرفي2 -> التصحيح_الصرفي2

# **3. أخطاء الإملاء:**
# اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
# الخطأ_الإملائي1 -> التصحيح_الإملائي1
# الخطأ_الإملائي2 -> التصحيح_الإملائي2

# **4. أخطاء التركيب:**
# اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
# الخطأ_التركيبي1 -> التصحيح_التركيبي1
# الخطأ_التركيبي2 -> التصحيح_التركيبي2

# **النص المُصحح كاملاً:**
# اكتب النص كاملاً بعد التصحيح

# **النص المراد تصحيحه:**
# {generated_text}

# ملاحظة: إذا لم توجد أخطاء في أي قسم، اكتب "لا توجد أخطاء" تحت ذلك القسم.
# """

#         analyze_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": analysis_prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.3,
#                 "maxOutputTokens": 4096,
#             }
#         }

#         analyze_result, analyze_error = make_gemini_request(GEMINI_TEXT_URL, analyze_body, GEMINI_API_KEYS)

#         if not analyze_result or 'candidates' not in analyze_result or len(analyze_result['candidates']) == 0:
#             return jsonify({
#                 'success': True,
#                 'generated_text': generated_text,
#                 'analysis': f'Analysis failed: {analyze_error}',
#                 'error_in_analysis': True
#             })

#         analysis_text = analyze_result['candidates'][0]['content']['parts'][0]['text'].strip()

#         return jsonify({
#             'success': True,
#             'generated_text': generated_text,
#             'analysis': analysis_text
#         })

#     except Exception as e:
#         return jsonify({
#             'error': f'Error in generate and analyze: {str(e)}',
#             'success': False
#         }), 500


# # ========== Health Check Endpoint ==========
# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({
#         'status': 'healthy',
#         'message': 'Enhanced Arabic Text Analyzer API is running',
#         'api_keys_count': len(GEMINI_API_KEYS),
#         'endpoints': {
#             'ocr': '/ocr - Extract Arabic text from images',
#             'analyze_arabic': '/analyze_arabic - Analyze Arabic text for errors',
#             'ocr_and_analyze': '/ocr_and_analyze - Combined OCR + Analysis',
#             'generate_arabic': '/generate_arabic - Generate Arabic text', 
#             'generate_and_analyze': '/generate_and_analyze - Generate + Analyze'
#         }
#     })


# if __name__ == '__main__':
#     print("Starting Enhanced Arabic Text Analyzer API...")
#     print(f"Using {len(GEMINI_API_KEYS)} API keys for fallback")
#     print("Available endpoints:")
#     print("   - POST /ocr - Extract Arabic text from images")
#     print("   - POST /analyze_arabic - Detailed Arabic text analysis")
#     print("   - POST /ocr_and_analyze - Combined OCR + Analysis (like Colab)")
#     print("   - POST /generate_arabic - Generate Arabic text")  
#     print("   - POST /generate_and_analyze - Generate + Analyze")
#     print("   - GET /health - Health check")
#     print(f"Server running on http://localhost:5000")
    
#     app.run(debug=True, port=5000, host='0.0.0.0')

# -----------

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import requests
import base64
import json  # pyright: ignore[reportUnusedImport]
import io
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# 🔑 Multiple API Keys for fallback
GEMINI_API_KEYS = [
    "AIzaSyAr-MKvNqz2KwULeAb8MmxQSImcKIU1DCs",
    # "AIzaSyBTmB82qstoN_jyqWLk5ZdDWcY_oZINvmo",
    # "AIzaSyDH1gH8aawtYUa-pPQHqOMwjl4ziPyL-Qk",
    # "AIzaSyAHzRxPzIov7LZDs47QnhwHvwPEfNFWfV4", 
    # "AIzaSyD6XObCpKK03BVP0SshWm4KV_noh-HCjCo", 
]

GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def encode_image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    if image.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def clean_arabic_text(text):
    """Clean Arabic text - PRESERVE HAROKAT (tashkeel)"""
    if not text:
        return ""
    
    # Only remove English explanations, NOT Arabic diacritics
    english_patterns = [
        r"Berikut (adalah )?teks Arab.*?:",
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
        r"\*\*.*?\*\*",  # Remove markdown bold
        r"[A-Za-z]{5,}.*?Arabic.*?\.",
    ]
    
    cleaned_text = text
    
    # Remove English patterns
    for pattern in english_patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove lines that are purely English (but keep Arabic with harokat)
    lines = cleaned_text.split('\n')
    arabic_lines = []
    for line in lines:
        # Check if line contains Arabic characters (including harokat)
        if re.search(r'[\u0600-\u06FF]', line):
            arabic_lines.append(line)
    
    cleaned_text = '\n'.join(arabic_lines)
    
    # Clean excessive whitespace but preserve structure
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)
    cleaned_text = re.sub(r' {3,}', ' ', cleaned_text)
    
    return cleaned_text.strip()

def make_gemini_request(url, body, api_keys):
    """Make request to Gemini API with fallback across multiple keys"""
    headers = {"Content-Type": "application/json"}
    
    for i, api_key in enumerate(api_keys):
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
                print(f"[!] API key {i+1} failed with status {response.status_code}: {response.text[:100]}...")
                continue
                
        except Exception as e:
            print(f"[!] API key {i+1} failed with error: {str(e)}")
            continue
    
    return None, "All API keys failed"

# ========== 1️⃣ FIXED OCR Endpoint - Preserve Harokat ==========
@app.route('/ocr', methods=['POST'])
def ocr_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided', 'success': False}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file', 'success': False}), 400

        image = Image.open(file.stream)
        base64_image = encode_image_to_base64(image)
        
        # IMPROVED PROMPT - Explicitly request harokat preservation
        body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": """استخرج النص العربي من هذه الصورة بدقة عالية.

⚠️ مهم جداً:
1. احتفظ بجميع الحركات (الفتحة، الضمة، الكسرة، السكون، الشدة، التنوين) كما هي في الصورة
2. لا تضف أي تفسير أو شرح باللغة الإنجليزية أو العربية
3. أعد كتابة النص العربي فقط مع الحركات الكاملة (التشكيل الكامل)
4. احتفظ بتنسيق النص كما هو في الصورة

النص العربي المطلوب:"""
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
                "temperature": 0.1,  # Low temperature for accuracy
                "maxOutputTokens": 2048,
            }
        }
        
        result, error = make_gemini_request(GEMINI_VISION_URL, body, GEMINI_API_KEYS)
        
        if result and 'candidates' in result and len(result['candidates']) > 0:
            extracted_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Clean but preserve harokat
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


# ========== 2️⃣ FIXED Arabic Analysis - Handle Harokat ==========
@app.route('/analyze_arabic', methods=['POST'])
def analyze_arabic():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided', 'success': False}), 400
            
        arabic_text = data.get('text', '')

        if not arabic_text.strip():
            return jsonify({'error': 'No text provided', 'success': False}), 400

        # Analysis prompt that respects harokat
        prompt = f"""قم بتحليل وتصحيح الأخطاء في النص التالي مع المحافظة على الحركات (التشكيل):

**1. أخطاء النحو:**
اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
الخطأ_النحوي1 -> التصحيح_النحوي1
الخطأ_النحوي2 -> التصحيح_النحوي2

**2. أخطاء الصرف:**
اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
الخطأ_الصرفي1 -> التصحيح_الصرفي1
الخطأ_الصرفي2 -> التصحيح_الصرفي2

**3. أخطاء الإملاء:**
اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
الخطأ_الإملائي1 -> التصحيح_الإملائي1
الخطأ_الإملائي2 -> التصحيح_الإملائي2

**4. أخطاء التركيب:**
اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
الخطأ_التركيبي1 -> التصحيح_التركيبي1
الخطأ_التركيبي2 -> التصحيح_التركيبي2

**5. أخطاء الحركات (التشكيل):**
اذكر أخطاء الحركات وتصحيحها بهذا الشكل:
الخطأ_في_التشكيل1 -> التصحيح_في_التشكيل1
الخطأ_في_التشكيل2 -> التصحيح_في_التشكيل2

**النص المُصحح كاملاً:**
اكتب النص كاملاً بعد التصحيح مع الحركات الصحيحة

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


# ========== 3️⃣ FIXED Combined OCR + Analysis ==========
@app.route('/ocr_and_analyze', methods=['POST'])
def ocr_and_analyze():
    """Combined OCR and Analysis - Preserve harokat"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided', 'success': False}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file', 'success': False}), 400

        # Step 1: OCR with harokat preservation
        print("Performing OCR with Gemini (preserving harokat)...")
        image = Image.open(file.stream)
        base64_image = encode_image_to_base64(image)
        
        ocr_body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": """استخرج النص العربي من هذه الصورة بدقة عالية.

⚠️ مهم جداً:
1. احتفظ بجميع الحركات (الفتحة، الضمة، الكسرة، السكون، الشدة، التنوين) كما هي في الصورة
2. لا تضف أي تفسير أو شرح باللغة الإنجليزية أو العربية
3. أعد كتابة النص العربي فقط مع الحركات الكاملة (التشكيل الكامل)
4. احتفظ بتنسيق النص كما هو في الصورة

النص العربي المطلوب:"""
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
        
        ocr_result, ocr_error = make_gemini_request(GEMINI_VISION_URL, ocr_body, GEMINI_API_KEYS)
        
        if not ocr_result or 'candidates' not in ocr_result or len(ocr_result['candidates']) == 0:
            return jsonify({
                'error': f'OCR failed: {ocr_error}',
                'success': False
            }), 500
            
        extracted_text = ocr_result['candidates'][0]['content']['parts'][0]['text']
        cleaned_extracted_text = clean_arabic_text(extracted_text)
        
        print("Performing Language Analysis...")
        
        # Step 2: Analysis
        analysis_prompt = f"""قم بتحليل وتصحيح الأخطاء في النص التالي مع المحافظة على الحركات (التشكيل):

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

**5. أخطاء الحركات (التشكيل):**
اذكر أخطاء الحركات وتصحيحها بهذا الشكل:
الخطأ_في_التشكيل1 -> التصحيح_في_التشكيل1

**النص المُصحح كاملاً:**
اكتب النص كاملاً بعد التصحيح مع الحركات الصحيحة

**النص المراد تصحيحه:**
{cleaned_extracted_text}

ملاحظة: إذا لم توجد أخطاء في أي قسم، اكتب "لا توجد أخطاء" تحت ذلك القسم.
"""

        analysis_body = {
            "contents": [
                {
                    "parts": [
                        {"text": analysis_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4096,
            }
        }
        
        analysis_result, analysis_error = make_gemini_request(GEMINI_TEXT_URL, analysis_body, GEMINI_API_KEYS)
        
        if not analysis_result or 'candidates' not in analysis_result or len(analysis_result['candidates']) == 0:
            return jsonify({
                'success': True,
                'extracted_text': cleaned_extracted_text,
                'analysis': f'Analysis failed: {analysis_error}',
                'error_in_analysis': True
            })
            
        analysis_text = analysis_result['candidates'][0]['content']['parts'][0]['text']
        
        return jsonify({
            'success': True,
            'extracted_text': cleaned_extracted_text,
            'analysis': analysis_text.strip(),
            'message': 'OCR and analysis completed successfully',
            'raw_extracted_text': extracted_text
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error in OCR and analysis: {str(e)}',
            'success': False
        }), 500


# ========== 4️⃣ Generate Arabic Text ==========
@app.route('/generate_arabic', methods=['POST'])
def generate_arabic():
    try:
        data = request.json
        if not data:
            data = {}
            
        prompt = data.get('prompt', 'اكتب لي نصا عربيا قصيرا')

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{prompt}\n\nملاحظة: اكتب النص بالتشكيل الكامل (مع الحركات)."}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            }
        }

        result, error = make_gemini_request(GEMINI_TEXT_URL, body, GEMINI_API_KEYS)
        
        if result and 'candidates' in result and len(result['candidates']) > 0:
            generated_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
            return jsonify({
                'success': True,
                'generated_text': generated_text
            })
        else:
            return jsonify({
                'error': error or 'Failed to generate text',
                'success': False
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': f'Error generating text: {str(e)}',
            'success': False
        }), 500


# ========== 5️⃣ Generate + Analyze Combined ==========
@app.route('/generate_and_analyze', methods=['POST'])
def generate_and_analyze():
    try:
        data = request.json
        if not data:
            data = {}
            
        prompt = data.get('prompt', 'اكتب لي نصا عربيا قصيرا')

        # Step 1: Generate text with harokat
        generate_body = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{prompt}\n\nملاحظة: اكتب النص بالتشكيل الكامل (مع الحركات)."}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            }
        }

        gen_result, gen_error = make_gemini_request(GEMINI_TEXT_URL, generate_body, GEMINI_API_KEYS)
        
        if not gen_result or 'candidates' not in gen_result or len(gen_result['candidates']) == 0:
            return jsonify({
                'error': f'Text generation failed: {gen_error}',
                'success': False
            }), 500

        generated_text = gen_result['candidates'][0]['content']['parts'][0]['text'].strip()

        # Step 2: Analyze
        analysis_prompt = f"""قم بتحليل وتصحيح الأخطاء في النص التالي مع المحافظة على الحركات (التشكيل):

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

**5. أخطاء الحركات (التشكيل):**
اذكر أخطاء الحركات وتصحيحها بهذا الشكل:
الخطأ_في_التشكيل1 -> التصحيح_في_التشكيل1

**النص المُصحح كاملاً:**
اكتب النص كاملاً بعد التصحيح مع الحركات الصحيحة

**النص المراد تصحيحه:**
{generated_text}

ملاحظة: إذا لم توجد أخطاء في أي قسم، اكتب "لا توجد أخطاء" تحت ذلك القسم.
"""

        analyze_body = {
            "contents": [
                {
                    "parts": [
                        {"text": analysis_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4096,
            }
        }

        analyze_result, analyze_error = make_gemini_request(GEMINI_TEXT_URL, analyze_body, GEMINI_API_KEYS)

        if not analyze_result or 'candidates' not in analyze_result or len(analyze_result['candidates']) == 0:
            return jsonify({
                'success': True,
                'generated_text': generated_text,
                'analysis': f'Analysis failed: {analyze_error}',
                'error_in_analysis': True
            })

        analysis_text = analyze_result['candidates'][0]['content']['parts'][0]['text'].strip()

        return jsonify({
            'success': True,
            'generated_text': generated_text,
            'analysis': analysis_text
        })

    except Exception as e:
        return jsonify({
            'error': f'Error in generate and analyze: {str(e)}',
            'success': False
        }), 500


# ========== Health Check Endpoint ==========
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Enhanced Arabic Text Analyzer API with Harokat Support',
        'api_keys_count': len(GEMINI_API_KEYS),
        'features': ['OCR with harokat', 'Grammar analysis', 'Tashkeel detection'],
        'endpoints': {
            'ocr': '/ocr - Extract Arabic text with harokat from images',
            'analyze_arabic': '/analyze_arabic - Analyze Arabic text including tashkeel',
            'ocr_and_analyze': '/ocr_and_analyze - Combined OCR + Analysis',
            'generate_arabic': '/generate_arabic - Generate Arabic text with harokat', 
            'generate_and_analyze': '/generate_and_analyze - Generate + Analyze'
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Starting Enhanced Arabic Text Analyzer API")
    print("✅ Harokat (Tashkeel) Preservation Enabled")
    print("=" * 60)
    print(f"Using {len(GEMINI_API_KEYS)} API keys for fallback")
    print("\nAvailable endpoints:")
    print("   - POST /ocr - Extract Arabic text WITH HAROKAT from images")
    print("   - POST /analyze_arabic - Detailed Arabic text analysis")
    print("   - POST /ocr_and_analyze - Combined OCR + Analysis")
    print("   - POST /generate_arabic - Generate Arabic text with harokat")  
    print("   - POST /generate_and_analyze - Generate + Analyze")
    print("   - GET /health - Health check")
    print(f"\n🚀 Server running on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')

    
# versi old
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from PIL import Image
# import requests
# import base64
# import json
# import io
# import re

# from flask import jsonify
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# # 🔑 Multiple API Keys for fallback - ganti dengan API keys milikmu
# GEMINI_API_KEYS = [
#     # pakai yang no 1 
#         "AIzaSyAHzRxPzIov7LZDs47QnhwHvwPEfNFWfV4",

#         "AIzaSyD6XObCpKK03BVP0SshWm4KV_noh-HCjCo", 

#     "AIzaSyDvo1FDQbtVtLxpGk1E40_xE0wv3xtpuys", 
# ]

# # Ganti di kode Anda:
# GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
# GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
# def encode_image_to_base64(image):
#     """Convert PIL Image to base64 string"""
#     buffered = io.BytesIO()
#     # Convert to RGB if image has transparency (RGBA)
#     if image.mode in ('RGBA', 'LA'):
#         background = Image.new('RGB', image.size, (255, 255, 255))
#         background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
#         image = background
#     image.save(buffered, format="JPEG", quality=85)
#     return base64.b64encode(buffered.getvalue()).decode('utf-8')

# def clean_arabic_text(text):
#     """Clean Arabic text from unwanted English explanations"""
#     if not text:
#         return ""
    
#     # Remove common English phrases that appear in OCR results
#     english_patterns = [
#         r"Berikut teks Arab.*?:",
#         r"There are some.*?differences.*?\.",
#         r"I have corrected.*?\.",
#         r"The most significant difference.*?\.",
#         r"based on my understanding.*?\.",
#         r"common Arabic spelling.*?\.",
#         r"where the OCR.*?\.",
#         r"Here is the.*?:",
#         r"The Arabic text.*?:",
#         r"OCR misinterprets.*?\.",
#         r"Some minor.*?transcription\.",
#         r"[A-Za-z].*?spelling\.",
#         r".*?significant difference.*?\.",
#         r".*?understanding.*?context.*?\.",
#         r"\n\n[A-Za-z].*",  # Remove paragraph starting with English
#         r"[A-Za-z]{3,}.*?Arabic.*?\.",  # Remove English sentences mentioning Arabic
#     ]
    
#     cleaned_text = text
#     for pattern in english_patterns:
#         cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    
#     # Remove excessive whitespace and newlines
#     cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
#     cleaned_text = re.sub(r'\s{3,}', ' ', cleaned_text)
    
#     return cleaned_text.strip()

# def make_gemini_request(url, body, api_keys):
#     """Make request to Gemini API with fallback across multiple keys"""
#     headers = {"Content-Type": "application/json"}
    
#     for i, api_key in enumerate(api_keys):
#         try:
#             response = requests.post(
#                 f"{url}?key={api_key}",
#                 headers=headers,
#                 json=body,
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 return response.json(), None
#             else:
#                 print(f"[!] API key {i+1} failed with status {response.status_code}: {response.text[:100]}...")
#                 continue
                
#         except Exception as e:
#             print(f"[!] API key {i+1} failed with error: {str(e)}")
#             continue
    
#     return None, "All API keys failed"

# # ========== 1️⃣ Enhanced OCR Endpoint ==========
# @app.route('/ocr', methods=['POST'])
# def ocr_image():
#     try:
#         if 'image' not in request.files:
#             return jsonify({'error': 'No image file provided', 'success': False}), 400

#         file = request.files['image']
#         if file.filename == '':
#             return jsonify({'error': 'No selected file', 'success': False}), 400

#         # Open and process image
#         image = Image.open(file.stream)
        
#         # Convert image to base64
#         base64_image = encode_image_to_base64(image)
        
#         # Improved prompt to avoid English explanations
#         body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {
#                             "text": "استخرج النص العربي من هذه الصورة بدقة. أريد النص العربي فقط بدون أي تفسير أو تعليق إضافي."
#                         },
#                         {
#                             "inline_data": {
#                                 "mime_type": "image/jpeg",
#                                 "data": base64_image
#                             }
#                         }
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.1,
#                 "maxOutputTokens": 2048,
#             }
#         }
        
#         # Make request with fallback API keys
#         result, error = make_gemini_request(GEMINI_VISION_URL, body, GEMINI_API_KEYS)
        
#         if result and 'candidates' in result and len(result['candidates']) > 0:
#             extracted_text = result['candidates'][0]['content']['parts'][0]['text']
            
#             # Clean the extracted text
#             cleaned_text = clean_arabic_text(extracted_text)
            
#             return jsonify({
#                 'text': cleaned_text,
#                 'success': True,
#                 'raw_text': extracted_text  # Include raw text for debugging
#             })
#         else:
#             return jsonify({
#                 'error': error or 'Failed to extract text from image',
#                 'success': False
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'error': f'Error processing image: {str(e)}',
#             'success': False
#         }), 500


# # ========== 2️⃣ Enhanced Arabic Analysis ==========
# @app.route('/analyze_arabic', methods=['POST'])
# def analyze_arabic():
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'No JSON data provided', 'success': False}), 400
            
#         arabic_text = data.get('text', '')

#         if not arabic_text.strip():
#             return jsonify({'error': 'No text provided', 'success': False}), 400

#         # Use the same detailed prompt as the Colab version
#         prompt = f"""
# قم بتصحيح الأخطاء في النص التالي:

# **1. أخطاء النحو:**
# اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
# الخطأ_النحوي1 -> التصحيح_النحوي1
# الخطأ_النحوي2 -> التصحيح_النحوي2

# **2. أخطاء الصرف:**
# اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
# الخطأ_الصرفي1 -> التصحيح_الصرفي1
# الخطأ_الصرفي2 -> التصحيح_الصرفي2

# **3. أخطاء الإملاء:**
# اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
# الخطأ_الإملائي1 -> التصحيح_الإملائي1
# الخطأ_الإملائي2 -> التصحيح_الإملائي2

# **4. أخطاء التركيب:**
# اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
# الخطأ_التركيبي1 -> التصحيح_التركيبي1
# الخطأ_التركيبي2 -> التصحيح_التركيبي2

# **النص المُصحح كاملاً:**
# اكتب النص كاملاً بعد التصحيح

# **النص المراد تصحيحه:**
# {arabic_text}

# ملاحظة: إذا لم توجد أخطاء في أي قسم، اكتب "لا توجد أخطاء" تحت ذلك القسم.
# """

#         body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.3,
#                 "maxOutputTokens": 4096,
#             }
#         }

#         result, error = make_gemini_request(GEMINI_TEXT_URL, body, GEMINI_API_KEYS)
        
#         if result and 'candidates' in result and len(result['candidates']) > 0:
#             analysis_text = result['candidates'][0]['content']['parts'][0]['text']
            
#             return jsonify({
#                 'success': True,
#                 'analysis': analysis_text.strip(),
#                 'raw_response': analysis_text
#             })
#         else:
#             return jsonify({
#                 'error': error or 'Failed to analyze text',
#                 'success': False
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'error': f'Error analyzing text: {str(e)}',
#             'success': False
#         }), 500


# # ========== 3️⃣ Combined OCR + Analysis Endpoint ==========
# @app.route('/ocr_and_analyze', methods=['POST'])
# def ocr_and_analyze():
#     """Combined OCR and Analysis like the Colab version"""
#     try:
#         if 'image' not in request.files:
#             return jsonify({'error': 'No image file provided', 'success': False}), 400

#         file = request.files['image']
#         if file.filename == '':
#             return jsonify({'error': 'No selected file', 'success': False}), 400

#         # Step 1: OCR
#         print("Performing OCR with Gemini...")
#         image = Image.open(file.stream)
#         base64_image = encode_image_to_base64(image)
        
#         ocr_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {
#                             "text": "استخرج النص العربي من هذه الصورة بدقة. أريد النص العربي فقط بدون أي تفسير أو تعليق إضافي."
#                         },
#                         {
#                             "inline_data": {
#                                 "mime_type": "image/jpeg",
#                                 "data": base64_image
#                             }
#                         }
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.1,
#                 "maxOutputTokens": 2048,
#             }
#         }
        
#         ocr_result, ocr_error = make_gemini_request(GEMINI_VISION_URL, ocr_body, GEMINI_API_KEYS)
        
#         if not ocr_result or 'candidates' not in ocr_result or len(ocr_result['candidates']) == 0:
#             return jsonify({
#                 'error': f'OCR failed: {ocr_error}',
#                 'success': False
#             }), 500
            
#         extracted_text = ocr_result['candidates'][0]['content']['parts'][0]['text']
#         cleaned_extracted_text = clean_arabic_text(extracted_text)
        
#         print("Performing Language Analysis...")
        
#         # Step 2: Analysis using the same prompt as Colab
#         analysis_prompt = f"""
# قم بتصحيح الأخطاء في النص التالي:

# **1. أخطاء النحو:**
# اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
# الخطأ_النحوي1 -> التصحيح_النحوي1
# الخطأ_النحوي2 -> التصحيح_النحوي2

# **2. أخطاء الصرف:**
# اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
# الخطأ_الصرفي1 -> التصحيح_الصرفي1
# الخطأ_الصرفي2 -> التصحيح_الصرفي2

# **3. أخطاء الإملاء:**
# اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
# الخطأ_الإملائي1 -> التصحيح_الإملائي1
# الخطأ_الإملائي2 -> التصحيح_الإملائي2

# **4. أخطاء التركيب:**
# اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
# الخطأ_التركيبي1 -> التصحيح_التركيبي1
# الخطأ_التركيبي2 -> التصحيح_التركيبي2

# **النص المُصحح كاملاً:**
# اكتب النص كاملاً بعد التصحيح

# **النص المراد تصحيحه:**
# {cleaned_extracted_text}

# ملاحظة: إذا لم توجد أخطاء في أي قسم، اكتب "لا توجد أخطاء" تحت ذلك القسم.
# """

#         analysis_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": analysis_prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.3,
#                 "maxOutputTokens": 4096,
#             }
#         }
        
#         analysis_result, analysis_error = make_gemini_request(GEMINI_TEXT_URL, analysis_body, GEMINI_API_KEYS)
        
#         if not analysis_result or 'candidates' not in analysis_result or len(analysis_result['candidates']) == 0:
#             return jsonify({
#                 'success': True,
#                 'extracted_text': cleaned_extracted_text,
#                 'analysis': f'Analysis failed: {analysis_error}',
#                 'error_in_analysis': True
#             })
            
#         analysis_text = analysis_result['candidates'][0]['content']['parts'][0]['text']
        
#         return jsonify({
#             'success': True,
#             'extracted_text': cleaned_extracted_text,
#             'analysis': analysis_text.strip(),
#             'message': 'OCR and analysis completed successfully',
#             'raw_extracted_text': extracted_text  # Include for debugging
#         })
        
#     except Exception as e:
#         return jsonify({
#             'error': f'Error in OCR and analysis: {str(e)}',
#             'success': False
#         }), 500


# # ========== 4️⃣ Generate Arabic Text ==========
# @app.route('/generate_arabic', methods=['POST'])
# def generate_arabic():
#     try:
#         data = request.json
#         if not data:
#             data = {}
            
#         prompt = data.get('prompt', 'اكتب لي نصا عربيا قصيرا')

#         body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.7,
#                 "maxOutputTokens": 1024,
#             }
#         }

#         result, error = make_gemini_request(GEMINI_TEXT_URL, body, GEMINI_API_KEYS)
        
#         if result and 'candidates' in result and len(result['candidates']) > 0:
#             generated_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
#             return jsonify({
#                 'success': True,
#                 'generated_text': generated_text
#             })
#         else:
#             return jsonify({
#                 'error': error or 'Failed to generate text',
#                 'success': False
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             'error': f'Error generating text: {str(e)}',
#             'success': False
#         }), 500


# # ========== 5️⃣ Generate + Analyze Combined ==========
# @app.route('/generate_and_analyze', methods=['POST'])
# def generate_and_analyze():
#     try:
#         data = request.json
#         if not data:
#             data = {}
            
#         prompt = data.get('prompt', 'اكتب لي نصا عربيا قصيرا')

#         # Step 1: Generate text
#         generate_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.7,
#                 "maxOutputTokens": 1024,
#             }
#         }

#         gen_result, gen_error = make_gemini_request(GEMINI_TEXT_URL, generate_body, GEMINI_API_KEYS)
        
#         if not gen_result or 'candidates' not in gen_result or len(gen_result['candidates']) == 0:
#             return jsonify({
#                 'error': f'Text generation failed: {gen_error}',
#                 'success': False
#             }), 500

#         generated_text = gen_result['candidates'][0]['content']['parts'][0]['text'].strip()

#         # Step 2: Analyze the generated text
#         analysis_prompt = f"""
# قم بتصحيح الأخطاء في النص التالي:

# **1. أخطاء النحو:**
# اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
# الخطأ_النحوي1 -> التصحيح_النحوي1
# الخطأ_النحوي2 -> التصحيح_النحوي2

# **2. أخطاء الصرف:**
# اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
# الخطأ_الصرفي1 -> التصحيح_الصرفي1
# الخطأ_الصرفي2 -> التصحيح_الصرفي2

# **3. أخطاء الإملاء:**
# اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
# الخطأ_الإملائي1 -> التصحيح_الإملائي1
# الخطأ_الإملائي2 -> التصحيح_الإملائي2

# **4. أخطاء التركيب:**
# اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
# الخطأ_التركيبي1 -> التصحيح_التركيبي1
# الخطأ_التركيبي2 -> التصحيح_التركيبي2

# **النص المُصحح كاملاً:**
# اكتب النص كاملاً بعد التصحيح

# **النص المراد تصحيحه:**
# {generated_text}

# ملاحظة: إذا لم توجد أخطاء في أي قسم، اكتب "لا توجد أخطاء" تحت ذلك القسم.
# """

#         analyze_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": analysis_prompt}
#                     ]
#                 }
#             ],
#             "generationConfig": {
#                 "temperature": 0.3,
#                 "maxOutputTokens": 4096,
#             }
#         }

#         analyze_result, analyze_error = make_gemini_request(GEMINI_TEXT_URL, analyze_body, GEMINI_API_KEYS)

#         if not analyze_result or 'candidates' not in analyze_result or len(analyze_result['candidates']) == 0:
#             return jsonify({
#                 'success': True,
#                 'generated_text': generated_text,
#                 'analysis': f'Analysis failed: {analyze_error}',
#                 'error_in_analysis': True
#             })

#         analysis_text = analyze_result['candidates'][0]['content']['parts'][0]['text'].strip()

#         return jsonify({
#             'success': True,
#             'generated_text': generated_text,
#             'analysis': analysis_text
#         })

#     except Exception as e:
#         return jsonify({
#             'error': f'Error in generate and analyze: {str(e)}',
#             'success': False
#         }), 500


# # ========== Health Check Endpoint ==========
# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({
#         'status': 'healthy',
#         'message': 'Enhanced Arabic Text Analyzer API is running',
#         'api_keys_count': len(GEMINI_API_KEYS),
#         'endpoints': {
#             'ocr': '/ocr - Extract Arabic text from images',
#             'analyze_arabic': '/analyze_arabic - Analyze Arabic text for errors',
#             'ocr_and_analyze': '/ocr_and_analyze - Combined OCR + Analysis',
#             'generate_arabic': '/generate_arabic - Generate Arabic text', 
#             'generate_and_analyze': '/generate_and_analyze - Generate + Analyze'
#         }
#     })


# if __name__ == '__main__':
#     print("Starting Enhanced Arabic Text Analyzer API...")
#     print(f"Using {len(GEMINI_API_KEYS)} API keys for fallback")
#     print("Available endpoints:")
#     print("   - POST /ocr - Extract Arabic text from images")
#     print("   - POST /analyze_arabic - Detailed Arabic text analysis")
#     print("   - POST /ocr_and_analyze - Combined OCR + Analysis (like Colab)")
#     print("   - POST /generate_arabic - Generate Arabic text")  
#     print("   - POST /generate_and_analyze - Generate + Analyze")
#     print("   - GET /health - Health check")
#     print(f"Server running on http://localhost:5000")
    
#     app.run(debug=True, port=5000, host='0.0.0.0')
