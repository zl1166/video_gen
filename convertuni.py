import json

# Load the JSON content from a file that might have escape sequences
with open("course_tellmemore.json", "r") as json_file:
    raw_content = json_file.read()

# Decode Unicode escape sequences into their actual characters
decoded_content = raw_content.encode().decode('unicode_escape')

# Try to parse the decoded content as JSON
try:
    parsed_json = json.loads(decoded_content)
    
    # Save the fixed JSON back to a file
    with open("course_content_fixed.json", "w") as fixed_json_file:
        json.dump(parsed_json, fixed_json_file, indent=4, ensure_ascii=False)  # ensure_ascii=False will prevent escaping non-ASCII characters

    print("Fixed JSON content saved to 'course_content_fixed.json'.")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
