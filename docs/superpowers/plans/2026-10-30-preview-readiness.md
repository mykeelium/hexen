# Public preview readiness

Authorized scope: address the release review and onboarding gaps. Preserve the approved generated installer and interactive disk/credential safeguards.

1. Add first-boot entry point, prerequisites before Walker, review pinned recipes and exact built archives before sudo installation, then provision and print health checks.
2. Install Firefox from official packages; prefer Zen when present and use Firefox otherwise for normal/private shortcuts.
3. Improve installer input retries and plain-language summary with optional JSON.
4. Add public quickstart, accurate known issues, release checklist, third-party inventory and issue templates. License awaits owner choice. No publication or tag until a tested commit exists.
5. Run focused checks and prepare a fresh disposable VM; record remaining interactive install acceptance honestly.

Completed source changes: first-boot prerequisites and pinned build review; explicit existing-Walker reuse prompt; Firefox fallback; service-aware health report; input retries/plain summary; explicit HTTPS mirror subset; ESP/Plymouth fixes; MIT license and notices inventory; public quickstart/known issues/release checklist; bug template and focused CI.
Validation: 17 focused onboarding tests pass; all 51 Python tests pass with Unix socket access; shell/Python syntax and diff whitespace checks pass. Actual Archinstall 4.5 parser, menu confirmation, LUKS2+Btrfs creation, assisted package installation, Limine reboot and betauser UID1000/wheel login were exercised. First-boot setup passed, followed by a zero-change final-source provisioning rerun. Managed graphical login, Walker calculation/search, Firefox normal/private shortcuts and post-reboot firewall inspection passed.
Rulings: require exact normalized disk layout at final operation; reject mounted /mnt; preserve upstream initialization and hidden credential prompts; use explicit HTTPS mirror servers because region loading disregards URL subsets; SDDM need only be enabled before reboot. No commits, tags, visibility changes or publication performed.

Final runtime results: post-provisioning encrypted reboot, stock SDDM with managed Hyprland selected, desktop/Walker launch, calculator 1+1 -> 2, Google URL opened in Firefox, normal/private browser shortcuts, default HTTPS handler and post-reboot DROP firewall inspection passed. The repository is confirmed PRIVATE. Only publication/commit/tag and a clean run of that final public revision remain release gates for this onboarding increment; broader hardware/account/update/recovery acceptance stays on the main roadmap.
