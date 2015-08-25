import asyncio
import codecs
import logging
import struct

from two1.gen import swirl_pb2

decode_hex = codecs.getdecoder("hex_codec")


class SwirlMessageFactory():
    @staticmethod
    def _encode_object(obj):
        msg_str = obj.SerializeToString()
        header = struct.pack('>H', len(msg_str))
        return header + msg_str

    @staticmethod
    def create_auth_request(version, username, worker_uuid, hw_version):
        req = swirl_pb2.SwirlClientMessage()
        req.auth_request.version = version
        req.auth_request.username = username
        req.auth_request.hw_version = hw_version
        req.auth_request.worker_uuid = worker_uuid
        return SwirlMessageFactory._encode_object(req)

    @staticmethod
    def create_submit_request(message_id, work_id, enonce2, otime, nonce):
        req = swirl_pb2.SwirlClientMessage()
        req.submit_request.message_id = message_id
        req.submit_request.work_id = work_id
        req.submit_request.enonce2 = enonce2
        req.submit_request.otime = otime
        req.submit_request.nonce = nonce
        return SwirlMessageFactory._encode_object(req)

    @staticmethod
    @asyncio.coroutine
    def read_object_async(reader):
        head_buffer = yield from reader.read(2)
        if len(head_buffer) == 0:
            raise ConnectionError

        size, = struct.unpack('>H', head_buffer)
        pkt = yield from _read_exact_async(size, reader)
        client_message = swirl_pb2.SwirlServerMessage()
        client_message.ParseFromString(pkt)
        # take a look at the protobuf file to see what this means.
        message_type = client_message.WhichOneof("servermessages")
        if message_type is None:
            logger = logging.getLogger(__name__)
            logger.warn("Invalid or Empty Message Sent to Client")
            raise EncodingError("Invalid Client Message Received")
        return getattr(client_message, message_type)

    @staticmethod
    def read_object(content):
        head_buffer = content[0:2]
        if len(head_buffer) == 0:
            raise ValueError("invalid content from server")

        pkt = content[2:]
        client_message = swirl_pb2.SwirlServerMessage()
        client_message.ParseFromString(pkt)
        # take a look at the protobuf file to see what this means.
        message_type = client_message.WhichOneof("servermessages")
        if message_type is None:
            logger = logging.getLogger(__name__)
            logger.warn("Invalid or Empty Message Sent to Client")
            raise EncodingError("Invalid Client Message Received")
        return getattr(client_message, message_type)


@asyncio.coroutine
def _read_exact_async(n, reader):
    buffer = yield from reader.read(n)
    n -= len(buffer)
    if n == 0:
        return buffer

    buffer_list = [buffer]
    while 1:
        buffer = yield from reader.read(n)
        buffer_list.append(buffer)
        n -= len(buffer)
        if n == 0:
            return buffer


class EncodingError(Exception):
    pass