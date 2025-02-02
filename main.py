from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os
import glob
import requests
import re
from pydantic import BaseModel
from openai import OpenAI
from requests import request

# Load OpenAI API key
with open('video_gen/key.json', 'r') as file:
    key_data = json.load(file)
api_key = key_data['key']

# Set up OpenAI API
os.environ['OPENAI_API_KEY'] = api_key
client = OpenAI(api_key=api_key)

# Initialize FastAPI app
app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
mounted_directories = {}
# Mount static directories


def mount_static_directory(app, topic, idx, sub_path, directory, name):
    """
    Mounts a static directory for a given topic and index.
    :param app: FastAPI instance
    :param topic: The topic string
    :param idx: Index for the directory
    :param sub_path: Sub-path within the topic directory (e.g., 'images/img_{idx}')
    :param directory: Directory path on disk
    :param name: Mount name
    """
    mount_path = f"/static/{'_'.join(topic.split(' '))}/{sub_path}"
    if mount_path not in mounted_directories:
        if os.path.exists(directory):
            app.mount(mount_path, StaticFiles(directory=directory), name=name)
            mounted_directories[mount_path] = directory
            print(f"Mounted {directory} at {mount_path}")
        else:
            print(f"Directory {directory} does not exist. Skipping mount.")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request data model
class TopicDurationInput(BaseModel):
    topic: str
    week: int
    times: int

def save_image(url, filename):
    """Save an image from a URL to a local file."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Image saved as {filename}")
    else:
        print(f"Failed to download image from {url}")

def generate_image(description, style, folder_path, image_num):
    try:
        prompt = f"{description} {style} Ensure no words or letters appear in the image."
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        image_url = response.data[0].url
        save_image(image_url, os.path.join(folder_path, f"image_{image_num}.png"))
    except Exception as e:
        print(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail="Error generating image.")


def fetch_presentation_data(topic: str, idx: int):
    """
    Fetch slides, audio files, and transcripts based on dynamically generated directories.
    """
    # Derive the directories from topic and index
    img_dir = f"{'_'.join(topic.split(' '))}/images/img_{idx}"
    tts_dir = f"{'_'.join(topic.split(' '))}/mp3/mp3_{idx}"

    # Fetch slide images and audio files
    slide_pics = sorted(glob.glob(f"{img_dir}/*.png"))
    mp3_files = sorted(glob.glob(f"{tts_dir}/*.mp3"))

    # Pair slides and audio files
    slides_audio_pairs = [{"slide": slide, "audio": audio} for slide, audio in zip(slide_pics, mp3_files)]

    # Fetch the transcript file
    transcript_file = f"{'_'.join(topic.split(' '))}/subtrans/{idx}.json"
    if not os.path.exists(transcript_file):
        raise HTTPException(status_code=404, detail="Transcript file not found.")

    with open(transcript_file, "r") as file:
        transcripts = json.load(file)

    return slides_audio_pairs, transcripts


@app.get("/data")
def get_presentation_data(topic: str, idx: int):
    """
    Return all slides and transcriptions for a given topic and index.
    """
    slides_audio_pairs, transcriptions = fetch_presentation_data(topic, idx)
    return {"pairs": slides_audio_pairs, "transcriptions": transcriptions}

@app.get("/data/{index}")
def get_slide_by_index(topic: str, idx: int, index: int):
    """
    Return a specific slide with audio and transcription.
    """
    slides_audio_pairs, transcriptions = fetch_presentation_data(topic, idx)

    # Validate the index
    if index < 0 or index >= len(slides_audio_pairs):
        raise HTTPException(status_code=404, detail="Slide index out of range.")

    # Get the slide and corresponding transcription
    slide_data = slides_audio_pairs[index ]
    transcription = transcriptions[index ].get("transcript", "No transcription available.")

    # Construct URLs for the slide and audio
    version = os.path.getmtime(slide_data['slide'])
    slide_url = f"http://127.0.0.1:8000/static/{'_'.join(topic.split(' '))}/images/img_{idx}/{os.path.basename(slide_data['slide'])}"
    audio_url = f"http://127.0.0.1:8000/static/{'_'.join(topic.split(' '))}/mp3/mp3_{idx}/{os.path.basename(slide_data['audio'])}"
    # slide_url = f"http://127.0.0.1:8003/static/img_{idx}/{os.path.basename(slide_data['slide'])}"
    # audio_url = f"http://127.0.0.1:8003/static/mp3_{idx}/{os.path.basename(slide_data['audio'])}"

    return {
        "index": index,
        "slide": slide_url,
        "audio": audio_url,
        "transcription": transcription,
    }




# Define the request data model
class TopicDurationInput(BaseModel):
    topic: str
    week: int
    times: int
def save_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Image saved as {filename}")
    else:
        print(f"Failed to download image from {url}")
def generate_image(description, style, folder_path, image_num):
    prompt = f"{description} {style} Ensure that no words or letters appear in the image."
    
    # Call the OpenAI Image API
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    
    # Extract the image URL and save the image
    image_url = response.data[0].url
    save_image(image_url, os.path.join(folder_path, f"image_{image_num}.png"))


@app.post("/generate-content")
async def generate_content(input: TopicDurationInput):
    topic = input.topic
    num_times = input.week * input.times

    # Generate prompt for OpenAI API
    prompt = f"You are a course creator on {topic} for a total of {num_times} sessions." +"""

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
    

    # Call OpenAI API
    filename = f"""{"_".join(topic.split(" "))}/course_content.json"""
    if os.path.exists(filename):
        return
    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an online content creator."},
                {"role": "user", "content": prompt}
            ]
        )
        response_message = completion.choices[0].message.content

        # Try to parse the response as JSON
        try:
            extracted_json = json.loads(response_message)
            
            # Save the extracted JSON to a file
            
            filename = f"""{"_".join(topic.split(" "))}/course_content.json"""
            os.makedirs(f"""{"_".join(topic.split(" "))}""",exist_ok=True)
            with open(filename, "w") as json_file:
                json.dump(extracted_json, json_file, indent=4)
            
            return {"message": "Content generated and saved.", "filename": filename}
        
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Generated content is not valid JSON.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {e}")
# Function to sanitize subtitle for file naming
def sanitize_filename(subtitle):
    # Remove special characters and replace spaces with underscores
    return re.sub(r'[^a-zA-Z0-9\s]', '', subtitle).strip().replace(' ', '_')

