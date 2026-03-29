import argparse
import hmac
import hashlib
import base64
import sys

def hmac_sha256_hex_base64(message: str, key: str):
    message_bytes = message.encode('utf-8')
    key_bytes = key.encode('utf-8')
    hmac_digest = hmac.new(key_bytes, message_bytes, hashlib.sha256).digest()
    return hmac_digest.hex(), base64.b64encode(hmac_digest).decode('utf-8')

def main():
    parser = argparse.ArgumentParser(
        description="Generate HMAC-SHA256 of a message with a key. Outputs hex and base64 encodings."
    )
    parser.add_argument(
        "message",
        help="The message string to hash"
    )
    parser.add_argument(
        "-k", "--key",
        default="nomis",
        help="The key to use for HMAC (default: 'nomis')"
    )

    args = parser.parse_args()

    hex_result, base64_result = hmac_sha256_hex_base64(args.message, args.key)

    print(f"Message : {args.message}")
    print(f"Key     : {args.key}")
    print(f"Hex     : {hex_result}")
    print(f"Base64  : {base64_result}")

if __name__ == "__main__":
    main()