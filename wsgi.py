from app import app
import os

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting production server on port {port}...")
    serve(app, host="0.0.0.0", port=port)


