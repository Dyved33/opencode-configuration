#!/usr/bin/env bash
# Checks that this machine can run one of the OpenCode configurations of this repository.
#
#   ./doctor.sh notes /path/to/vault        university notes vault
#   ./doctor.sh web   /path/to/project      web project
#
# It prints what is missing and the command that fixes it. It never changes
# anything. Exit code 0 = the configuration can run, 1 = something essential is
# missing, 2 = wrong arguments.
#
# The same check runs at the end of ./install.sh.

if [ -z "${BASH_VERSION:-}" ]; then
  exec bash "$0" "$@"
fi

set -uo pipefail

PAYLOAD="${1:-notes}"
TARGET="${2:-}"

case "$PAYLOAD" in
  notes|web) ;;
  *)
    echo "ERROR: the first argument must be 'notes' or 'web', got '$PAYLOAD'"
    echo "usage: ./doctor.sh [notes|web] [target-folder]"
    exit 2
    ;;
esac

CRITICAL=0
WARNINGS=0
CONFIG=""

section() { printf '\n%s\n' "$1"; }
ok()      { printf '  [ ok ] %s\n' "$1"; }
warn()    { printf '  [WARN] %s\n' "$1"; WARNINGS=$((WARNINGS + 1)); }
fail()    { printf '  [FAIL] %s\n' "$1"; CRITICAL=$((CRITICAL + 1)); }
hint()    { printf '         fix: %s\n' "$1"; }

