useEffect(() => {
  fetch('http://localhost:3001/api/files')
    .then(res => res.json())
    .then(setFiles)
    .catch(console.error);
}, []);
