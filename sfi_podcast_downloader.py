#!/usr/bin/env python3
"""
Script để tải hết các file podcast từ sfipodd.se
"""

import requests
import re
import os
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class SFIPodcastDownloader:
    def __init__(self, download_dir="sfi_podcasts"):
        self.download_dir = download_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Tạo thư mục download
        os.makedirs(download_dir, exist_ok=True)
        
    def get_podcast_links(self):
        """Lấy tất cả link podcast từ trang tổng hợp"""
        url = "https://sfipodd.se/sok-en-podd/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Tìm tất cả link podcast
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm tất cả link dạng http://sfipodd.se/...
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'sfipodd.se/' in href and href not in ['https://sfipodd.se/', 'http://sfipodd.se/']:
                    # Đảm bảo URL đầy đủ
                    if href.startswith('http'):
                        links.append(href)
                    else:
                        links.append(urljoin(url, href))
            
            # Loại bỏ trùng lặp
            links = list(set(links))
            print(f"Tìm thấy {len(links)} link podcast")
            return links
            
        except Exception as e:
            print(f"Lỗi khi lấy danh sách podcast: {e}")
            return []
    
    def extract_mp3_url(self, podcast_url):
        """Trích xuất URL MP3 từ trang podcast"""
        try:
            response = self.session.get(podcast_url)
            response.raise_for_status()
            
            # Tìm link MP3 trong HTML
            content = response.text
            
            # Pattern 1: Tìm link trong text "Download" 
            download_pattern = r'Download.*?href=["\']([^"\']*\.mp3)["\']'
            match = re.search(download_pattern, content, re.IGNORECASE)
            
            if match:
                return match.group(1)
            
            # Pattern 2: Tìm bất kỳ link MP3 nào từ blubrry
            mp3_pattern = r'https?://[^"\'\s]*blubrry[^"\'\s]*\.mp3'
            match = re.search(mp3_pattern, content)
            
            if match:
                return match.group(0)
            
            # Pattern 3: Tìm trong BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            for a in soup.find_all('a', href=True):
                if '.mp3' in a['href'] and 'blubrry' in a['href']:
                    return a['href']
            
            print(f"Không tìm thấy link MP3 trong {podcast_url}")
            return None
            
        except Exception as e:
            print(f"Lỗi khi trích xuất MP3 từ {podcast_url}: {e}")
            return None
    
    def download_file(self, url, filename):
        """Tải về một file MP3"""
        filepath = os.path.join(self.download_dir, filename)
        
        # Kiểm tra file đã tồn tại chưa
        if os.path.exists(filepath):
            print(f"File {filename} đã tồn tại, bỏ qua...")
            return True
        
        try:
            print(f"Đang tải {filename}...")
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✓ Đã tải xong {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Lỗi khi tải {filename}: {e}")
            return False
    
    def get_filename_from_url(self, url, podcast_url=""):
        """Tạo tên file từ URL"""
        # Lấy tên file từ URL
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        if not filename or not filename.endswith('.mp3'):
            # Nếu không lấy được tên file, tạo từ podcast URL
            if podcast_url:
                podcast_name = os.path.basename(urlparse(podcast_url).path)
                filename = f"{podcast_name}.mp3"
            else:
                filename = f"podcast_{int(time.time())}.mp3"
        
        # Làm sạch tên file
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return filename
    
    def download_all(self):
        """Tải hết tất cả podcast"""
        print("Bắt đầu tải hết podcast SFI...")
        
        # Lấy danh sách link
        podcast_links = self.get_podcast_links()
        
        if not podcast_links:
            print("Không tìm thấy link nào!")
            return
        
        success_count = 0
        failed_count = 0
        
        for i, podcast_url in enumerate(podcast_links, 1):
            print(f"\n[{i}/{len(podcast_links)}] Xử lý: {podcast_url}")
            
            # Trích xuất URL MP3
            mp3_url = self.extract_mp3_url(podcast_url)
            
            if not mp3_url:
                print(f"✗ Không tìm thấy MP3 cho {podcast_url}")
                failed_count += 1
                continue
            
            # Tạo tên file
            filename = self.get_filename_from_url(mp3_url, podcast_url)
            
            # Tải file
            if self.download_file(mp3_url, filename):
                success_count += 1
            else:
                failed_count += 1
            
            # Nghỉ một chút để không spam server
            time.sleep(1)
        
        print(f"\n=== KẾT QUẢ ===")
        print(f"Thành công: {success_count}")
        print(f"Thất bại: {failed_count}")
        print(f"Tổng cộng: {len(podcast_links)}")
        print(f"Files được lưu trong thư mục: {self.download_dir}")

def main():
    downloader = SFIPodcastDownloader()
    downloader.download_all()

if __name__ == "__main__":
    main()