import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css"; // Import external CSS for styling

function App() {
  const [topic, setTopic] = useState("");
  const [storedTopic, setStoredTopic] = useState("");
  const [week, setWeek] = useState("");
  const [times, setTimes] = useState("");
  const [response, setResponse] = useState("");
  const [jsonEntries, setJsonEntries] = useState([]);
  const [entryCount, setEntryCount] = useState(0);
  const [isSlideView, setIsSlideView] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [slideData, setSlideData] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [totalSlides, setTotalSlides] = useState(0);
  const [loadingIndices, setLoadingIndices] = useState([]);
  const [completedIndices, setCompletedIndices] = useState([]);
  const audioRef = useRef(null);

  const handleSend = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/generate-content", {
        topic,
        week: parseInt(week),
        times: parseInt(times),
      });

      if (res.data.message) {
        setResponse("Content generation complete");
        setStoredTopic(topic);
        fetchJsonEntries(topic);
      } else {
        setResponse("Failed to generate content");
      }
    } catch (error) {
      console.error("Error:", error.message);
      setResponse("Error generating content. Please try again.");
    }
  };

  const fetchJsonEntries = async (topic) => {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/get-json-entries?topic=${encodeURIComponent(topic)}`
      );
      setJsonEntries(res.data.entries || []);
      setEntryCount(res.data.length || 0);
    } catch (error) {
      console.error("Error fetching JSON entries:", error.message);
      setJsonEntries([]);
      setEntryCount(0);
    }
  };

  const handleGenerateContent = async (index) => {
    // setCompletedIndices([]);
    setLoadingIndices((prev) => [...prev, index]);

    try {
      const res = await axios.post(
        `http://127.0.0.1:8000/generate-video-script/${index}`,
        null,
        {
          params: {
            topic: storedTopic,
          },
        }
      );

      if (res.data.message) {
        setResponse(`Content generated for Week ${Math.floor(index / times) + 1}, Session ${(index % times) + 1}`);
        setCompletedIndices((prev) => [...prev, index]);
      } else {
        setResponse(`Failed to generate content for Week ${Math.floor(index / times) + 1}, Session ${(index % times) + 1}`);
      }
    } catch (error) {
      console.error(`Error generating content for index ${index}:`, error.message);
      setResponse(`Error generating content for Week ${Math.floor(index / times) + 1}, Session ${(index % times) + 1}`);
    } finally {
      setLoadingIndices((prev) => prev.filter((i) => i !== index));
    }
  };

  const handleViewSlides = (index) => {
    setSelectedIndex(index);
    setIsSlideView(true);
    setCurrentIndex(1);
    fetchSlide(index);
  };

  useEffect(() => {
    if (isSlideView && storedTopic) {
      axios
        .get(
          `http://127.0.0.1:8000/data?topic=${encodeURIComponent(storedTopic)}&idx=${selectedIndex}`
        )
        .then((response) => {
          setTotalSlides(response.data.pairs.length);
        })
        .catch((error) => {
          console.error("Error fetching total slides:", error.message);
        });
    }
  }, [isSlideView, storedTopic, selectedIndex]);

  useEffect(() => {
    if (isSlideView && selectedIndex !== null) {
      fetchSlide(currentIndex-1);
    }
  }, [currentIndex, isSlideView, selectedIndex]);

  const fetchSlide = (index) => {
    const topicEncoded = encodeURIComponent(storedTopic);
    axios
      .get(`http://127.0.0.1:8000/data/${index}?topic=${topicEncoded}&idx=${selectedIndex}`)
      .then((response) => {
        setSlideData(response.data);
      })
      .catch((error) => {
        console.error(`Error fetching slide ${index}:`, error.message);
      });
  };

  useEffect(() => {
    if (audioRef.current && slideData?.audio) {
      audioRef.current.play().catch((err) => {
        console.warn("Audio playback failed:", err.message);
      });
    }
  }, [slideData]);

  const nextSlide = () => {
    if (currentIndex < totalSlides) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const prevSlide = () => {
    if (currentIndex > 1) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  return (
    <div>
      {!isSlideView ? (
        <div style={{ padding: "20px" }}>
          <h1>Enter Topic and Duration</h1>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter topic"
          />
          <input
            type="number"
            value={week}
            onChange={(e) => setWeek(e.target.value)}
            placeholder="Number of weeks"
          />
          <input
            type="number"
            value={times}
            onChange={(e) => setTimes(e.target.value)}
            placeholder="Times per week"
          />
          <button onClick={handleSend}>Generate Content</button>
          <p>Response from Backend: {response}</p>

          <div style={{ marginTop: "20px" }}>
            <h2>Generated Sections</h2>
            {jsonEntries.length > 0 ? (
              jsonEntries.map((entry, index) => (
                <div key={index} style={{ marginBottom: "10px", display: "flex", alignItems: "center" }}>
                  <span style={{ marginRight: "10px" }}>
                    {`Week ${Math.floor(index / times) + 1}, Session ${(index % times) + 1}`}
                  </span>
                  <button
                    style={{ margin: "0 10px", position: "relative" }}
                    onClick={() => handleGenerateContent(index)}
                    disabled={loadingIndices.includes(index)}
                  >
                    {loadingIndices.includes(index) ? (
                      <div className="spinner" />
                    ) : completedIndices.includes(index) ? (
                      <span style={{ color: "green" }}>✔</span>
                    ) : (
                      "Generate Content"
                    )}
                  </button>
                  <button onClick={() => handleViewSlides(index)}>
                    View Slides
                  </button>
                </div>
              ))
            ) : (
              <p>No sections generated yet. Please generate content first.</p>
            )}
            <p>Total Sections: {entryCount}</p>
          </div>
        </div>
      ) : (
        <div style={{ textAlign: "center", margin: "20px" }}>
          <h1>Slide and Audio Viewer</h1>
          {slideData ? (
            <>
              <img
                src={slideData.slide}
                alt={`Slide ${currentIndex}`}
                style={{
                  width: "80%",
                  height: "auto",
                  border: "2px solid #ddd",
                  boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
                  borderRadius: "10px",
                  marginBottom: "20px",
                }}
              />
              <div style={{ display: "flex", justifyContent: "center", gap: "15px" }}>
                <button onClick={prevSlide} disabled={currentIndex === 1}>
                  Previous
                </button>
                <span>
                  Slide {currentIndex} of {totalSlides}
                </span>
                <button onClick={nextSlide} disabled={currentIndex === totalSlides}>
                  Next
                </button>
              </div>
              <div>
                <strong>Transcript:</strong>
                <p>{slideData.transcription}</p>
              </div>
              <audio ref={audioRef} key={slideData.audio} src={slideData.audio} controls autoPlay />
              <div style={{ marginTop: "20px" }}>
                <button
                  onClick={() => setIsSlideView(false)}
                  style={{
                    backgroundColor: "#007BFF",
                    color: "white",
                    border: "none",
                    padding: "10px 20px",
                    borderRadius: "5px",
                    cursor: "pointer",
                    fontSize: "16px",
                  }}
                >
                  Back to Sections
                </button>
              </div>
            </>
          ) : (
            <p>Loading slide data...</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;



// import React, { useState, useEffect, useRef } from "react";
// import axios from "axios";
// import "./App.css"; // Import external CSS for styling

// function App() {
//   const [topic, setTopic] = useState("");
//   const [storedTopic, setStoredTopic] = useState("");
//   const [week, setWeek] = useState("");
//   const [times, setTimes] = useState("");
//   const [response, setResponse] = useState("");
//   const [jsonEntries, setJsonEntries] = useState([]);
//   const [entryCount, setEntryCount] = useState(0);
//   const [isSlideView, setIsSlideView] = useState(false);
//   const [selectedIndex, setSelectedIndex] = useState(0);
//   const [slideData, setSlideData] = useState(null);
//   const [currentIndex, setCurrentIndex] = useState(0);
//   const [totalSlides, setTotalSlides] = useState(0);
//   const [loadingIndices, setLoadingIndices] = useState([]);
//   const [completedIndices, setCompletedIndices] = useState([]);
//   const audioRef = useRef(null);

//   // Function to handle sending topic and duration to the backend
//   const handleSend = async () => {
//     try {
//       const res = await axios.post("http://127.0.0.1:8004/generate-content", {
//         topic,
//         week: parseInt(week),
//         times: parseInt(times),
//       });

//       if (res.data.message) {
//         setResponse("Content generation complete");
//         setStoredTopic(topic);
//         fetchJsonEntries(topic);
//       } else {
//         setResponse("Failed to generate content");
//       }
//     } catch (error) {
//       console.error("Error:", error.message);
//       setResponse("Error generating content. Please try again.");
//     }
//   };

//   const fetchJsonEntries = async (topic) => {
//     try {
//       const res = await axios.get(
//         `http://127.0.0.1:8004/get-json-entries?topic=${encodeURIComponent(topic)}`
//       );
//       setJsonEntries(res.data.entries || []);
//       setEntryCount(res.data.length || 0);
//     } catch (error) {
//       console.error("Error fetching JSON entries:", error.message);
//       setJsonEntries([]);
//       setEntryCount(0);
//     }
//   };

//   const handleGenerateContent = async (index) => {
//     setLoadingIndices((prev) => [...prev, index]);

//     try {
//       const res = await axios.post(
//         `http://127.0.0.1:8004/generate-video-script/${index}`,
//         null,
//         {
//           params: {
//             topic: storedTopic,
//           },
//         }
//       );

//       if (res.data.message) {
//         setResponse(`Content generated for Week ${Math.floor(index / times) + 1}, Session ${(index % times) + 1}`);
//         setCompletedIndices((prev) => [...prev, index]);
//       } else {
//         setResponse(`Failed to generate content for Week ${Math.floor(index / times) + 1}, Session ${(index % times) + 1}`);
//       }
//     } catch (error) {
//       console.error(`Error generating content for index ${index}:`, error.message);
//       setResponse(`Error generating content for Week ${Math.floor(index / times) + 1}, Session ${(index % times) + 1}`);
//     } finally {
//       setLoadingIndices((prev) => prev.filter((i) => i !== index));
//     }
//   };

//   const handleViewSlides = (index) => {
//     setSelectedIndex(index);
//     setIsSlideView(true);
//     setCurrentIndex(1); // Reset to the first slide
//     fetchSlide(index);
//   };

//   useEffect(() => {
//     if (isSlideView && storedTopic) {
//       axios
//         .get(
//           `http://127.0.0.1:8004/data?topic=${encodeURIComponent(storedTopic)}&idx=${selectedIndex}`
//         )
//         .then((response) => {
//           setTotalSlides(response.data.pairs.length);
//         })
//         .catch((error) => {
//           console.error("Error fetching total slides:", error.message);
//         });
//     }
//   }, [isSlideView, storedTopic, selectedIndex]);

//   useEffect(() => {
//     if (isSlideView && selectedIndex !== null) {
//       fetchSlide(currentIndex);
//     }
//   }, [currentIndex, isSlideView, selectedIndex]);

//   const fetchSlide = (index) => {
//     const topicEncoded = encodeURIComponent(storedTopic);
//     axios
//       .get(`http://127.0.0.1:8004/data/${index}?topic=${topicEncoded}&idx=${selectedIndex}`)
//       .then((response) => {
//         setSlideData(response.data);
//       })
//       .catch((error) => {
//         console.error(`Error fetching slide ${index}:`, error.message);
//       });
//   };

//   useEffect(() => {
//     if (audioRef.current && slideData?.audio) {
//       audioRef.current.play().catch((err) => {
//         console.warn("Audio playback failed:", err.message);
//       });
//     }
//   }, [slideData]);

//   const nextSlide = () => {
//     if (currentIndex < totalSlides) {
//       setCurrentIndex((prev) => prev + 1);
//     }
//   };

//   const prevSlide = () => {
//     if (currentIndex > 1) {
//       setCurrentIndex((prev) => prev - 1);
//     }
//   };

//   return (
//     <div>
//       {!isSlideView ? (
//         <div style={{ padding: "20px" }}>
//           <h1>Enter Topic and Duration</h1>
//           <input
//             type="text"
//             value={topic}
//             onChange={(e) => setTopic(e.target.value)}
//             placeholder="Enter topic"
//           />
//           <input
//             type="number"
//             value={week}
//             onChange={(e) => setWeek(e.target.value)}
//             placeholder="Number of weeks"
//           />
//           <input
//             type="number"
//             value={times}
//             onChange={(e) => setTimes(e.target.value)}
//             placeholder="Times per week"
//           />
//           <button onClick={handleSend}>Generate Content</button>
//           <p>Response from Backend: {response}</p>

//           <div style={{ marginTop: "20px" }}>
//             <h2>Generated Sections</h2>
//             {jsonEntries.length > 0 ? (
//               jsonEntries.map((entry, index) => (
//                 <div key={index} style={{ marginBottom: "10px", display: "flex", alignItems: "center" }}>
//                   <span style={{ marginRight: "10px" }}>
//                     {`Week ${Math.floor(index / times) + 1}, Session ${(index % times) + 1}`}
//                   </span>
//                   <button
//                     style={{ margin: "0 10px", position: "relative" }}
//                     onClick={() => handleGenerateContent(index)}
//                     disabled={loadingIndices.includes(index)}
//                   >
//                     {loadingIndices.includes(index) ? (
//                       <div className="spinner" />
//                     ) : completedIndices.includes(index) ? (
//                       <span style={{ color: "green" }}>✔</span>
//                     ) : (
//                       "Generate Content"
//                     )}
//                   </button>
//                   <button onClick={() => handleViewSlides(index)}>
//                     View Slides
//                   </button>
//                 </div>
//               ))
//             ) : (
//               <p>No sections generated yet. Please generate content first.</p>
//             )}
//             <p>Total Sections: {entryCount}</p>
//           </div>
//         </div>
//       ) : (
//         <div style={{ textAlign: "center", margin: "20px" }}>
//           <h1>Slide and Audio Viewer</h1>
//           {slideData ? (
//             <>
//               <img
//                 src={slideData.slide}
//                 alt={`Slide ${currentIndex}`}
//                 style={{
//                   width: "80%",
//                   height: "auto",
//                   border: "2px solid #ddd",
//                   boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
//                   borderRadius: "10px",
//                   marginBottom: "20px",
//                 }}
//               />
//               <div style={{ display: "flex", justifyContent: "center", gap: "15px" }}>
//                 <button onClick={prevSlide} disabled={currentIndex === 1}>
//                   Previous
//                 </button>
//                 <span>
//                   Slide {currentIndex} of {totalSlides}
//                 </span>
//                 <button onClick={nextSlide} disabled={currentIndex === totalSlides}>
//                   Next
//                 </button>
//               </div>
//               <div>
//                 <strong>Transcript:</strong>
//                 <p>{slideData.transcription}</p>
//               </div>
//               <audio ref={audioRef} key={slideData.audio} src={slideData.audio} controls autoPlay />
//             </>
//           ) : (
//             <p>Loading slide data...</p>
//           )}
//         </div>
//       )}
//     </div>
//   );
// }

// export default App;


// import React, { useState, useEffect, useRef } from "react";
// import axios from "axios";

// function App() {
//   const [topic, setTopic] = useState("");
//   const [storedTopic, setStoredTopic] = useState("");
//   const [week, setWeek] = useState("");
//   const [times, setTimes] = useState("");
//   const [response, setResponse] = useState("");
//   const [jsonEntries, setJsonEntries] = useState([]);
//   const [entryCount, setEntryCount] = useState(0);
//   const [isSlideView, setIsSlideView] = useState(false);
//   const [selectedIndex, setSelectedIndex] = useState(0);
//   const [slideData, setSlideData] = useState(null);
//   const [currentIndex, setCurrentIndex] = useState(0);
//   const [totalSlides, setTotalSlides] = useState(0);
//   const audioRef = useRef(null);

//   // Function to handle sending topic and duration to the backend
//   const handleSend = async () => {
//     try {
//       const res = await axios.post("http://127.0.0.1:8003/generate-content", {
//         topic,
//         week: parseInt(week),
//         times: parseInt(times),
//       });

//       if (res.data.message) {
//         setResponse("Content generation complete");
//         setStoredTopic(topic);
//         fetchJsonEntries(topic);
//       } else {
//         setResponse("Failed to generate content");
//       }
//     } catch (error) {
//       console.error("Error:", error.message);
//       setResponse("Error generating content. Please try again.");
//     }
//   };

//   // Function to fetch entries from the generated JSON file
//   const fetchJsonEntries = async (topic) => {
//     try {
//       const res = await axios.get(
//         `http://127.0.0.1:8003/get-json-entries?topic=${encodeURIComponent(topic)}`
//       );
//       setJsonEntries(res.data.entries || []);
//       setEntryCount(res.data.length || 0);
//     } catch (error) {
//       console.error("Error fetching JSON entries:", error.message);
//       setJsonEntries([]);
//       setEntryCount(0);
//     }
//   };

//   // Function to generate video script for a specific index
//   const handleGenerateContent = async (index) => {
//     try {
//       const res = await axios.post(
//         `http://127.0.0.1:8003/generate-video-script/${index}`,
//         null,
//         {
//           params: {
//             topic: storedTopic,
//           },
//         }
//       );

//       if (res.data.message) {
//         setResponse(`Content generated for index ${index}`);
//       } else {
//         setResponse(`Failed to generate content for index ${index}`);
//       }
//     } catch (error) {
//       console.error(`Error generating content for index ${index}:`, error.message);
//       setResponse(`Error generating content for index ${index}`);
//     }
//   };

//   // Function to switch to slide viewer for a specific index
//   const handleViewSlides = (index) => {
//     setSelectedIndex(index);
//     setIsSlideView(true);
//     setCurrentIndex(1); // Reset to the first slide
//     fetchSlide(index);
//   };

//   // Fetch slides when in slide view
//   useEffect(() => {
//     if (isSlideView && storedTopic) {
//       axios
//         .get(
//           `http://127.0.0.1:8003/data?topic=${encodeURIComponent(storedTopic)}&idx=${selectedIndex}`
//         )
//         .then((response) => {
//           setTotalSlides(response.data.pairs.length);
//         })
//         .catch((error) => {
//           console.error("Error fetching total slides:", error.message);
//         });
//     }
//   }, [isSlideView, storedTopic, selectedIndex]);

//   // Fetch specific slide when currentIndex changes
//   useEffect(() => {
//     if (isSlideView && selectedIndex !== null) {
//       fetchSlide(currentIndex);
//     }
//   }, [currentIndex, isSlideView, selectedIndex]);

//   // Fetch a specific slide
//   const fetchSlide = (index) => {
//     const topicEncoded = encodeURIComponent(storedTopic);
//     axios
//       .get(`http://127.0.0.1:8003/data/${index}?topic=${topicEncoded}&idx=${selectedIndex}`)
//       .then((response) => {
//         setSlideData(response.data);
//       })
//       .catch((error) => {
//         console.error(`Error fetching slide ${index}:`, error.message);
//       });
//   };

//   // Slide navigation
//   const nextSlide = () => {
//     if (currentIndex < totalSlides) {
//       setCurrentIndex((prev) => prev + 1);
//     }
//   };

//   const prevSlide = () => {
//     if (currentIndex > 1) {
//       setCurrentIndex((prev) => prev - 1);
//     }
//   };

//   return (
//     <div>
//       {!isSlideView ? (
//         <div style={{ padding: "20px" }}>
//           <h1>Enter Topic and Duration</h1>
//           <input
//             type="text"
//             value={topic}
//             onChange={(e) => setTopic(e.target.value)}
//             placeholder="Enter topic"
//           />
//           <input
//             type="number"
//             value={week}
//             onChange={(e) => setWeek(e.target.value)}
//             placeholder="Number of weeks"
//           />
//           <input
//             type="number"
//             value={times}
//             onChange={(e) => setTimes(e.target.value)}
//             placeholder="Times per week"
//           />
//           <button onClick={handleSend}>Generate Content</button>
//           <p>Response from Backend: {response}</p>

//           <div style={{ marginTop: "20px" }}>
//             <h2>Generated Sections</h2>
//             {jsonEntries.length > 0 ? (
//               jsonEntries.map((entry, index) => (
//                 <div key={index} style={{ marginBottom: "10px" }}>
//                   <button
//                     style={{ marginRight: "10px" }}
//                     onClick={() => handleGenerateContent(index)}
//                   >
//                     Generate Content for Index {index}
//                   </button>
//                   <button onClick={() => handleViewSlides(index)}>
//                     View Slides for Index {index}
//                   </button>
//                 </div>
//               ))
//             ) : (
//               <p>No sections generated yet. Please generate content first.</p>
//             )}
//             <p>Total Sections: {entryCount}</p>
//           </div>
//         </div>
//       ) : (
//         <div style={{ textAlign: "center", margin: "20px" }}>
//           <h1>Slide and Audio Viewer</h1>
//           {slideData ? (
//             <>
//               <img
//                 src={slideData.slide}
//                 alt={`Slide ${currentIndex}`}
//                 style={{
//                   width: "80%",
//                   height: "auto",
//                   border: "2px solid #ddd",
//                   boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
//                   borderRadius: "10px",
//                   marginBottom: "20px",
//                 }}
//               />
//               <div style={{ display: "flex", justifyContent: "center", gap: "15px" }}>
//                 <button onClick={prevSlide} disabled={currentIndex === 1}>
//                   Previous
//                 </button>
//                 <span>
//                   Slide {currentIndex} of {totalSlides}
//                 </span>
//                 <button onClick={nextSlide} disabled={currentIndex === totalSlides}>
//                   Next
//                 </button>
//               </div>
//               <div>
//                 <strong>Transcript:</strong>
//                 <p>{slideData.transcription}</p>
//               </div>
//               <audio ref={audioRef} key={slideData.audio} controls>
//                 <source src={slideData.audio} type="audio/mpeg" />
//                 Your browser does not support the audio element.
//               </audio>
//             </>
//           ) : (
//             <p>Loading slide data...</p>
//           )}
//         </div>
//       )}
//     </div>
//   );
// }

// export default App;






// import React, { useState } from 'react';

// function App() {
//     const [topic, setTopic] = useState('');
//     const [week, setWeek] = useState('');
//     const [times, setTimes] = useState('');
//     const [response, setResponse] = useState('');
//     const [jsonEntries, setJsonEntries] = useState([]); // State to store JSON entries
//     const [entryCount, setEntryCount] = useState(0); // State to store number of entries

//     // Function to handle sending topic and duration to the backend
//     const handleSend = async () => {
//         try {
//             const res = await fetch('http://127.0.0.1:8003/generate-content', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({ 
//                     topic,
//                     week: parseInt(week),
//                     times: parseInt(times)
//                 }),
//             });
//             const data = await res.json();
//             if (data.message) {
//                 setResponse("complete");
//                 fetchJsonEntries(topic); // Fetch JSON entries after successful generation
//             } else {
//                 setResponse("Failed to generate content");
//             }
//         } catch (error) {
//             console.error('Error:', error);
//             setResponse('Failed to generate content');
//         }
//     };

//     // Function to fetch entries from the generated JSON file
//     const fetchJsonEntries = async (topic) => {
//         try {
//             const res = await fetch(`http://127.0.0.1:8003/get-json-entries?topic=${encodeURIComponent(topic)}`);
//             const data = await res.json();
//             setJsonEntries(data.entries); // Update state with JSON entries
//             setEntryCount(data.length); // Store the number of entries
//         } catch (error) {
//             console.error('Error fetching JSON entries:', error);
//         }
//     };

//     return (
//         <div style={{ padding: '20px' }}>
//             <h1>Enter Topic and Duration</h1>
//             <input
//                 type="text"
//                 value={topic}
//                 onChange={(e) => setTopic(e.target.value)}
//                 placeholder="Enter topic"
//             />
//             <input
//                 type="number"
//                 value={week}
//                 onChange={(e) => setWeek(e.target.value)}
//                 placeholder="number of weeks"
//             />
//             <input
//                 type="number"
//                 value={times}
//                 onChange={(e) => setTimes(e.target.value)}
//                 placeholder="times per week"
//             />
//             <button onClick={handleSend}>Send</button>
//             <p>Response from Backend: {response}</p>

//             {/* Render buttons based on JSON entries */}
//             <div style={{ marginTop: '20px' }}>
//                 <h2>Generated Sections</h2>
//                 {jsonEntries.map((entry, index) => (
//                     <button key={index} style={{ display: 'block', margin: '10px 0' }}>
//                         {`Week ${Math.floor(index / times) + 1} Session ${(index % times) + 1}`}
//                     </button>
//                 ))}
//                 <p>Total Sections: {entryCount}</p>
//             </div>
//         </div>
//     );
// }

// export default App;
