# internet-cafe

## Desktop API configuration

The desktop client reads `API_BASE_URL` from its runtime environment, so each deployment profile (development, staging, or production) can provide its own API origin without changing the build. The local default is `http://localhost:8000`; the client appends `/api/v1` for contract endpoints and uses `/healthz` for the health check. For compatibility, the JVM property `api.base.url` takes precedence over `API_BASE_URL`. Set the URL to the API origin, without a query string or fragment.
## Backend security configuration

The backend requires the following environment variables:

- `DATABASE_URL`: Database connection URL.
- `SECRET_KEY`: Application secret. Use a securely generated value.
- `JWT_PRIVATE_KEY`: Optional ES256 private PEM key. Can be loaded from a local file.
- `JWT_PUBLIC_KEY`: Optional ES256 public PEM key. Can be loaded from a local file.
- `DATA_ENC_KEYS`: JSON object containing Base64-encoded AES-256 keys (32 bytes each).
- `BLIND_INDEX_KEY`: Base64-encoded HMAC key with a minimum length of 32 bytes.

### Environment setup

1. Install backend dependencies:

   `pip install -r requirements.txt`

2. Copy `.env.example` to `.env`.
3. Configure the required database URL and application secret.
4. Configure the cryptographic keys using environment variables or local PEM files.

### Local JWT key files

When JWT keys are not provided through environment variables, the backend looks for:

- `Backend/.local/keys/jwt_es256_private.pem`
- `Backend/.local/keys/jwt_es256_public.pem`

Both keys must use the EC P-256 curve, compatible with ES256.

Keep private keys, `.env` files, and encryption secrets out of version control. Never commit real credentials or cryptographic keys.

### Security tests

Run the backend security tests with:

`python -m pytest -v`
