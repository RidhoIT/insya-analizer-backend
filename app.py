
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from PIL import Image
# import requests
# import base64
# import io
# import re

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# # 🔑 Multiple API Keys for fallback
# GEMINI_API_KEYS = [
#     "AIzaSyB-BAHNETcF6QNDL6AHVxGJRoikRYZRy6I",
#     # Tambahkan API key lainnya di sini
# ]

# # URL untuk model yang tersedia
# GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
# GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# def encode_image_to_base64(image):
#     """Convert PIL Image to base64 string"""
#     try:
#         buffered = io.BytesIO()
#         if image.mode in ('RGBA', 'LA', 'P'):
#             background = Image.new('RGB', image.size, (255, 255, 255))
#             if image.mode == 'P':
#                 image = image.convert('RGBA')
#             background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
#             image = background
#         elif image.mode not in ('RGB', 'L'):
#             image = image.convert('RGB')
        
#         image.save(buffered, format="JPEG", quality=85)
#         return base64.b64encode(buffered.getvalue()).decode('utf-8')
#     except Exception as e:
#         print(f"Error encoding image: {str(e)}")
#         raise

# def clean_arabic_text(text):
#     """Clean Arabic text - PRESERVE HAROKAT (tashkeel)"""
#     if not text:
#         return ""
    
#     # Only remove English explanations, NOT Arabic diacritics
#     english_patterns = [
#         r"Berikut (adalah )?teks Arab.*?:",
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
#         r"\*\*.*?\*\*",  # Remove markdown bold
#         r"[A-Za-z]{5,}.*?Arabic.*?\.",
#     ]
    
#     cleaned_text = text
    
#     # Remove English patterns
#     for pattern in english_patterns:
#         cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    
#     # Remove lines that are purely English (but keep Arabic with harokat)
#     lines = cleaned_text.split('\n')
#     arabic_lines = []
#     for line in lines:
#         # Check if line contains Arabic characters (including harokat)
#         if re.search(r'[\u0600-\u06FF]', line):
#             arabic_lines.append(line)
    
#     cleaned_text = '\n'.join(arabic_lines)
    
#     # Clean excessive whitespace but preserve structure
#     cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)
#     cleaned_text = re.sub(r' {3,}', ' ', cleaned_text)
    
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
#                 result = response.json()
                
#                 # Validasi response
#                 if 'candidates' not in result or len(result['candidates']) == 0:
#                     print(f"[!] API key {i+1}: No candidates in response")
#                     continue
                    
#                 if 'content' not in result['candidates'][0]:
#                     print(f"[!] API key {i+1}: No content in candidate")
#                     continue
                    
#                 if 'parts' not in result['candidates'][0]['content']:
#                     print(f"[!] API key {i+1}: No parts in content")
#                     continue
                
#                 return result, None
                
#             elif response.status_code == 429:
#                 print(f"[!] API key {i+1} rate limited, trying next key...")
#                 continue
#             elif response.status_code == 400:
#                 error_text = response.text
#                 print(f"[!] API key {i+1} bad request: {error_text[:200]}...")
#                 return None, f"Bad request: {error_text[:200]}"
#             else:
#                 print(f"[!] API key {i+1} failed with status {response.status_code}: {response.text[:100]}...")
#                 continue
                
#         except requests.exceptions.Timeout:
#             print(f"[!] API key {i+1} timeout")
#             continue
#         except Exception as e:
#             print(f"[!] API key {i+1} failed with error: {str(e)}")
#             continue
    
#     return None, "All API keys failed or rate limited"

# # ========== 1️⃣ FIXED OCR Endpoint - Preserve Harokat ==========
# @app.route('/ocr', methods=['POST'])
# def ocr_image():
#     try:
#         if 'image' not in request.files:
#             return jsonify({'error': 'No image file provided', 'success': False}), 400

#         file = request.files['image']
#         if file.filename == '':
#             return jsonify({'error': 'No selected file', 'success': False}), 400

#         image = Image.open(file.stream)
#         base64_image = encode_image_to_base64(image)
        
