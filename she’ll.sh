#!/bin/bash

# GitHub Enterprise Base URL (Modify this)
GITHUB_ENTERPRISE_URL="https://your-github-enterprise.com"

# GitHub Admin Token (Must have 'admin:enterprise' permission)
GITHUB_TOKEN="your_github_admin_token_here"

# Output File
OUTPUT_FILE="user_emails.txt"

# Clear the output file
> "$OUTPUT_FILE"

# Pagination settings
PAGE=1
PER_PAGE=100

echo "🔍 Fetching users from GitHub Enterprise..."

while : ; do
    # API request to get users
    RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "$GITHUB_ENTERPRISE_URL/api/v3/admin/users?per_page=$PER_PAGE&page=$PAGE")

    # Check if response is empty (end of pagination)
    if [[ "$RESPONSE" == "[]" ]]; then
        break
    fi

    # Extract usernames and emails (emails might be null if private)
    echo "$RESPONSE" | jq -r '.[] | "\(.login), \(.email // "No Email Available")"' >> "$OUTPUT_FILE"

    ((PAGE++))
done

echo "✅ User email list saved in $OUTPUT_FILE."
