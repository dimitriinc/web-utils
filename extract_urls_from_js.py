import re
import requests

def extract_urls_from_js(js_content):
    # Regex pattern to find URLs (http, https, etc.)
    url_pattern = re.compile(r"(https?://[\w\-._~:/?#[\]@!$&\'()*+,;%=]+(?:\?[\w\-._~:/?#[\]@!$&\'()*+,;%=\{\}]*)?)")
    return url_pattern.findall(js_content)

def fetch_js_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the JavaScript file: {e}")
        return None

def write_urls_to_file(urls, output_file):
    try:
        with open(output_file, 'w') as file:
            for url in urls:
                file.write('• ' + url + '\n')
        print(f"URLs successfully written to {output_file}")
    except IOError as e:
        print(f"Error writing to file: {e}")

def main():
    js_file_url = input("Enter the URL of the JavaScript file (with schema): ")
    output_file = input("Enter the output file name (e.g., urls.txt): ")

    print("Fetching JavaScript file...")
    js_content = fetch_js_file(js_file_url)

    if js_content is not None:
        print("Extracting URLs...")
        urls = extract_urls_from_js(js_content)

        if urls:
            print(f"Found {len(urls)} URLs. Writing to file...")
            write_urls_to_file(urls, output_file)
        else:
            print("No URLs found in the JavaScript file.")

if __name__ == "__main__":
    main()

