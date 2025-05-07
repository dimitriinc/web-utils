import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys
import jsbeautifier

def extract_js_info(page_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        sys.exit(0)

    soup = BeautifulSoup(response.text, 'html.parser')

    base_domain = urlparse(page_url).netloc

    # External JS
    script_tags_with_src = soup.find_all('script', src=True)
    external_paths = []
    third_party_urls = []
    for tag in script_tags_with_src:
        full_url = urljoin(page_url, tag['src'])
        parsed = urlparse(full_url)
        if parsed.netloc == base_domain:
            external_paths.append(parsed.path)
        else:
            third_party_urls.append(full_url)

    # Inline JS code
    script_tags_inline = soup.find_all('script', src=False)
    inline_scripts = []
    for tag in script_tags_inline:
        raw_js = tag.string or ''
        pretty_js = jsbeautifier.beautify(raw_js)
        inline_scripts.append(pretty_js)

    return external_paths, third_party_urls, inline_scripts

if __name__ == "__main__":
    url = input("Enter the URL of the HTML page: ").strip()
    external_paths, third_party_urls, inline_scripts = extract_js_info(url)

    output_file = open("js-extracted.txt", "w")

    # Write external paths

    if external_paths:
        output_file.write("\nExternal JavaScript paths:\n")
        for path in external_paths:
            output_file.write("\n\t• " + path + "\n")
    else:
        output_file.write("\n\tNo external JavaScript files found.\n")

    output_file.write("\n\n" + "-"*40 + "\n\n")

    # Write third party URLs

    if third_party_urls:
        output_file.write("\nThird Party JavaScript URLs:\n")
        for url in third_party_urls:
            output_file.write("\n\t• " + url + "\n")
    else:
        output_file.write("\n\tNo third party JavaScript files found.\n")

    output_file.write("\n\n" + "-"*40 + "\n\n")

    # Write inline scripts

    if inline_scripts:
        output_file.write("Inline JavaScript blocks:\n\n")
        for i, js in enumerate(inline_scripts, 1):
            output_file.write(f"\n\t• [Inline Script {i}]\n\n{js.strip()}\n")
    else:
        output_file.write("\n\tNo inline JavaScript blocks found.")

    # Clean up

    output_file.close()
