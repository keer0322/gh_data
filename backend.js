const express = require('express');
const { Storage } = require('@google-cloud/storage');
const cors = require('cors');

const app = express();
app.use(cors());

const storage = new Storage({
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS || '/app/keyfile.json',
});

const bucketName = process.env.BUCKET_NAME;

app.get('/api/files', async (req, res) => {
  try {
    const [files] = await storage.bucket(bucketName).getFiles();

    const signedFiles = await Promise.all(
      files.map(async (file) => {
        const [url] = await file.getSignedUrl({
          version: 'v4',
          action: 'read',
          expires: Date.now() + 5 * 60 * 1000, // 5 min
        });
        return { name: file.name, url };
      })
    );

    res.json(signedFiles);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message });
  }
});

app.listen(3001, () => console.log('GCS backend running on port 3001'));
