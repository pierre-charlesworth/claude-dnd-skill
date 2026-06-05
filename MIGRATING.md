# Migrating from v1 (standalone skill) to v2 (plugin)

**v2.0.0 makes the D&D skill plugin-only.** The standalone install
(`~/.claude/skills/dnd`, invoked as `/dnd`) is replaced by the Claude Code
plugin `dm@neural-initiative`, invoked as **`/dm:dnd`**.

## TL;DR — your campaigns are safe

Your campaign data was **never inside the skill.** It lives at the data root
(`~/.claude/dnd`, or wherever `$DND_CAMPAIGN_ROOT` points) and is read the same
way by both the old standalone skill and the new plugin. Characters, campaigns,
and history need **zero migration** — both versions already share them.

Migration is just two steps:

```text
1. Install the plugin
   /plugin marketplace add neuralinitiative/claude-dnd-skill
   /plugin install dm@neural-initiative

2. Run the one-time migration helper
   python3 <plugin>/skills/dnd/scripts/migrate_v1_to_v2.py
```

Then use **`/dm:dnd`** going forward.

> The two installs coexist harmlessly between step 1 and step 2 (they share the
> same data root), so there's no window where anything is broken.

## What the helper does

`migrate_v1_to_v2.py`:

1. **Detects** your legacy standalone install and reports its version.
2. **Carries over runtime state** that older standalone builds wrote *inside* the
   skill (`~/.claude/skills/dnd/display/`) into the update-safe runtime dir
   (`<data-root>/.runtime`): **device approvals, the display auth token, and TLS
   certs.** This is the payoff — paired phones stay paired and HTTPS stays
   trusted, so nobody has to re-approve every device after the switch.
3. **Verifies** (does not move) your campaign data at the data root.
4. **Backs up and retires** the old `~/.claude/skills/dnd` (moved to
   `~/.claude/skills/dnd.v1-backup-<timestamp>`, not deleted) so the legacy
   `/dnd` no longer shadows or duplicates `/dm:dnd`.

It **does not** touch campaign data, and it **cannot** run `/plugin install` for
you (that's a Claude Code UI command) — which is why you install the plugin
first.

### Options

```text
python3 migrate_v1_to_v2.py            # interactive (asks before retiring v1)
python3 migrate_v1_to_v2.py --yes      # non-interactive
python3 migrate_v1_to_v2.py --dry-run  # show what would happen, change nothing
python3 migrate_v1_to_v2.py --keep-standalone   # relocate runtime only; leave /dnd in place
```

If your standalone install lives somewhere non-default, point the helper at it
with `DND_LEGACY_SKILL_DIR=/path/to/dnd`. If it's a **symlink** (a dev clone or a
GNU Stow setup), the helper detects that and leaves it alone — remove the link
yourself when ready.

## Rolling back

Nothing is deleted. To return to the standalone install, move the backup dir
(`~/.claude/skills/dnd.v1-backup-<timestamp>`) back to `~/.claude/skills/dnd`, or
reinstall from the frozen **`legacy-1.x`** branch. Your campaign data is
unaffected either way.

## Reporting issues

Migration edge cases are tracked in the pinned **"v2 migration reports"**
discussion thread on the repo. If something didn't carry over cleanly — a device
that needed re-approval, a cert that wasn't picked up — please drop a note there
with your prior version and OS so we can catch it early.
