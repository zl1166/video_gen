from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# Define your image files and audio files
image_files = ['image_0.png', 'image_1.png', 'image_2.png', 'image_3.png', 'image_4.png', 'image_5.png', 'image_6.png','image_7.png','image_8.png']
audio_files = ['section_0.mp3', 'section_1.mp3', 'section_2.mp3', 'section_3.mp3', 'section_4.mp3', 'section_5.mp3', 'section_6.mp3','section_7.mp3','section_8.mp3']


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

# Write the result to a video file
final_video.write_videofile("output_video2.mp4", fps=24, codec='libx264', audio_codec='aac')

