"""Satellite Emulator for SatLink P1.
UDP relay with configurable one-way delay, jitter, and packet loss.
Implements GEO profile (300 ms) as baseline.
"""

import asyncio
import random
import time
from asyncio import DatagramProtocol
from common.slp import unpack_slp_packet

# Configuration
# ports: terminal side 9000, gateway side 9001
LATENCY_MS = 300  # one-way latency in milliseconds
JITTER_MS = 10    # jitter variation
LOSS_RATE = 0.02  # 2% packet loss

class SatelliteEmulatorProtocol(DatagramProtocol):
    def __init__(self, direction_name, inbound_queue, outbound_queue, latency_ms, jitter_ms, loss_rate):
        self.direction = direction_name
        self.inbound = inbound_queue
        self.outbound = outbound_queue
        self.latency_ms = latency_ms
        self.jitter_ms = jitter_ms
        self.loss_rate = loss_rate

    def datagram_received(self, data, addr):
        """Pass incoming packet to outbound queue with simulated delay + jitter + loss."""
        # Random delay + jitter
        total_delay = LATENCY_MS + random.uniform(-JITTER_MS, JITTER_MS)
        if total_delay < 0:
            total_delay = 0
        # Random loss
        if random.random() < LOSS_RATE:
            return
        # Schedule delayed delivery
        asyncio.get_event_loop().call_later(total_delay / 1000.0, self._deliver, data, addr)

    def _deliver(self, data, addr):
        self.outbound.put((data, addr))

class SatelliteEmulator:
    def __init__(self, terminal_listener, gateway_listener, latency_ms=300, jitter_ms=10, loss_rate=0.02):
        self.terminal_listener = terminal_listener  # Socket for terminal -> gateway
        self.gateway_listener = gateway_listener    # Socket for gateway -> terminal
        self.latency_ms = latency_ms
        self.jitter_ms = jitter_ms
        self.loss_rate = loss_rate

    async def run(self):
        """Start UDP sockets for both directions."""
        loop = asyncio.get_running_loop()

        # Terminal -> Gateway direction
        self.terminal_listener = await loop.create_datagram_endpoint(
            lambda: SatelliteEmulatorProtocol("t2g", None, None, self.latency_ms, self.jitter_ms, self.loss_rate),
            local_addr=("0.0.0.0", 9000)
        )
        # Gateway -> Terminal direction
        self.gateway_listener = await loop.create_datagram_endpoint(
            lambda: SatelliteEmulatorProtocol("g2t", None, None, self.latency_ms, self.jitter_ms, self.loss_rate),
            local_addr=("0.0.0.0", 9001)
        )
        print(f"[Emulator] Listening terminal side 9000, gateway side 9001")
        print(f"[Emulator] LATENCY={self.latency_ms}ms, LOSS={self.loss_rate*100:.0f}%")

        return self.terminal_listener, self.gateway_listener

    async def stop(self):
        """Stop UDP sockets."""
        self.terminal_listener[0].close()
        self.gateway_listener[0].close()
        print("[Emulator] Stopped")

async def main():
    print("=== SatLink Satellite Emulator ===")
    emulator = SatelliteEmulator()
    try:
        await emulator.run()
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[Emulator] Exiting.")
        await emulator.stop()

if __name__ == "__main__":
    asyncio.run(main())