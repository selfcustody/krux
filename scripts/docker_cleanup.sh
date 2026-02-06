#!/bin/bash
# Docker cleanup when dangling images exceed 50GB

THRESHOLD_GB=50
KRUX_DIR="/Users/qlrd/github/krux"

total_bytes=0
while IFS= read -r size; do
    [[ -z "$size" ]] && continue
    num=$(echo "$size" | sed 's/[^0-9.]//g')
    unit=$(echo "$size" | sed 's/[0-9.]//g')
    case "$unit" in
        GB) bytes=$(echo "$num * 1073741824" | bc) ;;
        MB) bytes=$(echo "$num * 1048576" | bc) ;;
        *) bytes=0 ;;
    esac
    total_bytes=$(echo "$total_bytes + $bytes" | bc)
done < <(docker images --filter "dangling=true" --format "{{.Size}}" 2>/dev/null)

gb=$(echo "scale=2; $total_bytes / 1073741824" | bc)
if (( $(echo "$gb >= $THRESHOLD_GB" | bc -l) )); then
    cd "$KRUX_DIR" && /Users/qlrd/.local/bin/poetry run poe docker --purge krux
fi