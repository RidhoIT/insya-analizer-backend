from app import app

# Vercel expects a handler function at the module level
handler = app

# Export for Vercel
__all__ = ['handler']