# MCP Python Server - Security Platform Starter

This package upgrades the original `mcp-python-server` into a starter security-team MCP platform with:

- AWS adapter for GuardDuty, Security Hub, and CloudTrail
- Jira adapter for incident creation and comments
- Wiz adapter for critical exposure lookups
- OAuth/JWT bearer authentication with JWKS validation
- Protected Resource Metadata endpoint
- YAML policy engine for per-tool authorization
- JSON audit logging
- AWS Secrets Manager integration
- ECS Fargate task definition example
- GitHub Actions workflow to publish to GHCR

## Repo layout

```text
src/
  main.py
  config.py
  auth/
  adapters/
  audit/
  policy/
  tools/
```

## Quick start

### 1. Local Python run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export $(grep -v '^#' .env | xargs)
python src/main.py
```

Health endpoint:

```bash
curl http://localhost:8080/healthz
```

Protected resource metadata:

```bash
curl http://localhost:8080/.well-known/oauth-protected-resource
```

### 2. Docker

```bash
docker build -t mcp-python-server-security-platform .
docker run --rm -p 8080:8080 \
  -e OIDC_ISSUER=https://your-idp.example.com/oauth2/default \
  -e OIDC_AUDIENCE=mcp-server \
  -e OIDC_JWKS_URI=https://your-idp.example.com/oauth2/default/v1/keys \
  -e OAUTH_AUTHORIZATION_SERVER=https://your-idp.example.com/oauth2/default \
  mcp-python-server-security-platform
```

## Example tool calls

### GuardDuty

```bash
curl http://localhost:8080/mcp/tools/aws_list_guardduty_findings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"detector_id":"12abc34d567e8fa901bc234d5678e901","max_results":10}'
```

### Jira incident

```bash
curl http://localhost:8080/mcp/tools/jira_create_incident \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"summary":"Critical finding in prod","description":"Opened by MCP workflow","severity":"High"}'
```

### Wiz

```bash
curl http://localhost:8080/mcp/tools/wiz_list_critical_exposures \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project":"production"}'
```

## Secrets Manager pattern

The adapters expect **secret names** in environment variables. The values stored in those secrets should be the actual Jira/Wiz credentials or URLs.

Examples:

- `/mcp/jira/base_url` → `https://your-domain.atlassian.net`
- `/mcp/jira/email` → `security-bot@example.com`
- `/mcp/jira/api_token` → Jira API token
- `/mcp/jira/project_key` → `SEC`
- `/mcp/wiz/api_url` → Wiz API base URL
- `/mcp/wiz/client_id` → Wiz client ID
- `/mcp/wiz/client_secret` → Wiz client secret

## Notes

- The ECS task definition file is an example and should be updated before deployment.
- The JWT validation and protected resource metadata are ready, but you still need to configure your IdP values.
- The Wiz GraphQL query is a starter template and may need to be adjusted to your tenant schema.
- The AWS adapters assume the task role or an assumed role has the required read permissions.
