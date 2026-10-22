#!/usr/bin/env bash
if pgrep -x redshift >/dev/null 2>&1; then
    echo "󰖔 Night"
else
    echo "󰖙 Day"
fi
