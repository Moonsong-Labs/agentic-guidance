#!/usr/bin/env bash
# Moonsong Labs — Zero-to-One AI Engineering Setup
#
# Configures your AI coding tools with:
#   1. Engineering values — core principles injected into every AI session
#   2. Skills — engineering workflows (TDD, debugging, brainstorming, etc.)
#   3. Prompt-Train (optional) — shared API account with usage monitoring
#
# Usage:
#   bash <(curl -sSL https://github.com/Moonsong-Labs/agentic-guidance/releases/latest/download/setup.sh)
#   bash <(curl -sSL https://github.com/Moonsong-Labs/agentic-guidance/releases/latest/download/setup.sh) --install-claude
#
# Or locally:
#   ./setup.sh [--install-claude] [--help]
#
# Flags:
#   --install-claude    Prompt to install Claude Code even if other tools exist
#   --help              Show this help message
#
# Platforms: Claude Code, Cursor, Codex
# OS:        macOS, Linux
# Idempotent — safe to re-run to update.

set -euo pipefail

# --------------------------------------------------------------------------
# Parse flags
# --------------------------------------------------------------------------

INSTALL_CLAUDE=false
for arg in "$@"; do
    case "$arg" in
        --install-claude) INSTALL_CLAUDE=true ;;
        --help|-h)
            cat <<'HELP'
Moonsong Labs — Zero-to-One AI Engineering Setup

Configures your AI coding tools with:
  1. Engineering values — core principles injected into every AI session
  2. Skills — engineering workflows (TDD, debugging, brainstorming, etc.)
  3. Prompt-Train (optional) — shared API account with usage monitoring

Usage:
  bash <(curl -sSL https://github.com/Moonsong-Labs/agentic-guidance/releases/latest/download/setup.sh)
  ./setup.sh [--install-claude] [--help]

Flags:
  --install-claude    Prompt to install Claude Code even if other tools exist
  --help              Show this help message

Platforms: Claude Code, Cursor, Codex
OS:        macOS, Linux
Idempotent — safe to re-run to update.
HELP
            exit 0
            ;;
    esac
done

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

REPO_URL="https://github.com/Moonsong-Labs/knowledge-work-plugins.git"
REPO_BRANCH="main"
TRAIN_URL="https://train.msldev.io"
TRAIN_DASHBOARD="https://train.msldev.io/dashboard/projects"
VALUES_PROMPT_URL="https://raw.githubusercontent.com/Moonsong-Labs/knowledge-work-plugins/main/core-engineering/shared/msl-engineering-values.md"
PT_TOKEN=""

DID_PROMPTTRAIN=false
DID_CLAUDE_CODE=false
DID_CURSOR=false
DID_CODEX=false

# --------------------------------------------------------------------------
# Preflight
# --------------------------------------------------------------------------

OS="$(uname -s)"
case "$OS" in
    Darwin) OS="macos" ;;
    Linux)  OS="linux" ;;
    *)
        echo "✗ Unsupported OS: $OS. macOS and Linux only."
        exit 1
        ;;
esac

for cmd in git curl python3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "✗ Required: $cmd"
        exit 1
    fi
done

# --------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------

COLS=$(tput cols 2>/dev/null || echo 80)
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'

ui_header() {
    local rule; rule=$(printf '─%.0s' $(seq 1 "$COLS"))
    printf "\n%b%s%b\n" "$CYAN" "$rule" "$RESET"
    printf "%b  %s%b\n" "$BOLD" "$1" "$RESET"
    printf "%b%s%b\n\n" "$CYAN" "$rule" "$RESET"
}
ui_section() { printf "\n%b▸ %s%b\n" "${BOLD}${CYAN}" "$1" "$RESET"; }
ui_ok()      { printf "  %b✓%b %s\n" "$GREEN" "$RESET" "$1"; }
ui_warn()    { printf "  %b!%b %s\n" "$YELLOW" "$RESET" "$1"; }
ui_fail()    { printf "  %b✗%b %s\n" "$RED" "$RESET" "$1"; }
ui_info() {
    printf '%s' "$1" | fold -s -w $((COLS - 4)) | while IFS= read -r line || [[ -n "$line" ]]; do
        printf "  %b%s%b\n" "$DIM" "$line" "$RESET"
    done
}
ui_link() {
    printf '  \033]8;;%s\007%b\033[4m%s%b\033]8;;\007\n' "$1" "$BLUE" "${2:-$1}" "$RESET"
}

