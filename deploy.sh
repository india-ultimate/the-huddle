#!/bin/bash
set -e

PUBLIC_DIR="public"
GIT_URL=$(git remote get-url origin)

# Build the site
pushd $(dirname $0)
rm -rf "${PUBLIC_DIR}"
hugo

# Push to GitHub
pushd "${PUBLIC_DIR}"
git init
git add .
git commit -m "Deploy to GitHub Pages" \
    --author "Puneeth Chaganti <punchagan@muse-amuse.in>"
git push --force --quiet "${GIT_URL}" master:gh-pages
popd

popd
