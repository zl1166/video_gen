
## use the api
## run tell me more
## generate the images
## generate the mp3
import json
from openai import OpenAI
import os
import requests
import pdb
import glob
# Replace with your OpenAI API key
with open('key.json', 'r') as file:
    key_data = json.load(file)
api_key = key_data['key']
os.environ['OPENAI_API_KEY'] = api_key
client = OpenAI()
# Step 3: Set the API key as an environment variable

all = glob.glob(f'./good_e/*')
# Parse the JSON content into a Python dictionary
for vid, cur in enumerate(all):
    with open(cur, 'r', encoding='utf-8') as file:
        data = json.load(file)

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
        prompt = f"{description} {style} Ensure that no words or letters appear in the image."
        
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
        folder_path = f'./img_{vid}'

    # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Download and save the image
        save_image(image_url, os.path.join( folder_path,f"image_{image_num}.png"))


    # Define the consistent visual style
    consistent_style = "Use Clean Style. Ensure that no words or no letters appear in the image."

    # Loop through each subtitle in the parsed data and generate an image
    for idx, subtitle in enumerate(data, start=0):
        # Access the description from the subtitle dictionary
        generate_image(data[idx]["subtitle"], consistent_style, idx)
