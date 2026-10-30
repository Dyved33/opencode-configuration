#!/usr/bin/env bash
# Installs one of the OpenCode configurations of this repository into a target folder.
#
#   ./install.sh notes /path/to/vault        university notes vault
#   ./install.sh web   /path/to/project      web project (portals and websites)
#   ./install.sh notes /path/to/vault --force   back up and overwrite existing files
#   ./install.sh notes /path/to/vault --check   check the environment, install nothing
#   ./install.sh notes /path/to/vault --no-check  install, skip the environment check
#
# The whole content of notes/ or web/ is copied into the target: AGENTS.md and
# opencode.json at the top, everything else under .opencode/.
# Files that already exist are never touched unless --force is given, and with
# --force they are first copied into <target>/.opencode-backup-<timestamp>/.
#
# Requirements: bash (not POSIX sh) and OpenCode v2 (npm install -g @opencode/cli@latest).
# At the end the environment is checked with ./doctor.sh: the files are installed
# even if something is missing, and the report says what to fix.
#
# Exit codes: 0 = installed and ready, 1 = the installation failed,
# 2 = installed but the environment is not ready yet.

if [ -z "${BASH_VERSION:-}" ]; then
  exec bash "$0" "$@"
fi

set -euo pipefail

usage() {
  sed -n '3,20p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

PAYLOAD_NAME="${1:-}"
TARGET="${2:-}"
FORCE=0
MODE=install
for arg in "${@:3}"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --check) MODE=check ;;
    --no-check) MODE=install-no-check ;;
    *) echo "ERROR: unknown option $arg"; usage ;;
  esac
done

[ -n "$PAYLOAD_NAME" ] && [ -n "$TARGET" ] || usage
[ "$PAYLOAD_NAME" = "notes" ] || [ "$PAYLOAD_NAME" = "web" ] || {
  echo "ERROR: first argument must be 'notes' or 'web', got '$PAYLOAD_NAME'"
  usage
}

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD="$REPO_DIR/$PAYLOAD_NAME"

[ -d "$PAYLOAD" ] || { echo "ERROR: $PAYLOAD not found"; exit 1; }
[ -f "$PAYLOAD/opencode.json" ] || { echo "ERROR: $PAYLOAD has no opencode.json"; exit 1; }

# the configuration must be valid JSON, or OpenCode will not start at all
if command -v python3 >/dev/null 2>&1; then
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$PAYLOAD/opencode.json" || {
    echo "ERROR: $PAYLOAD/opencode.json is not valid JSON, nothing was installed"
    exit 1
  }
fi

# the target is created if it does not exist, it must not be the payload itself
if [ -e "$TARGET" ] && [ ! -d "$TARGET" ]; then
  echo "ERROR: target '$TARGET' exists and is not a folder"
  exit 1
fi
if [ ! -d "$TARGET" ]; then
  mkdir -p "$TARGET"
  echo "Created the target folder $TARGET"
fi
TARGET="$(cd "$TARGET" && pwd)"
if [ "$TARGET" = "$(cd "$PAYLOAD" && pwd)" ]; then
  echo "ERROR: the target is the payload folder itself, nothing was installed"
  exit 1
fi

if [ "$MODE" = "check" ]; then
  exec "$REPO_DIR/doctor.sh" "$PAYLOAD_NAME" "$TARGET"
fi

COPIED=()
SKIPPED=()
OVERWRITTEN=()
BACKUP_DIR=""

backup_file() {
  local file="$1"
  if [ -z "$BACKUP_DIR" ]; then
    BACKUP_DIR="$TARGET/.opencode-backup-$(date +%Y%m%d-%H%M%S)"
  fi
  local rel="${file#"$TARGET"/}"
  mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
  cp -p "$file" "$BACKUP_DIR/$rel"
}

