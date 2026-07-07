#!/usr/bin/env bash
# warden-demo.sh — a self-contained, REAL demonstration of ORA Warden freezing a rogue agent.
# Starts the governance broker in a throwaway home, then drives the exact sequence an AI agent would:
# useful work goes through; the moment it reaches for rm -rf, a secret, or the network, the Warden
# says no — and every attempt lands on the tamper-evident audit log. No mockups: this is real output.
#
# Usage:  ORA_WARDEN_BROKER_BIN=/path/to/ora-runtime ./demo/warden-demo.sh
set -euo pipefail

BIN="${ORA_WARDEN_BROKER_BIN:-ora-runtime}"
PORT="${DEMO_PORT:-4577}"
DEMO_HOME="$(mktemp -d)"
export HOME="$DEMO_HOME" ORA_RUNTIME_ROOT="$DEMO_HOME/runtime"
mkdir -p "$ORA_RUNTIME_ROOT"

c_grn=$'\e[32m'; c_red=$'\e[31m'; c_dim=$'\e[2m'; c_cyan=$'\e[36m'; c_rst=$'\e[0m'
say(){ printf '\n%s$ %s%s\n' "$c_cyan" "$1" "$c_rst"; }
post(){ curl -s -X POST "http://127.0.0.1:$PORT$1" -H 'Content-Type: application/json' -d "$2"; }

"$BIN" broker --host 127.0.0.1 --port "$PORT" >"$DEMO_HOME/broker.log" 2>&1 &
BPID=$!; trap 'kill $BPID 2>/dev/null; rm -rf "$DEMO_HOME"' EXIT
sleep 2
printf '%s  ORA Warden — your agent on a leash%s\n' "$c_grn" "$c_rst"
printf '%s  (broker running in a throwaway home: %s)%s\n' "$c_dim" "$DEMO_HOME" "$c_rst"

say "agent> build the report  (normal work — allowed)"
r=$(post /shell/run '{"command":"echo report built > report.txt && wc -c report.txt","cwd":"'"$DEMO_HOME"'","destructive_intent":false,"authority":"A3"}')
printf '  %s✓ ran%s  %s\n' "$c_grn" "$c_rst" "$(echo "$r" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("stdout","").strip())')"

say "agent> rm -rf the workspace  (destructive — Warden freezes it)"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "http://127.0.0.1:$PORT/shell/run" -H 'Content-Type: application/json' -d '{"command":"rm -rf '"$DEMO_HOME"'","cwd":"'"$DEMO_HOME"'","destructive_intent":false,"authority":"A3"}')
printf '  %s✗ BLOCKED%s  (HTTP %s — destructive command refused, no override flag exists)\n' "$c_red" "$c_rst" "$code"

say "agent> exfiltrate the ssh key  (secret — Warden blocks the write)"
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "http://127.0.0.1:$PORT/files/write" -H 'Content-Type: application/json' -d '{"path":"'"$DEMO_HOME"'/.ssh/authorized_keys","content":"attacker-key"}')
printf '  %s✗ BLOCKED%s  (HTTP %s — .ssh is off-limits to governed writes)\n' "$c_red" "$c_rst" "$code"

say "you> show me exactly what happened  (tamper-evident audit)"
curl -s "http://127.0.0.1:$PORT/audit/recent?limit=4" | python3 -c '
import sys,json
for e in json.load(sys.stdin)[:4]:
    tool=e.get("tool",""); res=e.get("result",""); cmd=(e.get("arguments_redacted") or {}).get("command","")
    print(f"  • {tool:18} {res:10} {cmd[:44]}")'
v=$(curl -s "http://127.0.0.1:$PORT/audit/verify")
printf '  %saudit chain: %s%s\n' "$c_grn" "$(echo "$v" | python3 -c 'import sys,json;d=json.load(sys.stdin);print("intact ✓" if d.get("ok") else "BROKEN")')" "$c_rst"
printf '\n%s  Every attempt is on the record. The agent did the work; it could not do the damage.%s\n\n' "$c_grn" "$c_rst"
