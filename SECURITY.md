# Security Policy

## Reporting a vulnerability

Please **do not** report security vulnerabilities through public GitHub issues.

Instead, use [GitHub Private Vulnerability Reporting](https://github.com/NicolasKingreen/portals-python/security/advisories/new)
on this repository so we can investigate and coordinate a fix before disclosure.

## API key handling

- Never commit your Portals Partner API key to source control or hard-code it in client-side code.
- Pass the key via environment variables or a secret manager on your server.
- The client sends `Authorization: partners <api_key>` to the configured `base_url`
  (`https://portal-market.com` by default). Only override `base_url` with a trusted HTTPS endpoint
  or a local test transport.
- `portals-api` does not configure loggers or log request headers/bodies on its own. If you enable
  debug logging on `httpx2` or `httpcore2`, ensure `Authorization` headers are redacted in your log
  pipeline.
