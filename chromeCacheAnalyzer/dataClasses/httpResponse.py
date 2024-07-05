class CachedMetadataFlags(enum.IntFlag):
# net/http/http_response_info.cc

    RESPONSE_INFO_VERSION = 3
    RESPONSE_INFO_VERSION_MASK = 0xFF
    RESPONSE_INFO_HAS_CERT = 1 << 8
    RESPONSE_INFO_HAS_SECURITY_BITS = 1 << 9
    RESPONSE_INFO_HAS_CERT_STATUS = 1 << 10
    RESPONSE_INFO_HAS_VARY_DATA = 1 << 11
    RESPONSE_INFO_TRUNCATED = 1 << 12
    RESPONSE_INFO_WAS_SPDY = 1 << 13
    RESPONSE_INFO_WAS_ALPN = 1 << 14
    RESPONSE_INFO_WAS_PROXY = 1 << 15
    RESPONSE_INFO_HAS_SSL_CONNECTION_STATUS = 1 << 16
    RESPONSE_INFO_HAS_ALPN_NEGOTIATED_PROTOCOL = 1 << 17
    RESPONSE_INFO_HAS_CONNECTION_INFO = 1 << 18
    RESPONSE_INFO_USE_HTTP_AUTHENTICATION = 1 << 19
    RESPONSE_INFO_HAS_SIGNED_CERTIFICATE_TIMESTAMPS = 1 << 20
    RESPONSE_INFO_UNUSED_SINCE_PREFETCH = 1 << 21
    RESPONSE_INFO_HAS_KEY_EXCHANGE_GROUP = 1 << 22
    RESPONSE_INFO_PKP_BYPASSED = 1 << 23
    RESPONSE_INFO_HAS_STALENESS = 1 << 24
    RESPONSE_INFO_HAS_PEER_SIGNATURE_ALGORITHM = 1 << 25
    RESPONSE_INFO_RESTRICTED_PREFETCH = 1 << 26
    RESPONSE_INFO_HAS_DNS_ALIASES = 1 << 27
    RESPONSE_INFO_SINGLE_KEYED_CACHE_ENTRY_UNUSABLE = 1 << 28
    RESPONSE_INFO_ENCRYPTED_CLIENT_HELLO = 1 << 29
    RESPONSE_INFO_BROWSER_RUN_ID = 1 << 30