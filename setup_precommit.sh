#!/bin/bash

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null
then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install the pre-commit hook
echo "Installing pre-commit hooks..."
pre-commit install

# Run all hooks on all files initially
echo "Running pre-commit on all files..."
pre-commit run --all-files

echo "✅ Pre-commit setup complete."
