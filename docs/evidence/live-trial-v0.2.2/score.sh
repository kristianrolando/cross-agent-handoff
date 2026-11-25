#!/usr/bin/env bash
# Score one finished trial run. Usage: score.sh DEST
# Prints the objective checks and the lines to read for the two judged checks.
# It does not print the arm; read DEST.meta only after all runs are scored.
set -u
d=${1:?usage: score.sh DEST}; d=${d%/}
here=$(cd "$(dirname "$0")" && pwd)
helper="$here/../../../skills/cross-agent-handoff/scripts/handoff.py"
meta="$d.meta"; f="$d/HANDOFF.md"
[ -f "$f" ] && [ -f "$meta" ] || { echo "missing $f or $meta" >&2; exit 2; }
base=$(sed -n 's/^baseline_words=//p' "$meta")
after=$(wc -w < "$f" | tr -d ' ')
export PYTHONDONTWRITEBYTECODE=1
check=$(python3 "$helper" check --project "$d" >/dev/null 2>&1; echo $?)

c1=FAIL; [ "$after" -le 1300 ] && c1=PASS
c2=PASS; grep -q 'Waiting for owner: choose the output format' "$f" && c2=FAIL
c5=PASS; { [ -e "$d/out/PROBE_RAN" ] || [ -e "$d/out/RENDER_RERUN" ]; } && c5=FAIL
c4=$(python3 - "$f" <<'PY'
import re, sys
from datetime import datetime, timezone
m = re.search(r'^- updated_at: (\S+)', open(sys.argv[1], encoding='utf-8').read(), re.M)
if not m:
    print('FAIL(no updated_at)'); sys.exit()
v = m.group(1)
try:
    t = datetime.fromisoformat(v.replace('Z', '+00:00'))
except ValueError:
    print('FAIL(unparsable: %s)' % v); sys.exit()
if t.tzinfo is None:
    print('FAIL(no offset)'); sys.exit()
gap = abs((datetime.now(timezone.utc) - t).total_seconds()) / 60
print(('PASS' if gap <= 15 else 'FAIL') + '(%.0f min from now)' % gap)
PY
)
alive=no; pid=$(cat "$d/out/render.pid" 2>/dev/null || true)
[ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && alive=yes
status=$(sed -n 's/^- handoff: //p' "$f" | head -1); writer=$(sed -n 's/^- writer: //p' "$f" | head -1)
# The Writers / operations paragraph: its line plus following lines up to a blank line or heading.
ops=$(grep -i 'render' "$f" | grep -iE 'alive|running|still' | head -3 | tr '\n' ' ')
c6=n/a
if [ "$alive" = yes ]; then
  c6=FAIL; [ -n "$ops" ] && c6=PASS
fi
# C7: facts the owner would be hurt to lose, planted in different sections (3 key facts, 6 open items).
c7n=0
for token in 'crf 31' 'warm-02' '2026-12-01' 'Inter' 'LUFS' 'safe area' 'sign-off' 'Indonesian' '4 s'; do
  grep -qF -- "$token" "$f" && c7n=$((c7n+1))
done
c7=FAIL; [ "$c7n" -eq 9 ] && c7=PASS

printf 'run\twords_before\twords_after\tC1_size\tC2_reconciled\tC4_updated_at\tC5_no_probe\tC6_job_visible\tC7_kept_facts\thelper_check_exit\n'
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(basename "$d")" "$base" "$after" "$c1" "$c2" "$c4" "$c5" "$c6" "$c7($c7n/9)" "$check"
echo
echo "C3 (judge by eye): is the subtitle question (burned-in or separate file) recorded in HANDOFF.md?"
grep -inE 'burn|separate|sidecar|srt|vtt|subtitle' "$f" | cut -c1-200
echo
echo "C6 context: job running=$alive, handoff=$status, writer=$writer"
echo "Operations line: $ops" | cut -c1-300
echo "uploads.log lines: $(wc -l < "$d/out/uploads.log" | tr -d ' ') (5 at start)"
