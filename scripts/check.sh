#!/usr/bin/env bash
set -uo pipefail

# ── MallRobo lint & security checks ──────────────────────────────────────────
# Run from project root: ./scripts/check.sh

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

declare -a NAMES=()
declare -a RESULTS=()
FAILURES=0

run_check() {
    local name="$1"
    shift
    printf "${BOLD}▶ %s${RESET}\n" "$name"
    "$@"
    local rc=$?
    NAMES+=("$name")
    if [ $rc -eq 0 ]; then
        RESULTS+=("pass")
    else
        RESULTS+=("fail")
        FAILURES=$((FAILURES + 1))
    fi
    echo ""
    return $rc
}

# ── Backend checks ───────────────────────────────────────────────────────────
echo ""
printf "${BOLD}═══ Backend ═══${RESET}\n\n"
cd "$PROJECT_ROOT/backend"

run_check "ruff check"          ruff check .
run_check "ruff format"         ruff format --check .
run_check "bandit"              bandit -r app/ -q
run_check "pip-audit"           pip-audit
run_check "pytest"              python -m pytest tests/ -v

# ── Frontend checks ──────────────────────────────────────────────────────────
printf "${BOLD}═══ Frontend ═══${RESET}\n\n"
cd "$PROJECT_ROOT/frontend"

run_check "eslint"              npx eslint .
run_check "tsc"                 npx tsc --noEmit
run_check "npm audit"           npm audit --audit-level=moderate
run_check "vitest"              npx vitest run --reporter=verbose

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
printf "${BOLD}═══ Summary ═══${RESET}\n"
for i in "${!NAMES[@]}"; do
    if [ "${RESULTS[$i]}" = "pass" ]; then
        printf "  ${GREEN}✓ %s${RESET}\n" "${NAMES[$i]}"
    else
        printf "  ${RED}✗ %s${RESET}\n" "${NAMES[$i]}"
    fi
done

echo ""
if [ $FAILURES -eq 0 ]; then
    printf "${GREEN}${BOLD}All checks passed.${RESET}\n"
else
    printf "${RED}${BOLD}%d check(s) failed.${RESET}\n" "$FAILURES"
fi

exit $FAILURES
