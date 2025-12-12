import json
import requests
import re
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Vercel serverless function to handle podcast downloads"""

        # Set up session
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Parse query parameters
        query_components = parse_qs(urlparse(self.path).query)
        podcast_url = query_components.get('url', [None])[0]

        if not podcast_url:
            error_data = json.dumps({'error': 'Missing podcast URL'})
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(error_data.encode())
            return

        # Extract MP3 URL
        mp3_url = extract_mp3_url(podcast_url, session)

        if not mp3_url:
            error_data = json.dumps({'error': 'No MP3 found for the given URL'})
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(error_data.encode())
            return

        # Return the MP3 URL for client-side download
        response_data = json.dumps({'mp3_url': mp3_url, 'podcast_url': podcast_url})
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response_data.encode())


def extract_mp3_url(podcast_url, session):
    """Helper function to extract MP3 URL from podcast page"""
    try:
        response = session.get(podcast_url)
        response.raise_for_status()

        content = response.text

        # Pattern 1: Find link in text "Download"
        download_pattern = r'Download.*?href=["\']([^"\']*\.mp3)["\']'
        match = re.search(download_pattern, content, re.IGNORECASE | re.DOTALL)

        if match:
            return match.group(1)

        # Pattern 2: Find any MP3 link from blubrry
        mp3_pattern = r'https?://[^"\'\s>]*blubrry[^"\'\s>]*\.mp3'
        match = re.search(mp3_pattern, content)

        if match:
            return match.group(0)

        # Pattern 3: Look for audio elements
        audio_pattern = r'<audio[^>]*src=["\']([^"\']*\.mp3)["\'][^>]*>'
        match = re.search(audio_pattern, content, re.IGNORECASE)

        if match:
            return match.group(1)

        # Pattern 4: Find in BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Look for mp3 links in <a> tags
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.mp3' in href.lower():
                # Convert relative URLs to absolute
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    parsed_url = urlparse(podcast_url)
                    href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                return href

        # Look for mp3 links in various attributes
        for element in soup.find_all():
            for attr in ['src', 'data-mp3', 'data-src', 'data-url', 'data-audio', 'data-file']:
                if element.has_attr(attr):
                    val = element[attr]
                    if '.mp3' in val.lower():
                        if val.startswith('//'):
                            val = 'https:' + val
                        elif val.startswith('/'):
                            parsed_url = urlparse(podcast_url)
                            val = f"{parsed_url.scheme}://{parsed_url.netloc}{val}"
                        return val

        return None

    except Exception as e:
        print(f"Error extracting MP3 from {podcast_url}: {e}")
        return None
