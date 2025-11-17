# INSYA Analyzer Backend

Backend API untuk aplikasi INSYA Analyzer yang berfungsi untuk menganalisis teks islami.

## Fitur

- User registration dan authentication
- Text analysis untuk konten islami
- History tracking untuk analisis user
- API endpoints yang RESTful
- CORS support untuk frontend integration

## API Endpoints

### Authentication
- `POST /api/register` - Register user baru
- `POST /api/login` - Login user

### Analysis
- `POST /api/analyze` - Analisis text
- `GET /api/history/<email>` - Get history analisis user
- `POST /api/save-result` - Simpan hasil analisis

### System
- `GET /api/health` - Health check endpoint
- `GET /` - Home endpoint dengan info API

## Installation

1. Clone repository
```bash
git clone https://github.com/RidhoIT/insya-analizer-backend.git
cd insya-analizer-backend
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python app.py
```

## Environment Variables

- `PORT`: Port untuk menjalankan aplikasi (default: 5000)

## Deployment

Project ini bisa di-deploy ke Vercel menggunakan konfigurasi `vercel.json`.

## Development

Untuk development dengan auto-reload:

```bash
export FLASK_ENV=development
python app.py
```

## API Documentation

### Register User

**Endpoint:** `POST /api/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}
```

**Response:**
```json
{
  "message": "Registrasi berhasil",
  "user": {
    "name": "User Name",
    "email": "user@example.com"
  }
}
```

### Analyze Text

**Endpoint:** `POST /api/analyze`

**Request Body:**
```json
{
  "text": "Text yang akan dianalisis",
  "user_email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Analisis berhasil",
  "result": {
    "text": "Text yang akan dianalisis",
    "word_count": 5,
    "keyword_count": 2,
    "reading_time_minutes": 1,
    "insya_score": 40.0,
    "analyzed_at": "2023-11-17T14:30:00.000Z",
    "user_email": "user@example.com"
  }
}
```

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License