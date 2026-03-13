import os
import signal
import sys
import logging
from waitress import serve
from app import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

is_shutting_down = False

def graceful_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    global is_shutting_down
    print(f"\nReceived signal {signum}. Starting graceful shutdown...")
    logger.warning(f"Received shutdown signal {signum}. Starting graceful shutdown...")
    is_shutting_down = True
    
    print("No longer accepting new connections...")
    logger.info("Server no longer accepting new connections")
    
    cleanup()
    
    print("Shutdown complete.")
    logger.info("Graceful shutdown complete")
    sys.exit(0)

def cleanup():
    """Clean up resources before shutdown."""
    pass

@app.before_request
def check_shutting_down():
    """Reject new requests during shutdown."""
    from flask import jsonify
    if is_shutting_down:
        return jsonify({"error": "Server is shutting down", "status": "unavailable"}), 503

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)
    
    logger.info(f"Ramya Production Server starting on port {port}")
    print(f"Ramya running on port {port}...")
    print("Press Ctrl+C to stop gracefully")
    
    serve(app, host='0.0.0.0', port=port, threads=6)
