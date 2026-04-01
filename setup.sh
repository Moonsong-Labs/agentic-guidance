#!/usr/bin/env bash
# Moonsong Labs — Zero-to-One AI Engineering Setup
#
# Usage:
#   bash <(curl -sSL https://raw.githubusercontent.com/Moonsong-Labs/agentic-guidance/main/setup.sh)
#   bash <(curl -sSL https://raw.githubusercontent.com/Moonsong-Labs/agentic-guidance/main/setup.sh) --install-claude
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

Usage:
  bash <(curl -sSL https://raw.githubusercontent.com/Moonsong-Labs/agentic-guidance/main/setup.sh)
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

# TODO: switch to Moonsong-Labs/knowledge-work-plugins once PR is merged
REPO_URL="https://github.com/gabriel-hurtado/knowledge-work-plugins.git"
REPO_BRANCH="feat/msl-engineering-values"
TRAIN_URL="https://train.msldev.io"
TRAIN_DASHBOARD="https://train.msldev.io/dashboard/projects"
# TODO: switch to Moonsong-Labs once PR is merged
VALUES_PROMPT_URL="https://raw.githubusercontent.com/gabriel-hurtado/knowledge-work-plugins/feat/msl-engineering-values/core-engineering/shared/msl-engineering-values.md"
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
# Install gum
# --------------------------------------------------------------------------

install_gum() {
    command -v gum &>/dev/null && return 0

    mkdir -p "$HOME/.local/bin"
    local arch
    arch=$(uname -m)
    [[ "$arch" == "aarch64" ]] && arch="arm64"

    local os_name
    [[ "$OS" == "macos" ]] && os_name="Darwin" || os_name="Linux"

    if [[ "$OS" == "macos" ]] && command -v brew &>/dev/null; then
        brew install gum >/dev/null 2>&1 && return 0
    fi

    local url
    url=$(curl -fsSL https://api.github.com/repos/charmbracelet/gum/releases/latest \
        | grep "browser_download_url.*${os_name}_${arch}.tar.gz" \
        | head -1 | cut -d '"' -f 4) || return 1
    curl -fsSL "$url" | tar xz -C "$HOME/.local/bin" gum 2>/dev/null || return 1
    export PATH="$HOME/.local/bin:$PATH"
    command -v gum &>/dev/null
}

HAS_GUM=false
if command -v gum &>/dev/null; then
    HAS_GUM=true
else
    printf "\033[0;36m▸\033[0m Installing gum (pretty terminal UI)...\n"
    if install_gum 2>/dev/null; then
        HAS_GUM=true
        printf "\033[0;32m✓\033[0m gum installed\n"
    else
        printf "\033[0;33m!\033[0m gum not available — using plain output\n"
    fi
fi

# --------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------

ui_header() {
    if $HAS_GUM; then
        echo ""
        gum style --bold --border rounded --padding "0 2" --border-foreground 27 "$1"
    else
        printf "\n\033[1m── %s ──\033[0m\n" "$1"
    fi
}

ui_section() {
    if $HAS_GUM; then
        echo ""
        gum style --bold --foreground 27 "▸ $1"
    else
        printf "\n\033[1m▸ %s\033[0m\n" "$1"
    fi
}

ui_ok()   { $HAS_GUM && gum style --foreground 245 "  ✓ $1" || printf "  \033[0;37m✓\033[0m %s\n" "$1"; }
ui_warn() { $HAS_GUM && gum style --foreground 220 "  ! $1" || printf "  \033[0;33m!\033[0m %s\n" "$1"; }
ui_fail() { $HAS_GUM && gum style --foreground 197 "  ✗ $1" || printf "  \033[0;31m✗\033[0m %s\n" "$1"; }
ui_info() { $HAS_GUM && gum style --foreground 39  "  $1"   || printf "  \033[0;36m\033[0m%s\n" "$1"; }

ui_confirm() {
    if $HAS_GUM; then
        gum confirm --selected.foreground 255 --selected.background 27 --unselected.foreground 245 "$1"
    else
        printf "\033[0;36m▸\033[0m %s [Y/n] " "$1"
        local answer; read -r answer; answer="${answer:-Y}"
        [[ "$answer" =~ ^[Yy] ]]
    fi
}

ui_input() {
    local prompt="$1" placeholder="${2:-}"
    if $HAS_GUM; then
        gum input --header "▸ $prompt" --placeholder "$placeholder" --width 60 \
            --prompt.foreground 39 --cursor.foreground 27 --header.foreground 39
    else
        printf "\033[0;36m▸\033[0m %s " "$prompt"
        local val; read -r val; echo "$val"
    fi
}

ui_spin() {
    local title="$1"; shift
    if $HAS_GUM; then
        gum spin --title "$title" --spinner.foreground 27 -- "$@"
    else
        ui_info "$title"; "$@"
    fi
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
        mv "$tmp" "$SHELL_RC"
    else
        printf '\n%s\n%s\n' "$marker" "$alias_line" >> "$SHELL_RC"
    fi
}

clone_or_update() {
    local target="$1"
    if [ -d "$target/.git" ]; then
        local current_remote
        current_remote=$(git -C "$target" remote get-url origin 2>/dev/null)
        if [[ "$current_remote" != "$REPO_URL" ]]; then
            ui_warn "Remote changed, re-cloning..."
            rm -rf "$target"
            ui_spin "Cloning knowledge-work-plugins..." git clone --depth 1 --branch "$REPO_BRANCH" --quiet "$REPO_URL" "$target"
        else
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
    elif grep -q "${key} *= *" "$file" 2>/dev/null; then
        local tmp; tmp=$(mktemp)
        sed "s/${key} *=.*/${key} = ${val}/" "$file" > "$tmp"; mv "$tmp" "$file"
    elif grep -q "\[features\]" "$file" 2>/dev/null; then
        local tmp; tmp=$(mktemp)
        awk -v feat="$key = $val" '/\[features\]/{print; print feat; next} {print}' "$file" > "$tmp"; mv "$tmp" "$file"
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
ui_info "This script configures your AI coding tools with MSL's"
ui_info "engineering values, skills, and Prompt-Train proxy."
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
        ui_info "Routes Claude Code through MSL's proxy for monitoring"
        ui_info "and shared account pooling."
        echo ""
        ui_info "To get a key, either:"
        ui_info "  • Ask your project lead for one, or"
        ui_info "  • Create your own (open a project → API Keys → Generate)"
        echo ""
        if ui_confirm "Open Prompt-Train dashboard in browser?"; then
            open "$TRAIN_DASHBOARD" 2>/dev/null || xdg-open "$TRAIN_DASHBOARD" 2>/dev/null || echo "    $TRAIN_DASHBOARD"
        fi
        echo ""
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
import json

path = '$settings_file'
try:
    with open(path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

# TODO: switch to Moonsong-Labs/knowledge-work-plugins, remove ref
markets = settings.setdefault('extraKnownMarketplaces', {})
markets['moonsong-labs'] = {
    'source': {
        'source': 'github',
        'repo': 'gabriel-hurtado/knowledge-work-plugins',
        'ref': 'feat/msl-engineering-values',
    }
}

plugins = settings.setdefault('enabledPlugins', {})
plugins.setdefault('core-engineering@moonsong-labs', True)

with open(path, 'w') as f:
    json.dump(settings, f, indent=2)
print('ok')
") || { ui_fail "Could not update settings.json"; return 1; }

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
    ui_warn "Cursor sessionStart hooks are buggy — using global rules as workaround"
    local rules_dir="$HOME/.cursor/rules"
    mkdir -p "$rules_dir"
    if curl -fsSL "$VALUES_PROMPT_URL" -o "$rules_dir/msl-engineering-values.mdc" 2>/dev/null; then
        ui_ok "Values injected into ~/.cursor/rules/"
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

summary_lines=()
$DID_PROMPTTRAIN && summary_lines+=("✓ Prompt-Train configured") || true
$DID_CLAUDE_CODE && summary_lines+=("✓ Claude Code: marketplace + plugin$([ -n "$PT_TOKEN" ] && echo " + 'cld' alias")") || true
$DID_CURSOR      && summary_lines+=("✓ Cursor: skills from plugin + values in global rules (hook workaround)") || true
$DID_CODEX       && summary_lines+=("✓ Codex: skills + session-start hook from plugin") || true
summary_lines+=("")
if [[ -n "$PT_TOKEN" ]]; then
    summary_lines+=("Restart your shell to load the 'cld' alias.")
fi
summary_lines+=("Start a new session to activate.")
summary_lines+=("Re-run this script to pull latest values and skills.")

echo ""
if $HAS_GUM; then
    printf '%s\n' "${summary_lines[@]}" | gum style --border rounded --padding "1 2" --border-foreground 27
else
    ui_header "Setup complete"
    for line in "${summary_lines[@]}"; do
        [[ -n "$line" ]] && echo "  $line" || echo ""
    done
fi
