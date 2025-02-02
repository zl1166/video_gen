
import json
from openai import OpenAI
import os

# Replace with your OpenAI API key
with open('key.json', 'r') as file:
    key_data = json.load(file)
api_key = key_data['key']

# Step 3: Set the API key as an environment variable
os.environ['OPENAI_API_KEY'] = api_key


client = OpenAI()
client.api_key = key_data['key']
topic = "the book good energy by Casey Means with Calley Means"
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are an online content creator."},
        {
            "role": "user",
            "content": f"You are a course creator on {topic} for 2 weeks." +"""

You generate podcast sections, where each section introduces one or multiple similar ideas. 

Each section must include the following fields:
- 'title': A concise summary of the main idea for that day's lesson.
- 'text': A explanation or overview for that section and main points that we are going to talk about.

You will output the course **strictly in JSON format**, following the structure below:

[
  {
    "title": "Section Title",
    "text": "A overview for this section. be specific about the topics that this section going to cover. each section should be unique" 
  }
]

Ensure that every JSON response adheres to valid formatting rules and does not include non-JSON characters or formatting. Do not include any formatting, code blocks, or markdown such as ```json or ``` at the start or end. Return the output as valid JSON only.
"""
        }
    ]
)

# Print the response from the assistant


# Assuming 'completion' is the response from the API
response_message = completion.choices[0].message.content
print(response_message )

# Try to parse the response content as JSON
try:
    extracted_json = json.loads(response_message)
    
    # Save the extracted JSON to a file
    import os
    os.makedirs(f"""{"_".join(topic.split(" "))}""",exist_ok=True)
    with open(f"""{"_".join(topic.split(" "))}/course_content.json""", "w") as json_file:
        json.dump(extracted_json, json_file, indent=4)
    
    print(f"JSON content saved to {topic}/course_content.json")
except json.JSONDecodeError:
    print("Error: The content is not valid JSON.")

