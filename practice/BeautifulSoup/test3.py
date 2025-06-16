import json

def flatten_json(node, flat_list):
    flat_node = {
        "tag": node.get("tag"),
        "meta": node.get("meta"),
        "group": node.get("group"),
        "selector": node.get("selector")
    }
    flat_list.append(flat_node)

    children = node.get("children", [])
    if children:
        for child in children:
            flatten_json(child, flat_list)

    return flat_list

# Load JSON file
with open("C:\languages\Tecolution\structured_amazon_data_with_selectors.json",encoding="utf-8") as f:
    nested_data = json.load(f)

# Check if top level is a list
flat_result = []
if isinstance(nested_data, list):
    for node in nested_data:
        flatten_json(node, flat_result)
else:
    flatten_json(nested_data, flat_result)

# Save or view the output
with open("flattened_output.json", "w",encoding="utf-8") as f:
    data={"url":"https://www.amazon.com","data":flat_result}
    json.dump(data, f, indent=2)
