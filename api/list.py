import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Vercel serverless function to list all podcast URLs"""

        # Set up session
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        try:
            response = session.get("https://sfipodd.se/sok-en-podd/")
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'sfipodd.se/' in href and href not in ['https://sfipodd.se/', 'http://sfipodd.se/']:
                    if href.startswith('http'):
                        links.append(href)
                    else:
                        links.append(urljoin("https://sfipodd.se/sok-en-podd/", href))

            # Filter and clean links to include only podcast pages
            filtered_links = []
            for link in links:
                # Only include links that look like podcast pages (not homepage, search, etc.)
                if ('sfipodd.se/' in link and
                    link != 'https://sfipodd.se/' and
                    link != 'http://sfipodd.se/' and
                    'search' not in link.lower() and
                    not link.endswith('/') and
                    not link.endswith('/sok-en-podd/') and
                    not link.endswith('/om-sfi-podd/') and
                    not link.endswith('/kontakt/')):
                    filtered_links.append(link)

            # Remove duplicates
            filtered_links = list(set(filtered_links))

            response_data = json.dumps({'podcast_urls': filtered_links, 'count': len(filtered_links)})

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(response_data.encode())

        except Exception as e:
            error_data = json.dumps({'error': f'Failed to fetch podcast list: {str(e)}'})

            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(error_data.encode())
