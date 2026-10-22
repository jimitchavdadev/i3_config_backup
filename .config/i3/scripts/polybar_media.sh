#!/usr/bin/env bash
# Polybar Media Player Module (Playerctl)

if ! command -v playerctl &>/dev/null; then
    exit 0
fi

STATUS=$(playerctl status 2>/dev/null)

if [ "$STATUS" = "Playing" ]; then
    ARTIST=$(playerctl metadata artist 2>/dev/null)
    TITLE=$(playerctl metadata title 2>/dev/null)
    if [ -n "$TITLE" ]; then
        if [ -n "$ARTIST" ]; then
            TRACK="$ARTIST - $TITLE"
        else
            TRACK="$TITLE"
        fi
        if [ ${#TRACK} -gt 35 ]; then
            TRACK="${TRACK:0:32}..."
        fi
        echo "󰝚 $TRACK"
    else
        echo "󰝚 Playing"
    fi
elif [ "$STATUS" = "Paused" ]; then
    TITLE=$(playerctl metadata title 2>/dev/null)
    if [ -n "$TITLE" ]; then
        if [ ${#TITLE} -gt 25 ]; then
            TITLE="${TITLE:0:22}..."
        fi
        echo "󰝛 $TITLE"
    else
        echo "󰝛 Paused"
    fi
else
    echo ""
fi
