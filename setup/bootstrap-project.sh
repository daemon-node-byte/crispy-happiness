#!/usr/bin/env bash

set -euo pipefail

echo "🚀 Bootstrapping GitHub Project for Tarot & Astrology Web App..."

# -----------------------------
# Config
# -----------------------------
PROJECT_TITLE="Tarot & Astrology Web App — MVP"
OWNER="@me"

LABELS=(
  "epic:5319e7"
  "backend:0e8a16"
  "frontend:1d76db"
  "infra:fbca04"
  "blocked:d73a4a"
  "needs-design:cfd3d7"
  "needs-decision:fef2c0"
  "v2-planned:a2eeef"
)

MILESTONES=(
  "EPIC 0 — Foundation & Guardrails"
  "EPIC 1 — Authentication & Core Platform"
  "EPIC 2 — Tarot Card Data & Gallery"
  "EPIC 3 — Tarot Readings & Card of the Day"
  "EPIC 4 — Tarot Journal"
  "EPIC 5 — Tarot Spreads & Spread Editor"
  "EPIC 6 — Astrology Profiles & Natal Charts"
  "EPIC 7 — Synastry, Transits & Dice"
  "EPIC 8 — Astrology Info Center & SEO"
  "EPIC 9 — Data Portability & Privacy"
  "EPIC 10 — Testing, Accessibility & Polish"
  "EPIC 11 — MVP Release Readiness"
)

EPICS=(
  "EPIC 0 — Project Foundation & Guardrails|Foundational setup, guardrails, linting, config, and MVP scope lock."
  "EPIC 1 — Authentication & Core Platform|Supabase auth, user profiles, dashboard shell, telemetry."
  "EPIC 2 — Tarot Card Data & Gallery|Tarot card data, YAML loaders, gallery UI."
  "EPIC 3 — Tarot Readings & Card of the Day|Reading flow, animations, persistence, daily card logic."
  "EPIC 4 — Tarot Journal|Private journal entries, editing, filtering, export."
  "EPIC 5 — Tarot Spreads & Spread Editor|Default spreads, Konva editor, public/private spreads."
  "EPIC 6 — Astrology Profiles & Natal Charts|Birth data, pyswisseph calculations, SVG chart rendering."
  "EPIC 7 — Synastry, Transits & Dice|Synastry charts, basic transits, astrological dice."
  "EPIC 8 — Astrology Info Center & SEO|Reference content, YAML-backed pages, SEO."
  "EPIC 9 — Data Portability & Privacy|Exports, account deletion, privacy guarantees."
  "EPIC 10 — Testing, Accessibility & Polish|90%+ coverage, a11y audit, performance pass."
  "EPIC 11 — MVP Release Readiness|Final QA, scope freeze, MVP release checklist."
)

# -----------------------------
# Create Project
# -----------------------------

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

# -----------------------------
# Create Labels
# -----------------------------
echo "🏷️ Creating labels..."
for LABEL in "${LABELS[@]}"; do
  NAME="${LABEL%%:*}"
  COLOR="${LABEL##*:}"
  gh label create "$NAME" --color "$COLOR" || true
done

# -----------------------------
# Create Milestones
# -----------------------------
echo "🎯 Creating milestones..."
for MILESTONE in "${MILESTONES[@]}"; do
  gh milestone create "$MILESTONE" || true
done

# -----------------------------
# Create EPIC Issues
# -----------------------------
echo "🧱 Creating EPIC issues..."
for EPIC in "${EPICS[@]}"; do
  TITLE="${EPIC%%|*}"
  BODY="${EPIC##*|}"

  gh issue create \
    --title "$TITLE" \
    --label epic \
    --milestone "$TITLE" \
    --body "$BODY"
done

# -----------------------------
# Add EPIC Issues to Project
# -----------------------------
echo "📌 Adding EPIC issues to project..."
gh issue list --label epic --limit 50 --json number \
  | jq -r '.[].number' \
  | xargs -I{} gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --issue {}

echo "🎉 Bootstrap complete!"
echo "👉 Next step: Open the project in GitHub UI and add Status field columns."

# ----------------------------- 
# Create Phase field
# -----------------------------
echo "🧭 Creating Phase field..."

PHASE_FIELD_ID=$(gh api graphql -f query='
  mutation ($project: ID!) {
    createProjectV2Field(
      input: {
        projectId: $project
        dataType: SINGLE_SELECT
        name: "Phase"
        singleSelectOptions: [
          { name: "Foundation" }
          { name: "Tarot" }
          { name: "Astrology" }
          { name: "Polish" }
          { name: "Release" }
        ]
      }
    ) {
      projectV2Field { id }
    }
  }
' -f project="$PROJECT_ID" --jq '.data.createProjectV2Field.projectV2Field.id')

echo "✅ Phase field created"

# -----------------------------
# EPIC -> Phase mapping
# -----------------------------
declare -A EPIC_PHASE_MAP=(
  ["EPIC 0"]="Foundation"
  ["EPIC 1"]="Foundation"
  ["EPIC 2"]="Tarot"
  ["EPIC 3"]="Tarot"
  ["EPIC 4"]="Tarot"
  ["EPIC 5"]="Tarot"
  ["EPIC 6"]="Astrology"
  ["EPIC 7"]="Astrology"
  ["EPIC 8"]="Astrology"
  ["EPIC 9"]="Polish"
  ["EPIC 10"]="Polish"
  ["EPIC 11"]="Release"
)

# -----------------------------
# Assign Phase automatically based on EPIC
# -----------------------------
echo "🔗 Assigning EPICs to Phase..."

gh issue list --label epic --limit 100 --json number,title,node_id \
| jq -c '.[]' \
| while read ISSUE; do
  TITLE=$(echo "$ISSUE" | jq -r '.title')
  NODE_ID=$(echo "$ISSUE" | jq -r '.node_id')

  for KEY in "${!EPIC_PHASE_MAP[@]}"; do
    if [[ "$TITLE" == "$KEY"* ]]; then
      PHASE="${EPIC_PHASE_MAP[$KEY]}"

      OPTION_ID=$(gh api graphql -f query='
        query ($project: ID!, $field: ID!) {
          node(id: $project) {
            ... on ProjectV2 {
              field(id: $field) {
                ... on ProjectV2SingleSelectField {
                  options { id name }
                }
              }
            }
          }
        }
      ' -f project="$PROJECT_ID" -f field="$PHASE_FIELD_ID" \
      --jq ".data.node.field.options[] | select(.name==\"$PHASE\") | .id")

      gh api graphql -f query='
        mutation ($project: ID!, $content: ID!, $field: ID!, $option: String!) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $project
              contentId: $content
              fieldId: $field
              value: { singleSelectOptionId: $option }
            }
          ) { clientMutationId }
        }
      ' -f project="$PROJECT_ID" -f content="$NODE_ID" -f field="$PHASE_FIELD_ID" -f option="$OPTION_ID"

      echo "✔ $TITLE → $PHASE"
    fi
  done
done