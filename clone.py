import urllib.request
import urllib.parse
import re
import os
import sys

BASE_URL = "https://sagar-nidhi.dilseinvite.in/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return resp.read()

def download_file(rel_path, target_path=None):
    if not target_path:
        target_path = rel_path.lstrip("/")
    # Clean query string if any
    clean_target = target_path.split("?")[0]
    full_url = urllib.parse.urljoin(BASE_URL, rel_path)
    print(f"Downloading: {full_url} -> {clean_target}")
    try:
        data = fetch(full_url)
        os.makedirs(os.path.dirname(clean_target) or ".", exist_ok=True)
        with open(clean_target, "wb") as f:
            f.write(data)
        print(f"  OK ({len(data)} bytes)")
        return data
    except Exception as e:
        print(f"  FAILED: {e}")
        return None

def main():
    # 1. Download index.html
    html_data = download_file("index.html")
    if not html_data:
        print("Could not download index.html")
        return

    html_text = html_data.decode("utf-8", errors="ignore")

    # Known files from index.html
    initial_files = [
        "favicon.svg",
        "apple-touch-icon.png",
        "og.jpg",
        "media/poster-mobile.webp",
        "media/poster-desktop.webp",
        "media/sn-logo.webp",
        "assets/index-C8niuQze.js",
        "assets/index-B1-Wbvcr.css"
    ]

    for f in initial_files:
        download_file(f)

    # Read JS and CSS to find all asset links
    js_path = "assets/index-C8niuQze.js"
    css_path = "assets/index-B1-Wbvcr.css"

    text_to_search = html_text
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8", errors="ignore") as f:
            text_to_search += "\n" + f.read()

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8", errors="ignore") as f:
            text_to_search += "\n" + f.read()

    # Regex to find any asset references
    asset_regex = re.compile(r'([a-zA-Z0-9_\-\./]+\.(?:webp|png|jpg|jpeg|gif|svg|mp3|m4a|aac|wav|ogg|mp4|webm|woff2|woff|ttf|otf|json))', re.IGNORECASE)
    matches = set(asset_regex.findall(text_to_search))
    
    print(f"\nDiscovered {len(matches)} potential assets. Filtering...")
    
    # Filter matches
    downloaded = set(initial_files)
    downloaded.add("index.html")

    for match in sorted(matches):
        match_clean = match.strip("'\"`() ")
        if match_clean.startswith("http://") or match_clean.startswith("https://"):
            if "dilseinvite.in" in match_clean:
                # relative path
                rel = match_clean.split("dilseinvite.in/")[-1]
                if rel and rel not in downloaded:
                    download_file(rel)
                    downloaded.add(rel)
            continue
        
        # relative files
        # clean up leading ./ or /
        rel = match_clean.lstrip("./").lstrip("/")
        if not rel or rel.startswith("node_modules") or rel.startswith("src/"):
            continue

        if rel not in downloaded:
            # Let's test downloading it
            res = download_file(rel)
            if res:
                downloaded.add(rel)

if __name__ == "__main__":
    main()
