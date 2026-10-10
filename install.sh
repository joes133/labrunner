#!/usr/bin/env bash
#
# labrunner installer (macOS / Linux)
#
# Usage:
#   ./install.sh                    # auto-detect every supported client
#   ./install.sh --client claude    # install to one client only
#   ./install.sh --list             # show known clients and their paths
#
# Output is ASCII-only on purpose, to stay consistent with install.ps1.

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT="auto"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --client) CLIENT="${2:-}"; shift 2 ;;
        --list)   CLIENT="__list__"; shift ;;
        -h|--help) CLIENT="__list__"; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Client registry: name -> skill dir, and the parent dir used for detection.
# SKILL.md is an open standard (Anthropic Agent Skills); only the location
# differs between clients.
client_dir() {
    case "$1" in
        workbuddy) echo "$HOME/.workbuddy/skills/labrunner" ;;
        claude)    echo "$HOME/.claude/skills/labrunner" ;;
        cursor)    echo "$HOME/.cursor/skills/labrunner" ;;
        codex)     echo "$HOME/.codex/skills/labrunner" ;;
        agents)    echo "$HOME/.agents/skills/labrunner" ;;
        kiro)      echo "$HOME/.kiro/agents/labrunner" ;;
        *)         echo "" ;;
    esac
}

client_root() {
    case "$1" in
        workbuddy) echo "$HOME/.workbuddy" ;;
        claude)    echo "$HOME/.claude" ;;
        cursor)    echo "$HOME/.cursor" ;;
        codex)     echo "$HOME/.codex" ;;
        agents)    echo "$HOME/.agents" ;;
        kiro)      echo "$HOME/.kiro" ;;
        *)         echo "" ;;
    esac
}

ALL_CLIENTS="workbuddy claude cursor codex agents kiro"

show_list() {
    echo "Known clients:"
    for c in $ALL_CLIENTS; do
        mark=" "
        [ -d "$(client_root "$c")" ] && mark="*"
        printf "  %s %-10s %s\n" "$mark" "$c" "$(client_dir "$c")"
    done
    echo ""
    echo "  * = detected on this machine"
    exit 0
}

[ "$CLIENT" = "__list__" ] && show_list

install_to() {
    local name="$1" dst="$2"
    echo ""
    echo "[$name]"
    echo "  -> $dst"

    mkdir -p "$dst"
    for f in SKILL.md README.md LICENSE; do
        [ -f "$SRC/$f" ] && cp -f "$SRC/$f" "$dst/"
    done
    # Replace directories wholesale. cp -R into an existing directory nests
    # a copy inside it (dst/references/references), so remove first.
    for d in scripts references; do
        if [ -d "$SRC/$d" ]; then
            rm -rf "$dst/$d"
            cp -Rf "$SRC/$d" "$dst/"
        fi
    done

    # .local holds personal config: profile.json is NEVER touched, but
    # profile.example.json is just a template and is always refreshed.
    mkdir -p "$dst/.local"
    [ -f "$SRC/.local/profile.example.json" ] \
        && cp -f "$SRC/.local/profile.example.json" "$dst/.local/"

    echo "  installed"
}

echo "Installing labrunner ..."
echo "  from : $SRC"

if [ "$CLIENT" = "auto" ]; then
    # Auto mode installs to workbuddy only. Every other client must be named
    # explicitly with --client, so labrunner never writes into a directory
    # you did not ask for.
    TARGETS="workbuddy"
    echo "  auto mode: workbuddy only"
    echo "  run --list to see every supported client"
else
    if [ -z "$(client_dir "$CLIENT")" ]; then
        echo ""
        echo "Unknown client: $CLIENT"
        show_list
    fi
    TARGETS="$CLIENT"
fi

for t in $TARGETS; do
    install_to "$t" "$(client_dir "$t")"
done

echo ""
echo "Next step - install dependencies:"
echo "  pip install pillow python-docx chardet"
echo ""
echo "Note: window capture (capture.py) is Windows + pywin32 only."
echo "      On macOS/Linux labrunner falls back to full-screen capture."
echo ""
echo "Done. Trigger with: /labrunner  or  \"help me run this lab\""
