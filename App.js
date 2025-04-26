import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [linkedinUrl, setLinkedinUrl] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setLinkedinUrl(data.linkedin_url);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Upload Resume PDF</h2>
      <input type="file" accept=".pdf" onChange={handleFileChange} />
      <button onClick={handleUpload}>Extract LinkedIn URL</button>
      {linkedinUrl && <p>Extracted LinkedIn URL: {linkedinUrl}</p>}
    </div>
  );
}

export default App;
