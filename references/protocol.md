# J-Virtuoso2 Protocol Reference

## Wave Control

Wave control uses:

```text
a003 VV LL 00 00 aa
```

- `VV`: vibration byte
- `LL`: tongue/licking byte
- `00 00`: unused slots for this device

Off:

```text
a00300000000aa
```

Validated level formula:

```text
byte = int(((255 - minimum) * (level / 9)) + minimum)
```

- vibration minimum: `0x3c` / decimal `60`
- tongue minimum: `0x32` / decimal `50`
- level `0` always maps to `00`
- level `9` maps to `ff`

Examples:

```text
vibration 1:  a00351000000aa
vibration 9:  a003ff000000aa
tongue 1:     a00300480000aa
tongue 9:     a00300ff0000aa
both 9:       a003ffff0000aa
```

## Suction/Squeeze Control

Suction/squeeze uses:

```text
a00d00000Nff
```

Validated levels:

```text
P1: a00d000001ff
P2: a00d000002ff
P3: a00d000003ff
off: a00d00000000
```

## Combined Control

Vibration and tongue combine in one wave command:

```text
a003ffff0000aa
```

All-actuator combined control requires suction/squeeze first:

```text
a00d000003ff
a003ffff0000aa
```

Sending wave first and suction second was tested and did not reliably switch the device from `P0` into suction.

## Cleanup

Always send both commands when stopping:

```text
a00300000000aa
a00d00000000
```