#         # IMPROVED PROMPT - Explicitly request harokat preservation
#         body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {
#                             "text": """استخرج النص العربي من هذه الصورة بدقة عالية.

# ⚠️ مهم جداً:
# 1. احتفظ بجميع الحركات (الفتحة، الضمة، الكسرة، السكون، الشدة، التنوين) كما هي في الصورة
# 2. لا تضف أي تفسير أو شرح باللغة الإنجليزية أو العربية
# 3. أعد كتابة النص العربي فقط مع الحركات الكاملة (التشكيل الكامل)
# 4. احتفظ بتنسيق النص كما هو في الصورة

# النص العربي المطلوب:"""
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
        
#         result, error = make_gemini_request(GEMINI_VISION_URL, body, GEMINI_API_KEYS)
        
#         if result and 'candidates' in result and len(result['candidates']) > 0:
#             extracted_text = result['candidates'][0]['content']['parts'][0]['text']
#             cleaned_text = clean_arabic_text(extracted_text)
            
#             return jsonify({
#                 'text': cleaned_text,
#                 'success': True,
#                 'raw_text': extracted_text
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


# # ========== 2️⃣ FIXED Arabic Analysis - Handle Harokat ==========
# @app.route('/analyze_arabic', methods=['POST'])
# def analyze_arabic():
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'No JSON data provided', 'success': False}), 400
            
#         arabic_text = data.get('text', '')

#         if not arabic_text.strip():
#             return jsonify({'error': 'No text provided', 'success': False}), 400

#         # Analysis prompt that respects harokat
#         prompt = f"""قم بتحليل وتصحيح الأخطاء في النص التالي مع المحافظة على الحركات (التشكيل):

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

# **5. أخطاء الحركات (التشكيل):**
# اذكر أخطاء الحركات وتصحيحها بهذا الشكل:
# الخطأ_في_التشكيل1 -> التصحيح_في_التشكيل1
# الخطأ_في_التشكيل2 -> التصحيح_في_التشكيل2

# **النص المُصحح كاملاً:**
# اكتب النص كاملاً بعد التصحيح مع الحركات الصحيحة

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


# # ========== 3️⃣ FIXED Combined OCR + Analysis ==========
# @app.route('/ocr_and_analyze', methods=['POST'])
# def ocr_and_analyze():
#     """Combined OCR and Analysis - Preserve harokat"""
#     try:
#         if 'image' not in request.files:
#             return jsonify({'error': 'No image file provided', 'success': False}), 400

#         file = request.files['image']
#         if file.filename == '':
#             return jsonify({'error': 'No selected file', 'success': False}), 400

#         # Step 1: OCR with harokat preservation
#         print("Performing OCR with Gemini (preserving harokat)...")
#         image = Image.open(file.stream)
#         base64_image = encode_image_to_base64(image)
        
#         ocr_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {
#                             "text": """استخرج النص العربي من هذه الصورة بدقة عالية.

# ⚠️ مهم جداً:
# 1. احتفظ بجميع الحركات (الفتحة، الضمة، الكسرة، السكون، الشدة، التنوين) كما هي في الصورة
# 2. لا تضف أي تفسير أو شرح باللغة الإنجليزية أو العربية
# 3. أعد كتابة النص العربي فقط مع الحركات الكاملة (التشكيل الكامل)
# 4. احتفظ بتنسيق النص كما هو في الصورة

# النص العربي المطلوب:"""
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
        
#         # Step 2: Analysis
#         analysis_prompt = f"""قم بتحليل وتصحيح الأخطاء في النص التالي مع المحافظة على الحركات (التشكيل):

# **1. أخطاء النحو:**
# اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
# الخطأ_النحوي1 -> التصحيح_النحوي1

# **2. أخطاء الصرف:**
# اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
# الخطأ_الصرفي1 -> التصحيح_الصرفي1

# **3. أخطاء الإملاء:**
# اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
# الخطأ_الإملائي1 -> التصحيح_الإملائي1

# **4. أخطاء التركيب:**
# اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
# الخطأ_التركيبي1 -> التصحيح_التركيبي1

