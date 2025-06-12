import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import json


def get_css_selector(element):
    """Build a Chrome DevTools-like CSS selector."""
    if not element or not hasattr(element, 'name'):
        return ""
    
    path = []
    current = element

    while current and current.name and current.name != '[document]':
        selector = current.name
        
        # Handle ID - if element has ID, use it and stop
        if current.has_attr('id') and current['id']:
            selector = f"#{current['id']}"
            path.insert(0, selector)
            break
        
        # Add classes if present
        if current.has_attr('class') and current['class']:
            classes = [cls for cls in current['class'] if cls]
            if classes:
                selector += '.' + '.'.join(classes)
        
        path.insert(0, selector)
        current = current.parent
    
    return ' > '.join(path)

def extract_metadata(tag: Tag):
    """Dynamically extract metadata from any HTML tag."""
    metadata = []

    # Extract all attributes (like src, href, alt, data-*, etc.)
    for attr, value in tag.attrs.items():
        if isinstance(value, list):
            value = " ".join(value)
        metadata.append({
            "type": f"attribute:{attr}",
            "value": value,
            "selector": get_css_selector(tag)
        })

    # Extract visible text (if non-empty and not just whitespace)
    text = tag.get_text(strip=True)
    if text:
        metadata.append({
            "type": "text",
            "value": text,
            "selector": get_css_selector(tag)
        })

    return metadata if metadata else None

def parse_element(element: Tag, group_id: str):
    """Recursively parse HTML elements and attach the parent group ID."""
    if not isinstance(element, Tag):
        return None

    data = {
        "tag": element.name,
        "meta": extract_metadata(element),
        "group": group_id,
        "selector": get_css_selector(element)
    }

    children = []
    for child in element.children:
        if isinstance(child, Tag):
            parsed = parse_element(child, group_id)
            if parsed:
                children.append(parsed)
        elif isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                children.append({
                    "text": text,
                    "group": group_id
                })

    if children:
        data["children"] = children

    return data

def group_by_first_parent(root: Tag):
    """Group direct children of the root element and assign a group ID."""
    if not root:
        return []

    grouped = []
    count = 1

    for child in root.children:
        if isinstance(child, Tag):
            group_id = f"group_{count}"
            parsed = parse_element(child, group_id)
            if parsed:
                grouped.append(parsed)
                count += 1

    return grouped

# --- MAIN SCRIPT ---
def main():
    url = "https://www.harpercollins.ca/9780778387770/a-most-puzzling-murder/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    root = soup.find("div", {"id": "dp-container"}) or soup.find("div", {"id": "dpx-center"}) or soup.body
    if not root:
        print("Could not find suitable root element")
        return

    print(f"Using root: {root.name} with id: {root.get('id', 'N/A')}")

    structured_groups = group_by_first_parent(root)

    if not structured_groups:
        print("No groups found")
        return

    print(f"Found {len(structured_groups)} groups")

    print("\nPreview of first 2 groups:")
    print(json.dumps(structured_groups[:2], indent=2, ensure_ascii=False))

    try:
        with open("structured_amazon_data_with_selectors.json", "w", encoding="utf-8") as f:
            json.dump(structured_groups, f, indent=2, ensure_ascii=False)
        print(f"\nFull data saved to 'structured_amazon_data_with_selectors.json'")
    except IOError as e:
        print(f"Failed to save file: {e}")

if __name__ == "__main__":
    main()
