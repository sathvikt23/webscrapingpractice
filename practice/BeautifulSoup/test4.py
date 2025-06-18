def extract_fields(schema, parent_key=None, result=None):
    if result is None:
        result = []

    for key, value in schema.items():
        if isinstance(value, dict):
            # Check if this dict represents a schema field (has a selector)
            if 'selector' in value:
                result.append({
                    
                    'key': key,
                    'selector': value.get('selector', ''),
                    'userCreated': value.get('userCreated', ''),
                    'isDynamic': value.get('isDynamic', '')
                })
            
            # Recurse into children (other keys that might be fields)
            for subkey, subvalue in value.items():
                if isinstance(subvalue, dict) and 'selector' in subvalue:
                    extract_fields({subkey: subvalue}, parent_key=key, result=result)
    
    return result

def build_project(schema_dict, path="schema"):
    def wrap_fields(full_path):
        return {
            "selector": { "$ifNull": [f"${full_path}.selector", None] },
            "userCreated": { "$ifNull": [f"${full_path}.userCreated", None] },
            "isDynamic": { "$ifNull": [f"${full_path}.isDynamic", None] },
            "value": { "$ifNull": [f"${full_path}.value", None] }
        }

    result = {}

    for key, val in schema_dict.items():
        if isinstance(val, dict) and 'selector' in val:
            full_path = f"{path}.{key}"
            result[key] = wrap_fields(full_path)

            # Check if this field has nested child fields
            for child_key, child_val in val.items():
                if isinstance(child_val, dict) and 'selector' in child_val:
                    result[key][child_key] = wrap_fields(f"{path}.{child_key}")
                    
    return result

data ={
    "product_name": {
        "selector": ".p-sdnfsjhjd",
        "userCreated": "false",
        "isDynamic": "true",
        "value": ""
    },
        "select size": {
            "selector": ".p-sdnfsjhjd",
            "userCreated": "true",
            "isDynamic": "true",
            "value": ""
        }
    }
import json
print(json.dumps(build_project(data),indent=1))