# **5. أخطاء الحركات (التشكيل):**
# اذكر أخطاء الحركات وتصحيحها بهذا الشكل:
# الخطأ_في_التشكيل1 -> التصحيح_في_التشكيل1

# **النص المُصحح كاملاً:**
# اكتب النص كاملاً بعد التصحيح مع الحركات الصحيحة

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
#             'raw_extracted_text': extracted_text
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
#                         {"text": f"{prompt}\n\nملاحظة: اكتب النص بالتشكيل الكامل (مع الحركات)."}
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

#         # Step 1: Generate text with harokat
#         generate_body = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": f"{prompt}\n\nملاحظة: اكتب النص بالتشكيل الكامل (مع الحركات)."}
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

#         # Step 2: Analyze
#         analysis_prompt = f"""قم بتحليل وتصحيح الأخطاء في النص التالي مع المحافظة على الحركات (التشكيل):

# **1. أخطاء النحو:**
# اذكر الأخطاء النحوية وتصحيحها بهذا الشكل:
# الخطأ_النحوي1 -> التصحيح_النحوي1

# **2. أخطاء الصرف:**
# اذكر الأخطاء الصرفية وتصحيحها بهذا الشكل:
# الخطأ_الصرفي1 -> التصحيح_الصرفي1

# **3. أخطاء الإملاء:**
# اذكر الأخطاء الإملائية وتصحيحها بهذا الشكل:
# الخطأ_الإملائي1 -> التصحيح_الإملائي1

# **4. أخطاء التركيب:**
# اذكر أخطاء التركيب وتصحيحها بهذا الشكل:
# الخطأ_التركيبي1 -> التصحيح_التركيبي1

# **5. أخطاء الحركات (التشكيل):**
# اذكر أخطاء الحركات وتصحيحها بهذا الشكل:
# الخطأ_في_التشكيل1 -> التصحيح_في_التشكيل1

# **النص المُصحح كاملاً:**
# اكتب النص كاملاً بعد التصحيح مع الحركات الصحيحة

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
#         'message': 'Enhanced Arabic Text Analyzer API with Harokat Support',
#         'api_keys_count': len(GEMINI_API_KEYS),
#         'model_used': 'gemini-2.0-flash',
#         'features': ['OCR with harokat', 'Grammar analysis', 'Tashkeel detection'],
#         'endpoints': {
#             'ocr': '/ocr - Extract Arabic text with harokat from images',
#             'analyze_arabic': '/analyze_arabic - Analyze Arabic text including tashkeel',
#             'ocr_and_analyze': '/ocr_and_analyze - Combined OCR + Analysis',
#             'generate_arabic': '/generate_arabic - Generate Arabic text with harokat', 
#             'generate_and_analyze': '/generate_and_analyze - Generate + Analyze'
#         }
#     })


# if __name__ == '__main__':
#     print("=" * 60)
#     print("Starting Enhanced Arabic Text Analyzer API")
#     print("✅ Harokat (Tashkeel) Preservation Enabled")
#     print("✅ Using Gemini 2.0 Flash Model")
#     print("=" * 60)
#     print(f"Using {len(GEMINI_API_KEYS)} API keys for fallback")
#     print("\nAvailable endpoints:")
#     print("   - POST /ocr - Extract Arabic text WITH HAROKAT from images")
#     print("   - POST /analyze_arabic - Detailed Arabic text analysis")
#     print("   - POST /ocr_and_analyze - Combined OCR + Analysis")
#     print("   - POST /generate_arabic - Generate Arabic text with harokat")  
#     print("   - POST /generate_and_analyze - Generate + Analyze")
#     print("   - GET /health - Health check")
#     print(f"\n🚀 Server running on http://localhost:5000")
#     print("=" * 60)
    
#     app.run(debug=True, port=5000, host='0.0.0.0')
# Revisi (Nahwo Only)
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import requests
import base64
import io
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# 🔑 Multiple API Keys for fallback
GEMINI_API_KEYS = [
    "AIzaSyB-BAHNETcF6QNDL6AHVxGJRoikRYZRy6I",
    # Tambahkan API key lainnya di sini
]

