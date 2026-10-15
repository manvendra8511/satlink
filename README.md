# SatLink System Overview

## Project Description
SatLink is a Satellite IoT Telemetry Platform designed to move sensor data reliably over slow, lossy satellite links using a custom UDP protocol (SLP). The system simulates terminals sending telemetry data through a network emulator that adds realistic satellite link characteristics (delay, jitter, packet loss), then processes the data through a gateway into Kafka for stream processing and storage.

## System Architecture

### High-Level Flow
```
Terminal Simulator → Satellite Emulator → Gateway → Kafka → Writer Service 
                                                  ↓
                                         PostgreSQL (History) 
                                                  ↓
                                         Redis (Latest State + Pub/Sub)
                                                  ↓
                                         FastAPI → WebSocket → Dashboard
```

### Component Details

1. **Terminal Simulator** (`terminal/sim.py`)
   - Simulates N terminals (ship, aircraft, sensor) each generating one reading per second
   - Creates realistic sensor data: temperature, battery percentage, SNR, GPS coordinates
   - Implements SLP client with sliding window, in-flight packet tracking, and adaptive RTO
   - Sends SLP DATA packets to gateway via UDP port 9001

2. **Satellite Emulator** (`emulator/emulator.py`)
   - UDP relay that applies configurable network impairments:
     - One-way delay (GEO: ~300ms, LEO: ~20ms profiles)
     - Random packet loss (1-5% typical for satellite)
     - Optional jitter and reordering
   - Profiles: GEO, LEO, RAIN_FADE, BLACKOUT (runtime-switchable)

3. **Gateway** (`gateway/gateway.py`)
   - UDP server (asyncio) that:
     - Validates incoming SLP packets (CRC32 check)
     - Performs deduplication using (terminal_id, seq) tracking
     - Manages receive window and buffers out-of-order packets
     - Publishes validated telemetry to Kafka topic `telemetry.raw`
     - Sends ACK packets back to terminals only after Kafka delivery confirms
   - Key reliability principle: ACK only after Kafka delivery ensures no acknowledged packet is lost

4. **Infrastructure Services** (`docker-compose.yml`)
   - **Apache Kafka**: Message queuing system (topic: `telemetry.raw`, 3 partitions)
   - **Redis**: 
     - Latest terminal state per terminal (cache-aside with 60s TTL)
     - Pub/sub channel for live alert fan-out to WebSocket clients
   - **PostgreSQL**: Persistent storage for historical telemetry and alerts

5. **Writer Service** (`services/writer/writer.py`)
   - Kafka consumer group `writer`
   - Batch processing: flush every 500 rows or 200ms
   - Idempotent storage: Uses `INSERT ... ON CONFLICT DO NOTHING` to handle Kafka's at-least-once delivery
   - State management: Updates Redis cache, persists history to PostgreSQL
   - Alert generation: Triggers on low battery (<20%) or poor SNR → stored in Postgres + pushed via Redis pub/sub

6. **API Service** (`services/api/main.py`)
   - Built with FastAPI
   - REST endpoints: 
     - `/health`
     - `/terminals` (list all terminals)
     - `/terminals/{id}/state` (current state)
     - `/terminals/{id}/telemetry` (historical data)
     - `/alerts`
   - WebSocket endpoint: `/ws/live` for real-time updates via Redis pub/sub

7. **Dashboard** 
   - `frontend/index.html`: Theory + problem statement page
   - `dashboard/dashboard.html`: Live status + feed dashboard
   - Displays: terminal table, live charts, alert feed, endpoint reference

## Technology Stack

### Core Innovation
- **SLP (SatLink Protocol)**: Custom reliable transport over UDP implementing:
  - Selective repeat ARQ (only missing packets retransmitted)
  - Sliding window sized from bandwidth-delay product
  - Adaptive RTO with Karn's rule and exponential backoff
  - SACK bitmap for precise retransmission
  - CRC32 error detection

### Programming Language
- **Python 3.10+**: Used throughout all components

### Infrastructure & Services
- **Apache Kafka**: Message queuing for decoupling producers and consumers
- **Redis**: In-memory data store for latest state and pub/sub
- **PostgreSQL**: Persistent storage for historical data

### Web/API Layer
- **FastAPI**: High-performance Python web framework for REST API
- **WebSocket**: Real-time bidirectional communication for live updates
- **HTML/CSS/JavaScript**: Frontend dashboard

### Networking
- **UDP Sockets**: All inter-component communication uses UDP:
  - Terminal → Satellite Emulator → Gateway (SLP DATA packets)
  - Gateway → Terminal (SLP ACK packets)
  - Gateway → Kafka (telemetry publishing)
  - Writer service consumes from Kafka

