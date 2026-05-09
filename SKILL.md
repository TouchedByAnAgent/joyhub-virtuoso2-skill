---
name: joyhub-virtuoso2
description: Control and document the validated Joyhub-compatible J-Virtuoso2 / Virtuoso 2 BLE device. Use when Codex needs to operate, script, verify, or hand off safe commands for this specific device, including vibration, tongue/licking, suction/squeeze P modes, all-off cleanup, and all-actuator combined control.
---

# Joyhub Virtuoso2

Use this skill for the validated device:

- Product link: https://amzn.to/4tpeo5E
- Disclosure: This is a paid affiliate link. As an Amazon Associate I earn from qualifying purchases.
- Device: `J-Virtuoso2 / Virtuoso 2`
- BLE address validated in live testing: `FF:25:07:11:DD:36`
- `productCode`: `3131`
- `icCode`: `8d`
- `abilityCode`: `01100000`
- `abilityLimit`: `060050000000`
- `switch_code`: `0803`
- BLE service: `0000ffa0-0000-1000-8000-00805f9b34fb`
- Write characteristic: `0000ffa1-0000-1000-8000-00805f9b34fb`
- Notify characteristic: `0000ffa2-0000-1000-8000-00805f9b34fb`

## Workflow

1. Confirm the operator can observe the device and stop immediately if needed.
2. Use the bundled script first: `scripts/joyhub_virtuoso2.py`.
3. For live control, install `bleak`, subscribe to notifications when possible, then write hex commands to `ffa1`.
4. Every actuator path must support automatic cleanup. The bundled script enables cleanup by default for `send` and `preset`.
5. For all-actuator combined control, send suction/squeeze first, then wave control. The reverse order stayed in `P0` and did not reliably enable suction on the tested unit.

## Commands

See [references/protocol.md](references/protocol.md) for command generation details.
See [references/prompts.md](references/prompts.md) for reusable agent prompts.

Core commands:

```text
wave off:          a00300000000aa
suction off:       a00d00000000
suction P1/P2/P3:  a00d000001ff / a00d000002ff / a00d000003ff
max vibration:     a003ff000000aa
max tongue:        a00300ff0000aa
max wave combo:    a003ffff0000aa
all actuators max: a00d000003ff then a003ffff0000aa
```

## Safety Rules

- Keep the device close, visible, and physically interruptible during live use.
- Default `send` and `preset` operations to cleanup enabled.
- Explicit all-off must send both `a00300000000aa` and `a00d00000000`.
- Do not add APK artifacts, decompiled source, UI code, scraping, unrelated device support, or broad product research.

## Verification

Verify this skill and bundled code with:

```bash
python scripts/joyhub_virtuoso2.py preset all-actuators-max --dry-run
python scripts/joyhub_virtuoso2.py presets
```

The dry run must print suction first, wave second, then cleanup.
