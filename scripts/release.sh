#!/usr/bin/env bash

set -e

# shellcheck source=/dev/null
source "$(dirname "$0")/utils.sh"

# Ensure required commands are installed
command_exists jq uvx

cd "$(dirname "$0")/.."

# Ensure the working directory is clean
if [[ -n "$(git status --porcelain)" ]]; then
    log_error "Error: Uncommitted changes detected. Please commit or stash them before running this script."
    exit 1
fi

# Ensure a single argument for version number is provided
if [ "$#" -ne 1 ]; then
    log_error "Usage: $0 <new_version>"
    exit 1
fi

NEW_VERSION=$1
TAG="v$NEW_VERSION"

# Validate version format (SemVer)
if [[ ! "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    log_error "Error: Version must be in the format X.Y.Z (e.g., 1.2.3)"
    exit 1
fi

PROJECT=$(jq -r .name custom_components/ori/manifest.json)
CURRENT_VERSION=$(jq -r .version custom_components/ori/manifest.json)

log_yellow "Updating $PROJECT version from $CURRENT_VERSION to $NEW_VERSION"

# Update Python project version
uvx --from=toml-cli toml set --toml-path=pyproject.toml project.version "$NEW_VERSION"

# Use jq to update manifest.json
jq --arg new_version "$NEW_VERSION" '.version = $new_version' \
    custom_components/ori/manifest.json > manifest.tmp \
    && mv manifest.tmp custom_components/ori/manifest.json
npm run prettier -- --log-level silent --write custom_components/ori/manifest.json

# Update other files safely with sed
sed -i "s/\"$CURRENT_VERSION\"/\"$NEW_VERSION\"/g" \
    .github/ISSUE_TEMPLATE/bug.yaml \
    custom_components/ori/const.py

# Confirm before committing
while true; do
    read -r -p "Are the updated project files correct? (yes/no): " CONFIRMATION
    case "$CONFIRMATION" in
        yes) break ;;
        no)  log_error "Aborted. Reverting changes..."; git restore .; exit 0 ;;
        *)   log_error "Invalid input. Please type 'yes' or 'no'." ;;
    esac
done

# Commit and push changes
log_yellow "Committing changes..."
git add .
git commit -m "Release version \`$NEW_VERSION\`"
git tag "$TAG"

log_yellow "Pushing changes..."
git push origin
git push origin --tags

log_yellow "Release commit and tag $NEW_VERSION created and pushed successfully"
