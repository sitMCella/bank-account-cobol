#!/bin/sh
awk '{printf("%04d00%s\n", NR, substr($0,7,120)) }' "$1" > "$1.tmp" && mv "$1.tmp" "$1"