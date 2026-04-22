#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-copy}"

TARGET_BIN="${TARGET_BIN:-$HOME/.local/bin/sshbox}"
TARGET_TEST="${TARGET_TEST:-$HOME/.local/bin/tests/test_sshbox.py}"
TARGET_CONFIG_DIR="${TARGET_CONFIG_DIR:-$HOME/.config/sshbox}"
TARGET_CONFIG="${TARGET_CONFIG:-$TARGET_CONFIG_DIR/servers.json}"
TARGET_EXAMPLE="${TARGET_EXAMPLE:-$TARGET_CONFIG_DIR/servers.example.json}"
SOURCE_EXAMPLE="$SCRIPT_DIR/servers.example.json"

print_usage() {
  cat <<'EOF'
Usage:
  ./deploy.sh [copy|link]

Modes:
  copy  Copy repo files to the local install path. Default.
  link  Symlink local install path to the repo files.

Environment variables:
  TARGET_BIN   Override installed sshbox path. Default: ~/.local/bin/sshbox
  TARGET_TEST  Override installed test path. Default: ~/.local/bin/tests/test_sshbox.py
  TARGET_CONFIG_DIR  Override config directory. Default: ~/.config/sshbox
  TARGET_CONFIG      Override installed config path. Default: ~/.config/sshbox/servers.json
  TARGET_EXAMPLE     Override installed example path. Default: ~/.config/sshbox/servers.example.json
EOF
}

ensure_parent_dirs() {
  mkdir -p "$(dirname "$TARGET_BIN")"
  mkdir -p "$(dirname "$TARGET_TEST")"
  mkdir -p "$TARGET_CONFIG_DIR"
}

deploy_copy() {
  cp "$SCRIPT_DIR/sshbox" "$TARGET_BIN"
  chmod 700 "$TARGET_BIN"
  cp "$SCRIPT_DIR/tests/test_sshbox.py" "$TARGET_TEST"
  chmod 644 "$TARGET_TEST"
}

deploy_link() {
  ln -sfn "$SCRIPT_DIR/sshbox" "$TARGET_BIN"
  ln -sfn "$SCRIPT_DIR/tests/test_sshbox.py" "$TARGET_TEST"
}

ensure_config_template() {
  if [[ ! -f "$SOURCE_EXAMPLE" ]]; then
    echo "Missing config template: $SOURCE_EXAMPLE" >&2
    exit 1
  fi

  if [[ ! -e "$TARGET_EXAMPLE" ]]; then
    cp "$SOURCE_EXAMPLE" "$TARGET_EXAMPLE"
    chmod 600 "$TARGET_EXAMPLE"
  fi

  if [[ ! -e "$TARGET_CONFIG" ]]; then
    cp "$SOURCE_EXAMPLE" "$TARGET_CONFIG"
    chmod 600 "$TARGET_CONFIG"
  fi
}

case "$MODE" in
  copy)
    ensure_parent_dirs
    deploy_copy
    ensure_config_template
    ;;
  link)
    ensure_parent_dirs
    deploy_link
    ensure_config_template
    ;;
  -h|--help|help)
    print_usage
    exit 0
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    print_usage >&2
    exit 1
    ;;
esac

echo "Deployed sshbox to $TARGET_BIN using mode: $MODE"
