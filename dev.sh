#!/bin/bash

# Print colored text for better terminal output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Fintech Ledger API Development Environment...${NC}"

# 1. Check if the .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found! Please create one before starting."
    exit 1
fi

# 2. Spin up the PostgreSQL Database in the background
echo -e "${GREEN}Starting PostgreSQL container...${NC}"
sudo docker compose up -d

# Optional: Add a brief 2-second sleep to ensure Postgres is fully awake before FastAPI hits it
sleep 2

# 3. Launch the FastAPI server
echo -e "${GREEN}Launching Uvicorn server...${NC}"
uv run uvicorn app.main:app --reload