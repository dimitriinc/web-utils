import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

visited_pages = set()

HEADERS = {
    "User-Agent": requests.utils.default_user_agent()
}

# Allowed URL suffixes for HTML-type documents
ALLOWED_EXTENSIONS = {'.html', '.htm', '.aspx', '.ashx', ''}

# Max depth of recursion
MAX_DEPTH = 3

def extract_filename(url):
    path = urlparse(url).path
    return os.path.basename(path) if path else None

def is_valid_link(link):
    parsed = urlparse(link)

    if parsed.scheme and parsed.scheme not in {'http', 'https'}:
        return False

    if parsed.fragment:
        return False

    if '/docs/' in parsed.path.lower():
        return False

    ext = os.path.splitext(parsed.path)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def is_internal_link(link, base_domain):
    parsed = urlparse(link)
    return parsed.netloc == "" or parsed.netloc == base_domain

def scrape_page_for_resources(url, base_domain, collected_filenames, depth=0):
    if depth > MAX_DEPTH:
        return
    if url in visited_pages:
        return

    print(f"[Depth {depth}] Visiting: {url}")
    visited_pages.add(url)

    time.sleep(1 / 3)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Collect referenced resources
    tags_attrs = {
        'img': 'src',
        'script': 'src',
        'link': 'href',
        'source': 'src',
        'iframe': 'src',
        'audio': 'src',
        'video': 'src',
    }

    for tag, attr in tags_attrs.items():
        for element in soup.find_all(tag):
            resource_url = element.get(attr)
            if resource_url:
                full_url = urljoin(url, resource_url)
                filename = extract_filename(full_url)
                if filename and filename not in collected_filenames:
                    collected_filenames[filename] = full_url

    # Follow internal, valid, non-static links recursively
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        full_link = urljoin(url, link)

        if is_internal_link(full_link, base_domain) and is_valid_link(full_link):
            scrape_page_for_resources(full_link, base_domain, collected_filenames, depth + 1)

def save_to_markdown(filenames, output_file="resources.md"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Referenced Resource Filenames (All Pages)\n\n")
        f.write("| Filename | Full URL |\n")
        f.write("|----------|----------|\n")
        for filename, full_url in sorted(filenames.items()):
            f.write(f"| `{filename}` | [{full_url}]({full_url}) |\n")
    print(f"\nSaved Markdown file to `{output_file}`.")

def save_filenames_to_txt(filenames, output_file="filenames.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for filename in sorted(filenames.keys()):
            f.write(f"{filename}\n")
    print(f"Saved plain filename list to `{output_file}`.")

if __name__ == "__main__":
    target_url = input("Enter a URL to scrape recursively: ").strip()
    parsed_base = urlparse(target_url)
    base_domain = parsed_base.netloc

    print(f"\nStarting recursive scraping within `{base_domain}` (depth ≤ {MAX_DEPTH})...\n")
    all_files = {}
    scrape_page_for_resources(target_url, base_domain, all_files)

    if all_files:
        save_to_markdown(all_files)
        save_filenames_to_txt(all_files)
    else:
        print("No referenced filenames found.")