ui_confirm() {
    printf "%b▸%b %s %b[Y/n]%b " "$CYAN" "$RESET" "$1" "$DIM" "$RESET"
    local answer; read -r answer; answer="${answer:-Y}"
    [[ "$answer" =~ ^[Yy] ]]
}

ui_input() {
    printf "%b▸%b %s " "$CYAN" "$RESET" "$1"
    local val; read -r val; echo "$val"
}

ui_spin() {
    local title="$1"; shift
    ui_info "$title"; "$@"
}

# --------------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------------

detect_shell_rc() {
    if [[ -n "${ZSH_VERSION:-}" ]] || [[ "$SHELL" == */zsh ]]; then echo "$HOME/.zshrc"
    elif [[ -n "${BASH_VERSION:-}" ]] || [[ "$SHELL" == */bash ]]; then echo "$HOME/.bashrc"
    else echo "$HOME/.profile"; fi
}
SHELL_RC="$(detect_shell_rc)"

write_alias() {
    local marker="$1" alias_line="$2"
    if grep -q "$marker" "$SHELL_RC" 2>/dev/null; then
        local tmp; tmp=$(mktemp)
        awk -v marker="$marker" -v alias_cmd="$alias_line" \
            '$0 == marker { print marker; print alias_cmd; getline; next } { print }' \
            "$SHELL_RC" > "$tmp"
        # Validate: output must be at least as long as input (minus 1 line for the replaced alias)
        local orig_lines new_lines
        orig_lines=$(wc -l < "$SHELL_RC")
        new_lines=$(wc -l < "$tmp")
        if [[ "$new_lines" -lt $((orig_lines - 1)) ]]; then
            ui_warn "Shell RC update looks wrong — keeping original"
            rm -f "$tmp"
            return 1
        fi
        cp "$SHELL_RC" "${SHELL_RC}.bak"
        mv "$tmp" "$SHELL_RC"
    else
        cp "$SHELL_RC" "${SHELL_RC}.bak" 2>/dev/null || true
        printf '\n%s\n%s\n' "$marker" "$alias_line" >> "$SHELL_RC"
    fi
}

clone_or_update() {
    local target="$1"
    if [ -d "$target/.git" ]; then
        local current_remote
        current_remote=$(git -C "$target" remote get-url origin 2>/dev/null)
        if [[ "$current_remote" != "$REPO_URL" ]]; then
            ui_warn "Remote changed — moving old clone to ${target}.bak"
            rm -rf "${target}.bak"
            mv "$target" "${target}.bak"
            ui_spin "Cloning knowledge-work-plugins..." git clone --depth 1 --branch "$REPO_BRANCH" --quiet "$REPO_URL" "$target"
        else
            # Check for local modifications before resetting
            if [ -n "$(git -C "$target" status --porcelain 2>/dev/null)" ]; then
                ui_warn "Local modifications detected in $target — stashing"
                git -C "$target" stash --quiet 2>/dev/null || true
            fi
            ui_spin "Updating knowledge-work-plugins..." git -C "$target" fetch --depth 1 origin "$REPO_BRANCH" --quiet
            git -C "$target" reset --hard FETCH_HEAD --quiet
        fi
    else
        ui_spin "Cloning knowledge-work-plugins..." git clone --depth 1 --branch "$REPO_BRANCH" --quiet "$REPO_URL" "$target"
    fi
    [ -d "$target/core-engineering" ] || { ui_fail "Clone failed"; return 1; }
}

