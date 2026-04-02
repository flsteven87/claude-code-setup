#!/bin/sh
input=$(cat)
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
five=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
week=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
dir=$(basename "$cwd")

# Claude brand colors via ANSI 256-color codes
# Orange/coral (Claude primary): 209  Muted gold accent: 179  Soft lavender: 183  Steel blue: 110
ORANGE="\033[1;38;5;209m"
GOLD="\033[38;5;179m"
LAVENDER="\033[38;5;183m"
STEEL="\033[38;5;110m"
DIM_SEP="\033[2;37m"
RESET="\033[0m"

# Directory — soft lavender
printf "${LAVENDER}%s${RESET}" "$dir"

# Model — orange/coral (Claude primary brand color), bold
if [ -n "$model" ]; then
  printf "${DIM_SEP}  ${RESET}${ORANGE}%s${RESET}" "$model"
fi

# Context used — gold, only when data is available
if [ -n "$used" ]; then
  printf "${DIM_SEP}  ${RESET}${GOLD}ctx:$(printf '%.0f' "$used")%%${RESET}"
fi

# Rate limits — steel blue
if [ -n "$five" ] || [ -n "$week" ]; then
  printf "${DIM_SEP}  ${RESET}"
  if [ -n "$five" ]; then
    printf "${STEEL}5h:$(printf '%.0f' "$five")%%${RESET}"
  fi
  if [ -n "$week" ]; then
    [ -n "$five" ] && printf "${DIM_SEP} ${RESET}"
    w=$(printf '%.0f' "$week")
    # Progress bar: 20 chars wide (5% per block)
    filled=$(( w / 5 ))
    [ $filled -gt 20 ] && filled=20
    bar=""
    i=0; while [ $i -lt $filled ]; do bar="${bar}▓"; i=$((i+1)); done
    while [ $i -lt 20 ]; do bar="${bar}░"; i=$((i+1)); done
    printf "${STEEL}7d${RESET}${DIM_SEP}:${RESET}${STEEL}%s${RESET} ${STEEL}%s%%${RESET}" "$bar" "$w"
  fi
fi
