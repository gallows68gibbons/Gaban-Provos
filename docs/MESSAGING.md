# Messaging topology: Telegram + Discord

Gaban Provos uses **two separate bot identities**. They are separate security principals, not two names for one shared credential.

| Identity | Telegram bot | Discord app/bot | Responsibility |
| --- | --- | --- | --- |
| Hermes Lead | `Gaban Hermes` | `Gaban Hermes` | Owner-facing intake, planning, approvals, delegation, final response |
| OpenClaw Worker | `Gaban Worker` | `Gaban Worker` | Bounded execution, progress evidence, and hand-back to Hermes |

## Collaboration contract

```text
Owner ──> Hermes bot ──> Control-plane task + approval record ──> OpenClaw worker
  ▲              │                                                   │
  └── final plan / evidence / status <──────── audit event ──────────┘
```

1. The owner sends a mission to **Hermes**, never directly to the worker for privileged work.
2. Hermes classifies risk, creates a plan, and requests approval when required.
3. For an approved bounded step, Hermes posts a task envelope to the internal queue for OpenClaw. The envelope must carry a task ID, permitted tools, permitted data scope, deadline, and expected evidence.
4. OpenClaw returns results and logs to the control plane—not an instruction that Hermes must blindly execute.
5. Hermes validates evidence, summarizes the result, and replies to the owner. Any external side effect remains human-approved.

The two bots may appear in the same Telegram group or Discord server for visibility, but they must **not** treat each other's ordinary chat messages as executable instructions. Only signed/validated control-plane task envelopes are delegation messages.

## Telegram setup

Create two bots with [@BotFather](https://t.me/BotFather): one token for Hermes and a different token for OpenClaw. Store each token only in its corresponding runtime secret store.

Recommended group layout:

| Group | Members | Purpose |
| --- | --- | --- |
| `Gaban Control` | Owner + Hermes | Mission intake, plans, approvals, final reports |
| `Gaban Operations` | Owner + Hermes + OpenClaw | Read-only operational status; no free-form execution requests |

Keep privacy mode enabled unless a narrowly scoped workflow genuinely needs messages beyond commands/mentions. Set explicit Telegram chat/user allowlists during each product's onboarding. Do not put bot tokens in `.env`, source code, screenshots, or Git.

For OpenClaw, its official channel flow supports:

```bash
openclaw channels add --channel telegram --token <worker-bot-token>
openclaw channels status --probe
```

Run this only inside the `openclaw` container or its documented onboarding flow. Do not reuse the Hermes token.

For Hermes, run its official interactive gateway setup inside the `hermes` container and add only the Hermes bot token. Verify the gateway state before connecting it to any group.

```bash
hermes gateway setup
hermes gateway
```

## Discord setup

Create **two Discord Applications** in the Discord Developer Portal, each with its own bot token and minimal scopes. Invite both to a private server only. Give them distinct roles:

- `Gaban Hermes`: can read/send only in `#control` and `#approvals`.
- `Gaban Worker`: can read/send only in `#operations`; no administrator permission.

Use channel allowlists and mention gating. Hermes defaults to mention-required behavior in server channels; keep that enabled. OpenClaw should use its documented Discord pairing and guild/channel allowlists. Never set either bot to process every channel, every DM, or messages from other bots by default.

Recommended channels:

```text
#control       owner ↔ Hermes
#approvals     explicit human approvals and decision log
#operations    status from Hermes/OpenClaw (not a command channel)
#audit         append-only notices, restricted to administrators
```

## Secret and permission policy

- One token per bot, one least-privilege service identity per external integration.
- Mount secrets at runtime through a VPS secret manager or protected Docker secret mechanism; rotate immediately if a token is exposed.
- Do not grant `Administrator`, host Docker socket access, shell access, or unrestricted filesystem mounts to a chat bot.
- Disable or require approval for money movement, account administration, code deployment, deletion, messaging outside approved destinations, and credential access.
- Record task ID, initiating user, approval, tools invoked, outcome, and artifact hashes for every delegation.

## Official references

- [Hermes Discord setup](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord/)
- [Hermes messaging/session sources](https://hermes-agent.nousresearch.com/docs/user-guide/sessions)
- [OpenClaw chat channels](https://docs.openclaw.ai/channels/index.html)
- [OpenClaw Discord channel](https://docs.openclaw.ai/channels/discord)

