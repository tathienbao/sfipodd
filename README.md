# SFI Podcast Downloader

A Python tool to download podcasts from SFI (Swedish Radio International).

## Features

- Download podcasts from SFI
- Manage downloaded podcast files
- Simple one-click web interface for easy use
- Deployable on Vercel for instant access

## Installation

1. Clone this repository:
```bash
git clone <your-repository-url>
cd sfipodd
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Local Usage
Run the main script:
```bash
python sfi_podcast_downloader.py
```

### Web Deployment (Vercel)
Deploy directly to Vercel for a web-based solution:
1. Push your code to a GitHub repository
2. Connect to Vercel and deploy
3. Access the simple one-click download interface from anywhere

The web interface allows you to download all SFI podcasts with a single button click.

## Project Structure

```
sfipodd/
├── sfi_podcast_downloader.py  # Main script
├── api/download.py             # API endpoint for web version
├── index.html                  # Web interface
├── sfi_podcasts/              # Directory for downloaded podcasts
├── package.json               # Node.js dependencies for Vercel
├── vercel.json                # Vercel configuration
├── requirements.txt           # Python dependencies
├── README.md                  # This documentation
└── .gitignore                 # Git ignore rules
```

## Contributions

All contributions are welcome! Please create an issue or submit a pull request.

## License

MIT License 