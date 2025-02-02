import json
import re
from openai import OpenAI
import os
import glob
# Replace with your OpenAI API key
with open('key.json', 'r') as file:
    key_data = json.load(file)
api_key = key_data['key']
topic = "the book good energy by Casey Means with Calley Means"
all = glob.glob(f"""{"_".join(topic.split(" "))}/subtrans/*""")
print(all)

# Step 3: Set the API key as an environment variable
os.environ['OPENAI_API_KEY'] = api_key
# Initialize the OpenAI client (make sure to replace 'your-api-key' with your actual API key)
client = OpenAI()

for idx,cur in enumerate(all):
    # Load your JSON data (if it's stored in a file named 'data.json')
    with open(cur, 'r') as file:
        data = json.load(file)

    # Function to sanitize subtitle for file naming
    def sanitize_filename(subtitle):
        # Remove special characters and replace spaces with underscores
        return re.sub(r'[^a-zA-Z0-9\s]', '', subtitle).strip().replace(' ', '_')

    # Iterate through each section and create TTS for each transcript
    for i,section in enumerate(data):
        # Sanitize the subtitle to create a suitable filename
        subtitle = section["subtitle"]
        sanitized_subtitle = sanitize_filename(subtitle)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="echo",  # Replace "echo" with the desired voice, if applicable
            input=section["transcript"]
        )
        
        # Save the response to a file, naming it based on the sanitized subtitle
        import os

        folder_path = f"""{"_".join(topic.split(" "))}/mp3/mp3_{idx}"""

        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_name =  f"{i}.mp3"
        response.stream_to_file(os.path.join(folder_path,file_name))

        print(f"Generated {file_name} for subtitle: {subtitle}")