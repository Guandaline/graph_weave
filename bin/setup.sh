#!/bin/bash

echo "🚀 Starting Graph Weave environment setup..."

# Ensure the script is being run from the project root
SCRIPT_PATH_ABS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH_ABS")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT" || { echo "❌ Failed to change to project root."; exit 1; }
echo "📂 Working directory: $(pwd)"


# 1️⃣ Create virtual environment in the project directory (using Poetry)
echo ""
echo "🐍 Setting up Python virtual environment with Poetry..."
poetry config virtualenvs.in-project true --local

PYTHON_CMD="python3" # Default to python3
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif ! command -v python3 &> /dev/null; then
    echo "   ❌ Python 3 not found. Please install Python 3.8+."
    exit 1
fi
echo "   Using Python command: $($PYTHON_CMD --version)"


if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo "   ❌ Failed to create virtual environment."
        exit 1
    fi
fi

# 2️⃣ Activate the virtual environment
echo "   Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "   ❌ Failed to activate virtual environment."
    exit 1
fi
echo "   ✅ Virtual environment activated."

# 3️⃣ Install/Update Poetry and dependencies
echo ""
echo "📦 Installing/Updating pip, poetry, and project dependencies..."
pip install -U pip poetry
poetry install --no-interaction --sync # --sync removes unnecessary packages
if [ $? -ne 0 ]; then
    echo "   ❌ Failed to install dependencies with Poetry."
    exit 1
fi
echo "   ✅ Dependencies installed."

# 4️⃣ Create .env if it doesn't exist
echo ""
echo "⚙️  Setting up .env file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "   Creating .env file from .env.example..."
        cp .env.example .env
        echo "   ✅ .env file created."
    else
        echo "   ⚠️  WARNING: .env.example not found. Create a .env file manually if needed."
    fi
else
    echo "   ℹ️ .env file already exists."
fi

# 5️⃣ Generate mongo-keyfile for MongoDB Replica Set
echo ""
echo "🔑 Generating mongo-keyfile for MongoDB Replica Set..."
MONGO_KEYFILE_SCRIPT="./devtools/mongo/generate-mongo-keyfile.sh" # Path relative to root
if [ -f "$MONGO_KEYFILE_SCRIPT" ]; then
    bash "$MONGO_KEYFILE_SCRIPT" # Run the dedicated script
else
    echo "   ⚠️  WARNING: Script ${MONGO_KEYFILE_SCRIPT} not found. Create the mongo-keyfile manually."
fi

# 6️⃣ Set release tokens (GitHub or GitLab)
echo ""
echo "🔐 Setting up release tokens..."
# (Your existing logic for GH_TOKEN / CI_JOB_TOKEN)
if grep -q "GH_TOKEN=" .env; then
    export GH_TOKEN=$(grep GH_TOKEN .env | cut -d '=' -f2)
    echo "   GH_TOKEN loaded from .env"
elif [ -n "$CI_JOB_TOKEN" ]; then
    export GH_TOKEN="$CI_JOB_TOKEN"
    echo "   CI_JOB_TOKEN detected (GitLab CI), exported as GH_TOKEN for compatibility"
else
    echo "   ⚠️  WARNING: No release token (GH_TOKEN or CI_JOB_TOKEN) found. Automated releases may fail."
fi
echo "   GH_TOKEN=${GH_TOKEN:0:4}********"


# 8️⃣ Pre-commit hook
echo ""
echo "🎣 Installing pre-commit hooks..."
poetry run pre-commit install
poetry run pre-commit autoupdate
# poetry run pre-commit run --all-files # Commented to speed up initial setup


echo ""
echo "🎉 Environment setup completed successfully!"
echo "➡️  To start the Docker infrastructure, use: docker compose -f infra/docker-compose.all.yml up -d"
echo "➡️  Remember to run 'source .venv/bin/activate' if you are not already in the virtual environment."