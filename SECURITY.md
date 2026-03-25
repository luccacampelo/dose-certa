# Security Policy

## Supported Version
- 1.0.0

## Security Principles
- No secrets in repository.
- No runtime patient/user data tracked in Git.
- Public deployment must run in isolated hosting (recommended: Streamlit Community Cloud).
- Temporary local tunnels are for quick tests only and are not recommended for production use.

## Sensitive Files (must not be committed)
- `.env`, `.env.*`
- `*.pem`, `*.key`, `*.p12`
- `data/*.json`
- `data/_test/*`
- `logs/*`

## How to report a vulnerability
Open a private contact to the maintainer and include:
- affected file/module
- reproduction steps
- expected impact
