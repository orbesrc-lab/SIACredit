import json
import re

def extract_json_from_response(text):
    text = text.strip()
    
    # Extract markdown block if present
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip()
        
    # Find start of JSON
    start_idx = -1
    for i, char in enumerate(text):
        if char in ('{', '['):
            start_idx = i
            break
            
    if start_idx == -1:
        return text
        
    text = text[start_idx:]
    
    try:
        obj, end = json.JSONDecoder().raw_decode(text)
        return json.dumps(obj)
    except Exception as e:
        print("raw_decode failed:", e)
        # Fallback
        end_obj = text.rfind("}")
        end_arr = text.rfind("]")
        end_idx = max(end_obj, end_arr)
        if end_idx != -1:
            return text[:end_idx+1]
        return text

test_str1 = """Here is your json:
```json
{
    "topics": ["A", "B"]
}
```
And here is some extra data: { "bad": "data" }
"""

print("Test 1:")
print(extract_json_from_response(test_str1))

test_str2 = """{ "topics": ["A"] } And extra garbage { "b": 1 }"""
print("Test 2:")
print(extract_json_from_response(test_str2))

test_str3 = """Just { "topics": [] }"""
print("Test 3:")
print(extract_json_from_response(test_str3))
