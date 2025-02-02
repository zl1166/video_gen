
import json
from openai import OpenAI
import os
import requests
import pdb

# Replace with your OpenAI API key
with open('key.json', 'r') as file:
    key_data = json.load(file)
api_key = key_data['key']

# Step 3: Set the API key as an environment variable
os.environ['OPENAI_API_KEY'] = api_key

# Parse the JSON content into a Python dictionary
with open('course_tellmemore_long.json', 'r') as file:
    data = json.load(file)

client = OpenAI()
overalltitle = data[0]["title"]
def save_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        # Save the image content to a file
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Image saved as {filename}")
    else:
        print(f"Failed to download image from {url}")
# Function to generate images
def generate_image(description, style, image_num):
    # Create the prompt for the image generation
    prompt = f"{description} {style}"
    
    # Call the OpenAI Image API
    response = client.images.generate(
  model="dall-e-3",
  prompt=prompt,
  size="1024x1024",
  quality="standard",
  style= "natural",
  n=1,
)
    
    # Extract and print the image URL
    image_url = response.data[0].url
    print(f"Image {image_num} URL: {image_url}")

    # Download and save the image
    save_image(image_url, f"image_{image_num}.png")


# Define the consistent visual style
consistent_style = "Clean Style. Ensure that no words or no letters appear in the image."

# Loop through each subtitle in the parsed data and generate an image
for idx, subtitle in enumerate(data[0]["content"], start=0):
    # Access the description from the subtitle dictionary
    if idx ==0:
        generate_image(overalltitle, consistent_style, idx)
    else:
        generate_image(subtitle["subsection"], consistent_style, idx)
