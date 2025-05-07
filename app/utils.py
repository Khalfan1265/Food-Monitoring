# app/utils.py

import secrets

def generate_reset_secret_key(length: int = 64) -> str:
    return secrets.token_urlsafe(length)

print(generate_reset_secret_key())
