from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Data sementara (nanti bisa diganti dengan database)
users = {}
results_history = []

@app.route('/')
def home():
    return jsonify({
        'message': 'INSYA Analyzer Backend API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Validasi input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email dan password harus diisi'}), 400

        email = data['email']
        password = data['password']
        name = data.get('name', '')

        # Cek jika email sudah terdaftar
        if email in users:
            return jsonify({'error': 'Email sudah terdaftar'}), 400

        # Simpan user (dalam implementasi nyata, hash password dulu)
        users[email] = {
            'name': name,
            'email': email,
            'password': password,  # Ini harus di-hash di produksi
            'created_at': datetime.now().isoformat()
        }

        return jsonify({
            'message': 'Registrasi berhasil',
            'user': {
                'name': name,
                'email': email
            }
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email dan password harus diisi'}), 400

        email = data['email']
        password = data['password']

        # Cek user
        if email not in users or users[email]['password'] != password:
            return jsonify({'error': 'Email atau password salah'}), 401

        return jsonify({
            'message': 'Login berhasil',
            'user': {
                'name': users[email]['name'],
                'email': email
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()

        if not data or not data.get('text'):
            return jsonify({'error': 'Text harus diisi'}), 400

        text = data['text']
        user_email = data.get('user_email', '')

        # Analisis dasar (ini bisa dikembangkan lebih lanjut)
        words = text.lower().split()
        word_count = len(words)

        # Deteksi kata kunci INSYA (contoh sederhana)
        insya_keywords = ['insya', 'allah', 'islam', 'iman', 'tauhid', 'ibadah', 'shalat', 'puasa', 'zakat', 'haji']
        keyword_count = sum(1 for word in words if any(keyword in word for keyword in insya_keywords))

        # Hitung durasi baca (perkiraan 200 kata per menit)
        reading_time = max(1, round(word_count / 200))

        result = {
            'text': text,
            'word_count': word_count,
            'keyword_count': keyword_count,
            'reading_time_minutes': reading_time,
            'insya_score': min(100, (keyword_count / word_count) * 100) if word_count > 0 else 0,
            'analyzed_at': datetime.now().isoformat(),
            'user_email': user_email
        }

        # Simpan hasil
        results_history.append(result)

        return jsonify({
            'message': 'Analisis berhasil',
            'result': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<email>', methods=['GET'])
def get_history(email):
    try:
        user_results = [r for r in results_history if r.get('user_email') == email]

        return jsonify({
            'history': user_results,
            'count': len(user_results)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-result', methods=['POST'])
def save_result():
    try:
        data = request.get_json()

        if not data or not data.get('text') or not data.get('user_email'):
            return jsonify({'error': 'Data tidak lengkap'}), 400

        # Simpan hasil ke history
        result = {
            'text': data['text'],
            'user_email': data['user_email'],
            'analysis': data.get('analysis', {}),
            'saved_at': datetime.now().isoformat()
        }

        results_history.append(result)

        return jsonify({
            'message': 'Hasil berhasil disimpan',
            'result': result
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)