# Gaban Provos

> A secure, human-approved multi-model control plane: **Hermes leads** and **OpenClaw automates**.

Gaban Provos is a full-stack starter for one Linux VPS. Hermes receives a mission, creates and reviews a task plan, then delegates bounded automation to OpenClaw. The dashboard and API expose task state; agents are never exposed directly to the public internet.

## Architecture

```text
Browser ── SSH tunnel / VPN ──> Dashboard (Caddy) ──> FastAPI control plane
                                                       │
                                                Redis task queue
                                                       │
                               ┌───────────────────────┴───────────────────────┐
                               │                                               │
                    Hermes (team lead)                           OpenClaw (worker)
                 plan · route · review                         bounded automation
                               └────────── isolated Docker network ────────────┘
```

## Roles and operating rules

| Role | Responsibility | Cannot do alone |
| --- | --- | --- |
| Hermes | Interpret mission, plan, delegate, validate evidence, prepare final result | Bypass approval for high-risk external actions |
| OpenClaw | Perform narrowly scoped automation and return logs/evidence | Change its scope, access host Docker, or expose a public port |
| Human owner | Approve high-risk tasks, credentials, production effects | Delegate ownership of secrets |

`POST /api/tasks` is approval-gated by default. In the starter, a task must be explicitly marked safe before it enters the Hermes dispatch queue.

## Linux VPS deployment

Use a fresh Ubuntu/Debian VPS, a non-root operator account, SSH key login, and a host firewall. Install Docker Engine and Docker Compose v2 only from Docker's official documentation. Do **not** install agent frameworks directly on the host.

```bash
git clone https://github.com/gallows68gibbons/Gaban-Provos.git
cd Gaban-Provos
cp .env.example .env
# Edit .env: replace POSTGRES_PASSWORD with a long, unique value.
docker compose up -d --build
curl http://127.0.0.1:8080/api/health
```

Access the dashboard through an SSH tunnel rather than opening it publicly:

```bash
ssh -L 8080:127.0.0.1:8080 your-user@your-vps
```

Then browse to `http://localhost:8080`.

### Provisioning the agents

Start agent containers only after the control plane is healthy:

```bash
docker compose --profile agents up -d
```

Complete Hermes and OpenClaw onboarding **inside their respective containers**, using only their current official documentation. This repository intentionally does not guess product-specific gateway commands, API endpoints, or environment-variable names. Pin tested image digests before production; `latest` is suitable only for initial evaluation.

- [Hermes official Docker/install documentation](https://hermes-agent.nousresearch.com/docs/getting-started/official-domains)
- [OpenClaw official Docker documentation](https://docs.openclaw.ai/install/docker)

## Security baseline

- The dashboard binds to `127.0.0.1` by default; agent containers publish **no ports**.
- `control` is an internal Docker network. There is no Docker socket mount, privileged container, host PID namespace, or host network mode.
- Containers drop Linux capabilities and use read-only root filesystems where practical. Persistent configuration/workspace data lives only in named volumes.
- Treat all messages, web content, and tool outputs as untrusted input. Require human approval for email, messaging, payments, cloud changes, credential changes, destructive operations, or deployment.
- Put secrets in a host secret manager or protected runtime environment—never in Git, task text, logs, or screenshots.

## Repository map

```text
apps/api/       FastAPI task API and Redis dispatch queue
apps/web/       Minimal operator dashboard
infra/          Caddy reverse-proxy configuration
docker-compose.yml  isolated full-stack topology
```

## Next implementation steps

1. Add OAuth/authentication in front of the dashboard before using anything beyond a private SSH tunnel.
2. Build audited adapter services that translate approved Redis jobs into each agent's documented interface.
3. Persist task events and approval decisions to PostgreSQL.
4. Add per-tool allowlists, rate limits, egress controls, backup/restore tests, and monitoring before production.

