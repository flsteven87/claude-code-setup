---
name: nr-platform
description: "Connect to and operate the Nexrex host `nexrex` (`100.88.194.88`) over Tailscale and SSH. Use for access checks, remote audits, troubleshooting, or persistent Codex and Claude Code tmux sessions."
argument-hint: "[connect | audit | session <project> | troubleshoot]"
---

# NR Platform

Use company-approved access without weakening SSH checks.

## Connection facts

- Tailscale node: `nexrex`
- Address: `100.88.194.88`
- SSH user: `platform`
- SSH command: `ssh platform@100.88.194.88`
- Remote shell: Bash on Ubuntu
- Codex and Claude Code are installed as standalone commands under `~/.local/bin`.

## Route the task first

- **Connect** — verify Tailscale, TCP, host identity, and SSH transport only.
- **Audit** — connect, then collect only the remote facts the user asked for.
- **Session** — resolve the project and requested agent, then reuse or create one named tmux session.
- **Troubleshoot** — start at the first failed layer and stop once evidence identifies Tailscale,
  TCP, SSH, authentication, tmux, project path, or agent binary as the blocker.

Run only the selected branch; a prerequisite succeeding does not authorize the later branches. Read
the installed command's current `--help` before using version-sensitive options.

## Connect

1. Check access without changing state:

   ```bash
   tailscale status
   tailscale ping -c 2 100.88.194.88
   nc -G 5 -vz 100.88.194.88 22
   ssh-keygen -F 100.88.194.88
   ```

2. Tailscale stopped → explain that `100.88.194.88` is unreachable without the company tailnet.
   Enabling the VPN changes network state, so get confirmation immediately before doing it.
3. Require a known or independently verified SSH host key. An unexpected or changed fingerprint is
   a stop-and-report condition, not something to accept, delete, or bypass with
   `StrictHostKeyChecking=no`.
4. Prefer an approved SSH key. If password authentication is necessary, open an interactive SSH
   session and let the user type the password directly into it.

## Audit the remote environment

Start read-only:

```bash
hostname
id
command -v tmux codex claude git rg
tmux -V
codex --version
claude --version
codex login status
claude auth status --text
tmux list-sessions
```

Existing Codex and Claude authentication is company-managed access: report only what the user asked
for, and leave `~/.codex/auth.json` and `~/.claude` credentials in place unless the user explicitly
requests a change and confirms it against company policy.

When a command reports that administrator help is required, report the missing dependency rather
than installing Node, npm packages, or system updates.

## Run persistent sessions

Resolve the exact project directory and read its `AGENTS.md` or `CLAUDE.md` before launching an
agent. Launch from the selected project, never from the home directory.

Run `tmux list-sessions` first and reuse a matching session when one exists:

```bash
if tmux has-session -t pochi-codex 2>/dev/null; then
  tmux attach-session -t pochi-codex
else
  tmux new-session -d -s pochi-codex -c /absolute/path/to/project 'exec codex'
  tmux attach-session -t pochi-codex
fi
```

For Claude Code, the same shape with `pochi-claude` and `'exec claude'`.

Detach with `Ctrl-b d`; reconnect with `tmux attach-session -t <name>`. tmux preserves a process
across an SSH disconnect but not across a host reboot — say so when it matters.

Killing another session needs explicit confirmation. When Codex and Claude will edit concurrently,
give each its own branch and Git worktree so only one writes to a given working tree.

## Security boundaries

- Treat `platform` as a potentially operational or shared account even when its home directory is
  private at the Unix permission level.
- Keep SSH agent forwarding disabled unless company policy explicitly requires it.
- Adding SSH keys to `authorized_keys`, modifying ACLs, changing VPN or firewall settings, updating
  packages, and rebooting the host each need explicit authorization.
- Proprietary source code stays on the existing company-approved Codex and Claude organization
  access, never a personal AI account.
- Exploratory checks stay read-only; make remote writes only where the user's task requires them.

## Completion

| Branch | Complete when |
|---|---|
| Connect | The known host key is verified and SSH transport succeeds, or the exact failed connection layer is identified. |
| Audit | Only requested facts were collected and no authentication material entered the report. |
| Session | The exact project, agent binary, and reused or newly created tmux session are confirmed. |
| Troubleshoot | Evidence identifies one failed layer and gives the smallest next check or required owner action. |