copy_tree() {
  local src="$1" dst="$2"
  local entry name target
  mkdir -p "$dst"
  shopt -s dotglob nullglob
  for entry in "$src"/*; do
    shopt -u dotglob nullglob
    [ -e "$entry" ] || continue
    name="$(basename "$entry")"
    # .gitignore is handled separately: its lines are merged, not replaced
    [ "$name" = ".gitignore" ] && { shopt -s dotglob nullglob; continue; }
    # the python cache is not part of the configuration
    [ "$name" = "__pycache__" ] && { shopt -s dotglob nullglob; continue; }
    case "$name" in
      *.pyc) shopt -s dotglob nullglob; continue ;;
    esac
    target="$dst/$name"
    if [ -d "$entry" ] && [ ! -L "$entry" ]; then
      copy_tree "$entry" "$target"
    elif [ -e "$target" ]; then
      if [ "$FORCE" -eq 1 ]; then
        backup_file "$target"
        cp -p "$entry" "$target"
        OVERWRITTEN+=("$target")
      else
        SKIPPED+=("$target")
      fi
    else
      cp -p "$entry" "$target"
      COPIED+=("$target")
    fi
    shopt -s dotglob nullglob
  done
  shopt -u dotglob nullglob
}

merge_gitignore() {
  local line added=0
  if [ -f "$PAYLOAD/.gitignore" ]; then
    if [ ! -f "$TARGET/.gitignore" ]; then
      cp -p "$PAYLOAD/.gitignore" "$TARGET/.gitignore"
      COPIED+=("$TARGET/.gitignore")
    else
      while IFS= read -r line; do
        [ -n "$line" ] || continue
        grep -qxF "$line" "$TARGET/.gitignore" && continue
        printf '%s\n' "$line" >> "$TARGET/.gitignore"
        added=1
      done < "$PAYLOAD/.gitignore"
    fi
  fi
  # the backups of --force must not show up as untracked files
  if [ -f "$TARGET/.gitignore" ] && ! grep -qxF ".opencode-backup-*/" "$TARGET/.gitignore" 2>/dev/null; then
    printf '%s\n' ".opencode-backup-*/" >> "$TARGET/.gitignore"
    added=1
  fi
  [ "$added" -eq 1 ] && echo "Added the missing ignore lines to $TARGET/.gitignore"
  return 0
}

echo "Installing '$PAYLOAD_NAME' into $TARGET"
copy_tree "$PAYLOAD" "$TARGET"
merge_gitignore

count() { [ "$1" -gt 0 ] && echo "$1" || echo "0"; }
echo
echo "Copied:      $(count ${#COPIED[@]}) new files"
if [ "${#SKIPPED[@]}" -gt 0 ]; then
  echo "Kept as they were (already present):"
  printf '  %s\n' "${SKIPPED[@]}"
fi
if [ "${#OVERWRITTEN[@]}" -gt 0 ]; then
  echo "Overwritten (backup in ${BACKUP_DIR#"$TARGET"/}/):"
  printf '  %s\n' "${OVERWRITTEN[@]}"
fi
if [ "${#SKIPPED[@]}" -gt 0 ] && [ "$FORCE" -eq 0 ]; then
  echo
  echo "The files above already existed and were NOT touched. To replace them"
  echo "(after a backup) run the same command with --force."
fi

echo
echo "Next steps:"
echo "  1. cd \"$TARGET\""
echo "  2. start opencode (restart it if it is already running)"
echo "  3. opencode debug config    # to see what OpenCode actually loaded"
if [ "$PAYLOAD_NAME" = "notes" ]; then
  echo "  4. prerequisites for the notes config:"
  echo "       opencode plugin add opencode-parser"
  echo "       sudo apt install tesseract-ocr tesseract-ocr-ita poppler-utils"
  echo "       python3 -m pip install --user --break-system-packages pypdf \"obsidian-mcp-search[server]\" docling"
fi

if [ "$MODE" = "install-no-check" ]; then
  echo
  echo "Environment check skipped (--no-check)."
  exit 0
fi

echo
if "$REPO_DIR/doctor.sh" "$PAYLOAD_NAME" "$TARGET"; then
  exit 0
else
  echo
  echo "The files are installed, but the environment is not ready: fix the [FAIL] lines above."
  exit 2
fi