# version_ge 2.1.0 2.0.0 -> true when the first version is greater or equal
version_ge() {
  [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# a module is importable
has_python_module() {
  python3 -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('$1') else 1)" >/dev/null 2>&1
}

# a TCP port answers
port_open() {
  timeout 2 bash -c "exec 3<>/dev/tcp/$1/$2" >/dev/null 2>&1
}

# the file exists and is valid JSON
valid_json() {
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$1" >/dev/null 2>&1
}

# the plugins declared in the configuration, one per line
declared_plugins() {
  [ -n "$CONFIG" ] && [ -f "$CONFIG" ] || return 0
  python3 - "$CONFIG" <<'PY' 2>/dev/null
import json, sys
try:
    cfg = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
for p in cfg.get("plugins", []) or []:
    if isinstance(p, str):
        print(p)
PY
}

# ---------------------------------------------------------------- OpenCode ---

section "OpenCode"

if ! command -v opencode >/dev/null 2>&1; then
  fail "opencode is not installed"
  hint "npm install -g @opencode/cli@latest"
  echo "         (the package 'opencode-ai' is version 1: this configuration needs version 2)"
else
  OPENCODE_VERSION="$(opencode --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)"
  if [ -z "$OPENCODE_VERSION" ]; then
    warn "opencode is installed but its version could not be read"
  elif version_ge "$OPENCODE_VERSION" "2.0.0"; then
    ok "opencode $OPENCODE_VERSION"
  else
    fail "opencode $OPENCODE_VERSION is version 1: this configuration needs version 2"
    hint "npm install -g @opencode/cli@latest"
  fi
fi

# --------------------------------------------------------- Node, npm, python --

section "Node and npm (the plugins are npm packages)"

if command -v node >/dev/null 2>&1; then
  NODE_VERSION="$(node --version 2>/dev/null)"
  if version_ge "${NODE_VERSION#v}" "18.0.0"; then
    ok "node $NODE_VERSION"
  else
    warn "node $NODE_VERSION is old, 18 or later is recommended"
  fi
else
  warn "node is not installed: the plugins cannot be installed"
  hint "install Node.js 18 or later"
fi

if command -v npm >/dev/null 2>&1; then
  ok "npm $(npm --version 2>/dev/null)"
else
  warn "npm is not installed: the plugins cannot be installed"
fi

section "Python (the scripts)"

if command -v python3 >/dev/null 2>&1; then
  PY_VERSION="$(python3 -c 'import platform;print(platform.python_version())' 2>/dev/null)"
  if version_ge "$PY_VERSION" "3.9.0"; then
    ok "python $PY_VERSION"
  else
    fail "python $PY_VERSION is too old, 3.9 or later is needed"
  fi
else
  fail "python3 is not installed: the scripts cannot run"
  hint "sudo apt install python3"
fi

# ----------------------------------------------------------- Configuration ---

section "Configuration in the target"

if [ -z "$TARGET" ]; then
  warn "no target folder given: the configuration files are not checked"
elif [ ! -d "$TARGET" ]; then
  fail "the target folder '$TARGET' does not exist"
else
  ok "target $TARGET"
  CONFIG="$TARGET/opencode.json"

  if [ ! -f "$CONFIG" ]; then
    fail "opencode.json is missing in the target"
    hint "./install.sh $PAYLOAD \"$TARGET\""
  elif valid_json "$CONFIG"; then
    ok "opencode.json is valid JSON"
  else
    fail "opencode.json is not valid JSON: OpenCode will not start"
  fi

  for f in .opencode/style.md .opencode/agents .opencode/commands; do
    if [ -e "$TARGET/$f" ]; then
      ok "$f"
    else
      warn "$f is missing in the target"
    fi
  done
fi

# ----------------------------------------------------------------- Plugins ---

section "Plugins"

PLUGIN_LIST=""
if [ -n "$TARGET" ] && [ -d "$TARGET" ]; then
  PLUGIN_LIST="$(cd "$TARGET" && opencode plugin list 2>/dev/null)"
else
  PLUGIN_LIST="$(opencode plugin list 2>/dev/null)"
fi
if [ -z "$PLUGIN_LIST" ]; then
  warn "opencode plugin list returned nothing: the plugins may not be installed"
fi

# the first run installs the plugins declared in the configuration: it needs the
# network and some seconds, so the list is read once more before complaining
MISSING_PLUGINS=""
for plugin in $(declared_plugins); do
  printf '%s' "$PLUGIN_LIST" | grep -qF -- "$plugin" || MISSING_PLUGINS="$MISSING_PLUGINS $plugin"
done
if [ -n "$MISSING_PLUGINS" ]; then
  sleep 5
  if [ -n "$TARGET" ] && [ -d "$TARGET" ]; then
    PLUGIN_LIST="$(cd "$TARGET" && opencode plugin list 2>/dev/null)"
  else
    PLUGIN_LIST="$(opencode plugin list 2>/dev/null)"
  fi
fi

while IFS= read -r plugin; do
  [ -n "$plugin" ] || continue
  if printf '%s' "$PLUGIN_LIST" | grep -qF -- "$plugin"; then
    ok "$plugin"
  else
    warn "$plugin is not installed yet: OpenCode installs it at the first start, it needs the network"
    hint "opencode plugin add $plugin"
  fi
done <<EOF
$(declared_plugins)
EOF

# ------------------------------------------------------------------ Ollama ---

section "Ollama (local model for titles and compaction)"

if ! command -v ollama >/dev/null 2>&1; then
  warn "ollama is not installed: the local model is not available"
  hint "install ollama, then: ollama pull qwen2.5:7b"
elif ! port_open 127.0.0.1 11434; then
  warn "ollama is installed but not running"
  hint "ollama serve"
elif ollama list 2>/dev/null | grep -q "qwen2.5:7b"; then
  ok "ollama is running and qwen2.5:7b is pulled"
else
  warn "the model qwen2.5:7b is not pulled: the titles and the compaction fall back to the remote model"
  hint "ollama pull qwen2.5:7b"
fi

# ------------------------------------------------------- Notes: OCR and MCP ---

if [ "$PAYLOAD" = "notes" ]; then
  section "Slides, PDFs and OCR"

  if command -v tesseract >/dev/null 2>&1; then
    if tesseract --list-langs 2>/dev/null | grep -qx "ita\|it"; then
      ok "tesseract with the italian language"
    else
      warn "tesseract has no italian language pack"
      hint "sudo apt install tesseract-ocr-ita"
    fi
  else
    warn "tesseract is not installed: the photos of the slides are not read"
    hint "sudo apt install tesseract-ocr tesseract-ocr-ita"
  fi

  for tool in pdftotext pdftoppm; do
    if command -v "$tool" >/dev/null 2>&1; then
      ok "$tool"
    else
      warn "$tool is not installed: the PDFs are not read"
      hint "sudo apt install poppler-utils"
    fi
  done

  section "Python packages of the scripts"

  for module in pypdf docling obsidian_mcp_search; do
    if has_python_module "$module"; then
      ok "$module"
    else
      warn "$module is not installed"
      hint "python3 -m pip install --user --break-system-packages pypdf \"obsidian-mcp-search[server]\" docling"
    fi
  done

  section "Semantic search (obsidian-search MCP server)"

  if port_open 127.0.0.1 8848; then
    ok "the server answers on 127.0.0.1:8848"
  else
    warn "the server is not running on 127.0.0.1:8848: the search by meaning does not work"
    hint "systemctl --user status obsidian-mcp-search"
  fi
fi

# ------------------------------------------------------------- Style skills ---

section "Style skills (optional, they make the writing tighter)"

if [ -f "$HOME/.agents/skills/no-ai-slop/SKILL.md" ] || [ -f "$HOME/.config/opencode/skills/no-ai-slop/SKILL.md" ]; then
  ok "no-ai-slop"
else
  warn "no-ai-slop is not installed: the filler text is not checked"
  hint "copy the skill folder from the other machine to ~/.agents/skills/no-ai-slop/"
fi

if [ -f "$HOME/.config/opencode/vendor/i-have-adhd/skills/i-have-adhd/SKILL.md" ]; then
  ok "i-have-adhd"
else
  warn "i-have-adhd is not installed: the layout rules are missing"
  hint "copy ~/.config/opencode/vendor/i-have-adhd/ from the other machine"
fi

# ----------------------------------------------------------------- Summary ---

printf '\n'
if [ "$CRITICAL" -gt 0 ]; then
  printf 'NOT READY: %s essential problem(s), %s warning(s).\n' "$CRITICAL" "$WARNINGS"
  printf 'The configuration is installed but OpenCode will not work well until the [FAIL] lines are fixed.\n'
  exit 1
fi
if [ "$WARNINGS" -gt 0 ]; then
  printf 'READY WITH WARNINGS: %s warning(s). The configuration works, the [WARN] lines are optional.\n' "$WARNINGS"
  exit 0
fi
printf 'READY: everything is in place.\n'
exit 0