@app.post("/generate-video-script/{idx}")
async def generate_video_script(idx: int, topic: str = Query(..., description="The topic for the video script")):
    input_file = f"""{'_'.join(topic.split(' '))}/course_content.json"""
    if not os.path.exists(input_file):
        raise HTTPException(status_code=404, detail="Course content file not found.")
    try:
        trans_exist=False
        output_dir = f"{'_'.join(topic.split(' '))}/subtrans"
        output_file = f"{output_dir}/{idx}.json"
        if not os.path.exists(output_file):
                # Load the course content JSON
            with open(input_file, 'r') as file:
                sections = json.load(file)

            # Validate index
            if idx < 0 or idx >= len(sections):
                raise HTTPException(status_code=400, detail="Invalid index. Please provide a valid section index.")

            # Get the specified section
            section = sections[idx]
            subtopic = section["text"]

            # Generate the script using OpenAI API
            prompt = (
                f"You are creating a video script for the course on {topic}." +
                f"Write a detailed 5-minute script based on the concept: {subtopic}" + """
                Structure:
                - Introduction (~60-75 words)
                - Main Content (~500 words, with examples and actionable advice)
                - Conclusion (~60-75 words)
                
                Output strictly as JSON:
                [
                    {
                        "subtitle": "Segment Title",
                        "transcript": "Corresponding transcript"
                    }
                ]
                """
            )

            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an online content creator."},
                    {"role": "user", "content": prompt},
                ],
            )
            response_message = completion.choices[0].message.content
            extracted_json = json.loads(response_message)

            # Save the generated script to a file
            
            os.makedirs(output_dir, exist_ok=True)
            output_file = f"{output_dir}/{idx}.json"

            with open(output_file, "w") as json_file:
                json.dump(extracted_json, json_file, indent=4)
        else:
            output_dir = f"{'_'.join(topic.split(' '))}/subtrans"
            os.makedirs(output_dir, exist_ok=True)
            output_file = f"{output_dir}/{idx}.json"
            trans_exist=True

        # Generate TTS for each transcript section
        tts_dir = f"{'_'.join(topic.split(' '))}/mp3/mp3_{idx}"
        mp3_exist=False
        if not os.path.exists(tts_dir):
            os.makedirs(tts_dir, exist_ok=True)
            print(f"creating {tts_dir}")

            for i, section in enumerate(extracted_json):
                subtitle = section["subtitle"]
                sanitized_subtitle = sanitize_filename(subtitle)

                # Use OpenAI's TTS API to create audio
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="echo",  # Replace with the desired voice
                    input=section["transcript"]
                )

                # Save the audio file
                file_name = f"{i}.mp3"
                response.stream_to_file(os.path.join(tts_dir, file_name))
        else:
            mp3_exist=True
        
            
        img_dir = f"{'_'.join(topic.split(' '))}/images/img_{idx}"
        img_exist=False
        if not os.path.exists(img_dir):
            os.makedirs(img_dir, exist_ok=True)
            print(f"creating {img_dir}")
            consistent_style = "Clean and modern style. Ensure no words or letters appear in the image."

            for i, section in enumerate(extracted_json):
                # Generate TTS
                subtitle = section["subtitle"]
                sanitized_subtitle = sanitize_filename(subtitle)

                tts_response = client.audio.speech.create(
                    model="tts-1",
                    voice="echo",  # Replace with the desired voice
                    input=section["transcript"]
                )
                tts_file_name = f"{i}.mp3"
                tts_response.stream_to_file(os.path.join(tts_dir, tts_file_name))

                # Generate Image
                generate_image(subtitle, consistent_style, img_dir, i)
                # Mount the directory for images
                img_dir = f"{'_'.join(topic.split(' '))}/images/img_{idx}"
                mount_static_directory(app, topic, idx, f"images/img_{idx}", img_dir, f"images_{idx}")

                # Mount the directory for audio
                tts_dir = f"{'_'.join(topic.split(' '))}/mp3/mp3_{idx}"
                mount_static_directory(app, topic, idx, f"mp3/mp3_{idx}", tts_dir, f"audio_{idx}")



            return {
                "message": "Video script, TTS audio, and images generated and saved.",
                "script_filename": output_file,
                "audio_directory": tts_dir,
                "image_directory": img_dir,}
        else:
            img_exist=True
            # Mount the directory for images
            img_dir = f"{'_'.join(topic.split(' '))}/images/img_{idx}"
            mount_static_directory(app, topic, idx, f"images/img_{idx}", img_dir, f"images_{idx}")

            # Mount the directory for audio
            tts_dir = f"{'_'.join(topic.split(' '))}/mp3/mp3_{idx}"
            mount_static_directory(app, topic, idx, f"mp3/mp3_{idx}", tts_dir, f"audio_{idx}")


            return {
                "message": f"Video script exist {trans_exist}, TTS audio exist {mp3_exist} , and images exist {img_exist}.",
                "script_filename": output_file,
                "audio_directory": tts_dir,
                "image_directory": img_dir,
            } 

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error in JSON format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating script, TTS, or images: {e}")
@app.get("/get-json-entries")
async def get_json_entries(topic: str = Query(..., description="The topic name for which JSON file is generated")):
    # Construct the filename based on the topic
    filename = f"""{"_".join(topic.split(" "))}/course_content.json"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
            return {"length": len(data), "entries": data}
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error reading JSON file")
    else:
        raise HTTPException(status_code=404, detail="JSON file not found")
