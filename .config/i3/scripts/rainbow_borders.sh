#!/bin/bash
# Simple script to cycle border colors for focused window

while true; do
    i3-msg client.focused border pixel 3 >/dev/null
    i3-msg client.focused border color #ff0000 >/dev/null
    sleep 3
    i3-msg client.focused border color #00ff00 >/dev/null
    sleep 3
    i3-msg client.focused border color #0000ff >/dev/null
    sleep 3
done
