import React, { useEffect, useState } from 'react';
import FileList from './FileList';
import FileViewer from './FileViewer';

function App() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetch('/api/files') // Replace with your actual endpoint
      .then(res => res.json())
      .then(setFiles)
      .catch(console.error);
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <FileList files={files} onSelect={setSelectedFile} />
      <FileViewer file={selectedFile} />
    </div>
  );
}

export default App;
