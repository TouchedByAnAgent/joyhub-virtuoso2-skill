# Joyhub Virtuoso2 Codex Skill

Agent skill and bundled control script for the validated Joyhub-compatible device:

- Product link: https://amzn.to/4tpeo5E
- Device: `J-Virtuoso2 / Virtuoso 2`
- Validated BLE address: `FF:25:07:11:DD:36`
- `productCode`: `3131`
- `icCode`: `8d`
- `abilityCode`: `01100000`
- `abilityLimit`: `060050000000`
- `switch_code`: `0803`

This repository is intentionally a skill repo. It includes prompts, protocol notes, and a bundled Python script that an agent can run directly. It is not a full Python package.

## Contents

```text
SKILL.md                     Codex skill instructions
agents/openai.yaml           Skill UI/default prompt metadata
references/protocol.md       Protocol and command-generation reference
references/prompts.md        Reusable handoff and verification prompts
scripts/joyhub_virtuoso2.py  Minimal executable controller script
```

## Install Locally

Clone or copy this repository into the Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R joyhub-virtuoso2-skill ~/.codex/skills/joyhub-virtuoso2
```

Then restart Codex so the skill metadata is discovered.

For live BLE control, install `bleak` in the Python environment that has Bluetooth access:

```bash
python -m pip install bleak
```

On Windows, use Windows Python for live BLE commands. WSL Python may not have Bluetooth adapter access.

## Skill Usage

Use the skill when an agent needs to:

- Operate the validated device safely.
- Generate or verify BLE commands for vibration, tongue/licking, suction/squeeze, or all-actuator control.
- Build or patch a minimal controller while preserving automatic cleanup.
- Hand off instructions to another agent or operator.

The main skill file is `SKILL.md`. It directs agents to the bundled script and protocol references.

## Script Quick Start

From the skill directory:

```bash
python scripts/joyhub_virtuoso2.py --help
python scripts/joyhub_virtuoso2.py presets
python scripts/joyhub_virtuoso2.py preset all-actuators-max --dry-run
```

Expected all-actuator dry-run output:

```text
a00d000003ff
a003ffff0000aa
# cleanup
a00300000000aa
a00d00000000
```

## Live Control Examples

All `preset` and `send` commands perform automatic all-off cleanup by default.

Turn on tongue/licking max for 10 seconds:

```bash
python scripts/joyhub_virtuoso2.py preset tongue-9 --hold-seconds 10
```

Turn on vibration max for 10 seconds:

```bash
python scripts/joyhub_virtuoso2.py preset vibration-9 --hold-seconds 10
```

Turn on suction/squeeze `P3` for 10 seconds:

```bash
python scripts/joyhub_virtuoso2.py preset suction-p3 --hold-seconds 10
```

Turn on suction/squeeze plus tongue:

```bash
python scripts/joyhub_virtuoso2.py send a00d000003ff a00300ff0000aa --hold-seconds 10
```

Turn on all actuators:

```bash
python scripts/joyhub_virtuoso2.py preset all-actuators-max --hold-seconds 10
```

Explicit stop:

```bash
python scripts/joyhub_virtuoso2.py all-off
```

## Validated Protocol

Wave control:

```text
a003 VV LL 00 00 aa
```

- `VV`: vibration level byte
- `LL`: tongue/licking level byte
- level `0`: `00`
- level `9`: `ff`
- vibration minimum: decimal `60`
- tongue minimum: decimal `50`

Core wave commands:

```text
wave off:       a00300000000aa
max vibration:  a003ff000000aa
max tongue:     a00300ff0000aa
max both:       a003ffff0000aa
```

Suction/squeeze:

```text
P1:  a00d000001ff
P2:  a00d000002ff
P3:  a00d000003ff
off: a00d00000000
```

All-actuator combined control requires suction first, then wave:

```text
a00d000003ff
a003ffff0000aa
```

The reverse order was tested and did not reliably switch the device from `P0` into suction.

## Safety

- Keep the device visible and physically interruptible during live operation.
- Prefer `preset` and `send` without `--no-cleanup`.
- If anything behaves unexpectedly, run `all-off`.
- Automatic cleanup sends both:

```text
a00300000000aa
a00d00000000
```

## Test Battery

Validate the skill structure:

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
```

Compile the script:

```bash
python -m py_compile scripts/joyhub_virtuoso2.py
```

Run dry-run checks:

```bash
python scripts/joyhub_virtuoso2.py presets
python scripts/joyhub_virtuoso2.py preset all-actuators-max --dry-run
python scripts/joyhub_virtuoso2.py send a003ff000000aa --dry-run
```

Live BLE tests should only be run with the operator watching the device.
