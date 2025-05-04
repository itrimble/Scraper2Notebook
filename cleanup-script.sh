#!/bin/bash
# Script to remove temporary fix scripts before pushing to GitHub

# List of files to remove
FILES_TO_REMOVE=(
  "fix-script-corrected-robust.py"
  "fix-script-corrected.py"
  "fix-script-runner-corrected.sh"
  "fix-script-runner.sh"
  "fix-script.py"
  "fix_repository.py"
  "fix_repository_robust.py"
  "git-push-script.sh"
  "push_to_github.sh"
  "chroma_db.zip"
)

echo "Cleaning up temporary files..."

# Check and remove each file
for file in "${FILES_TO_REMOVE[@]}"; do
  if [ -f "$file" ]; then
    echo "Removing $file"
    rm "$file"
  else
    echo "$file not found, skipping"
  fi
done

# Also make sure any .gitignore entries are correct for ChromaDB
if [ -f ".gitignore" ]; then
  if ! grep -q "chroma_db" .gitignore; then
    echo "Adding ChromaDB directories to .gitignore"
    echo -e "\n# ChromaDB\nchroma_db/\nchroma_db_*/\nchroma_db.zip" >> .gitignore
  fi
else
  echo "Creating .gitignore with ChromaDB entries"
  echo -e "# ChromaDB\nchroma_db/\nchroma_db_*/\nchroma_db.zip" > .gitignore
fi

echo "Cleanup complete! You can now commit and push your changes."
