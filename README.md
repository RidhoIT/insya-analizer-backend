# Enhanced Arabic Text Analyzer Backend

API backend for analyzing Arabic text with OCR capabilities using Google Gemini AI.

## Features

- **OCR**: Extract Arabic text from images
- **Text Analysis**: Detailed analysis of Arabic text for grammatical, morphological, spelling, and structural errors
- **Combined OCR + Analysis**: Perform both operations in a single request
- **Text Generation**: Generate Arabic text content
- **Generate + Analyze**: Generate text and then analyze it

## API Endpoints

### POST /ocr
Extract Arabic text from images.
- **Request**: Form data with `image` file
- **Response**: JSON with extracted text

### POST /analyze_arabic
Analyze Arabic text for errors.
- **Request**: JSON with `text` field
- **Response**: JSON with detailed analysis

### POST /ocr_and_analyze
Combined OCR and analysis.
- **Request**: Form data with `image` file
- **Response**: JSON with both extracted text and analysis

### POST /generate_arabic
Generate Arabic text.
- **Request**: JSON with `prompt` field
- **Response**: JSON with generated text

### POST /generate_and_analyze
Generate text and analyze it.
- **Request**: JSON with `prompt` field
- **Response**: JSON with generated text and analysis

### GET /health
Health check endpoint.
- **Response**: JSON with API status

## Deployment to Vercel

### Prerequisites
- Vercel CLI installed
- Git repository

### Steps

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

### Environment Variables
Set these in your Vercel dashboard under Environment Variables:
- `GEMINI_API_KEYS`: Your Google Gemini API keys (comma-separated)
- `PYTHON_VERSION`: Set to `3.10`

### Files Created for Deployment
- `vercel.json`: Vercel configuration
- `requirements.txt`: Python dependencies
- `.gitignore`: Git ignore file

## Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**
   ```bash
   python app.py
   ```

3. **Access the API**
   The API will be available at `http://localhost:5000`

## Configuration

Update the `GEMINI_API_KEYS` list in `app.py` with your actual API keys from Google AI Studio.

## Dependencies

- Flask 2.3.3
- Flask-CORS 4.0.0
- Pillow 10.0.1
- requests 2.31.0
- Werkzeug 2.3.7

## License

MIT