"""SatLink Writer Service.
Consumes telemetry from Kafka, writes to PostgreSQL batch, updates Redis cache,
and triggers alerts based on rules.
"""

import asyncio
import json
import time
from datetime import datetime
from redis import asyncio as aioredis
from confluent_kafka import Consumer, KafkaError
import psycopg2
from psycopg2.extras import execute_values

# Configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_GROUP_ID = "writer"
KAFKA_TOPIC = "telemetry.raw"
BATCH_SIZE = 500
BATCH_INTERVAL = 0.2  # seconds

# Redis configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# PostgreSQL configuration
PG_CONN_INFO = "host=localhost dbname=satlink user=satlink password=satlink_pass"

# Alert thresholds
BATTERY_LOW_THRESHOLD = 20
SNR_LOW_THRESHOLD = -10

async def main():
    print("=== SatLink Writer Service ===")
    print(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS}, Topic: {KAFKA_TOPIC}")
    print(f"Batch: {BATCH_SIZE} rows or {BATCH_INTERVAL}s")
    
    # Initialize Redis
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    
    # Initialize PostgreSQL connection
    pg_conn = psycopg2.connect(PG_CONN_INFO)
    pg_cursor = pg_conn.cursor()
    
    # Create tables if not exists
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            terminal_id INTEGER,
            ts TIMESTAMPTZ,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            temperature_c DOUBLE PRECISION,
            battery_pct DOUBLE PRECISION,
            snr_db DOUBLE PRECISION,
            rtt_ms DOUBLE PRECISION,
            PRIMARY KEY (terminal_id, ts)
        )
    """)
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id SERIAL PRIMARY KEY,
            terminal_id INTEGER,
            kind TEXT,
            severity TEXT,
            message TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            acknowledged BOOLEAN DEFAULT FALSE
        )
    """)
    pg_conn.commit()
    
    # Initialize Kafka consumer
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_GROUP_ID,
        'auto.offset.reset': 'latest'
    }
    consumer = Consumer(conf)
    consumer.subscribe([KAFKA_TOPIC])
    
    print("[Writer] Connected to Kafka, Redis, PostgreSQL")
    print("[Writer] Listening for telemetry...")
    
    batch = []
    pending_alerts = []
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"[Writer] Kafka error: {msg.error()}")
                continue
            
            # Parse message
            reading = json.loads(msg.value().decode())
            terminal_id = reading['ts'] % 1000000  # derive terminal_id from ts if not present
            
            # Add to batch
            batch.append((
                terminal_id,
                datetime.fromtimestamp(reading['ts'] / 1000.0),
                reading.get('lat', 0),
                reading.get('lon', 0),
                reading.get('temperature_c', 0),
                reading.get('battery_pct', 0),
                reading.get('snr_db', 0),
                reading.get('rtt_ms', 0)
            ))
            
            # Check for alerts
            battery = reading.get('battery_pct', 100)
            snr = reading.get('snr_db', 0)
            if battery < BATTERY_LOW_THRESHOLD:
                pending_alerts.append({
                    'terminal_id': terminal_id,
                    'kind': 'battery_low',
                    'severity': 'WARNING',
                    'message': f"Battery at {battery:.1f}%"
                })
            if snr < SNR_LOW_THRESHOLD:
                pending_alerts.append({
                    'terminal_id': terminal_id,
                    'kind': 'snr_low',
                    'severity': 'WARNING',
                    'message': f"SNR at {snr:.1f} dB"
                })
            
            # Flush batch if full or after interval
            if len(batch) >= BATCH_SIZE:
                flush_batch(pg_conn, batch, redis, pending_alerts)
                batch = []
                pending_alerts = []
            elif batch:
                # Wait for interval
                await asyncio.sleep(BATCH_INTERVAL)
                if batch:
                    flush_batch(pg_conn, batch, redis, pending_alerts)
                    batch = []
                    pending_alerts = []
                continue
            
            # Commit offset
            consumer.commit(asynchronous=False)
            
    except KeyboardInterrupt:
        print("\n[Writer] Shutting down...")
    finally:
        if batch:
            flush_batch(pg_conn, batch, redis, pending_alerts)
        consumer.close()
        pg_conn.close()
        await redis.close()

def flush_batch(pg_conn, batch, redis, alerts):
    """Write batch to PostgreSQL and update Redis."""
    if not batch:
        return
    
    print(f"[Writer] Flushing {len(batch)} rows to PostgreSQL")
    
    cursor = pg_conn.cursor()
    try:
        execute_values(
            cursor,
            "INSERT INTO telemetry (terminal_id, ts, lat, lon, temperature_c, battery_pct, snr_db, rtt_ms) VALUES %s ON CONFLICT DO NOTHING",
            batch
        )
        pg_conn.commit()
        
        # Update Redis
        for row in batch:
            terminal_id = row[0]
            state = {
                'ts': row[1].isoformat(),
                'lat': row[2],
                'lon': row[3],
                'temperature_c': row[4],
                'battery_pct': row[5],
                'snr_db': row[6],
                'rtt_ms': row[7]
            }
            redis.set(f"terminal:{terminal_id}:state", json.dumps(state), ex=60)
        
        print(f"[Writer] Updated Redis state for {len(batch)} terminals")
        
        # Log alerts
        for alert in alerts:
            cursor.execute(
                "INSERT INTO alerts (terminal_id, kind, severity, message, created_at) VALUES (%s, %s, %s, %s, NOW())",
                (alert['terminal_id'], alert['kind'], alert['severity'], alert['message'])
            )
            pg_conn.commit()
            print(f"[Writer] ALERT: {alert['kind']} on terminal {alert['terminal_id']}")
            
    except Exception as e:
        print(f"[Writer] Error flushing batch: {e}")
        pg_conn.rollback()
    finally:
        cursor.close()

if __name__ == "__main__":
    asyncio.run(main())