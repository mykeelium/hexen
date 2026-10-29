# Interactive package update review design

## Intent

Add an interactive review step to `hexen update-monitor` so the owner can
inspect each discovered Arch package update, record review intent, and decide
whether to proceed to Hexen's existing checkpointed full-system update flow.
This is opt-in package installation; the daily monitor remains discovery-only.

## Goals

- Present each candidate's installed and candidate version, repository, Arch
  package page, and packaging-recipe history.
- Let the owner mark a package as reviewed without selecting it, wanted for the
  upcoming full update, or needing follow-up.
- Save package-level choices and the final proceed/cancel decision in the
  existing private update evidence log.
- Summarize decisions before offering an explicit handoff to `hexen update`.
- Keep discovery and decision handling independent from the presentation layer
  so a richer TUI can be added on top of the same workflow later.
- Preserve Arch's full-system-upgrade requirement. Package flags record intent;
  they must never create a partial transaction.

## Non-goals

- No automatic package installation, privileged transaction, database refresh,
  or snapshot creation during package review.
- No package-by-package installation, package pinning, or promise that a flagged
  package alone will be updated.
- No third-party TUI dependency in the initial terminal implementation.
- No claim that package names, signatures, or recipe links establish that a
  source or build is harmless.

## User flow

1. The owner runs `hexen update-monitor review` in a real terminal. The command
   performs fresh discovery with the isolated `checkupdates` database and
   refuses to offer review when discovery is stale, failed, or has no updates.
2. A dependency-free terminal interface shows each candidate and its review
   links. For every package, the owner chooses **reviewed**, **want in upcoming
   update**, **follow up**, or **leave undecided**. The interface supports
   quitting safely; each completed choice is recorded immediately.
3. A final summary lists all candidates and their choices. The owner may
   explicitly choose **continue to full update** or **cancel**.
4. Continuing launches the existing `hexen update` workflow, which retains its
   own confirmation, source review, checkpoint, and Pacman transaction gates.
   Canceling makes no package changes.

## Approaches

1. **Build a rich TUI immediately.** This could provide keyboard navigation and
   a split package/detail view, but adds UI complexity before the review states
   and persistence behavior have been exercised.
2. **Use only a line-oriented terminal prompt.** This is simple and accessible,
   but risks coupling package review rules to the prompt implementation and
   makes a later TUI rewrite more likely.
3. **Separate review state and actions from a terminal-first interface.** The
   first version uses simple prompts without new dependencies, while the
   package model, choices, persistence, and final handoff stay independently
   callable for a future richer TUI. This follows the owner's preference and
   is the selected approach.

## Data and safety

- Reuse the current private state root and append-only `evidence.jsonl`.
- Associate review events with a discovery timestamp/report identity and package
  name, installed version, candidate version, repository, and one of the
  defined decision states.
- Save each decision as soon as it is made so interruption does not erase
  completed review. Keep state files private, owner-owned, and protected from
  symlink substitution, following the existing update-state checks.
- Record the final continue/cancel choice. Do not store credentials or package
  payloads in the review record.
- A continuation passes control to the existing full-system `hexen update`
  workflow. The update workflow must not consume package flags as a Pacman
  filter. Display this limitation before the final confirmation.
- Treat a changed candidate set between review and the later Pacman refresh as
  a new transaction state; the normal `hexen update` confirmation remains the
  authority for whether to proceed.

## Implementation boundaries

- Add a `review` subcommand beneath `update-monitor`; preserve the current
  no-argument `hexen update-monitor` behavior for scheduled discovery. Accept
  the existing `--vm` option on review and pass it to the normal update flow so
  VM-specific optional Ansible convergence remains available.
- Extract discovery results into a structured object usable by both the
  Markdown report and interactive review.
- Keep review decisions and terminal I/O in separate functions/modules so a
  later TUI can reuse them without changing the evidence format or update
  safety boundary.
- Update the desktop/update guide and roadmap with commands, decision meaning,
  full-upgrade behavior, and the planned TUI follow-up.

## Acceptance criteria

- Scheduled discovery behavior and report output remain unchanged.
- Review requires an interactive terminal and makes no change on stale,
  failed, offline, or empty discovery.
- Each candidate is shown with versions, repository, and direct review links.
- All four package choices and interruption behavior are clear; completed
  choices persist privately.
- The final summary accurately reflects choices, and both cancel and explicit
  continuation are recorded.
- Continuation invokes the existing full-system update path without bypassing
  its own confirmation; no partial update command is introduced.
- The core review model and evidence persistence can be exercised by another
  presentation layer in a later TUI step.