ensure_toml_feature() {
    local file="$1" key="$2" val="$3"
    mkdir -p "$(dirname "$file")"
    if [ ! -f "$file" ]; then
        printf '[features]\n%s = %s\n' "$key" "$val" > "$file"
    elif grep -q "^${key} *= *" "$file" 2>/dev/null; then
        # Match only at start of line to avoid hitting comments or values
        local tmp; tmp=$(mktemp)
        sed "s/^${key} *=.*/${key} = ${val}/" "$file" > "$tmp"
        if [ -s "$tmp" ]; then
            mv "$tmp" "$file"
        else
            ui_warn "TOML update produced empty file — keeping original"
            rm -f "$tmp"
        fi
    elif grep -q "^\[features\]" "$file" 2>/dev/null; then
        local tmp; tmp=$(mktemp)
        awk -v feat="$key = $val" '/^\[features\]/{print; print feat; next} {print}' "$file" > "$tmp"
        if [ -s "$tmp" ]; then
            mv "$tmp" "$file"
        else
            ui_warn "TOML update produced empty file — keeping original"
            rm -f "$tmp"
        fi
    else
        printf '\n[features]\n%s = %s\n' "$key" "$val" >> "$file"
    fi
}

# --------------------------------------------------------------------------
# Detect platforms
# --------------------------------------------------------------------------

platforms=()
command -v claude &>/dev/null && platforms+=("claude-code")
command -v codex  &>/dev/null && platforms+=("codex")
if [ "$OS" = "macos" ] && [ -d "/Applications/Cursor.app" ]; then
    platforms+=("cursor")
elif command -v cursor &>/dev/null; then
    platforms+=("cursor")
fi

ui_header "Moonsong Labs — AI Engineering Setup"
ui_info "This script sets up engineering values (behavioral principles injected into every AI session), skills (TDD, debugging, brainstorming, code review, etc. as slash commands), and optionally Prompt-Train (shared API account with usage monitoring)."
echo ""

# --------------------------------------------------------------------------
# Install Claude Code
# --------------------------------------------------------------------------

install_claude_code() {
    if command -v claude &>/dev/null; then
        ui_ok "Claude Code already installed"
        return 0
    fi
    ui_info "Claude Code is the recommended AI coding tool at MSL."
    ui_confirm "Install Claude Code?" || return 1

    ui_spin "Downloading..." curl -fsSL https://claude.ai/install.sh -o /tmp/claude-install.sh
    bash /tmp/claude-install.sh || { ui_fail "Installation failed"; rm -f /tmp/claude-install.sh; return 1; }
    rm -f /tmp/claude-install.sh

    ui_ok "Claude Code installed"
    if command -v claude &>/dev/null; then
        platforms+=("claude-code")
    elif [ -x "$HOME/.claude/bin/claude" ]; then
        export PATH="$HOME/.claude/bin:$PATH"
        platforms+=("claude-code")
        ui_warn "Restart your shell or: export PATH=\"\$HOME/.claude/bin:\$PATH\""
    fi
}

