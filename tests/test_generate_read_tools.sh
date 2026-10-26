#!/usr/bin/env bash
# Tests for scripts/generate-read-tools.sh against a stubbed registry.
#
# Requires curl and jq, like the generator. Run from anywhere:
#
#     ./tests/test_generate_read_tools.sh

set -u

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
GENERATOR="$HERE/../scripts/generate-read-tools.sh"

pass=0
fail=0

# Committed list: read-00..read-19. Registry tools are read-NN (read-only) and
# write-NN (not).
committed_list() {
    echo "# committed"
    for i in $(seq -w 0 19); do echo "read-$i"; done
}

# Writes a registry JSON with reads read-00..read-(R-1) and writes
# write-00..write-(W-1); writes listed in $3 (space-separated) are marked
# read-only instead.
registry() {
    local reads="$1" writes="$2" flipped="${3:-}" i
    {
        echo "{"
        for ((i = 0; i < reads; i++)); do
            printf '"read-%02d":{"annotations":{"readOnlyHint":true}},\n' "$i"
        done
        for ((i = 0; i < writes; i++)); do
            local name hint=false
            name="$(printf 'write-%02d' "$i")"
            [[ " $flipped " == *" $name "* ]] && hint=true
            printf '"%s":{"annotations":{"readOnlyHint":%s}},\n' "$name" "$hint"
        done
        echo '"last-write":{"annotations":{"readOnlyHint":false}}'
        echo "}"
    }
}

# Args: case name, expected outcome ("accept" or "refuse"), registry JSON or
# "-" for an unreachable registry, "none" to start without a committed list.
run_case() {
    local name="$1" expected="$2" registry_json="$3" committed="${4:-}"
    local dir status before after ok=1
    dir="$(mktemp -d)"
    mkdir -p "$dir/scripts" "$dir/hooks"
    cp "$GENERATOR" "$dir/scripts/"
    [[ "$committed" == none ]] || committed_list > "$dir/hooks/read-tools.txt"
    [[ "$registry_json" == - ]] || printf '%s' "$registry_json" > "$dir/registry.json"
    before="$(cat "$dir/hooks/read-tools.txt" 2>/dev/null)"

    REGISTRY_URL="file://$dir/registry.json" bash "$dir/scripts/generate-read-tools.sh" >/dev/null 2>&1
    status=$?
    after="$(cat "$dir/hooks/read-tools.txt" 2>/dev/null)"

    if [[ "$expected" == accept ]]; then
        [[ $status -eq 0 && "$after" != "$before" ]] || ok=0
    else
        [[ $status -ne 0 && "$after" == "$before" ]] || ok=0
    fi
    rm -rf "$dir"

    if (( ok )); then
        pass=$((pass + 1))
        printf "  ok   %s\n" "$name"
    else
        fail=$((fail + 1))
        printf "  FAIL %s\n       expected=%s status=%d\n" "$name" "$expected" "$status"
    fi
}

echo "Running generate-read-tools.sh tests..."

run_case "accepts one new read tool (5%)" accept "$(registry 21 10)"
run_case "accepts one removed read tool (5%)" accept "$(registry 19 10)"
run_case "accepts two new read tools (exactly 10%)" accept "$(registry 22 10)"
run_case "accepts two removed read tools (exactly 10%)" accept "$(registry 18 10)"
run_case "refuses three writes turning read-only (15%)" refuse "$(registry 20 10 'write-00 write-01 write-02')"
run_case "refuses three new read tools (15%)" refuse "$(registry 23 10)"
run_case "refuses three removed read tools (15%)" refuse "$(registry 17 10)"
run_case "refuses an empty registry" refuse '{}'
run_case "refuses an unreachable registry" refuse -
run_case "accepts any list when none is committed" accept "$(registry 23 10)" none

echo
echo "Passed: $pass  Failed: $fail"
(( fail == 0 ))
