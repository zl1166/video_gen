from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import glob
import os
# Define your image files and audio files
for i in range(6):
    image_files = glob.glob(f'./img_{i}/*')
    audio_files =  glob.glob(f'./mp3_{i}/*')

    # Ensure that the number of images and audio tracks match
    assert len(image_files) == len(audio_files), "Number of images and audio files must be equal."

    # Create video clips for each image with corresponding audio
    clips = []
    for img, audio in zip(image_files, audio_files):
        # Load the corresponding audio file
        audio_clip = AudioFileClip(audio)
        
        # Create an ImageClip with the duration matching the audio clip's duration
        image_clip = ImageClip(img).set_duration(audio_clip.duration)
        
        # Set the audio to the image clip
        image_clip = image_clip.set_audio(audio_clip)
        
        # Append the clip to the list
        clips.append(image_clip)

    # Concatenate all the clips into one video
    final_video = concatenate_videoclips(clips, method='compose')
    folder_path = f'./good_e'

# Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Write the result to a video file
    final_video.write_videofile(os.path.join(folder_path,f"good_e_{i}.mp4"), fps=24, codec='libx264', audio_codec='aac')

