import requests
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Proxy MP3 download to bypass CORS restrictions"""

        # Parse query parameters
        query_components = parse_qs(urlparse(self.path).query)
        mp3_url = query_components.get('url', [None])[0]

        if not mp3_url:
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Missing url parameter')
            return

        try:
            # Fetch the MP3 file from external server
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            response = session.get(mp3_url, stream=True, timeout=30)
            response.raise_for_status()

            # Get filename from URL
            filename = mp3_url.split('/')[-1].split('?')[0]
            if not filename.endswith('.mp3'):
                filename = 'podcast.mp3'

            # Send the file to browser
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Access-Control-Allow-Origin', '*')

            # Get content length if available
            content_length = response.headers.get('Content-Length')
            if content_length:
                self.send_header('Content-Length', content_length)

            self.end_headers()

            # Stream the file content
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    self.wfile.write(chunk)

        except requests.exceptions.Timeout:
            self.send_response(504)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Timeout fetching MP3 file')

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
