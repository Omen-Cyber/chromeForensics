from chromeCacheAnalyzer.dataClasses.HttpResponseData import HttpResponseData as CachedMetadataFlags
from chromeCacheAnalyzer.utils.binaryReader import BinaryReader
import datetime
import types
from typing import Optional, Iterable, Dict, Any, List, Set


class ResponseParser:
    # net/http/http_response_info.cc / net/http/http_response_info.h

    def __init__(
        self,
        header_declarations: Set[str],
        header_attributes: Dict[str, List[str]],
        request_time: datetime.datetime,
        response_time: datetime.datetime,
        certs: List[bytes],
        host_address: Optional[str],
        host_port: Optional[int],
        other_attributes: Dict[str, Any]
    ):
        self._declarations = header_declarations.copy()
        self._attributes = types.MappingProxyType(header_attributes.copy())
        self._request_time = request_time
        self._response_time = response_time
        self._certs = certs.copy()
        self._other_attributes = types.MappingProxyType(other_attributes)
        self._host_address = host_address
        self._host_port = host_port

    @property
    def certs(self) -> Iterable[bytes]:
        yield from self._certs

    @property
    def http_header_declarations(self) -> Iterable[str]:
        yield from self._declarations

    @property
    def request_time(self) -> datetime.datetime:
        return self._request_time

    @property
    def response_time(self) -> datetime.datetime:
        return self._response_time

    @property
    def http_header_attributes(self) -> Iterable[tuple[str, str]]:
        for key, vals in self._attributes.items():
            for val in vals:
                yield key, val

    def has_declaration(self, declaration: str) -> bool:
        return declaration in self._declarations

    def get_attribute(self, attribute: str) -> list[str]:
        return self._attributes.get(attribute.lower()) or []

    @property
    def other_cache_attributes(self):
        return self._other_attributes

    @property
    def host_address(self) -> Optional[str]:
        return self._host_address

    @property
    def host_port(self) -> Optional[int]:
        return self._host_port

    @classmethod
    def from_buffer(cls, buffer: bytes):
        reader = BinaryReader.from_bytes(buffer)
        total_length = reader.read_uint32()
        if total_length != len(buffer) - 4:
            raise ValueError("Metadata buffer is not the declared size")

        def align():
            alignment = reader.tell() % 4
            if alignment != 0:
                reader.read_raw(4 - alignment)

        flags_value = reader.read_uint32()
        try:
            flags = CachedMetadataFlags(flags_value)
        except ValueError:
            flags = CachedMetadataFlags(0)  # Default to 0 if an invalid value is encountered
            print(f"Warning: invalid CachedMetadataFlags value {flags_value}, defaulting to 0")

        request_time = reader.read_datetime()
        response_time = reader.read_datetime()

        http_header_length = reader.read_uint32()
        http_header_raw = reader.read_raw(http_header_length)

        header_attributes: Dict[str, List[str]] = {}
        header_declarations = set()

        for header_entry in http_header_raw.split(b"\00"):
            if not header_entry:
                continue
            parsed_entry = header_entry.decode("latin-1").split(":", 1)
            if len(parsed_entry) == 1:
                header_declarations.add(parsed_entry[0])
            elif len(parsed_entry) == 2:
                header_attributes.setdefault(parsed_entry[0].lower(), [])
                header_attributes[parsed_entry[0].lower()].append(parsed_entry[1].strip())

        other_attributes = {}

        certs = []
        if flags & CachedMetadataFlags.RESPONSE_INFO_HAS_CERT:
            align()
            cert_count = reader.read_uint32()
            for _ in range(cert_count):
                align()
                cert_length = reader.read_uint32()
                certs.append(reader.read_raw(cert_length))

        if flags & CachedMetadataFlags.RESPONSE_INFO_HAS_CERT_STATUS:
            align()
            other_attributes["cert_status"] = reader.read_uint32()

        if flags & CachedMetadataFlags.RESPONSE_INFO_HAS_SECURITY_BITS:
            align()
            other_attributes["security_bits"] = reader.read_int32()

        if flags & CachedMetadataFlags.RESPONSE_INFO_HAS_SSL_CONNECTION_STATUS:
            align()
            other_attributes["ssl_connection_status"] = reader.read_int32()

        if flags & CachedMetadataFlags.RESPONSE_INFO_HAS_SIGNED_CERTIFICATE_TIMESTAMPS:
            align()
            ts_count = reader.read_int32()
            for _ in range(ts_count):
                ts_version = reader.read_int32()
                str_len = reader.read_int32()
                ts_log_id = reader.read_raw(str_len)
                align()
                ts_timestamp = reader.read_datetime()
                str_len = reader.read_int32()
                ts_extensions = reader.read_raw(str_len)
                align()
                ts_hash_algo = reader.read_int32()
                ts_sig_algo = reader.read_int32()
                str_len = reader.read_int32()
                ts_sig_data = reader.read_raw(str_len)
                align()
                ts_origin = reader.read_int32()
                str_len = reader.read_int32()
                ts_log_desc = reader.read_raw(str_len)
                align()
                ts_status = reader.read_uint16()
                align()

        if flags & CachedMetadataFlags.RESPONSE_INFO_HAS_VARY_DATA:
            align()
            other_attributes["vary_data"] = reader.read_raw(16)

        host, port = None, None
        try:
            align()
            host_length = reader.read_uint32()
            host = reader.read_raw(host_length).decode("latin-1")
            align()
            port = reader.read_uint16()
        except ValueError:
            pass

        return ResponseParser(
            header_declarations, header_attributes, request_time, response_time, certs, host, port, other_attributes)