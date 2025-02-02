
import json
from openai import OpenAI
import os


# Replace with your OpenAI API key
with open('key.json', 'r') as file:
    key_data = json.load(file)
api_key = key_data['key']

# Step 3: Set the API key as an environment variable
os.environ['OPENAI_API_KEY'] = api_key
topic = "the book good energy by Casey Means with Calley Means"
with open(f"""{"_".join(topic.split(" "))}/course_content.json""", 'r') as file:
    current = json.load(file)
client = OpenAI()
client.api_key = key_data['key']


for idx,sub in enumerate(current):
    subtopic = sub["text"]
    prompt = f"You are a content creator to create a course on {topic}."+ f"Your task is to write a detailed 5-minute video script based on the following concept:{subtopic}"+"""The script should be engaging, clear, and informative. It should expand on the idea of concentration and explain how it helps in both personal and professional life. Include examples, benefits, and practical applications.

Requirements:
- The transcript for shorts video tailed for working professionals should take approximately 5 minutes to read aloud.
- It should not include any filler content, and the focus should stay on the concept provided.
- The structure should include:
  - Introduction to hook the listener. ( ~60-75 words)
  - Main Content expanding on the importance of the topic with examples (~100 words) and 3-4 actionable advice (~360-480 words). 
  - Conclusion summarizing the key points and encouraging listeners to practice learnings from this lesson in their daily lives. (~60-75 words))
  
Output:
- The output should be formatted strictly as JSON in the following structure, allowing for multiple segments:
  ```json
  [
      {
          "subtitle": "Segment Title 1",
          "transcript": "Corresponding transcript of this sec"
      },
      {
          "subtitle": "Segment Title 2",
          "transcript":  "Corresponding transcript of this sec"
      },
      ...
  ]
  ```

Make sure to include real-world applications and tips for improving concentration. The output should be purely in JSON format, without any additional text or formatting like markdown. Do not include any formatting, code blocks, or markdown such as ```json or ``` at the start or end. Return the output as valid JSON only.
"""

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an online content creator."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Print the response from the assistant


    # Assuming 'completion' is the response from the API
    response_message = completion.choices[0].message.content

    # Try to parse the response content as JSON
    try:
        extracted_json = json.loads(response_message)
        
        # Save the extracted JSON to a file
        import os 
        os.makedirs(f"""{"_".join(topic.split(" "))}/subtrans""",exist_ok=True)
        with open(f"""{"_".join(topic.split(" "))}/subtrans/{idx}.json""", "w") as json_file:
            json.dump(extracted_json, json_file, indent=4)
        
        print("JSON content saved to 'course_content.json'.")
    except json.JSONDecodeError:
        print("Error: The content is not valid JSON.")