### DevOps & Orchestration
- **Docker Compose**: Orchestrates infrastructure services (Kafka, Redis, PostgreSQL)
- **Healthchecks**: Configured for all services to ensure proper startup

### Testing & Quality
- **pytest**: Testing framework

## Key Design Principles

1. **Reliability over Satellite Link**: Gateways only send ACKs after Kafka delivery confirmation, ensuring acknowledged packets are never lost
2. **Idempotent Storage**: Writer service uses `INSERT ... ON CONFLICT DO NOTHING` to safely handle Kafka's at-least-once delivery guarantee
3. **Caching Layer**: Redis provides fast access to latest state (60s TTL), with PostgreSQL as persistent backup
4. **Separation of Concerns**: Each component has a single responsibility (simulation, transport, ingestion, storage, API)
5. **Real-time Updates**: Alerts and latest state pushed via Redis pub/sub to WebSocket clients

## Satellite Link Challenges Addressed

SatLink specifically addresses the challenges of GEO satellite communication (~36,000 km altitude):
- **High Latency**: ~600ms round-trip time (RTT)
- **Packet Loss**: 1-5% typical for satellite radio links
- **TCP Inapplicability**: TCP performs poorly here because:
  - Throughput capped at `window / RTT` (e.g., 64KB window at 600ms RTT = ~0.87 Mbps regardless of link speed)
  - TCP treats random loss as congestion and halves sending rate (wrong assumption for satellite links)
  - Result: slow, unstable telemetry

By implementing a custom UDP-based protocol with application-layer reliability mechanisms (selective repeat, SACK, adaptive timers) and only acknowledging after persistent storage confirmation, SatLink provides reliable telemetry transport optimized for satellite link characteristics.

## Getting Started

### Prerequisites
- Docker + Docker Compose
- Python 3.10+
- Node.js (optional, for npm-based UI build later)
- `git`

### Installation
```bash
cd satlink
pip install -r requirements.txt  # if present, else: pip install flask fastapi uvicorn redis psycopg2-binary confluent-kafka
```

### Running the System
1. Start infrastructure:
   ```bash
   docker compose up -d
   ```

2. Verify services are healthy:
   ```bash
   docker compose ps
   ```

3. Initialize databases (first run):
   - PostgreSQL, Redis, and Kafka are ready once containers are healthy
   - Writer service creates its tables on first run

4. Start services in separate terminals:
   ```bash
   # Terminal 1 — terminal simulator (generates telemetry)
   python terminal/sim.py

   # Terminal 2 — satellite emulator (delays + drops)
   python emulator/emulator.py

   # Terminal 3 — gateway (receives SLP, publishes Kafka)
   python gateway/gateway.py

   # Terminal 4 — writer (consumes Kafka → DB + cache + alerts)
   python services/writer/writer.py

   # Terminal 5 — API server
   python services/api/main.py
   ```

5. Access the dashboard:
   - Homepage: `http://localhost:8000/index.html` (theory + problem statement)
   - Dashboard: `http://localhost:8000/dashboard/dashboard.html` (live status + feed)
   - API: `http://localhost:3000/health`

### Stopping Everything
```bash
docker compose down
kill $(lsof -ti:3000) 2>/dev/null
kill $(lsof -ti:8000) 2>/dev/null
```

## Project Structure
```
satlink/
├── common/slp.py              # packet pack/unpack, CRC32
├── terminal/sim.py            # terminal simulator + SLP sender
├── emulator/emulator.py       # delay/loss UDP relay
├── gateway/gateway.py         # SLP receiver + Kafka producer
├── services/
│   ├── writer/writer.py       # Kafka consumer → Postgres + Redis + alerts
│   └── api/main.py            # FastAPI REST + WebSocket
├── frontend/index.html        # homepage (theory + problem statement)
├── dashboard/dashboard.html   # live dashboard
├── docs/                      # architecture docs
├── tests/                     # pytest
├── docker-compose.yml         # Kafka + Redis + Postgres
└── README.md
```

## Design Notes

- **Reliability over satellite link**: ACK only after Kafka delivery confirms (so an acknowledged packet is never lost)
- **Idempotent storage**: Consumer writes use `ON CONFLICT DO NOTHING`; duplicates from Kafka at-least-once are handled silently
- **Caching**: Latest terminal state in Redis (60s TTL); history in Postgres
- **Secrets**: Never commit `.env`; use `docker-compose.yml` env or runtime env vars
- **Alerts**: Battery < 20% or SNR below threshold → stored in Postgres and pushed via Redis pub/sub

## Future Work (Prototype 2)

- C++ terminal agent, Java Spring Boot consumer
- Encryption (X25519 + AES-GCM, replay protection)
- TimescaleDB, Kubernetes, JWT/RBAC
- Orbit/TLE service (pass prediction, scheduling, routing)
- ML anomaly detection, React dashboard

## License

MIT.
