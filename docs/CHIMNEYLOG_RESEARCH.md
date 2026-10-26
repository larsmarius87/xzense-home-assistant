# ChimneyLog / ErrLog — v4.10_RC2 research, 2026-10-21

This note records directly verifiable binary/string evidence. It does **not** claim a working BLE log-download request, a decoded log record schema, or verified burn-count/operation-hours data.

## Binary evidence

Source: official Xzense 5.0.5 XAPK uploaded by the user. Its bundled `assets/flutter_assets/assets/fw/exodraft.gbl` is **455,488 bytes**, SHA-256 `42fafc7b51f8811f48c80a4290a83fd7823c747c12855ba3884bdf17b74b2bd6` and reports `v4.10_RC2`.

The following are offsets in `exodraft.gbl` (file offsets, **not code addresses**):

| Offset (hex) | String / significance |
|---|---|
| `0x56231` | `ChimneyLog` filename |
| `0x5623C` | `ErrLog` filename |
| `0x5631F` | `BLE> FileTransfer %s (Size: 0x%X)!` |
| `0x5FE29` | `ChimneyLog> %04X(%s): Fan: %u, Temps: %d, %d, %d, hPa: %d, %d` |
| `0x604D7` | `--- Chimney Log (%u) (Last hour) ---` |
| `0x603F0` | `--- Error Log (%u) (Last 15) ---` |
| `0x61442` | `BleLog> Sending %s of size 0x%lX (Blocks: %d at %d)` |
| `0x622D6` | `FileTransfer> Preparing slot for %s of size 0x%lX (BlockSize: %u)` |
| `0x625EE` | `FileTransfer> Unknown FT Request (%02X)` |

These strings establish that the controller contains named log files, logs chimney samples comprising fan, temperature(s), pressure, and other values, and has file-transfer block/sequence handling. They do not establish the exact bytes needed to issue a safe read request.

The `config.arm64_v8a.apk` split contains Flutter `libapp.so` (5,637,040 bytes). Plain strings there include `ChimneyLog`, `FileTransferType.log`, `burnCount`, `operationTime`, and an API endpoint ending `/api/v2/chimneyLogEntry/`. These suggest an application-side log workflow and data fields but do not prove that the BLE reply is immediately parseable as JSON or that the cloud endpoint is needed for local retrieval. No cloud endpoint was called.

## Confirmed BLE context

The current Xzense integration has authenticated CONNECT/ACK, STATUS and GLOBAL read/write. Firmware and protocol notes identify `0x0C` as `FILE_TRANSFER`; this packet family also handles **firmware upgrades**, not only log retrieval. It is **not safe to probe unknown 0x0C subcommands as though they were read-only**.

## Next safe investigation

1. Recover the Flutter app's **outbound log request** bytes or identify the firmware's log-only `FileTransferRequest` / `XzFileType` enum from static code.
2. Confirm filename / type selector, request type, block size, sequence index, completion and ACK/NACK behavior without calling any firmware-write or APPLY operation.
3. Add a **passive packet capture** or a dedicated **strictly read-only** command only after the opcode is verified.
4. Compare log-record samples with the user-visible Xzense history to map record time, temperature, pressure, fan speed, burn count and operation time.

Unresolved: log-record binary layout, units, timestamps, request selectors, safe maximum length, and whether total burn count and operation time are directly stored or derived.