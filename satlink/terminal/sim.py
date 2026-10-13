"""Terminal Simulator for SatLink P1.
Simulates N terminals each sending one reading per second over SLP to gateway.
Uses UDP sockets and the SLP protocol defined in common/slp.py.
"""

import asyncio
import struct
import random
import time
import signal
import sys
from collections import defaultdict
from common.slp import pack_slp_packet, PACKET_HEADER_SIZE

# Configuration
TERMINAL_ID_MIN = 1
TERMINAL_ID_MAX = 50
READING_INTERVAL = 1.0  # seconds
DEFAULT_RTT = 0.3  # 300 ms one-way (per README)
DEFAULT_LOSS = 0.02  # 2% packet loss
BUFFER_SIZE = 100  # ring buffer capacity per terminal

# Global state
terminals = {}  # id -> {buffer, last_seq, in_flight, rtt_estimate}
running = True

# Simulated network parameters (can be overridden)
rtt = DEFAULT_RTT
loss_rate = DEFAULT_LOSS

def generate_reading(terminal_id, ts=None):
    """Generate a satellite telemetry reading."""
    if ts is None:
        ts = time.time()
    # Generate realistic-ish sensor values
    battery = random.uniform(20, 100)
    temperature = random.uniform(-40, 85)
    snr = random.uniform(-20, 30)  # Signal-to-noise ratio
    lat = random.uniform(-90, 90)
    lon = random.uniform(-180, 180)
    return {
        "ts": int(ts * 1000),
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "temperature_c": round(temperature, 2),
        "battery_pct": round(battery, 1),
        "snr_db": round(snr, 1)
    }

class Terminal:
    def __init__(self, tid):
        self.id = tid
        self.buffer = []  # ring buffer of readings
        self.last_seq = 0
        self.in_flight = {}  # seq -> (packet_bytes, timestamp)
        self.rtt_estimate = rtt
        self.rtvar = rtt * 0.25
        self.drops_count = 0
        self.sent_count = 0

    def add_reading(self, reading):
        """Add to ring buffer; drop oldest if full."""
        if len(self.buffer) >= BUFFER_SIZE:
            self.drops_count += 1
            self.buffer.pop(0)  # drop oldest
        self.buffer.append(reading)

    def make_slp_packet(self, seq, reading_bytes):
        """Pack reading into SLP DATA packet."""
        return pack_slp_packet(self.id, seq, reading_bytes, is_ack=False)

async def send_loop(terminal, writer_transport):
    """Sender loop: send SLP packets at 1 reading/sec."""
    while running:
        try:
            # Get reading from buffer
            if not terminal.buffer:
                await asyncio.sleep(READING_INTERVAL)
                continue
            reading = terminal.buffer.pop(0)
            reading_bytes = str(reading).encode()
            seq = terminal.last_seq + 1
            packet = terminal.make_slp_packet(seq, reading_bytes)
            # Send to gateway via UDP
            writer_transport.sendto(packet, ("127.0.0.1", 9001))  # gateway port
            # Track in-flight
            terminal.in_flight[seq] = (packet, time.time())
            terminal.last_seq = seq
            terminal.sent_count += 1
            await asyncio.sleep(READING_INTERVAL)
        except Exception as e:
            print(f"[Terminal {terminal.id} send error]: {e}")
            await asyncio.sleep(0.1)

async def rtt_measurement_loop():
    """Simple RTT estimation based on ACK arrival times."""
    global rtt, rtvar
    while running:
        await asyncio.sleep(5)  # update every 5 seconds
        # Simple: just keep static rtt; in production would measure ACK->packet RTT

async def main():
    global running, terminals, rtt, loss_rate
    print("=== SatLink Terminal Simulator ===")
    print(f"RTT: {rtt}s, Packet loss: {loss_rate*100:.0f}%")
    print(f"Terminals: {TERMINAL_ID_MAX}, Buffer: {BUFFER_SIZE} readings each")
    print("Ctrl+C to stop")
    
    # Initialize terminals
    for tid in range(TERMINAL_ID_MIN, TERMINAL_ID_MAX + 1):
        terminals[tid] = Terminal(tid)
    
    # Start UDP listener on port 9000 (terminal->gateway)
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: asyncio.DatagramProtocol(),
        local_addr=("0.0.0.0", 9000)
    )
    print("[Terminal] Listening on port 9000")
    
    # Start sender loops for all terminals
    sender_tasks = []
    for tid, terminal in terminals.items():
        task = asyncio.create_task(send_loop(terminal, transport))
        sender_tasks.append(task)
    
    # Start RTT estimation
    rtt_task = asyncio.create_task(rtt_measurement_loop())
    
    try:
        await asyncio.gather(*sender_tasks, rtt_task)
    except asyncio.CancelledError:
        pass
    finally:
        running = False
        for t in sender_tasks:
            t.cancel()
        print("\n[Terminal] Stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Terminal] Exiting.")