

# **🎥 AI Video Generation (`video_gen`)**
> **Generate AI-powered videos from text descriptions using OpenAI APIs.**  

The **`video_gen`** project enables **AI-powered video generation** using **text-based prompts**. Users can:
- **Input topics they want to learn**
- **Specify the number of sessions (~5 minutes per session)**
- **Receive AI-generated videos tailored to their learning needs**  

This system integrates:
- 🎨 **A React frontend** for user input and session management.  
- ⚡ **A FastAPI backend** that interacts with OpenAI APIs to generate video content.  


---

## **🌟 Features**
✅ **AI-Powered Video Creation** – Convert text-based prompts into educational videos.  
✅ **Interactive Frontend** – Users specify their learning topics and session duration.  
✅ **Multi-Session Learning** – Generate videos in **5-minute sessions** for structured learning.  
✅ **FastAPI Backend** – Handles API requests and processes AI-generated content.  
✅ **OpenAI API Integration** – Uses **GPT-4** (text) and **DALL·E** (image/video generation).  
✅ **Lightweight JSON Storage** – Stores user inputs and video generation requests **without a database**.  

---

## **🛠️ Tech Stack**
| **Component**  | **Technology Used**                     |
|---------------|--------------------------------------|
| **Frontend**  | React.js, JavaScript, Axios         |
| **Backend**   | FastAPI, Python                     |
| **AI Model**  | GPT-4 (text), DALL·E (image/video)  |
| **Storage**   | JSON file-based storage (NoSQL-like) |
| **Deployment** | Localhost, Future Cloud Deployment (AWS/GCP) |

---


## **📁 Project Structure**
```
video_gen/
│
├── backend/
│   ├── callapi.py              # Handles API requests to OpenAI
│   ├── create_images.py        # Generates images using DALL·E
│   ├── create_images_long.py   # Generates extended images for long prompts
│   ├── fuse_all.py             # Merges audio and video into a final product
│   ├── fuse_img_audi.py        # Combines generated images with AI audio
│   ├── main.py                 # FastAPI backend server
│   ├── nlt_download.py         # Downloads required NLTK corpora
│   ├── tell_meore.py           # Text generation logic
│   ├── text2speech.py          # Converts generated text to speech
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.js              # Main React component
│   │   ├── api.js              # Handles API requests from the frontend
│   │   ├── InputForm.js        # Form for user topic input
│   │   ├── VideoDisplay.js     # Displays generated videos
│   │   ├── index.js            # Frontend entry point
│   ├── App.css                 # Styling for the app
│   ├── index.css               # Global styles
│
└── assets/                     # Example outputs and generated videos
```

---


## **🎬 How It Works**
1. **User Input**:
   - Enter a topic and the number of ~5-minute sessions you want.
2. **Content Generation**:
   - The backend generates images and text using OpenAI APIs.
   - Text is converted into speech, and videos are created using MoviePy.
3. **Video Delivery**:
   - The generated video is displayed on the frontend.

---



