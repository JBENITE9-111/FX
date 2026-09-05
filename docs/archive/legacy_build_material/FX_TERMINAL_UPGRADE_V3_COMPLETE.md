# FX Terminal Upgrade V3

This package is for:

```text
/Users/macmac/Documents/Codex/FX
```

It fixes the previous `ModuleNotFoundError: No module named 'services'`, integrates `FX_HARNESS_V1_1_NEXT_PATCH`, adds the FX Global Newspaper, and runs all 16 strategy workers with a $1 virtual paper account each.

## After downloading `FX_TERMINAL_UPGRADE_V3.zip` to your Downloads folder

Copy and paste this entire block into Terminal:

```bash
cd "$HOME/Downloads"

rm -rf FX_TERMINAL_UPGRADE_V3

mkdir -p FX_TERMINAL_UPGRADE_V3

unzip -o "FX_TERMINAL_UPGRADE_V3.zip" -d FX_TERMINAL_UPGRADE_V3

chmod +x FX_TERMINAL_UPGRADE_V3/install.sh

bash FX_TERMINAL_UPGRADE_V3/install.sh
```

After installation, normal use remains:

```bash
fx
```

New pages:

```text
http://127.0.0.1:8000/newspaper
http://127.0.0.1:8000/strategy-fleet
```

The newspaper refreshes every 30 minutes.

The strategy fleet refreshes every 5 minutes.

Each strategy has $1 of **virtual paper capital** assigned to it. A strategy is not forced to enter a trade when its setup is absent; `NO_TRADE` remains a valid output.

Real-money trading remains disabled.
