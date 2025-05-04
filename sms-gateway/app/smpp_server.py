import asyncio
import socket
import traceback
from loguru import logger
from .forwarder import forward_message
import struct
import uuid
import datetime

logger.info('[TOP] smpp_server.py loaded')
logger.add("sms_events.log", rotation="500 MB", retention="90 days", level="INFO")

# SMPP Server configuration
LISTEN_PORT = 2875
SYSTEM_ID = 'simsy1'
SYSTEM_PASS = 'n9mb335m'

class SMPPServer:
    def __init__(self):
        self.server_socket = None
        self.running = False
        self.clients = set()

    async def handle_client(self, reader, writer):
        logger.info(f"[ENTER] handle_client")
        """Handle individual client connection"""
        addr = writer.get_extra_info('peername')
        logger.info(f"[START] handle_client for {addr}")
        try:
            logger.info(f"[STEP] About to read bind request from {addr}")
            # Read the bind request
            data = await reader.read(1024)
            logger.info(f"[STEP] Raw data received for bind: {data!r}")
            if not data:
                logger.info(f"[STEP] No data received for bind from {addr}")
                return

            logger.info(f"[STEP] About to parse bind request from {addr}")
            # Parse the bind request (properly extract sequence number)
            seq_num = struct.unpack(">I", data[12:16])[0]
            logger.info(f"[STEP] Parsed sequence number: {seq_num}")
            data_str = data.decode('ascii', errors='ignore')
            logger.info(f"[STEP] Decoded data for bind: {data_str!r}")
            
            if SYSTEM_ID in data_str and SYSTEM_PASS in data_str:
                logger.info(f"[STEP] Client authenticated successfully: {SYSTEM_ID}")
                # Build a proper bind_transceiver_resp PDU
                system_id_bytes = SYSTEM_ID.encode() + b'\x00'
                pdu_length = 16 + len(system_id_bytes)
                response = struct.pack(">IIII", pdu_length, 0x80000009, 0, seq_num) + system_id_bytes
                writer.write(response)
                await writer.drain()

                while self.running:
                    logger.info(f"[STEP] About to read submit_sm from {addr}")
                    # Read message
                    data = await reader.read(1024)
                    logger.info(f"[STEP] Raw data received for submit_sm: {data!r}")
                    if not data:
                        logger.info(f"[STEP] No data received for submit_sm from {addr}")
                        break

                    if len(data) >= 16:
                        # Parse header
                        pdu_length, command_id, command_status, seq_num = struct.unpack(">IIII", data[:16])
                        logger.info(f"[STEP] submit_sm header: len={pdu_length}, cmd_id={command_id}, status={command_status}, seq={seq_num}")

                        if command_id == 0x00000004:  # submit_sm
                            # Parse submit_sm body (see SMPP spec for field order)
                            # Header is 16 bytes, then:
                            # service_type (CString), source_addr_ton (1), source_addr_npi (1), source_addr (CString),
                            # dest_addr_ton (1), dest_addr_npi (1), destination_addr (CString), ... short_message ...
                            try:
                                i = 16
                                # service_type
                                end = data.index(b'\x00', i)
                                service_type = data[i:end].decode(errors='ignore')
                                i = end + 1
                                # source_addr_ton, source_addr_npi
                                source_addr_ton = data[i]
                                source_addr_npi = data[i+1]
                                i += 2
                                # source_addr
                                end = data.index(b'\x00', i)
                                source_addr = data[i:end].decode(errors='ignore')
                                i = end + 1
                                # dest_addr_ton, dest_addr_npi
                                dest_addr_ton = data[i]
                                dest_addr_npi = data[i+1]
                                i += 2
                                # destination_addr
                                end = data.index(b'\x00', i)
                                destination_addr = data[i:end].decode(errors='ignore')
                                i = end + 1
                                # Skip rest to short_message (skip fields: esm_class, protocol_id, priority_flag, schedule_delivery_time, validity_period, registered_delivery, replace_if_present_flag, data_coding, sm_default_msg_id)
                                i += 5 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1
                                sm_length = data[i]
                                i += 1
                                short_message = data[i:i+sm_length].decode(errors='ignore')
                                logger.info(f"[STEP] Parsed submit_sm: from={source_addr}, to={destination_addr}, msg={short_message}")
                                logger.bind(event="submit_sm").info(f"submit_sm received: from={source_addr}, to={destination_addr}, msg={short_message}")
                                # Forward the message
                                msg_obj = type('SMPPMessage', (), {
                                    'destination': destination_addr,
                                    'source': source_addr,
                                    'short_message': short_message,
                                    'time': None,
                                    'log_id': None
                                })
                                await forward_message(msg_obj)
                            except Exception as e:
                                logger.error(f"[STEP] Error parsing submit_sm body: {e}")
                            # Generate a unique message_id
                            message_id = uuid.uuid4().hex[:10]
                            # Build submit_sm_resp
                            resp_length = 16 + len(message_id) + 1
                            resp_command_id = 0x80000004
                            resp_status = 0
                            resp_seq = seq_num
                            resp_message_id = message_id.encode() + b'\x00'
                            response = struct.pack(">IIII", resp_length, resp_command_id, resp_status, resp_seq) + resp_message_id
                            writer.write(response)
                            await writer.drain()
                            logger.info(f"[STEP] Sent submit_sm_resp for seq {seq_num} with message_id {message_id}")
                            # Immediately send deliver_sm with standard receipt
                            now = datetime.datetime.utcnow()
                            date_str = now.strftime('%y%m%d%H%M')
                            dlr_text = f"id:{message_id} sub:001 dlvrd:001 submit date:{date_str} done date:{date_str} stat:DELIVRD err:000 text:"
                            dlr_bytes = dlr_text.encode()
                            # Build deliver_sm PDU
                            # Header: 16 bytes
                            # service_type: null (1 byte)
                            # source_addr_ton, source_addr_npi, source_addr (null)
                            # dest_addr_ton, dest_addr_npi, destination_addr (null)
                            # esm_class, protocol_id, priority_flag, schedule_delivery_time (null), validity_period (null), registered_delivery, replace_if_present_flag, data_coding, sm_default_msg_id, sm_length, short_message
                            deliver_sm_body = (
                                b'\x00' +  # service_type
                                bytes([dest_addr_ton, dest_addr_npi]) + destination_addr.encode() + b'\x00' +
                                bytes([source_addr_ton, source_addr_npi]) + source_addr.encode() + b'\x00' +
                                b'\x04' +  # esm_class: 0x04 = delivery receipt
                                b'\x00' +  # protocol_id
                                b'\x00' +  # priority_flag
                                b'\x00' +  # schedule_delivery_time (null)
                                b'\x00' +  # validity_period (null)
                                b'\x00' +  # registered_delivery
                                b'\x00' +  # replace_if_present_flag
                                b'\x00' +  # data_coding
                                b'\x00' +  # sm_default_msg_id
                                bytes([len(dlr_bytes)]) + dlr_bytes
                            )
                            deliver_sm_length = 16 + len(deliver_sm_body)
                            deliver_sm_header = struct.pack(">IIII", deliver_sm_length, 0x00000005, 0, seq_num)
                            deliver_sm_pdu = deliver_sm_header + deliver_sm_body
                            writer.write(deliver_sm_pdu)
                            await writer.drain()
                            logger.info(f"[STEP] Sent deliver_sm receipt for message_id {message_id}")
                            logger.bind(event="deliver_sm").info(f"deliver_sm sent: message_id={message_id}, to={source_addr}, from={destination_addr}, text={dlr_text}")
                        elif command_id == 0x00000015:  # enquire_link
                            # Respond to enquire_link
                            resp_length = 16
                            resp_command_id = 0x80000015
                            resp_status = 0
                            resp_seq = seq_num
                            response = struct.pack(">IIII", resp_length, resp_command_id, resp_status, resp_seq)
                            writer.write(response)
                            await writer.drain()
                            logger.info(f"[STEP] Sent enquire_link_resp for seq {seq_num}")
                        elif command_id == 0x00000006:  # unbind
                            # Respond to unbind
                            resp_length = 16
                            resp_command_id = 0x80000006
                            resp_status = 0
                            resp_seq = seq_num
                            response = struct.pack(">IIII", resp_length, resp_command_id, resp_status, resp_seq)
                            writer.write(response)
                            await writer.drain()
                            logger.info(f"[STEP] Sent unbind_resp for seq {seq_num}")
                            break
                        else:
                            logger.warning(f"[STEP] Received non-submit_sm PDU: command_id={command_id}")
                    else:
                        logger.warning(f"[STEP] Received too-short PDU: len={len(data)}")

            else:
                logger.warning(f"[STEP] Authentication failed for system_id: {SYSTEM_ID}")
                # Send error response
                response = b'\x00\x00\x00\x10\x80\x00\x00\x02\x00\x00\x00\x0E\x00\x00\x00\x01'
                writer.write(response)
                await writer.drain()

        except Exception as e:
            logger.error(f"[EXCEPTION] Error handling client {addr}: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"[END] Connection closed from {addr}")

    async def start(self):
        logger.info('[ENTER] SMPPServer.start()')
        """Start the SMPP server"""
        server = await asyncio.start_server(
            self.handle_client,
            '0.0.0.0',
            LISTEN_PORT
        )
        
        self.running = True
        logger.info(f"SMPP Server listening on port {LISTEN_PORT}")
        
        async with server:
            await server.serve_forever()

    def stop(self):
        """Stop the SMPP server"""
        self.running = False

async def run_server():
    """Run the SMPP server"""
    server = SMPPServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down SMPP server...")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
    finally:
        server.stop()

def main():
    """Entry point for the SMPP server"""
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main() 