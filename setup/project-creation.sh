#!/usr/bin/env bash
set -euo pipefail

PROJECT_TITLE="Tarot & Astrology Web App — MVP"

echo "🔎 Resolving viewer ID..."
VIEWER_ID=$(gh api graphql -f query='
  query { viewer { id login } }
' --jq '.data.viewer.id')

echo "📦 Creating Project V2..."
PROJECT_ID=$(gh api graphql -f query='
  mutation ($owner: ID!, $title: String!) {
    createProjectV2(input: { ownerId: $owner, title: $title }) {
      projectV2 { id number }
    }
  }
' -f owner="$VIEWER_ID" -f title="$PROJECT_TITLE" --jq '.data.createProjectV2.projectV2.id')

echo "✅ Project created with ID: $PROJECT_ID"