# URL untuk model yang tersedia
GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def encode_image_to_base64(image):
    """Convert PIL Image to base64 string"""
    try:
        buffered = io.BytesIO()
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        image.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {str(e)}")
        raise

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
                result = response.json()
                
                # Validasi response
                if 'candidates' not in result or len(result['candidates']) == 0:
                    print(f"[!] API key {i+1}: No candidates in response")
                    continue
                    
                if 'content' not in result['candidates'][0]:
                    print(f"[!] API key {i+1}: No content in candidate")
                    continue
                    
                if 'parts' not in result['candidates'][0]['content']:
                    print(f"[!] API key {i+1}: No parts in content")
                    continue
                
                return result, None
                
            elif response.status_code == 429:
                print(f"[!] API key {i+1} rate limited, trying next key...")
                continue
            elif response.status_code == 400:
                error_text = response.text
                print(f"[!] API key {i+1} bad request: {error_text[:200]}...")
                return None, f"Bad request: {error_text[:200]}"
            else:
                print(f"[!] API key {i+1} failed with status {response.status_code}: {response.text[:100]}...")
                continue
                
        except requests.exceptions.Timeout:
            print(f"[!] API key {i+1} timeout")
            continue
        except Exception as e:
            print(f"[!] API key {i+1} failed with error: {str(e)}")
            continue
    
    return None, "All API keys failed or rate limited"

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


# ========== 2️⃣ FIXED Arabic Analysis - ONLY NAHWU ERRORS ==========
@app.route('/analyze_arabic', methods=['POST'])
def analyze_arabic():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided', 'success': False}), 400
            
        arabic_text = data.get('text', '')

        if not arabic_text.strip():
            return jsonify({'error': 'No text provided', 'success': False}), 400

        # UPDATED PROMPT - Only detect Nahwu errors from 13 basic rules
        prompt = f"""⚠️ تعليمات مهمة جداً: أنت مدقق نحوي متخصص. قم بفحص النص فقط من ناحية القواعد النحوية الأساسية الـ 13 التالية. لا تذكر أخطاء الصرف أو الإملاء أو التركيب أو الحركات.

**القواعد النحوية الأساسية المطلوب فحصها:**

1️⃣ أجزاء الجملة: الاسم، الفعل، الحرف
2️⃣ الفعل الماضي: يدل على حدث في الزمن الماضي
3️⃣ الفعل المضارع: يبدأ بـ (أ، ن، ي، ت) ويدل على الحاضر أو المستقبل
4️⃣ فعل الأمر: طلب حصول شيء في المستقبل
5️⃣ الفاعل: اسم مرفوع بعد الفعل دل على من فعل الفعل
6️⃣ المفعول به: اسم منصوب وقع عليه فعل الفاعل
7️⃣ المبتدأ والخبر: المبتدأ اسم مرفوع في أول الجملة، والخبر اسم مرفوع يكمله
8️⃣ نصب الفعل المضارع: بعد (أن، لن، إذن، كي)
9️⃣ جزم الفعل المضارع: بعد (لم، لا الناهية، إن)
🔟 كان وأخواتها: ترفع الاسم وتنصب الخبر
1️⃣1️⃣ إن وأخواتها: تنصب الاسم وترفع الخبر
1️⃣2️⃣ حروف الجر: من، إلى، عن، على، في، الباء، اللام (تجر الاسم بعدها)
1️⃣3️⃣ النعت: يتبع المنعوت في الإعراب (الرفع، النصب، الجر)

**تعليمات الفحص:**
- ابحث فقط عن الأخطاء النحوية المتعلقة بالقواعد الـ 13 أعلاه
- لا تتحدث عن أخطاء الصرف (التصريف)
- لا تتحدث عن أخطاء الإملاء (الكتابة)
- لا تتحدث عن أخطاء التركيب (بناء الجملة)
- لا تتحدث عن أخطاء الحركات أو التشكيل

**صيغة الإجابة المطلوبة:**

**أخطاء النحو:**
(إذا وُجدت أخطاء نحوية، اذكرها بهذا الشكل بالضبط:)
الكلمة_الخاطئة -> التصحيح (القاعدة: اسم القاعدة)

مثال:
الكتابُ -> الكتابَ (القاعدة: المفعول به - يجب أن يكون منصوباً)
يذهبُ -> يذهبْ (القاعدة: جزم الفعل المضارع - بعد "لم" يُجزم الفعل)

(إذا لم توجد أخطاء نحوية، اكتب فقط:)
لا توجد أخطاء نحوية

**النص المُصحح:**
(اكتب النص كاملاً بعد تصحيح الأخطاء النحوية فقط)

---

**النص المراد فحصه:**
{arabic_text}

⚠️ تذكير نهائي: اذكر فقط الأخطاء النحوية من القواعد الـ 13. تجاهل تماماً أي أخطاء أخرى.
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
                "temperature": 0.2,  # Lower temperature for more focused analysis
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
    """Combined OCR and Analysis - Only Nahwu errors"""
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
        
        print("Performing Nahwu Analysis (13 rules only)...")
        
        # Step 2: Nahwu Analysis ONLY
        analysis_prompt = f"""⚠️ تعليمات مهمة جداً: أنت مدقق نحوي متخصص. قم بفحص النص فقط من ناحية القواعد النحوية الأساسية الـ 13 التالية. لا تذكر أخطاء الصرف أو الإملاء أو التركيب أو الحركات.

