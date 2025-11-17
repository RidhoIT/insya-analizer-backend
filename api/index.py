from app import app

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

# Export for Vercel
app.handler = handler

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')