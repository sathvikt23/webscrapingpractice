import json
from pathlib import Path
from pydantic import BaseModel, Field, validator, root_validator
from typing import Dict, Union, Any, Optional, List
from logger import logger
#from models.web_scraping.web_scraping_models import SchemaField
#from models.web_scraping.web_scraping_models import UserCustomSchemaRequest
#from models.web_scraping.web_scraping_models import companyWatermark

class SchemaField(BaseModel):
    selector: str
    userCreated: str
    isDynamic: str
    value: str
    # Store nested fields in a separate dict to avoid Pydantic validation issues
    nested_fields: Dict[str, 'SchemaField'] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"
        # Allow arbitrary types for nested SchemaField objects
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        # Separate base fields from nested SchemaField objects
        base_fields = {'selector', 'userCreated', 'isDynamic', 'value', 'nested_fields'}
        nested = {}
        base_data = {}
        
        for key, value in data.items():
            if key in base_fields:
                base_data[key] = value
            elif isinstance(value, (SchemaField, dict)):
                # Convert dict to SchemaField if needed
                if isinstance(value, dict) and all(k in value for k in ['selector', 'userCreated', 'isDynamic', 'value']):
                    nested[key] = SchemaField(**value)
                elif isinstance(value, SchemaField):
                    nested[key] = value
                else:
                    base_data[key] = value
            else:
                base_data[key] = value
        
        # Add nested fields to the nested_fields dict
        if nested:
            if 'nested_fields' not in base_data:
                base_data['nested_fields'] = {}
            base_data['nested_fields'].update(nested)
        
        super().__init__(**base_data)
        
        # Also store nested fields as direct attributes for backward compatibility
        for key, value in nested.items():
            setattr(self, key, value)

    @root_validator(pre=True)
    def handle_nested_schema_fields(cls, values):
        """Pre-process to handle nested SchemaField objects"""
        if not isinstance(values, dict):
            return values
            
        base_fields = {'selector', 'userCreated', 'isDynamic', 'value', 'nested_fields'}
        nested_fields = {}
        cleaned_values = {}
        
        for key, value in values.items():
            if key in base_fields:
                cleaned_values[key] = value
            elif isinstance(value, dict) and 'selector' in value:
                # This looks like a SchemaField dict
                nested_fields[key] = value
            else:
                cleaned_values[key] = value
        
        if nested_fields:
            if 'nested_fields' not in cleaned_values:
                cleaned_values['nested_fields'] = {}
            cleaned_values['nested_fields'].update(nested_fields)
        
        return cleaned_values


# Forward reference resolution
SchemaField.model_rebuild()

class companyWatermark(BaseModel):
    isDynamic: str
    staticValue: str


class UserCustomSchemaRequest(BaseModel):
    task_id: str
    schema: Dict[str, Union[SchemaField, Any]]
    companyname: companyWatermark
    class Config:
        extra = "allow" 

