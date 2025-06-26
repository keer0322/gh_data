import React from 'react';

function FileViewer({ file }) {
  if (!file) return <div style={{ padding: '1rem' }}>Select a file to view</div>;

  const isHtml = file.name.endsWith('.html');

  return (
    <div style={{ flexGrow: 1, padding: '1rem' }}>
      <h2>Viewing: {file.name}</h2>
      {isHtml ? (
        <iframe
          src={file.url}
          title={file.name}
          style={{ width: '100%', height: '90%' }}
          sandbox="allow-same-origin allow-scripts"
        />
      ) : (
        <p>Preview not available. <a href={file.url} target="_blank" rel="noopener noreferrer">Download</a></p>
      )}
    </div>
  );
}

export default FileViewer;
