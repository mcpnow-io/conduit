---
mode: agent
---
# Tips: How to run unittests

## Quick Setup
```bash
# 1. Start Phorge container (if not running)
cd tests && docker build -t phorge_debug . && docker run -d --rm -p 8080:80 --name phorge_debug phorge_debug

# 2. Get API token
docker exec phorge_debug /usr/local/bin/get-api-token.sh

# 3. Run tests
cd .. && source venv/bin/activate && PHABRICATOR_TOKEN=<api-token> PHABRICATOR_URL=http://127.0.0.1:8080/api/ pytest
```

## Tips
- **Always check if container running first**: `docker ps | grep phorge_debug`
- **Run specific test**: `pytest -k "whoami" -v`
- **Browser access**: http://127.0.0.1:8080/ (modify Dockerfile to set password)
