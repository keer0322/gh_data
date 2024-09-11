const axios = require('axios');

const vaultAddress = process.argv[2];
const vaultToken = process.argv[3];
const vaultSecretPath = process.argv[4];
const circleciToken = process.argv[5];
const circleciOrgSlug = process.argv[6];
const circleciContextId = process.argv[7];

// Fetch secrets from a Vault path
async function fetchVaultSecrets() {
  const vaultUrl = `${vaultAddress}/v1/${vaultSecretPath}`;
  const headers = { 'X-Vault-Token': vaultToken };

  try {
    const response = await axios.get(vaultUrl, { headers });
    return response.data.data; // Assuming the secrets are in the 'data' object
  } catch (error) {
    console.error(`Failed to fetch secrets from Vault: ${error.message}`);
    process.exit(1);
  }
}

// Add or update secret in CircleCI Context
async function updateCircleCIContext(secretKey, secretValue) {
  const circleciUrl = `https://circleci.com/api/v2/context/${circleciContextId}/environment-variable`;
  const headers = {
    'Circle-Token': circleciToken,
    'Content-Type': 'application/json',
  };

  try {
    await axios.post(
      circleciUrl,
      { name: secretKey, value: secretValue },
      { headers }
    );
    console.log(`Updated secret '${secretKey}' in CircleCI context`);
  } catch (error) {
    console.error(`Failed to update CircleCI context: ${error.message}`);
    process.exit(1);
  }
}

// Main function to sync Vault secrets to CircleCI
async function syncVaultToCircleCI() {
  const secrets = await fetchVaultSecrets();

  // Loop through each secret from Vault and update CircleCI context
  for (const [key, value] of Object.entries(secrets)) {
    await updateCircleCIContext(key, value);
  }
  console.log('Successfully synced all secrets from Vault to CircleCI Context');
}

syncVaultToCircleCI();
