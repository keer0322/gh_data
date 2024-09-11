const axios = require('axios');
const fs = require('fs');

const GITHUB_API_URL = 'https://api.github.com';
const orgName = process.argv[2];
const githubToken = process.argv[3];

async function fetchOrgRepos() {
    try {
        const headers = githubToken
            ? { Authorization: `Bearer ${githubToken}` }
            : {};

        const response = await axios.get(`${GITHUB_API_URL}/orgs/${orgName}/repos`, {
            headers,
            params: {
                per_page: 100,
            },
        });

        const repoNames = response.data.map((repo) => repo.name);

        // Write output to a file
        fs.writeFileSync('repo-output.txt', JSON.stringify(repoNames));
        console.log('Repositories fetched successfully:', repoNames);
    } catch (error) {
        console.error('Error fetching repositories:', error);
        process.exit(1);
    }
}

fetchOrgRepos();
