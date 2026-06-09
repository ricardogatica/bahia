#!/bin/sh
# Bahia - uninstaller
#
#   sh -c "$(curl -fsSL https://raw.githubusercontent.com/ricardogatica/bahia/main/uninstall.sh)"
#
# Removes the install dir (~/.bahia) and the 'bahia' launcher from PATH.

set -e

BAHIA_DIR="${BAHIA_DIR:-$HOME/.bahia}"

echo ""
echo "🗑  Desinstalando Bahia..."

# Remove launcher from common bin dirs.
for d in "$BIN_DIR" /usr/local/bin "$HOME/.local/bin"; do
    [ -z "$d" ] && continue
    if [ -f "$d/bahia" ]; then
        rm -f "$d/bahia" && echo "  ✓ Eliminado $d/bahia"
    fi
done

# Remove install dir.
if [ -d "$BAHIA_DIR" ]; then
    rm -rf "$BAHIA_DIR" && echo "  ✓ Eliminado $BAHIA_DIR"
fi

echo ""
echo "Listo. Puedes borrar la línea 'Added by Bahia installer' de tu ~/.zshrc si quieres."
echo ""
