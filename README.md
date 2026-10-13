Here it is — the full SatLink README:

---

SatLink — Satellite IoT Telemetry Platform

 Reliable satellite IoT telemetry over slow, lossy links (UDP/SLP, Kafka, Redis, PostgreSQL, FastAPI).

Table of Contents

- What it is
- The Problem
- The Solution
- Architecture
- SLP Protocol
- Components
- Getting Started
- Run End-to-End
- Project Structure
- Design Notes
- Future Work
- License

What it is

SatLink moves sensor data reliably over a slow, lossy satellite-like link using a custom UDP protocol (SLP), then streams it through Kafka into a database, a cache, and a live dashboard. Built while learning every concept it uses: UDP, reliable transport, Kafka, Redis, SQL, REST.

The Problem

A GEO satellite is ~36,000 km up. Round-trip time (RTT) is ~600 ms and radio loss is 1–5%. TCP performs badly here:

- Throughput is capped at window / RTT. A 64 KB window at 600 ms gives ~0.87 Mbps, regardless of link speed.
- TCP treats random loss as congestion and halves its sending rate — the wrong assumption for satellite links.
- Result: slow, unstable telemetry.

The Solution

SLP (SatLink Protocol) — a custom reliable transport over UDP with:

- Selective repeat (only missing packets retransmitted)
- Sliding window sized from bandwidth-delay product
- Adaptive RTO (SRTT/RTTVAR estimator, Karn's rule, exponential backoff capped)
- SACK bitmap for precise retransmission
- CRC32 over header + payload

Architecture

Terminal Simulator        Satellite Emulator        Gateway
(Python, N terminals)  --UDP-->  (UDP relay)  --UDP-->  (asyncio)
 SLP DATA packets        delay + jitter + loss       CRC check, dedupe,
 <------------------------ ACK / SACK <------------   ACK, publish
                                                            |
                                                            v
                                                  Kafka topic: telemetry.raw
                                                  (key = terminal_id)
                                                            |
                                                            v
                                                   Writer / Consumer (Python)
                                                   batch insert, cache, alerts
                                                       |            |           |
                                                       v            v           v
                                                   PostgreSQL   Redis      Redis pub/sub
                                                   (history)   (latest)    (alerts/live)
                                                       \           |          /
                                                        \          |         /
                                                         v          v         v
                                                       FastAPI  (REST + WebSocket)
                                                                   |
                                                                   v
                                                          Dashboard (HTML + JS)


Everything except the Python services runs from one docker-compose.yml (Kafka, Redis, PostgreSQL).

SLP Protocol

Reliable transport over UDP. Header is 24 bytes, network byte order (struct format !BBHIIIII):

Version + Type
• Size: 1 B
• Meaning: high nibble = version (1), low nibble = type (1 = DATA, 2 = ACK)

Flags
• Size: 1 B
• Meaning: reserved (RETRANSMIT, FIN later)

Payload length
• Size: 2 B
• Meaning: bytes after the header

Terminal ID
• Size: 4 B
• Meaning: identifies the terminal

Sequence number
• Size: 4 B
• Meaning: per-terminal packet counter, starts at 0

Cumulative ACK
• Size: 4 B (1/3)