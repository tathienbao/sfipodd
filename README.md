# SFI Podcast Downloader

A tool to download all podcasts from SFI (Swedish for Immigrants) - available as both a Python CLI and a web app.

## Live Demo

**https://sfipodd.vercel.app/**

## Features

- Download all 246+ SFI podcasts with one click
- **Web version**: Select folder once, all files download automatically (Chrome/Edge)
- **CLI version**: Run locally with Python
- No popups or interruptions - smooth batch download

## Web Usage

1. Visit **https://sfipodd.vercel.app/**
2. Click **"Download All Podcasts"**
3. Select a folder (asked only once)
4. All podcasts download automatically to your chosen folder

*Best experience in Chrome or Edge (uses File System Access API)*

## Local CLI Usage

```bash
# Clone repository
git clone https://github.com/tathienbao/sfipodd.git
cd sfipodd

# Install dependencies
pip install -r requirements.txt

# Run the downloader
python sfi_podcast_downloader.py
```

Podcasts will be saved to `sfi_podcasts/` folder.

## Project Structure

```
sfipodd/
├── api/
│   ├── list.py           # API: Get all podcast URLs
│   ├── download.py       # API: Extract MP3 URL from podcast page
│   ├── proxy.py          # API: Proxy MP3 downloads (bypass CORS)
│   └── requirements.txt  # Python dependencies for Vercel
├── public/
│   └── index.html        # Web interface
├── sfi_podcast_downloader.py  # CLI script for local use
├── vercel.json           # Vercel configuration
├── package.json          # Node.js config
├── requirements.txt      # Python dependencies (local)
└── README.md
```

## How It Works

1. Scrapes podcast list from sfipodd.se
2. Extracts MP3 URLs from each podcast page
3. Downloads MP3 files (via proxy to bypass CORS in web version)

## License

MIT License 