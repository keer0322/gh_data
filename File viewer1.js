import React from 'react';

function FileList({ files, onSelect }) {
  return (
    <div style={{ width: '30%', borderRight: '1px solid #ccc', padding: '1rem' }}>
      <h2>Files</h2>
      <ul>
        {files.map(file => (
          <li key={file.url}>
            <button onClick={() => onSelect(file)}>{file.name}</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default FileList;
