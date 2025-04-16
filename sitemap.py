import xml.etree.ElementTree as ET
from collections import defaultdict
from urllib.parse import urlparse
import requests
import json
import sys

bullets = ['•', '◇', '▪', '★', '◇', '-', '→', '⇒']

def print_usage():
    print("Usage: sitemap.py <URL> <output filename> <output format: 'txt' or 'json'>")
    sys.exit(1)

def build_tree(urls):
    tree = defaultdict(dict)
    
    for url in urls:
        path = urlparse(url).path.strip('/')
        parts = path.split('/')
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
    
    return tree

def render_tree_to_text(tree, file, level=0):
    for key, subtree in sorted(tree.items()):
        file.write('  ' * level + f'{bullets[level]} {key}' + '\n')
        render_tree_to_text(subtree, file, level + 1)

def parse_sitemap(xml_path):
    try:
        response = requests.get(xml_path)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [url_elem.text for url_elem in root.findall('ns:url/ns:loc', namespace)]
        
        return build_tree(urls)
    except requests.RequestException as e:
        print(f"Error fetching sitemap: {e}")

def save_tree_to_json(tree, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)

if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Error: incorrect number of arguments")
        print_usage()

    url = sys.argv[1]
    output_filename = sys.argv[2]
    output_extension = sys.argv[3]

    if output_extension != "txt" or output_extension != "json":
        print("Error: invalid file extension.")
        print_usage()

    xml_path = "https://www.bolsasymercados.es/bme-exchange/Sitemap.ashx"

    output_json = "sitemap.json"
    output_text = "sitemap.txt"

    tree = parse_sitemap(xml_path)

    if output_extension == "txt":
        with open(output_text, 'w') as file:
            render_tree_to_text(tree, file)
    else:
        save_tree_to_json(tree, output_json)