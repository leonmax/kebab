#!/bin/bash

# Assume poetry, git and gh (github cli) are installed
# This script will create a new release on github

VERSION_OR_RULE=$1
if [ $# -eq 0 ]; then
    echo "./release.sh <version|rule>"
    echo "  The new version should ideally be a valid semver string or a valid bump rule:
  patch, minor, major, prepatch, preminor, premajor, prerelease."
    exit 1;
fi

# Update poetry
poetry update
poetry version $VERSION_OR_RULE
export VERSION=`poetry version -s`

# Commit and push
git add pyproject.toml poetry.lock
git commit -m "release $VERSION"
git push

# Create release
if [ $VERSION_OR_RULE == "pre*" ] ; then
    gh release create --generate-notes --latest --prerelease "$VERSION"
else
    gh release create --generate-notes --latest "$VERSION"
fi

