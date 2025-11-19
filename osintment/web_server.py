#!/usr/bin/env python3
"""
OSINTment Web Server Entry Point

Run this script to start the web application:
    python -m osintment.web_server

Or with custom options:
    python -m osintment.web_server --host 0.0.0.0 --port 8000
"""
import argparse
from .web.app import run_web_server


def main():
    parser = argparse.ArgumentParser(description='OSINTment Web Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              OSINTment Web Application                        ║
║         Professional OSINT Automation & Reporting             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Starting server on http://{args.host}:{args.port}

Configuration:
  - Host: {args.host}
  - Port: {args.port}
  - Debug: {args.debug}

Open your browser and navigate to:
  → http://localhost:{args.port} (if running locally)
  → http://{args.host}:{args.port} (if accessible remotely)

Press Ctrl+C to stop the server
    """)

    run_web_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
