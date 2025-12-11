import json
import sys
import os
from io import BytesIO
from urllib.parse import urljoin, urlparse
import requests
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def handler(event, context):
    """Vercel serverless function to handle podcast downloads"""
    
    # Set up session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    # Get query parameters
    params = event.get('queryStringParameters', {})

    # Determine action based on path
    path = event.get('path', '')

    if path == '/api/download' or params.get('action') == 'download':
        # Download specific podcast
        podcast_url = params.get('url')

        if not podcast_url:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': json.dumps({'error': 'Missing podcast URL'})
            }

        # Extract MP3 URL
        mp3_url = extract_mp3_url(podcast_url, session)

        if not mp3_url:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': json.dumps({'error': 'No MP3 found for the given URL'})
            }

        # Return the MP3 URL for client-side download
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({'mp3_url': mp3_url, 'podcast_url': podcast_url})
        }

    elif path == '/api/list' or params.get('action') == 'list':
        # List all podcasts
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

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': json.dumps({'podcast_urls': filtered_links, 'count': len(filtered_links)})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': json.dumps({'error': f'Failed to fetch podcast list: {str(e)}'})
            }
    
    else:
        # Return API info
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({
                'message': 'SFI Podcast Downloader API',
                'endpoints': {
                    '/api/list': 'Get list of all podcast URLs',
                    '/api/download?url=<podcast_url>': 'Get download link for specific podcast'
                }
            })
        }


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