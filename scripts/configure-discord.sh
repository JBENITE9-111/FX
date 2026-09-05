#!/bin/zsh
set -euo pipefail

project_dir="/Users/macmac/Documents/Codex/FX"
env_file="$project_dir/.env"

cd "$project_dir"
umask 077

printf "Paste the Discord webhook URL (input is hidden): "
IFS= read -r -s webhook
printf "\n"

case "$webhook" in
  https://discord.com/api/webhooks/*|https://discordapp.com/api/webhooks/*) ;;
  *)
    unset webhook
    printf "That is not a Discord webhook URL. No file was changed.\n" >&2
    exit 1
    ;;
esac

touch "$env_file"
temp_file="$(mktemp "$project_dir/.env.discord.XXXXXX")"
trap 'rm -f "$temp_file"; unset webhook' EXIT

found=0
while IFS= read -r line || [[ -n "$line" ]]; do
  if [[ "$line" == DISCORD_WEBHOOK_URL=* ]]; then
    printf 'DISCORD_WEBHOOK_URL=%s\n' "$webhook" >> "$temp_file"
    found=1
  else
    printf '%s\n' "$line" >> "$temp_file"
  fi
done < "$env_file"

if [[ "$found" -eq 0 ]]; then
  printf '\nDISCORD_WEBHOOK_URL=%s\n' "$webhook" >> "$temp_file"
fi

chmod 600 "$temp_file"
mv "$temp_file" "$env_file"
unset webhook
trap - EXIT

launchctl kickstart -k "gui/$(id -u)/com.fx.api"

printf "Waiting for FX to restart...\n"
for attempt in {1..20}; do
  if curl -fsS "http://127.0.0.1:8000/api/status" >/dev/null 2>&1; then
    result="$(curl -fsS -X POST "http://127.0.0.1:8000/api/operations/notifications/discord/test")"
    if [[ "$result" == *'"ok":true'* ]]; then
      printf "Discord is connected. A paper-only FX test message was delivered.\n"
      exit 0
    fi
    printf "FX restarted, but Discord did not confirm delivery. Open http://127.0.0.1:8000/operations and check channel health.\n" >&2
    exit 1
  fi
  sleep 2
done

printf "The webhook was saved, but FX did not restart in time. Run: launchctl kickstart -k gui/$(id -u)/com.fx.api\n" >&2
exit 1
