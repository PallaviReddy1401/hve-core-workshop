#!/bin/bash
set -e

echo "=== HVE-Core Workshop: Post-Create Setup ==="

# Upgrade pip
python -m pip install --upgrade pip

# Upgrade Azure CLI to fix module-loading errors (monitor, rdbms)
pip install --upgrade azure-cli 2>/dev/null || true

# Verify tool versions
echo ""
echo "--- Environment Verification ---"
echo "Python:    $(python --version)"
echo "pip:       $(pip --version | awk '{print $2}')"
echo "Azure CLI: $(az version --query \"\\\"azure-cli\\\"\" -o tsv 2>/dev/null || az version -o yaml | head -1)"
echo "azd:       $(azd version)"
echo "GitHub CLI: $(gh --version | head -1)"
echo "Docker:    $(docker --version)"
echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps — authenticate and create Azure resources:"
echo "  1. az login"
echo "  2. azd auth login"
echo "  3. gh auth login"
echo "  4. Run: bash .devcontainer/azure-setup.sh"