**القواعد النحوية الأساسية المطلوب فحصها:**

1️⃣ أجزاء الجملة: الاسم، الفعل، الحرف
2️⃣ الفعل الماضي: يدل على حدث في الزمن الماضي
3️⃣ الفعل المضارع: يبدأ بـ (أ، ن، ي، ت) ويدل على الحاضر أو المستقبل
4️⃣ فعل الأمر: طلب حصول شيء في المستقبل
5️⃣ الفاعل: اسم مرفوع بعد الفعل دل على من فعل الفعل
6️⃣ المفعول به: اسم منصوب وقع عليه فعل الفاعل
7️⃣ المبتدأ والخبر: المبتدأ اسم مرفوع في أول الجملة، والخبر اسم مرفوع يكمله
8️⃣ نصب الفعل المضارع: بعد (أن، لن، إذن، كي)
9️⃣ جزم الفعل المضارع: بعد (لم، لا الناهية، إن)
🔟 كان وأخواتها: ترفع الاسم وتنصب الخبر
1️⃣1️⃣ إن وأخواتها: تنصب الاسم وترفع الخبر
1️⃣2️⃣ حروف الجر: من، إلى، عن، على، في، الباء، اللام (تجر الاسم بعدها)
1️⃣3️⃣ النعت: يتبع المنعوت في الإعراب (الرفع، النصب، الجر)

**صيغة الإجابة المطلوبة:**

**أخطاء النحو:**
(إذا وُجدت أخطاء، اذكرها بالشكل التالي:)
الكلمة_الخاطئة -> التصحيح (القاعدة: اسم القاعدة)

(إذا لم توجد أخطاء:)
لا توجد أخطاء نحوية

**النص المُصحح:**
(النص بعد التصحيح النحوي)

**النص المراد فحصه:**
{cleaned_extracted_text}

⚠️ تذكير: فقط الأخطاء النحوية من القواعد الـ 13. تجاهل أي أخطاء أخرى تماماً.
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
                "temperature": 0.2,
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
            'message': 'OCR and Nahwu analysis completed successfully',
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