class tools:
    def extract_fields_dfs(self, schema: Dict[str, Any], result: List[Dict] = None) -> List[Dict]:
        """
        DFS traversal to extract all SchemaField objects from the schema.
        Returns a flat list of fields with no parent path prefix in keys.
        """
        if result is None:
            result = []

        stack = [schema]  # Start with the whole schema dict

        while stack:
            current_dict = stack.pop()

            for key, value in current_dict.items():
                if isinstance(value, SchemaField):
                    result.append({
                        'key': key,  # Only the field name, no path
                        'selector': value.selector,
                        'userCreated': value.userCreated,
                        'isDynamic': value.isDynamic,
                        'value': value.value
                    })

                    # Process nested fields inside this SchemaField
                    nested_fields = self._extract_all_nested_fields_dfs(value)
                    if nested_fields:
                        stack.append(nested_fields)

                elif isinstance(value, dict):
                    stack.append(value)

        return result

    def _extract_all_nested_fields_dfs(self, schema_field: SchemaField) -> Dict[str, Any]:
        """
        Extracts all nested SchemaField objects from within a SchemaField.
        Only field names are used as keys (no prefix).
        """
        nested_fields = {}
        base_fields = {'selector', 'userCreated', 'isDynamic', 'value'}

        stack = [schema_field.__dict__]

        while stack:
            current_dict = stack.pop()

            for attr_name, attr_value in current_dict.items():
                if attr_name in base_fields:
                    continue

                if isinstance(attr_value, SchemaField):
                    nested_fields[attr_name] = attr_value
                elif isinstance(attr_value, dict):
                    stack.append(attr_value)
                elif hasattr(attr_value, '__dict__'):
                    stack.append(attr_value.__dict__)

        return nested_fields

    def extract_fields(self, schema: Dict[str, Any], result: List[Dict] = None, parent_key: str = "") -> List[Dict]:
        """
        Wrapper method that uses DFS for complete field extraction
        """
        return self.extract_fields_dfs(schema, result, parent_key)

    def build_project(self, schema_dict: Dict[str, Any], path: str = "schema") -> Dict[str, Any]:
        """Build MongoDB projection preserving the exact original schema structure"""
        
        def build_nested_projection(obj: Any, current_path: str) -> Any:
            """Recursively build projection maintaining nested structure"""
            
            if isinstance(obj, SchemaField):
                # Build the base SchemaField projection
                base_projection = {
                    "selector": {"$ifNull": [f"$schema.{current_path}.selector", None]},
                    "userCreated": {"$ifNull": [f"$schema.{current_path}.userCreated", obj.userCreated]},
                    "isDynamic": {"$ifNull": [f"$schema.{current_path}.isDynamic", obj.isDynamic]},
                    "value": {"$ifNull": [f"$schema.{current_path}.value", None]}
                }
                
                # Process nested fields within this SchemaField
                # Check both nested_fields dict and direct attributes
                nested_attrs = {}
                
                # Check nested_fields dict first
                if hasattr(obj, 'nested_fields') and obj.nested_fields:
                    for nested_key, nested_value in obj.nested_fields.items():
                        nested_path = f"{nested_key}"
                        nested_attrs[nested_key] = build_nested_projection(nested_value, nested_path)
                
                # Also check direct attributes for backward compatibility
                base_fields = {'selector', 'userCreated', 'isDynamic', 'value', 'nested_fields'}
                for attr_name in dir(obj):
                    if (not attr_name.startswith('_') and 
                        attr_name not in base_fields and 
                        attr_name not in nested_attrs):  # Don't duplicate
                        
                        attr_value = getattr(obj, attr_name)
                        if isinstance(attr_value, SchemaField):
                            nested_path = f"{current_path}.{attr_name}"
                            nested_attrs[attr_name] = build_nested_projection(attr_value, nested_path)
                
                # Merge base projection with nested attributes
                if nested_attrs:
                    base_projection.update(nested_attrs)
                
                return base_projection
                
            elif isinstance(obj, dict):
                # Handle regular dict objects
                result = {}
                for key, value in obj.items():
                    nested_path = f"{key}"
                    result[key] = build_nested_projection(value, nested_path)
                return result
                
            else:
                # For any other type, just return the MongoDB reference
                return {"$ifNull": [f"${current_path}", None]}
        
        # Start the projection from the schema root
        projected = {}
        
        for key, value in schema_dict.items():
            field_path = f"{key}"
            projected[key] = build_nested_projection(value, field_path)
        
        return projected

    def getSelector_isDynamic_userCreated_dfs(self, schema: Dict[str, Any]):
        """
        DFS approach to get selectors, dynamic values, and created values
        """
        cases = []
        selectors = []
        isDynamicValues = []
        isCreatedValues = []
        
        # Use DFS to get all fields
        all_fields = self.extract_fields_dfs(schema)
        
        logger.info(f"DFS found {len(all_fields)} total fields")
        
        for field_info in all_fields:
            field_key = field_info['key']
            selector = field_info['selector']
            user_created = str(field_info['userCreated']).lower() == "true"
            is_dynamic = str(field_info['isDynamic']).lower() == "true"
            
            # Add case for MongoDB switch statement
            cases.append({
                'case': {'$eq': ['$data.selector', selector]},
                'then': field_key
            })
            
            # Add selector to list
            selectors.append(selector)
            
            # Add to appropriate boolean lists
            if user_created:
                isCreatedValues.append(field_key)
            if is_dynamic:
                isDynamicValues.append(field_key)
        
        logger.info("DFS Results:")
        logger.info(f"Total cases: {len(cases)}")
        logger.info(f"Selectors: {selectors}")
        logger.info(f"Dynamic Values: {isDynamicValues}")
        logger.info(f"Created Values: {isCreatedValues}")
        logger.info("Cases: %s", json.dumps(cases, indent=2))
        
        return cases, selectors, isDynamicValues, isCreatedValues

    def getSelector_isDynamic_userCreated(self, schema: Dict[str, Any]):
        """
        Use DFS version for complete extraction
        """
        return self.getSelector_isDynamic_userCreated_dfs(schema)

    def build_pipeline(self, URLs: list[str], request_model: UserCustomSchemaRequest):
        """Build MongoDB aggregation pipeline with DFS-based field extraction"""
        schema = request_model.schema

        cases, selectors, isDynamicValues, isCreatedValues = self.getSelector_isDynamic_userCreated_dfs(schema)
        print(schema)
        project_schema = self.build_project(schema)
        
        pipeline = [
            {
                '$match': {'url': {'$in': URLs}}
            },
            {
                '$unwind': '$data'
            },
            {
                '$match': {'data.selector': {'$in': selectors}}
            },
            {
                '$addFields': {
                    'fieldName': {
                        '$switch': {
                            'branches': cases,
                            'default': 'unknown'
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': {
                       
                        'url': '$url'
                    },
                    'schemaFields': {
                        '$push': {
                            'k': '$fieldName',
                            'v': {
                                'selector': '$data.selector',
                                'userCreated': {
                                    '$cond': [
                                        {'$in': ['$fieldName', isCreatedValues]},
                                        'true',
                                        'false'
                                    ]
                                },
                                'isDynamic': {
                                    '$cond': [
                                        {'$in': ['$fieldName', isDynamicValues]},
                                        'true',
                                        'false'
                                    ]
                                },
                                'value': '$data.meta'
                            }
                        }
                    }
                }
            },
            {
                '$project': {
                    '_id': 0,
                   
                    'url': '$_id.url',
                    'schema': {
                        '$arrayToObject': '$schemaFields'
                    }
                }
                
            },
            {
            '$project': {
                    '_id': 0,
                    
                    'url': 1,
                    'schema':project_schema
                }
            }
        ]

        # Save pipeline for debugging
        with open("debug_pipeline.json", "w") as f:
            json.dump(pipeline, f, indent=2)
        logger.info("Saved pipeline to debug_pipeline.json")

        return pipeline

    def print_schema_structure_dfs(self, schema: Dict[str, Any], indent: int = 0):
        """DFS-based schema structure visualization"""
        all_fields = self.extract_fields_dfs(schema)
        
        print("DFS Schema Structure (All Fields):")
        print("=" * 80)
        
        # Group fields by their depth level
        depth_groups = {}
        for field_info in all_fields:
            depth = field_info['key'].count('.')
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(field_info)
        
        # Print fields grouped by depth
        for depth in sorted(depth_groups.keys()):
            print(f"\nDepth Level {depth}:")
            print("-" * 40)
            for field_info in depth_groups[depth]:
                indent_str = "  " * depth
                print(f"{indent_str}├── {field_info['key']}")
                print(f"{indent_str}│   ├── selector: {field_info['selector']}")
                print(f"{indent_str}│   ├── userCreated: {field_info['userCreated']}")
                print(f"{indent_str}│   ├── isDynamic: {field_info['isDynamic']}")
                print(f"{indent_str}│   └── value: {field_info['value']}")


if __name__ == "__main__":
    # Your code here

    # Create complex nested schema structure to test DFS
       
        mock_schema = {
            "product_name": SchemaField(
                selector="html.no-js > body.wp-singular.page-template.page-template-templates.page-template-book-details.page-template-templatesbook-details-php.page.page-id-16894.wp-theme-harper-collins-global.wp-child-theme-harper-collins-ca-child.fl-builder-2-8-6-1.tribe-no-js > noscript",
                userCreated="false",
                isDynamic="true",
                value="Product Name",
                # Multiple nested fields at different levels
                select_size=SchemaField(
                    selector=".size-select",
                    userCreated="true",
                    isDynamic="true",
                    value="Size Selector",
                    # Deeply nested field
                    size_options=SchemaField(
                        selector=".size-options",
                        userCreated="true",
                        isDynamic="false",
                        value="Size Options",
                        # Even deeper nesting
                        available_sizes=SchemaField(
                            selector=".available-sizes",
                            userCreated="false",
                            isDynamic="true",
                            value="Available Sizes"
                        )
                    )
                ),
                # Another nested field at the same level
                product_color=SchemaField(
                    selector=".product-color",
                    userCreated="true",
                    isDynamic="true",
                    value="Product Color",
                    color_variants=SchemaField(
                        selector=".color-variants",
                        userCreated="false",
                        isDynamic="true",
                        value="Color Variants"
                    )
                )
            ),
            "select_size": SchemaField(
                selector=".size-select-main",
                userCreated="true",
                isDynamic="true",
                value="Main Size Select"
            ),
            "price": SchemaField(
                selector=".price",
                userCreated="false",
                isDynamic="true",
                value="Price",
                # Nested pricing fields that should now be extracted
                discount_price=SchemaField(
                    selector=".discount-price",
                    userCreated="true",
                    isDynamic="true",
                    value="Discount Price"
                ),
                original_price=SchemaField(
                    selector=".original-price",
                    userCreated="false",
                    isDynamic="true",
                    value="Original Price",
                    # Even deeper nesting to test DFS
                    currency_info=SchemaField(
                        selector=".currency-info",
                        userCreated="true",
                        isDynamic="false",
                        value="Currency Information"
                    )
                )
            )
        }

        watermark = companyWatermark(isDynamic="true", staticValue="DemoCompany")

        user_request = UserCustomSchemaRequest(
            task_id="task_001",
            schema=mock_schema,
            companyname=watermark
        )

        tool = tools()
        
        # Test DFS extraction
        print("DFS Field Extraction Test:")
        print("=" * 80)
        
        fields = tool.extract_fields_dfs(mock_schema)
        
        print(f"Total fields extracted: {len(fields)}")
        print("\nAll extracted fields:")
        for i, field in enumerate(fields, 1):
            print(f"{i:2d}. {field['key']}")
            print(f"    ├── selector: {field['selector']}")
            print(f"    ├── userCreated: {field['userCreated']}")
            print(f"    ├── isDynamic: {field['isDynamic']}")
            print(f"    └── value: {field['value']}")
            print()
        
        # Visualize structure
        print("\n" + "=" * 80)
        tool.print_schema_structure_dfs(mock_schema)
        
        # Test pipeline generation
        print("\n" + "=" * 80)
        print("Pipeline Generation Test:")
        print("=" * 80)
        
        urls = ["https://example.com/product1", "https://example.com/product2"]
        pipeline = tool.build_pipeline(urls, user_request)
        
        # Verify discount_price and original_price are in the pipeline
        print("Checking if discount_price and original_price are extracted:")
        pipeline_str = json.dumps(pipeline, indent=2)
        
        if "price.discount_price" in pipeline_str:
            print("✅ discount_price found in pipeline as 'price.discount_price'")
        else:
            print("❌ discount_price NOT found in pipeline")
        
        if "price.original_price" in pipeline_str:
            print("✅ original_price found in pipeline as 'price.original_price'")
        else:
            print("❌ original_price NOT found in pipeline")
        
        if "price.original_price.currency_info" in pipeline_str:
            print("✅ currency_info found in pipeline as 'price.original_price.currency_info'")
        else:
            print("❌ currency_info NOT found in pipeline")
        
        print(f"\nGenerated pipeline with {len(json.loads(json.dumps(pipeline))[3]['$addFields']['fieldName']['$switch']['branches'])} cases")
        print(json.dumps(pipeline, indent=2))
        