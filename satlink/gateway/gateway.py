"""SatLink Gateway.
Receives SLP packets from terminals, validates CRC and deduplicates, then publishes to Kafka.
Sends ACKs back to terminals.
"""

import asyncio
import struct
import zlib
from asyncio import DatagramProtocol
from collections import defaultdict
from common.slp import PACKET_HEADER_SIZE

from confluent_kafka import Producer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "telemetry.raw"
KAFKA_ACK_TIMEOUT = 1000  # ms

# Global state
received_windows = defaultdict(int)  # terminal_id -> next expected seq
received_buffers = defaultdict(list)  # terminal_id -> list of unprocessed packets
sack_sent = defaultdict(set)  # terminal_id -> set of ACKed seqs
dedupe_set = set()  # (terminal_id, seq) for deduplication

class GatewayProtocol(DatagramProtocol):
    def __init__(self, kafka_producer):
        self.producer = kafka_producer
        self.outbound_queue = asyncio.Queue()

    def datagram_received(self, data, addr):
        """Process incoming UDP packets."""
        try:
            header = data[:PACKET_HEADER_SIZE]
            payload_len = struct.unpack("!H", header[2:4])[0]
            packet_type = header[0] & 0xF  # low nibble = type
            
            if packet_type == 1:  # SLP_DATA
                # Extract fields from packet (simplified unpack)
                # Format: !BBHIIIII (24 bytes)
                if len(data) < PACKET_HEADER_SIZE + payload_len:
                    return
                unpacked = struct.unpack("!BBHIIIII", header)
                terminal_id = unpacked[4]
                seq = unpacked[5]
                ack = unpacked[6]
                sack_bitmap = unpacked[7]
                payload = data[PACKET_HEADER_SIZE:PACKET_HEADER_SIZE+payload_len]
                
                # CRC validation
                crc_calc = zlib.crc32(data[:PACKET_HEADER_SIZE-4] + payload) & 0xffffffff
                crc_stored = unpacked[7]  # Actually CRC is last field
                if crc_calc != crc_stored:
                    print(f"[Gateway] Bad CRC from terminal {terminal_id}, seq {seq}")
                    return
                
                # Deduplication
                key = (terminal_id, seq)
                if key in dedupe_set:
                    print(f"[Gateway] Duplicate packet {terminal_id}:{seq}")
                    return
                dedupe_set.add(key)
                
                # Update receive window
                expected_next = received_windows.get(terminal_id, 0)
                if seq != expected_next:
                    # Out-of-order - buffer for later
                    received_buffers[terminal_id].append((seq, payload, addr))
                    received_buffers[terminal_id].sort(key=lambda x: x[0])
                    # Print ordering info
                    print(f"[Gateway] Terminal {terminal_id} out-of-order: expected {expected_next}, got {seq}")
                else:
                    # Expected packet - process immediately
                    process_packet(terminal_id, seq, payload, addr)
                    expected_next += 1
                    received_windows[terminal_id] = expected_next
                    # Try to deliver any buffered packets
                    deliver_buffered_packets(terminal_id)

            elif packet_type == 2:  # SLP_ACK
                # Handle ACK from terminal
                print(f"[Gateway] ACK received from terminal {addr[0]}")
                
        except Exception as e:
            print(f"[Gateway] Error processing packet: {e}")

    def send_ack(self, terminal_id, terminal_addr, seq, ack, sack_bitmap):
        """Send ACK back to terminal."""
        packet = struct.pack("!BBHIIIII", 
                              0x12,  # version 1 + ACK type (2)
                              0,  # flags
                              0,  # payload len
                              terminal_id, seq, ack, sack_bitmap, 0)  # CRC zeroed
        crc = zlib.crc32(packet) & 0xffffffff
        packet = struct.pack("!BBHIIIII", 
                              0x12, 0, 0, terminal_id, seq, ack, sack_bitmap, crc)
        self.transport.write(packet, terminal_addr)

    def delivery_success_callback(self, err, msg):
        """Callback for Kafka producer delivery."""
        if err:
            print(f"[Gateway] Kafka delivery failed: {err}")
        else:
            print(f"[Gateway] Published to Kafka partition {msg.partition()}, offset {msg.offset()}")

def process_packet(terminal_id, seq, payload, addr):
    """Process a received telemetry packet."""
    try:
        # Parse JSON payload
        import json
        reading = json.loads(payload.decode())
        print(f"[Gateway] Received telemetry: terminal {terminal_id}, seq {seq}, lat {reading.get('lat')}, lon {reading.get('lon')}")
        
        # Publish to Kafka
        import json as json_module
        producer = kafka_producer
        producer.produce(
            KAFKA_TOPIC,
            key=str(terminal_id).encode(),
            value=json_module.dumps(reading).encode(),
            callback=delivery_success_callback
        )
        producer.flush()
        
        # Send ACK back
        send_ack(terminal_id, addr, seq, received_windows.get(terminal_id, 0), 0)
        
    except Exception as e:
        print(f"[Gateway] Error processing packet {terminal_id}:{seq}: {e}")

def deliver_buffered_packets(terminal_id):
    """Deliver buffered out-of-order packets."""
    buffers = received_buffers.get(terminal_id, [])
    if not buffers:
        return
    
    expected_next = received_windows.get(terminal_id, 0)
    delivered = False
    
    while buffers:
        seq, payload, addr = buffers[0]
        if seq == expected_next:
            # Deliver this packet
            buffers.pop(0)
            delivered = True
            process_packet(terminal_id, seq, payload, addr)
            expected_next += 1
            received_windows[terminal_id] = expected_next
        else:
            break

# Initialize Kafka producer
kafka_producer = Producer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'acks': 'all',
    'delivery.timeout.ms': KAFKA_ACK_TIMEOUT,
})

async def main():
    print("=== SatLink Gateway ===")
    print(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS}, Topic: {KAFKA_TOPIC}")
    print("[Gateway] Listening on UDP 9001 (gateway side)")
    
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: GatewayProtocol(kafka_producer),
        local_addr=("0.0.0.0", 9001)
    )
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[Gateway] Exiting.")
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())