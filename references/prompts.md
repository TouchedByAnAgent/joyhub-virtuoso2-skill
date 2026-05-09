# Agent Prompts

Use these prompts when handing the skill to another agent.

## Build or Patch Controller

```text
Use the joyhub-virtuoso2 skill. Build or patch a minimal Python bleak controller for the validated J-Virtuoso2 / Virtuoso 2 device. Keep commands focused on scan, connect, send, preset, presets, and all-off. Ensure send and preset paths use automatic all-off cleanup by default. Verify all-actuator combined control sends suction first, then wave control.
```

## Live Operation

```text
Use the joyhub-virtuoso2 skill to operate the validated device. Keep the operator watching the device. Before actuator commands, state what to observe. After every live command, ensure cleanup sends a00300000000aa and a00d00000000.
```

## Verification

```text
Use the joyhub-virtuoso2 skill to verify a controller implementation. Check device identity, command generation for vibration 1-9, tongue 1-9, combined wave, suction P1-P3, all-actuator combined control, all-off cleanup, and CLI dry-run output.
```
