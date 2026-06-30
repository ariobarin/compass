#!/bin/sh

if [ -n "$CODEX_HOME" ]; then
  codex_home=$CODEX_HOME
else
  codex_home=$HOME/.codex
fi

guard=$codex_home/hooks/portable_guard.py
if [ ! -f "$guard" ]; then
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$guard"
fi

if command -v python >/dev/null 2>&1; then
  exec python "$guard"
fi

exit 0
