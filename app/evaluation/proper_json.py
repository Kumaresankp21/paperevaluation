import json

def parse_json_string(json_string):
    """
    Takes a JSON string and converts it into a proper JSON object (Python dictionary).
    If the string is not valid JSON, it returns an empty dictionary with an error message.
    """
    try:
        print(type(json_string))
        return json.loads(json_string)  # Convert JSON string to dictionary
    except json.JSONDecodeError as e:
        return {"error": "Invalid JSON format", "details": str(e)}