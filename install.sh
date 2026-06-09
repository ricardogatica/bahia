#!/bin/sh
# Bahia - macOS port monitor TUI
# Self-contained installer (oh-my-zsh style):
#
#   sh -c "$(curl -fsSL https://raw.githubusercontent.com/ricardogatica/bahia/main/install.sh)"
#   sh -c "$(wget -qO- https://raw.githubusercontent.com/ricardogatica/bahia/main/install.sh)"
#
# After install, just run:  bahia
#
# Environment overrides:
#   BAHIA_DIR   install location           (default: ~/.bahia)
#   BAHIA_REPO  owner/repo on GitHub        (default: ricardogatica/bahia)
#   BAHIA_REF   branch or tag to install    (default: main)
#   BIN_DIR     where the launcher goes     (default: first writable of /usr/local/bin, ~/.local/bin)

set -e

# ----- config -----
BAHIA_DIR="${BAHIA_DIR:-$HOME/.bahia}"
BAHIA_REPO="${BAHIA_REPO:-ricardogatica/bahia}"
BAHIA_REF="${BAHIA_REF:-main}"

# ----- colors (only if stdout is a tty) -----
if [ -t 1 ]; then
    GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'
else
    GREEN=''; RED=''; YELLOW=''; BOLD=''; NC=''
fi

info()  { printf "%b\n" "$1"; }
ok()    { printf "  ${GREEN}✓${NC} %s\n" "$1"; }
warn()  { printf "  ${YELLOW}⚠${NC} %s\n" "$1"; }
fail()  { printf "  ${RED}✗${NC} %s\n" "$1" >&2; exit 1; }

info ""
info "${BOLD}╔═══════════════════════════════════╗${NC}"
info "${BOLD}║   BAHIA · Monitor de Puertos      ║${NC}"
info "${BOLD}╚═══════════════════════════════════╝${NC}"
info ""

# ----- 1. detect python3 -----
info "🔍 Buscando Python 3..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
else
    fail "Python 3 no encontrado. Instala con: brew install python3"
fi
ok "$($PYTHON --version 2>&1)"

# ----- 2. fetch the source into BAHIA_DIR -----
info ""
info "📥 Descargando Bahia en $BAHIA_DIR ..."

if [ -d "$BAHIA_DIR/.git" ]; then
    # Existing git checkout: update it.
    git -C "$BAHIA_DIR" remote set-url origin "https://github.com/$BAHIA_REPO.git" 2>/dev/null || true
    git -C "$BAHIA_DIR" fetch --depth=1 origin "$BAHIA_REF" >/dev/null 2>&1 || fail "No se pudo actualizar el repo"
    git -C "$BAHIA_DIR" reset --hard "origin/$BAHIA_REF" >/dev/null 2>&1 || \
        git -C "$BAHIA_DIR" reset --hard FETCH_HEAD >/dev/null 2>&1
    ok "Actualizado a la última versión"
elif command -v git >/dev/null 2>&1; then
    rm -rf "$BAHIA_DIR"
    git clone -q --depth=1 --branch "$BAHIA_REF" \
        "https://github.com/$BAHIA_REPO.git" "$BAHIA_DIR" 2>/dev/null \
        || git clone -q --depth=1 "https://github.com/$BAHIA_REPO.git" "$BAHIA_DIR" \
        || fail "No se pudo clonar https://github.com/$BAHIA_REPO.git"
    ok "Clonado vía git"
else
    # No git: download a tarball.
    rm -rf "$BAHIA_DIR"
    mkdir -p "$BAHIA_DIR"
    TARBALL="https://codeload.github.com/$BAHIA_REPO/tar.gz/refs/heads/$BAHIA_REF"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$TARBALL" | tar -xz -C "$BAHIA_DIR" --strip-components=1 \
            || fail "No se pudo descargar el tarball"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- "$TARBALL" | tar -xz -C "$BAHIA_DIR" --strip-components=1 \
            || fail "No se pudo descargar el tarball"
    else
        fail "Necesitas git, curl o wget para instalar"
    fi
    ok "Descargado (tarball)"
fi

# ----- 3. isolated virtual environment + deps -----
info ""
info "📦 Instalando dependencias (entorno aislado)..."
VENV="$BAHIA_DIR/.venv"
"$PYTHON" -m venv "$VENV" || fail "No se pudo crear el entorno virtual (¿falta 'python3 -m venv'?)"
VENV_PY="$VENV/bin/python"
"$VENV_PY" -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true
if "$VENV_PY" -m pip install --quiet textual >/dev/null 2>&1; then
    ok "textual instalado"
else
    fail "No se pudieron instalar las dependencias"
fi

# ----- 4. launcher on PATH -----
info ""
info "🔗 Creando el comando 'bahia'..."

# Pick a writable bin dir.
if [ -n "$BIN_DIR" ]; then
    :
elif [ -w "/usr/local/bin" ] 2>/dev/null; then
    BIN_DIR="/usr/local/bin"
else
    BIN_DIR="$HOME/.local/bin"
fi
mkdir -p "$BIN_DIR"

LAUNCHER="$BIN_DIR/bahia"
cat > "$LAUNCHER" <<EOF
#!/bin/sh
# Bahia launcher — runs the app from its isolated venv.
exec "$VENV/bin/python" "$BAHIA_DIR/bahia.py" "\$@"
EOF
chmod +x "$LAUNCHER"
ok "Lanzador: $LAUNCHER"

# ----- 5. ensure BIN_DIR is on PATH -----
case ":$PATH:" in
    *":$BIN_DIR:"*)
        PATH_OK=true ;;
    *)
        PATH_OK=false
        # Persist the PATH update to the user's shell rc.
        SHELL_NAME="$(basename "${SHELL:-}")"
        case "$SHELL_NAME" in
            zsh)  RC="$HOME/.zshrc" ;;
            bash) RC="$HOME/.bashrc" ;;
            *)    RC="$HOME/.profile" ;;
        esac
        LINE="export PATH=\"$BIN_DIR:\$PATH\""
        if [ -f "$RC" ] && grep -qF "$LINE" "$RC" 2>/dev/null; then
            :
        else
            printf '\n# Added by Bahia installer\n%s\n' "$LINE" >> "$RC"
        fi
        ;;
esac

# ----- done -----
info ""
info "${BOLD}╔═══════════════════════════════════╗${NC}"
info "${BOLD}║   ¡Instalación completa! ✓        ║${NC}"
info "${BOLD}╚═══════════════════════════════════╝${NC}"
info ""
if [ "$PATH_OK" = "false" ]; then
    warn "Agregué $BIN_DIR a tu PATH en $RC"
    info "  Abre una terminal nueva, o ejecuta:"
    info "      ${GREEN}export PATH=\"$BIN_DIR:\$PATH\"${NC}"
    info ""
fi
info "Para abrir la app, escribe:"
info "      ${GREEN}${BOLD}bahia${NC}"
info ""
info "Controles:  ↑↓ navegar · k matar · r refrescar · q salir"
info ""
