#!/usr/bin/env bash
# Installs one of the OpenCode configurations of this repository into a target folder.
#
#   ./install.sh notes /path/to/vault        university notes vault
#   ./install.sh web   /path/to/project      web project (portals and websites)
#   ./install.sh notes /path/to/vault --force   back up and overwrite existing files
#
# The whole content of notes/ or web/ is copied into the target: AGENTS.md and
# opencode.json at the top, everything else under .opencode/.
# Files that already exist are never touched unless --force is given, and with
# --force they are first copied into <target>/.opencode-backup-<timestamp>/.

set -euo pipefail

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
}

PAYLOAD_NAME="${1:-}"
TARGET="${2:-}"
FORCE=0
for arg in "${@:3}"; do
  case "$arg" in
    --force) FORCE=1 ;;
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
[ -d "$TARGET" ] || { echo "ERROR: target '$TARGET' does not exist or is not a folder"; exit 1; }
TARGET="$(cd "$TARGET" && pwd)"

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
  [ -f "$PAYLOAD/.gitignore" ] || return 0
  if [ ! -f "$TARGET/.gitignore" ]; then
    cp -p "$PAYLOAD/.gitignore" "$TARGET/.gitignore"
    COPIED+=("$TARGET/.gitignore")
    return 0
  fi
  local line added=0
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    grep -qxF "$line" "$TARGET/.gitignore" && continue
    printf '%s\n' "$line" >> "$TARGET/.gitignore"
    added=1
  done < "$PAYLOAD/.gitignore"
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
  echo "       opencode plugin opencode-parser -g"
  echo "       sudo apt install tesseract-ocr tesseract-ocr-ita poppler-utils"
fi
