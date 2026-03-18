#!/usr/bin/env bash
# ══════════════════════════════════════════════════
#  Suggit — One-command installer
#  Usage: curl -sSL https://raw.githubusercontent.com/charitraa/suggit/main/install.sh | bash
# ══════════════════════════════════════════════════
set -e

REPO="https://github.com/charitraa/suggit"
RAW="https://raw.githubusercontent.com/charitraa/suggit/main"
INSTALL_DIR="/usr/local/bin"
FILES="commit.py git_utils.py ai_suggest.py local_suggest.py ui.py"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "  ✦ Suggit Installer"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Check OS ──────────────────────────────────────
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo -e "${RED}❌  Windows detected — please use WSL or follow manual install in README.${NC}"
    exit 1
fi

# ── Check dependencies ────────────────────────────
echo "Checking dependencies..."

if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌  Python 3 not found. Install it: sudo apt install python3${NC}"
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo -e "${RED}❌  Git not found. Install it: sudo apt install git${NC}"
    exit 1
fi

if ! command -v pip3 &>/dev/null && ! command -v pip &>/dev/null; then
    echo "  ⚙️   pip not found — installing..."
    sudo apt install -y python3-pip 2>/dev/null || true
fi

echo -e "  ${GREEN}✓  Python $(python3 --version | cut -d' ' -f2)${NC}"
echo -e "  ${GREEN}✓  Git $(git --version | cut -d' ' -f3)${NC}"

# ── Install prompt_toolkit ────────────────────────
echo ""
echo "Installing Python dependencies..."
pip install prompt_toolkit --break-system-packages -q 2>/dev/null || \
pip install prompt_toolkit -q 2>/dev/null || true
echo -e "  ${GREEN}✓  prompt_toolkit installed${NC}"

# Install Gemini SDK (optional — needed for AI suggestions)
pip install google-generativeai --break-system-packages -q 2>/dev/null || \
pip install google-generativeai -q 2>/dev/null || true
echo -e "  ${GREEN}✓  google-generativeai installed${NC}"

# ── Download files ────────────────────────────────
echo ""
echo "Downloading Suggit files..."

TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

for file in $FILES; do
    if command -v curl &>/dev/null; then
        curl -sSL "$RAW/$file" -o "$file"
    else
        wget -q "$RAW/$file" -O "$file"
    fi
    echo -e "  ${GREEN}✓  $file${NC}"
done

# Fix line endings
for file in $FILES; do
    sed -i 's/\r//' "$file" 2>/dev/null || true
done

# ── Install to system PATH ────────────────────────
echo ""
echo "  ⚙️   Installing to $INSTALL_DIR..."

sudo cp "$TMP_DIR"/commit.py   "$INSTALL_DIR/commit"
sudo cp "$TMP_DIR"/git_utils.py    "$INSTALL_DIR/"
sudo cp "$TMP_DIR"/ai_suggest.py   "$INSTALL_DIR/"
sudo cp "$TMP_DIR"/local_suggest.py "$INSTALL_DIR/"
sudo cp "$TMP_DIR"/ui.py           "$INSTALL_DIR/"

sudo chmod +x "$INSTALL_DIR/commit"

# Cleanup
rm -rf "$TMP_DIR"

# ── Setup API key ─────────────────────────────────
echo ""
SHELL_RC=""
if [[ -f "$HOME/.zshrc" ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ -f "$HOME/.bashrc" ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [[ -n "$GEMINI_API_KEY" ]]; then
    echo -e "  ${GREEN}✓  GEMINI_API_KEY already set${NC}"
else
    echo -e "  ${YELLOW} GEMINI_API_KEY not set${NC}"
    echo "      Get free key: https://aistudio.google.com/apikey"
    if [[ -n "$SHELL_RC" ]]; then
        echo "      Then run:"
        echo "        echo 'export GEMINI_API_KEY=\"AIza...\"' >> $SHELL_RC"
        echo "        source $SHELL_RC"
    fi
fi

# ── Recommended aliases ───────────────────────────
if [[ -n "$SHELL_RC" ]]; then
    if ! grep -q "alias ca=" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Suggit aliases" >> "$SHELL_RC"
        echo 'alias ca="commit --add"' >> "$SHELL_RC"
        echo 'alias cap="commit --push"' >> "$SHELL_RC"
        echo -e "  ${GREEN}✓  Aliases added to $SHELL_RC (ca, cap)${NC}"
    fi
fi

# ── Done ──────────────────────────────────────────
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN} Suggit installed successfully!${NC}"
echo ""
echo "  Usage:"
echo "    commit              # suggest + commit"
echo "    commit --add        # git add . + suggest + commit"
echo "    commit --push       # git add . + suggest + commit + push"
echo "    ca                  # alias for commit --add"
echo "    cap                 # alias for commit --push"
echo ""
echo "  Reload your shell:"
if [[ -n "$SHELL_RC" ]]; then
    echo "    source $SHELL_RC"
fi
echo ""
echo "  GitHub: $REPO"
echo ""