# ========== 5️⃣ Generate + Analyze Combined (Nahwu only) ==========
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

        # Step 2: Nahwu Analysis ONLY
        analysis_prompt = f"""⚠️ تعليمات مهمة جداً: أنت مدقق نحوي متخصص. قم بفحص النص فقط من ناحية القواعد النحوية الأساسية الـ 13 التالية. لا تذكر أخطاء الصرف أو الإملاء أو التركيب أو الحركات.

**القواعد النحوية المطلوب فحصها:**

1️⃣ أجزاء الجملة
2️⃣ الفعل الماضي
3️⃣ الفعل المضارع
4️⃣ فعل الأمر
5️⃣ الفاعل
6️⃣ المفعول به
7️⃣ المبتدأ والخبر
8️⃣ نصب الفعل المضارع
9️⃣ جزم الفعل المضارع
🔟 كان وأخواتها
1️⃣1️⃣ إن وأخواتها
1️⃣2️⃣ حروف الجر
1️⃣3️⃣ النعت

**صيغة الإجابة:**

**أخطاء النحو:**
(إذا وُجدت أخطاء:)
الكلمة -> التصحيح (القاعدة: ...)

(إذا لم توجد:)
لا توجد أخطاء نحوية

**النص المُصحح:**
(النص المصحح)

**النص المراد فحصه:**
{generated_text}
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
                "temperature": 0.2,
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
        'message': 'Arabic Nahwu Analyzer - 13 Basic Rules Only',
        'api_keys_count': len(GEMINI_API_KEYS),
        'model_used': 'gemini-2.5-flash',
        'features': ['OCR with harokat', 'Nahwu analysis (13 rules only)'],
        'nahwu_rules': [
            '1. Ajzaul Jumlah',
            '2. Al-Fil Al-Madi', 
            '3. Al-Fil Al-Mudori',
            '4. Filul Amri',
            '5. Al-Faail',
            '6. Mafulun Bihi',
            '7. Mubtada Khobar',
            '8. Nasbul Filil Mudori',
            '9. Jazmul Filil Mudori',
            '10. Kana wa Akhowatiha',
            '11. Inna wa Akhowatiha',
            '12. Jarrul Ismi',
            '13. Nat'
        ],
        'endpoints': {
            'ocr': '/ocr - Extract Arabic text with harokat',
            'analyze_arabic': '/analyze_arabic - Nahwu analysis (13 rules)',
            'ocr_and_analyze': '/ocr_and_analyze - Combined OCR + Nahwu',
            'generate_arabic': '/generate_arabic - Generate Arabic text', 
            'generate_and_analyze': '/generate_and_analyze - Generate + Nahwu Analysis'
        }
    })


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Starting Arabic Nahwu Analyzer API")
    print("=" * 70)
    print("✅ Harokat (Tashkeel) Preservation: ENABLED")
    print("✅ Nahwu Analysis: 13 BASIC RULES ONLY")
    print("✅ Model: Gemini 2.5 Flash")
    print("=" * 70)
    print(f"📌 Using {len(GEMINI_API_KEYS)} API key(s) for fallback")
    print("\n📋 13 Kaidah Nahwu yang Dideteksi:")
    print("   1️⃣  Ajzaul Jumlah (أجزاء الجملة)")
    print("   2️⃣  Al-Fil Al-Madi (الفعل الماضي)")
    print("   3️⃣  Al-Fil Al-Mudori (الفعل المضارع)")
    print("   4️⃣  Filul Amri (فعل الأمر)")
    print("   5️⃣  Al-Faail (الفاعل)")
    print("   6️⃣  Mafulun Bihi (مفعول به)")
    print("   7️⃣  Mubtada Khobar (المبتدأ والخبر)")
    print("   8️⃣  Nasbul Filil Mudori (نصب الفعل المضارع)")
    print("   9️⃣  Jazmul Filil Mudori (جزم الفعل المضارع)")
    print("   🔟 Kana wa Akhowatiha (كان وأخواتها)")
    print("   1️⃣1️⃣ Inna wa Akhowatiha (إن وأخواتها)")
    print("   1️⃣2️⃣ Jarrul Ismi (جر الاسم)")
    print("   1️⃣3️⃣ Nat (النعت)")
    print("\n📡 Available endpoints:")
    print("   - POST /ocr - Extract text WITH HAROKAT")
    print("   - POST /analyze_arabic - Nahwu analysis (13 rules)")
    print("   - POST /ocr_and_analyze - Combined OCR + Nahwu")
    print("   - POST /generate_arabic - Generate Arabic text")
    print("   - POST /generate_and_analyze - Generate + Nahwu")
    print("   - GET /health - Health check")
    print(f"\n🌐 Server running on http://localhost:5000")
    print("=" * 70)
    
    app.run(debug=True, port=5000, host='0.0.0.0')
