#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Prevent running with sudo/root
if [ "$EUID" -eq 0 ]; then
    echo "Error: This script must NOT be run as root." >&2
    exit 1
fi

# CONFIGURATION: Replace with your actual dotfiles repository URL
REPO_URL="https://github.com/diegoperezalvarez/dotfiles.git"
DOTFILES_DIR="$HOME/.dotfiles"

echo "=== Bootstrapping Dotfiles ==="

# 1. Clone as a bare repository if it doesn't already exist
if [ -d "$DOTFILES_DIR" ]; then
    echo "Notice: $DOTFILES_DIR already exists. Skipping clone."
else
    echo "Cloning dotfiles bare repository from $REPO_URL..."
    git clone --bare "$REPO_URL" "$DOTFILES_DIR"
fi

# 2. Hide untracked files in the home directory
echo "Configuring untracked files visibility..."
git --git-dir="$DOTFILES_DIR" --work-tree="$HOME" config --local status.showUntrackedFiles no

# 3. Force checkout files into the home directory (overwriting any default files)
echo "Checking out dotfiles into $HOME..."
git --git-dir="$DOTFILES_DIR" --work-tree="$HOME" checkout -f

# 4. Make all .sh and .py scripts in ~/.bash_scripts executable
if [ -d "$HOME/.bash_scripts" ]; then
    echo "Making .sh and .py scripts executable..."
    find "$HOME/.bash_scripts" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} +
fi

echo "=== Setup Complete! ==="
