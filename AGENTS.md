# AGENTS.md

Instructions for AI coding agents working on this repo.

## Working alongside other agents

Several AI agents (Claude, Codex, Grok, Grok Bot) and a human work on this repo, sometimes at
the same time. Coordinate so you don't overwrite each other.

1. **Before you start, see who's working on what.**
   - If you have the Agent Hub tools (MCP server `hub`, available on the owner's Mac mini):
     call `hub_status` with this repo's `owner/repo`. In a shell there, `hub status owner/repo` works too.
   - Otherwise (for example in a cloud environment): look at the open pull requests and recently
     pushed branches on GitHub, and avoid files they're already changing.
2. **Claim your work** with `hub_claim` when you have the hub: the area, the files or folders
   you'll touch, and your branch. If it reports a conflict, pick other work or coordinate.
   Don't edit the same files as another agent in parallel.
3. **Start branch names with your agent**: `claude/…`, `codex/…`, `grok/…`, `grok-bot/…`.
   This is how the hub tells who did what.
4. With the hub: post a short `hub_update` at milestones, use `hub_handoff` to pass work on,
   and `hub_release` when you're done.
