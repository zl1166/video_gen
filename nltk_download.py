# import whisper
# import re

# def is_sentence_end(text):
#     """Check if the text ends with a sentence-ending punctuation."""
#     return re.search(r'[.!?]["\']?\s*$', text.strip()) is not None

# def format_timestamp(seconds):
#     """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
#     milliseconds = int((seconds - int(seconds)) * 1000)
#     seconds = int(seconds)
#     hours = seconds // 3600
#     minutes = (seconds % 3600) // 60
#     seconds = seconds % 60
#     return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# def main():
#     # Load the Whisper model
#     model = whisper.load_model("base")

#     # Transcribe the audio file
#     result = model.transcribe("clip.mp3")
#     segments = result['segments']

#     # Process segments to group into sentences
#     sentence_list = []
#     current_sentence = ''
#     current_start_time = None

#     for segment in segments:
#         text = segment['text'].strip()
#         start_time = segment['start']
#         end_time = segment['end']
        
#         if current_start_time is None:
#             current_start_time = start_time
            
#         current_sentence += (' ' if current_sentence else '') + text
        
#         if is_sentence_end(text):
#             # End of a sentence
#             sentence_list.append({
#                 'start': current_start_time,
#                 'end': end_time,
#                 'text': current_sentence.strip()
#             })
#             current_sentence = ''
#             current_start_time = None

#     # Handle any remaining text
#     if current_sentence:
#         sentence_list.append({
#             'start': current_start_time,
#             'end': end_time,
#             'text': current_sentence.strip()
#         })

#     # Write the sentences to an SRT file
#     with open('output.srt', 'w', encoding='utf-8') as f:
#         for idx, sentence in enumerate(sentence_list, start=1):
#             start = format_timestamp(sentence['start'])
#             end = format_timestamp(sentence['end'])
#             text = sentence['text']
#             f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")

# if __name__ == "__main__":
#     main()
import speech_recognition as sr
from pydub import AudioSegment
import math

# Convert mp3 file to wav
def mp3_to_wav(audio_file_path):
    sound = AudioSegment.from_mp3(audio_file_path)
    audio_file_path = audio_file_path.replace(".mp3", ".wav")
    sound.export(audio_file_path, format="wav")
    return audio_file_path

# Transcribe audio file to text
def transcribe_audio(audio_file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            # using google speech recognition
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

# Create SRT file
def create_srt(transcript, audio_length, srt_file_path):
    sentences = [s.strip() for s in transcript.split('.') if s.strip()]
    num_sentences = len(sentences)
    segment_duration = math.ceil(audio_length / num_sentences)

    with open(srt_file_path, 'w') as file:
        start_time = 0
        for i, sentence in enumerate(sentences, 1):
            end_time = start_time + segment_duration
            # format times for SRT
            start_srt = f"{int(start_time // 3600):02}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02},000"
            end_srt = f"{int(end_time // 3600):02}:{int((end_time % 3600) // 60):02}:{int(end_time % 60):02},000"
            
            file.write(f"{i}\n{start_srt} --> {end_srt}\n{sentence}\n\n")
            start_time = end_time

def main():
    mp3_path = "clip.mp3"
    srt_path = "your_subtitle_file.srt"
    wav_path = mp3_to_wav(mp3_path)
    audio = AudioSegment.from_wav(wav_path)
    audio_length = len(audio) / 1000.0  # duration in seconds
    
    transcript = transcribe_audio(wav_path)
    create_srt(transcript, audio_length, srt_path)
    print("SRT file has been created successfully.")

if __name__ == "__main__":
    main()