if $INSTALL_CLAUDE || [ ${#platforms[@]} -eq 0 ]; then
    install_claude_code || true
fi

if [ ${#platforms[@]} -eq 0 ]; then
    ui_fail "No supported AI coding tool detected."
    ui_info "Install Claude Code: curl -fsSL https://claude.ai/install.sh | bash"
    exit 1
fi

ui_ok "Found $(IFS=,; tmp="${platforms[*]}"; echo "${tmp//,/, }") on $OS"
[[ -n "${ANTHROPIC_AUTH_TOKEN:-}" ]] && ui_ok "Prompt-Train token found in environment"

# --------------------------------------------------------------------------
# Prompt-Train (Claude Code only)
# --------------------------------------------------------------------------

configure_prompttrain() {
    ui_section "Prompt-Train"
    PT_TOKEN="${ANTHROPIC_AUTH_TOKEN:-}"

    if [[ ! " ${platforms[*]} " =~ " claude-code " ]] && ! $INSTALL_CLAUDE; then
        ui_info "Prompt-Train is for Claude Code only — skipping."
        return 0
    fi

    if [[ -z "$PT_TOKEN" ]]; then
        ui_info "Prompt-Train routes Claude through MSL's shared API account so you don't need your own Anthropic key — usage is tracked per-developer for cost management. This is optional; skipping still gives you values and skills."
        ui_info "To get a key, ask your project lead or create your own at the dashboard (open a project, then API Keys, then Generate)."
        echo ""
        if ui_confirm "Open Prompt-Train dashboard in browser?"; then
            open "$TRAIN_DASHBOARD" 2>/dev/null || xdg-open "$TRAIN_DASHBOARD" 2>/dev/null || echo "    $TRAIN_DASHBOARD"
        fi
        if ui_confirm "Do you have a Prompt-Train API key?"; then
            PT_TOKEN=$(ui_input "Paste your API key:" "cnp_live_...")
        fi
        if [[ -z "$PT_TOKEN" ]]; then
            ui_warn "Skipping Prompt-Train."
            return 0
        fi
    fi

    ui_ok "Token: ${PT_TOKEN:0:15}..."
    DID_PROMPTTRAIN=true
}

# --------------------------------------------------------------------------
# Claude Code — register marketplace + enable plugin via settings.json
# --------------------------------------------------------------------------

setup_claude_code() {
    ui_section "Claude Code"

    local settings_file="$HOME/.claude/settings.json"
    mkdir -p "$HOME/.claude"

    local status
    status=$(python3 -c "
import json, shutil, sys, os

path = '$settings_file'

# Load existing settings
try:
    with open(path) as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}
except json.JSONDecodeError:
    print('malformed')
    sys.exit(0)

# Back up before writing
if os.path.exists(path):
    shutil.copy2(path, path + '.bak')

markets = settings.setdefault('extraKnownMarketplaces', {})
markets['moonsong-labs'] = {
    'source': {
        'source': 'github',
        'repo': 'Moonsong-Labs/knowledge-work-plugins',
    }
}

plugins = settings.setdefault('enabledPlugins', {})
plugins.setdefault('core-engineering@moonsong-labs', True)

# Write to temp file, then rename (atomic on same filesystem)
tmp_path = path + '.tmp'
with open(tmp_path, 'w') as f:
    json.dump(settings, f, indent=2)

# Validate what we wrote before replacing
with open(tmp_path) as f:
    json.load(f)

os.replace(tmp_path, path)
print('ok')
") || { ui_fail "Could not update settings.json"; return 1; }

    if [[ "$status" == "malformed" ]]; then
        ui_fail "$HOME/.claude/settings.json is malformed JSON — skipping to avoid data loss"
        ui_info "Fix the file manually, then re-run this script."
        return 1
    fi

    if [[ "$status" == "ok" ]]; then
        ui_ok "Marketplace registered (moonsong-labs)"
        ui_ok "Plugin enabled (core-engineering)"
    else
        ui_warn "Could not verify — check ~/.claude/settings.json"
    fi

    if [[ -n "$PT_TOKEN" ]]; then
        write_alias \
            "# MSL Claude alias (managed by agentic-guidance setup)" \
            "alias cld='ANTHROPIC_BASE_URL=\"$TRAIN_URL\" ANTHROPIC_AUTH_TOKEN=\"$PT_TOKEN\" claude'"
        ui_ok "'cld' alias added — use 'cld' instead of 'claude' to route through Prompt-Train"
    fi

    DID_CLAUDE_CODE=true
}

# --------------------------------------------------------------------------
# Cursor — uses the same plugin hooks as Claude Code
# --------------------------------------------------------------------------

setup_cursor() {
    ui_section "Cursor"

    if [[ " ${platforms[*]} " =~ " claude-code " ]]; then
        ui_ok "Claude Code detected — Cursor picks up skills on restart."
    else
        ui_info "Cursor works best with Claude Code for plugin support."
        if install_claude_code; then setup_claude_code; fi
    fi

    # Cursor's sessionStart hooks from Claude Code plugins don't fire reliably
    # as of v2.6.x (known bug: forum.cursor.com/t/claude-hooks-dont-work/153614).
    # Workaround: inject values via global rules (~/.cursor/rules/).
    # TODO: switch to plugin hook once Cursor fixes sessionStart execution.
    ui_info "Installing values as Cursor global rules (loaded every session)"
    local rules_dir="$HOME/.cursor/rules"
    mkdir -p "$rules_dir"
    if curl -fsSL "$VALUES_PROMPT_URL" -o "$rules_dir/msl-engineering-values.mdc" 2>/dev/null; then
        ui_ok "Values installed in ~/.cursor/rules/"
        ui_info "Skills are available through the Claude Code plugin. Cursor hook support is limited, so values are delivered via global rules for now."
    else
        ui_warn "Could not download values prompt"
    fi

    DID_CURSOR=true
}

# --------------------------------------------------------------------------
# Codex — clone repo, symlink skills + hooks from the plugin
# --------------------------------------------------------------------------

setup_codex() {
    ui_section "Codex"

    local clone_dir="$HOME/.codex/knowledge-work-plugins"
    local skills_dir="$HOME/.agents/skills"

    clone_or_update "$clone_dir" || return 1

    # Symlink skills
    mkdir -p "$skills_dir"
    if [ -L "$skills_dir/core-engineering" ]; then
        ui_ok "Skills symlink exists"
    else
        ln -s "$clone_dir/core-engineering/skills" "$skills_dir/core-engineering"
        ui_ok "Skills symlinked"
    fi

    # Use the plugin's existing hooks — same session-start script that Claude Code uses
    local hooks_json="$HOME/.codex/hooks.json"
    local hook_cmd="$clone_dir/core-engineering/hooks/session-start"

    if [ ! -f "$hooks_json" ]; then
        cat > "$hooks_json" <<JSONEOF
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "CLAUDE_PLUGIN_ROOT=1 \\"\\$HOME/.codex/knowledge-work-plugins/core-engineering/hooks/session-start\\""
          }
        ]
      }
    ]
  }
}
JSONEOF
        ui_ok "hooks.json → plugin's session-start"
    elif ! grep -q "session-start" "$hooks_json" 2>/dev/null; then
        ui_warn "hooks.json exists — add $hook_cmd to SessionStart manually"
    else
        ui_ok "Hook already registered"
    fi

    # Enable hooks feature flag
    ensure_toml_feature "$HOME/.codex/config.toml" "codex_hooks" "true"
    ui_ok "Hooks enabled"
    ui_info "Engineering values and skills are now available in Codex. To update, re-run this script (Codex doesn't auto-update like Claude Code)."

    DID_CODEX=true
}

# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------

configure_prompttrain

for platform in "${platforms[@]}"; do
    case "$platform" in
        claude-code) setup_claude_code ;;
        cursor)      setup_cursor ;;
        codex)       setup_codex ;;
    esac
done

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------

echo ""
ui_header "Setup complete"
if $DID_PROMPTTRAIN; then ui_ok "Prompt-Train configured"; fi
if $DID_CLAUDE_CODE; then ui_ok "Claude Code: marketplace + plugin enabled, auto-updates on session start"; fi
if $DID_CURSOR; then ui_ok "Cursor: values in global rules, skills via Claude Code plugin"; fi
if $DID_CODEX; then ui_ok "Codex: values + skills via session-start hook (re-run to update)"; fi
echo ""
ui_info "Engineering values and skills (/brainstorming, /tdd, /systematic-debugging, /writing-plans, /requesting-code-review, etc.) will load automatically on your next session."
ui_info "Full skill catalog:"
ui_link "https://github.com/Moonsong-Labs/knowledge-work-plugins"
echo ""
if [[ -n "$PT_TOKEN" ]]; then ui_info "Use 'cld' instead of 'claude' to route through Prompt-Train (restart your shell first)."; fi
ui_info "Open a new session in any of your configured tools to get started."
