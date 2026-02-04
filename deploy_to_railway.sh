#!/bin/bash
# ========================================================================
#   ONE-CLICK RAILWAY DEPLOYMENT (Linux/Mac)
# ========================================================================

echo ""
echo "========================================================================"
echo "   RAILWAY AUTO-DEPLOYMENT STARTING..."
echo "========================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}[STEP 1/5] Railway CLI not found. Installing...${NC}"
    
    if command -v npm &> /dev/null; then
        npm install -g @railway/cli
        echo -e "${GREEN}[OK] Railway CLI installed!${NC}"
    else
        echo -e "${RED}[ERROR] npm not found!${NC}"
        echo -e "${YELLOW}Please install Node.js first: https://nodejs.org/${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}[STEP 1/5] Railway CLI found!${NC}"
fi

# Login to Railway
echo -e "\n${CYAN}[STEP 2/5] Logging into Railway...${NC}"
railway whoami &> /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK] Already logged in!${NC}"
else
    echo -e "${YELLOW}Please login to Railway (browser will open)...${NC}"
    railway login
fi

# Link project
echo -e "\n${CYAN}[STEP 3/5] Linking to Railway project...${NC}"
railway status &> /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK] Project already linked!${NC}"
else
    echo -e "${YELLOW}Please select your project...${NC}"
    railway link
fi

# Get Binance API keys
echo -e "\n${CYAN}[STEP 4/5] Binance API Keys...${NC}"
echo -e "${YELLOW}Enter your Binance API Key (or press Enter to skip):${NC}"
echo -e "${CYAN}Testnet keys: https://testnet.binance.vision/${NC}"
read -p "API Key: " BINANCE_API_KEY

if [ ! -z "$BINANCE_API_KEY" ]; then
    echo -e "${YELLOW}Enter your Binance API Secret:${NC}"
    read -sp "API Secret: " BINANCE_API_SECRET
    echo ""
fi

# Set environment variables
echo -e "\n${CYAN}[STEP 5/5] Setting environment variables...${NC}"

# Core variables
railway variables set JWT_SECRET_KEY=S9RCVkYrP0kpKmTaLFZXV9GeUG4oOKbNxM52dZJ5twwD0ZPx
railway variables set ENCRYPTION_KEY=k8LecZ7m5qZ15Ul31fZILAO8GL1fi7GK
railway variables set BINANCE_BASE_URL=https://testnet.binance.vision
railway variables set TELEGRAM_ENABLED=false

# Binance keys if provided
if [ ! -z "$BINANCE_API_KEY" ]; then
    railway variables set BINANCE_API_KEY=$BINANCE_API_KEY
    railway variables set BINANCE_API_SECRET=$BINANCE_API_SECRET
    echo -e "${GREEN}[OK] Binance API keys set!${NC}"
fi

# Deploy
echo -e "\n${CYAN}[STEP 6/6] Triggering deployment...${NC}"
git push origin master

echo ""
echo "========================================================================"
echo -e "${GREEN}   SETUP COMPLETE!${NC}"
echo "========================================================================"
echo ""
echo "Your app is deploying to Railway!"
echo "Check status: railway logs"
echo "Open app: railway open"
echo ""
