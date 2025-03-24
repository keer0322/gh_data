#!/bin/bash

# Ensure script stops on errors
set -e

# Check if repository URL is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <repo_url>"
    exit 1
fi

REPO_URL=$1

# Extract the repo owner and name from the URL
REPO_NAME=$(basename -s .git "$REPO_URL")
REPO_OWNER=$(echo "$REPO_URL" | awk -F[/:] '{print $(NF-1)}')

# Fetch the latest tag using GitHub API
LATEST_TAG=$(curl -s "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/tags" | jq -r '.[0].name')

# Check if a tag was found
if [ "$LATEST_TAG" == "null" ] || [ -z "$LATEST_TAG" ]; then
    echo "No tags found in repository."
    exit 1
fi

echo "Latest tag: $LATEST_TAG

VERSION=$LATEST_TAG
CLONE_DIR=$(basename "$REPO_URL" .git)

# Clone the repository recursively (including submodules)
echo "Cloning repository: $REPO_URL..."
git clone --recursive "$REPO_URL"
cd "$CLONE_DIR"

# Checkout the specified version (branch, tag, or commit)
echo "Checking out version: $VERSION..."
git checkout "$VERSION"

# Fetch latest submodules
git submodule update --init --recursive

# Get the commit ID for the current version
COMMIT_ID=$(git rev-parse HEAD)
echo "Current commit ID: $COMMIT_ID"

# Output commit ID
echo "Commit ID: $COMMIT_ID"

# Return to original directory
cd ..
