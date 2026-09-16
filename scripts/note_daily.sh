#!/usr/bin/env bash
# note.com daily repost runner. One approved article per day, driven by `claude -p --chrome`
# following scripts/note_daily_prompt.md. Ledger and logs stay under .notes/ (gitignored).
#
#   scripts/note_daily.sh run [publish|draft]   # one attempt now (default publish)
#   scripts/note_daily.sh install               # launchd agent, 09:00 Asia/Tokyo daily
#   scripts/note_daily.sh uninstall
#   scripts/note_daily.sh status
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.shimo4228.zenn-content.note-daily"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DB="${NOTE_DAILY_DB:-$REPO/.notes/note-publishing/queue.sqlite}"
RUNS="$REPO/.notes/note-publishing/runs"
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/note-uv-cache}"

run() {
  local mode="${1:-publish}"
  case "$mode" in publish|draft) ;; *) echo "mode must be publish or draft" >&2; exit 2;; esac
  local run_dir="$RUNS/$(TZ=Asia/Tokyo date +%Y-%m-%dT%H%M%S)-$mode"
  mkdir -p "$run_dir"
  local prompt
  prompt="$(sed -e "s|{{MODE}}|$mode|g" -e "s|{{DB}}|$DB|g" -e "s|{{RUN_DIR}}|$run_dir|g" \
    "$REPO/scripts/note_daily_prompt.md")"
  cd "$REPO"
  # Tool allowlist: browser, files, and only the shell commands the skill needs.
  claude -p --chrome --output-format json --max-turns 200 \
    --allowedTools "mcp__claude-in-chrome" Read Write Edit Glob Grep \
      "Bash(uv run --project scripts python scripts/note_publish.py:*)" \
      "Bash(osascript:*)" "Bash(python3:*)" "Bash(curl -s https://note.com/api/v3/notes/:*)" \
      "Bash(npm run:*)" "Bash(cp:*)" "Bash(mkdir:*)" "Bash(ls:*)" "Bash(cat:*)" \
    "$prompt" > "$run_dir/claude.json" 2> "$run_dir/claude.err" || true
  python3 - "$run_dir" <<'EOF'
import json, sys, pathlib
run = pathlib.Path(sys.argv[1])
try:
    data = json.loads((run / 'claude.json').read_text())
    print(json.dumps({'is_error': data.get('is_error'), 'turns': data.get('num_turns'),
                      'cost_usd': data.get('total_cost_usd'), 'result': data.get('result')},
                     ensure_ascii=False, indent=2))
except Exception as exc:  # claude did not produce JSON; the .err file has the reason
    print(f'runner produced no JSON: {exc}', file=sys.stderr)
    sys.exit(1)
EOF
  test -f "$run_dir/result.json" && cat "$run_dir/result.json"
}

install() {
  mkdir -p "$HOME/Library/LaunchAgents" "$RUNS"
  cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>
    <string>/bin/bash</string><string>$REPO/scripts/note_daily.sh</string><string>run</string><string>publish</string>
  </array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$RUNS/launchd.out.log</string>
  <key>StandardErrorPath</key><string>$RUNS/launchd.err.log</string>
  <key>EnvironmentVariables</key><dict><key>TZ</key><string>Asia/Tokyo</string></dict>
</dict></plist>
EOF
  launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST"
  echo "installed $LABEL (09:00 Asia/Tokyo daily); log: $RUNS/launchd.*.log"
}

uninstall() {
  launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
  rm -f "$PLIST"
  echo "removed $LABEL"
}

status() {
  launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | grep -E 'state|last exit|runs' || echo "not installed"
  uv run --project scripts python scripts/note_publish.py status --db "$DB"
}

case "${1:-}" in
  run) run "${2:-publish}" ;;
  install) install ;;
  uninstall) uninstall ;;
  status) status ;;
  *) sed -n '2,8p' "$0"; exit 2 ;;
esac
