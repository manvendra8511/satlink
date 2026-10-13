# SatLink Protocol (SLP) v1
# Header format: "!BBHIIIII" (network byte order)
# Version/Type: 1 byte (high nibble = version 1, low nibble = type)
# Flags: 1 byte
# Payload length: 2 bytes
# Terminal ID: 4 bytes (uint32)
# Sequence number: 4 bytes (uint32)
# Cumulative ACK: 4 bytes
# SACK bitmap: 4 bytes
# CRC32 (zlib): 4 bytes

PACKET_FORMAT = "!BBHIIIII"
PACKET_HEADER_SIZE = 24

SLP_DATA = 1
SLP_ACK = 2
VERSION_1 = 1

import struct
import zlib

def pack_slp_packet(terminal_id, seq, payload, is_ack=False, flags=0, ack=0, sack_bitmap=0):
    packet_type = SLP_ACK if is_ack else SLP_DATA
    version_nibble = VERSION_1 << 4
    type_byte = version_nibble | packet_type
    payload_bytes = payload.encode() if isinstance(payload, str) else payload
    payload_len = len(payload_bytes)
    header = struct.pack(PACKET_FORMAT, type_byte, flags, payload_len,
                         terminal_id, seq, ack, sack_bitmap, 0)  # CRC zeroed for calc
    crc = zlib.crc32(header + payload_bytes) & 0xffffffff
    header_with_crc = struct.pack(PACKET_FORMAT, type_byte, flags, payload_len,
                                  terminal_id, seq, ack, sack_bitmap, crc)
    return header_with_crc + payload_bytes

def unpack_slp_packet(data):
    if len(data) < PACKET_HEADER_SIZE:
        raise ValueError("Packet too short")
    header = data[:PACKET_HEADER_SIZE]
    payload = data[PACKET_HEADER_SIZE:]
    type_byte, flags, payload_len, terminal_id, seq, ack, sack_bitmap, crc = struct.unpack(PACKET_FORMAT, header)
    version = (type_byte >> 4) & 0xf
    packet_type = type_byte & 0xf
    computed_crc = zlib.crc32(data[:PACKET_HEADER_SIZE-4] + payload) & 0xffffffff
    if computed_crc != crc:
        raise ValueError(f"CRC error: expected {crc:08x}, got {computed_crc:08x}")
    return {
        "version": version,
        "type": packet_type,
        "flags": flags,
        "payload_len": payload_len,
        "terminal_id": terminal_id,
        "seq": seq,
        "ack": ack,
        "sack_bitmap": sack_bitmap,
        "payload": payload.decode() if payload else ""
    }
