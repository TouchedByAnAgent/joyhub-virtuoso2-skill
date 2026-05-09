#!/usr/bin/env python3
"""Minimal CLI for the validated J-Virtuoso2 / Virtuoso 2 BLE protocol."""

from __future__ import annotations

import argparse
import asyncio
import re
from collections.abc import Sequence


DEVICE_ADDRESS = "FF:25:07:11:DD:36"
SERVICE_UUID = "0000ffa0-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "0000ffa1-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000ffa2-0000-1000-8000-00805f9b34fb"
VIBRATION_MINIMUM = 60
TONGUE_MINIMUM = 50


def _hex_byte(value: int) -> str:
    if not 0 <= value <= 255:
        raise ValueError(f"byte out of range: {value}")
    return f"{value:02x}"


def intensity_byte(level: int, minimum: int, max_level: int = 9) -> int:
    if not 0 <= level <= max_level:
        raise ValueError(f"level must be 0..{max_level}, got {level}")
    if level == 0:
        return 0
    return int(((255 - minimum) * (level / max_level)) + minimum)


def wave_command(vibration_level: int = 0, tongue_level: int = 0) -> str:
    vibration = intensity_byte(vibration_level, VIBRATION_MINIMUM)
    tongue = intensity_byte(tongue_level, TONGUE_MINIMUM)
    return "a003" + _hex_byte(vibration) + _hex_byte(tongue) + "0000aa"


def suction_command(level: int) -> str:
    if not 0 <= level <= 3:
        raise ValueError(f"suction level must be 0..3, got {level}")
    if level == 0:
        return "a00d00000000"
    return "a00d0000" + _hex_byte(level) + "ff"


def all_off_commands() -> tuple[str, str]:
    return (wave_command(), suction_command(0))


def preset_commands(name: str) -> tuple[str, ...]:
    normalized = name.strip().lower()
    if normalized == "all-off":
        return all_off_commands()
    if normalized == "all-actuators-max":
        return (suction_command(3), wave_command(9, 9))
    if normalized.startswith("vibration-"):
        return (wave_command(vibration_level=int(normalized.removeprefix("vibration-"))),)
    if normalized.startswith("tongue-") or normalized.startswith("licking-"):
        return (wave_command(tongue_level=int(normalized.split("-", 1)[1])),)
    if normalized.startswith("combined-"):
        level = int(normalized.removeprefix("combined-"))
        return (wave_command(vibration_level=level, tongue_level=level),)
    if normalized.startswith("suction-p"):
        return (suction_command(int(normalized.removeprefix("suction-p"))),)
    raise ValueError(f"unknown preset: {name}")


def preset_names() -> list[str]:
    return (
        ["all-off"]
        + [f"vibration-{level}" for level in range(1, 10)]
        + [f"tongue-{level}" for level in range(1, 10)]
        + [f"combined-{level}" for level in range(1, 10)]
        + [f"suction-p{level}" for level in range(1, 4)]
        + ["all-actuators-max"]
    )


def bytes_from_hex(command: str) -> bytes:
    normalized = re.sub(r"\s+", "", command).lower()
    if len(normalized) % 2:
        raise ValueError(f"hex command has odd length: {command!r}")
    return bytes.fromhex(normalized)


def _load_bleak():
    try:
        from bleak import BleakClient, BleakScanner  # type: ignore
    except ImportError as exc:
        raise SystemExit("Install bleak first: python -m pip install bleak") from exc
    return BleakClient, BleakScanner


async def scan(seconds: float) -> None:
    _, scanner = _load_bleak()
    for device in await scanner.discover(timeout=seconds):
        print(f"{getattr(device, 'name', None) or '(no name)'} [{getattr(device, 'address', None)}]")


async def connect(address: str) -> None:
    BleakClient, _ = _load_bleak()
    async with BleakClient(address, timeout=20.0) as client:
        for service in client.services:
            print(service.uuid)
            for characteristic in service.characteristics:
                print(f"  {characteristic.uuid} {','.join(characteristic.properties)}")


async def send_commands(
    commands: Sequence[str],
    *,
    address: str,
    cleanup: bool,
    hold_seconds: float,
    between_command_delay: float,
) -> None:
    BleakClient, _ = _load_bleak()
    async with BleakClient(address, timeout=20.0) as client:
        try:
            for index, command in enumerate(commands):
                print(f"TX {command}")
                await client.write_gatt_char(WRITE_UUID, bytes_from_hex(command), response=False)
                if between_command_delay > 0 and index + 1 < len(commands):
                    await asyncio.sleep(between_command_delay)
            if hold_seconds > 0:
                await asyncio.sleep(hold_seconds)
        finally:
            if cleanup:
                for command in all_off_commands():
                    print(f"TX {command}")
                    await client.write_gatt_char(WRITE_UUID, bytes_from_hex(command), response=False)


def print_commands(commands: Sequence[str], cleanup: bool) -> None:
    for command in commands:
        print(command)
    if cleanup:
        print("# cleanup")
        for command in all_off_commands():
            print(command)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control the validated J-Virtuoso2 BLE device.")
    parser.add_argument("--address", default=DEVICE_ADDRESS)
    sub = parser.add_subparsers(dest="command", required=True)

    scan_parser = sub.add_parser("scan")
    scan_parser.add_argument("--seconds", type=float, default=8.0)

    sub.add_parser("connect")
    sub.add_parser("presets")
    sub.add_parser("all-off")

    send_parser = sub.add_parser("send")
    send_parser.add_argument("hex_command", nargs="+")
    send_parser.add_argument("--hold-seconds", type=float, default=0.0)
    send_parser.add_argument("--between-command-delay", type=float, default=0.0)
    send_parser.add_argument("--no-cleanup", action="store_true")
    send_parser.add_argument("--dry-run", action="store_true")

    preset_parser = sub.add_parser("preset")
    preset_parser.add_argument("name", choices=preset_names())
    preset_parser.add_argument("--hold-seconds", type=float, default=0.0)
    preset_parser.add_argument("--between-command-delay", type=float, default=0.0)
    preset_parser.add_argument("--no-cleanup", action="store_true")
    preset_parser.add_argument("--dry-run", action="store_true")
    return parser


async def run(args: argparse.Namespace) -> int:
    if args.command == "scan":
        await scan(args.seconds)
        return 0
    if args.command == "connect":
        await connect(args.address)
        return 0
    if args.command == "presets":
        print("\n".join(preset_names()))
        return 0
    if args.command == "all-off":
        await send_commands(all_off_commands(), address=args.address, cleanup=False, hold_seconds=0.0, between_command_delay=0.0)
        return 0
    if args.command == "send":
        cleanup = not args.no_cleanup
        if args.dry_run:
            print_commands(args.hex_command, cleanup)
            return 0
        await send_commands(
            args.hex_command,
            address=args.address,
            cleanup=cleanup,
            hold_seconds=args.hold_seconds,
            between_command_delay=args.between_command_delay,
        )
        return 0
    if args.command == "preset":
        commands = preset_commands(args.name)
        cleanup = not args.no_cleanup
        if args.dry_run:
            print_commands(commands, cleanup)
            return 0
        await send_commands(
            commands,
            address=args.address,
            cleanup=cleanup,
            hold_seconds=args.hold_seconds,
            between_command_delay=args.between_command_delay,
        )
        return 0
    raise SystemExit(f"unknown command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    return asyncio.run(run(build_parser().parse_args(argv)))


if __name__ == "__main__":
    raise SystemExit(main())
