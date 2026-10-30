# Application sources

Reviewed on 2026-10-28 for x86_64 Arch. Package versions are observations, not
pins. Refresh this review when recipes, source URLs, privileges, or signatures
change. The apps role installs five applications plus supporting packages from
signed official Arch repositories, and Bitwarden Desktop from the verified
Flathub listing.
The desktop role also installs selected official command-line tools and the
checksum-pinned LocalSend AppImage. The four AUR applications are built,
inspected, and installed with reviewed one-off commands in a disposable VM; the
latest clean-VM evidence is below. Hyprmon is built separately from its pinned
upstream source. No AUR automation is added to Ansible.

## Upstream review cadence

Review this inventory about once a month, and before changing any source URL,
version pin, checksum, signature key, packaging recipe, or automation. During
each review:

1. Check the official Arch package pages for tracked out-of-date flags and
   compare them with the date/version recorded here. A flag is a prompt to
   investigate, not a reason to install from another source.
2. For AUR and other third-party packages, compare the tracked recipe or source
   commit with upstream. Inspect changed `PKGBUILD`, install hooks, URLs,
   checksums, and signature keys; verify signatures against independently
   established fingerprints. Review release notes for relevant changes.
3. For pinned AppImages, binaries, Flatpaks, and editor tools, confirm the
   upstream project and release, then review the changed artifact permissions,
   hash/signature, and update procedure before moving the pin.
4. Update the review date and record findings or unavailable checks here. Keep
   unsupported checks explicit; an unchanged pin does not prove a safe upstream
   release.

Third-party builds remain manual. A review does not authorize automatic
downloads, recipe execution, or package installation.

Matugen and Hyprpaper are signed packages from Arch's official `extra`
repository: [matugen](https://archlinux.org/packages/extra/x86_64/matugen/) and
[hyprpaper](https://archlinux.org/packages/extra/x86_64/hyprpaper/). Matugen
renders local theme files from repository-owned templates; Hyprpaper restores
the selected local wallpaper. Theme selection does not download a theme or run
third-party hooks.

VM verification: the first full provisioning run installed the official apps
(`ok=42 changed=1 failed=0`); the second reported `ok=42 changed=0 failed=0`.
Neovim startup and Lazygit version output passed. The merged owner editor and
Obsidian's initial vault-selection window were also verified in the VM desktop;
no account sign-in or vault creation was performed.
The installed package manifest and dependency diff are retained in the VM under
`/home/mcuomo/hexen-vm-recovery/packages-after-apps.txt` and
`app-package-diff.txt`.

## Update ownership

`hexen update` handles the signed Arch package transaction, an optional
reviewed fast-forward of this repository, offers per-user migrations after
Pacman succeeds, and can offer a reviewed Ansible convergence. Its source report
checks local pins and installed state only; it does not query application
upstreams. It does not treat every application update as a Pacman update. Use
the owner and procedure below; keep manual or unsupported sources visibly
pending rather than installing an AUR helper or adding an unreviewed repository.

| Software/source | Update owner | Update procedure | Automation status |
| --- | --- | --- | --- |
| Signed Arch packages, including desktop tools, Starship, and language runtimes | Pacman and the Hexen package lists | Review the private daily `hexen update-monitor` report or run `hexen update-monitor review` for package-by-package decisions, then use `hexen update` for a full `pacman -Syu`; change package selection in the Ansible lists and apply through the reviewed provisioner. | Daily detection is scheduled; installation remains explicitly confirmed. Package-level flags do not filter Pacman into a partial upgrade. This does not include other rows or satisfy policies requiring unattended installation without employer confirmation. |
| Bitwarden Desktop | Flatpak from the configured Flathub remote | Run `flatpak update` separately; recheck the app ID, publisher listing, and permissions when changing the source. | Installed by Ansible; updates are separate and have no configured automatic schedule. Update checkpoints capture the installed ref, origin, and commit from local Flatpak metadata; repository signature and remote freshness are not independently checked by that report. |
| Zen, 1Password, Zoom, and Slack | Each vendor source plus its reviewed AUR recipe | Inspect the recipe/source/signature or checksum, build as a normal user, inspect the package archive, then install with Pacman. | Manual only; no AUR helper or unattended recipe refresh. Update checkpoints compare installed versions with the tracked reference-build records and include recipe commits, artifact hashes, and source-check summaries. The recorded hashes identify the reviewed VM artifacts; they do not prove the currently installed archive is identical. See the per-application review below. |
| Walker and Elephant | Pinned upstream commits and reviewed packaging recipes | Review the pinned source and recipe changes, rebuild as a normal user, inspect packages, and install manually. | Manual only; not updated by `pacman -Syu`. Update checkpoints report tracked recipe commits and source archive checksums beside installed package versions, but cannot verify that an installed binary came from those exact pins. See [`sources.lock`](../install/manual-apps/walker/sources.lock). |
| Hyprmon | Pinned upstream source and Go module graph | Review the commit/module changes, build and inspect the binary, then replace the manually installed build. | Manual only; not updated by Pacman. Update checkpoints record the tracked source commit and hash the installed binary when present, but cannot prove that binary was built from that commit. |
| LocalSend | Official pinned AppImage URL and SHA-256 | Review a release, update version/URL/hash together in the desktop role, then reapply the reviewed role. | Provisioned from a pin; no independent package-manager update. |
| Neovim plugins | `config/nvim/lazy-lock.json` and the tracked source pins | Review source/commit changes, update the tracked pin, then run `:Lazy restore`; `:Lazy update` alone does not advance the reviewed pin. | User-level and manual; outside Pacman. Update checkpoints compare local plugin Git HEADs with tracked pins when checkouts are present. This local comparison does not inspect working-tree contents, signatures, or upstream freshness. See the [Neovim update instructions](../config/nvim/README.md#installation-and-updates). |
| Treesitter parsers | `config/nvim/setup.lua`, `config/nvim/lua/config/tools.lua`, and the parser registry | Review the parser/registry changes, update the explicit setup list, then rerun the Neovim setup as the desktop user. | User-level and manual; outside Pacman. Update checkpoints hash installed parser binaries for the tracked language list. The upstream source revisions are not pinned, so hashes identify local bytes but do not establish trusted provenance. |
| Mason tools (Lua LSP, OmniSharp, gopls, basedpyright, Ruff) | Mason plus `config/nvim/setup.lua` and local `mason-receipt.json` files | Review tool release/platform changes, rerun the explicit setup as the desktop user, and refresh the installed receipts. | User-level and manual; update checkpoints record local Mason source IDs, registry version/checksum, and receipt hashes when available. This does not verify the installed executable against its receipt or query upstream freshness. The plugin lockfile does not pin tool versions. See the [Neovim update instructions](../config/nvim/README.md#installation-and-updates). |

## Requested CLI utilities

These requested tools are available from signed Arch `extra` packages; none
requires the AUR. `jq` was already in the desktop package list. The role now adds
the other packages. Arch package names and useful command details:

| Tool | Arch package | Note |
| --- | --- | --- |
| bat | [`bat`](https://archlinux.org/packages/extra/x86_64/bat/) | Bash `cat` alias uses `bat --paging=never`. |
| rsync | [`rsync`](https://archlinux.org/packages/extra/x86_64/rsync/) | File synchronization. |
| FreeRDP | [`freerdp`](https://archlinux.org/packages/extra/x86_64/freerdp/) | Version 3 client command is `xfreerdp3`. |
| jq | [`jq`](https://archlinux.org/packages/extra/x86_64/jq/) | Already installed by the role. |
| yq | [`go-yq`](https://archlinux.org/packages/extra/x86_64/go-yq/) | Arch package name for Mike Farah’s Go-based `yq` CLI; command is `yq`. The separate `yq` package is kislyuk’s jq wrapper. |
| tldr | [`tldr`](https://archlinux.org/packages/extra/any/tldr/) | Community command examples. |
| eza | [`eza`](https://archlinux.org/packages/extra/x86_64/eza/) | Modern `ls` replacement; no alias is forced. |
| btop | [`btop`](https://archlinux.org/packages/extra/x86_64/btop/) | The package page was flagged out-of-date on 2026-10-25; it remains an official signed package. |
| fzf | [`fzf`](https://archlinux.org/packages/extra/x86_64/fzf/) | Fuzzy finder. |
| just | [`just`](https://archlinux.org/packages/extra/x86_64/just/) | Project command runner. |
| GitHub CLI (`gh`) | [`github-cli`](https://archlinux.org/packages/extra/x86_64/github-cli/) | The package page was flagged out-of-date on 2026-10-21; it remains an official signed package. |
| sd | [`sd`](https://archlinux.org/packages/extra/x86_64/sd/) | Intuitive, regex-aware find and replace; installed from signed Arch `extra`. |
| zip | [`zip`](https://archlinux.org/packages/extra/x86_64/zip/) | Create and modify `.zip` archives; `unzip` is already installed for extraction. `tar` is included through the Arch `base` package group. |

Additional requested tools are also in the official repository:

| Tool | Arch package | Note |
| --- | --- | --- |
| Lazydocker | [`lazydocker`](https://archlinux.org/packages/extra/x86_64/lazydocker/) | Uses Podman's rootless Docker-compatible socket; Compose commands are configured as `podman compose`. |
| Bluetui | [`bluetui`](https://archlinux.org/packages/extra/x86_64/bluetui/) | BlueZ Bluetooth TUI; opened by Super+Shift+I in a centered floating Ghostty window. |
| Yazi | [`yazi`](https://archlinux.org/packages/extra/x86_64/yazi/) | `fd`, `fzf`, `jq`, `ripgrep`, and `wl-clipboard` are already selected; media/archive/PDF previews have optional dependencies. |
| Navi | [`navi`](https://archlinux.org/packages/extra/x86_64/navi/) | Uses the already selected `fzf`. |
| dust | [`dust`](https://archlinux.org/packages/extra/x86_64/dust/) | Disk-usage viewer. |
| tokei | [`tokei`](https://archlinux.org/packages/extra/x86_64/tokei/) | Code line counter. |
| pgcli | [`pgcli`](https://archlinux.org/packages/extra/any/pgcli/) | PostgreSQL interactive CLI. |
| Git diff pager | [`git-delta`](https://archlinux.org/packages/extra/x86_64/git-delta/) | Configured as the global Git pager with side-by-side output, line numbers, and navigation. |
| Podman | [`podman`](https://archlinux.org/packages/extra/x86_64/podman/) | Rootless container engine from `extra`; no Docker Desktop or rootful Docker daemon. |
| Podman Compose | [`podman-compose`](https://archlinux.org/packages/extra/any/podman-compose/) | Provider used by `podman compose` and LazyDocker. |

[`difftastic`](https://archlinux.org/packages/extra/x86_64/difftastic/) is
another official option for syntax-aware structural diffs, but it is not the
default pager here. Delta is the smaller, general-purpose everyday viewer.
The optional `podman-docker` package is intentionally not installed: this setup
uses `podman` explicitly and leaves the `docker` command name available for a
future Docker Engine installation.

The official package path uses pacman signatures and normal full-system
upgrades. The out-of-date flags are a freshness signal, not an AUR requirement;
review those package pages again when refreshing this inventory.

## Source and update inventory

| Application | Source and package | Update path | Current decision |
| --- | --- | --- | --- |
| Neovim | [Upstream](https://neovim.io/doc/install/), signed Arch `extra/neovim` | Full `pacman -Syu` | Automated; observed 0.12.6-1. Owner configuration merged and tested; see editor inventory below. |
| Lazygit | [Upstream](https://github.com/jesseduffield/lazygit), signed Arch `extra/lazygit` | Full `pacman -Syu` | Automated; observed 0.66.2-1. |
| Obsidian | [Vendor](https://obsidian.md/download), signed Arch [extra/obsidian](https://archlinux.org/packages/extra/x86_64/obsidian/) | Full `pacman -Syu` | Automated; observed 1.14.5-1, using Arch's electron43 dependency. App is proprietary; official repository does not mean open source. |
| OBS Studio | [Upstream](https://obsproject.com/), signed Arch [extra/obs-studio](https://archlinux.org/packages/extra/x86_64/obs-studio/) | Full `pacman -Syu` | Automated; official package was flagged out-of-date on 2026-10-23, so refresh this source review before relying on a particular feature/version. Hyprland screen capture uses the existing PipeWire portal. |
| Zed | [Upstream](https://zed.dev/), signed Arch [extra/zed](https://archlinux.org/packages/extra/x86_64/zed/) | Full `pacman -Syu` | Automated; checked 2026-10-28. Provides `/usr/bin/zeditor` and the `dev.zed.Zed` desktop entry. It opens in the clean VM, but its log records Vulkan adapter initialization failure and software-emulated llvmpipe. VM provisioning selects `vulkan-virtio`, but the VM's virtio video device has no 3D acceleration enabled. Select and verify a compatible provider on physical hardware; the VM GPU criterion remains open. |
| Zen Browser | [Vendor downloads](https://zen-browser.app/download/), candidate [zen-browser-bin](https://aur.archlinux.org/packages/zen-browser-bin) | Review updated AUR recipe, rebuild and install via pacman | Installed in the older acceptance VM and clean rehearsal VM (`hexen-rehearsal-20261027`). On 2026-10-28 the clean VM built recipe commit `ff5b152a31356577936690ccd32599e851326b85` for 1.23.4b-1; its release archive passed SHA-256 verification. The package registers `zen.desktop` for HTTP/HTTPS. `xdg-open` launched a Google URL, and the live Hyprland client list showed the Google Search page in Zen. |
| 1Password | [Vendor Arch instructions](https://support.1password.com/install-linux/#arch-linux), candidate [1password](https://aur.archlinux.org/packages/1password) | Review updated AUR recipe and vendor signing key, rebuild | Clean rehearsal VM built and installed 8.12.42-36 from pinned recipe `c384584bedaa1ffebd3939d03a52bf4ff48e2bff`; vendor signature and archive were checked. The launch created a Crash Reporter window instead of the welcome screen; investigate before accepting. GNOME keyring service is active. Account sign-in remains owner-only. |
| Bitwarden Desktop | [Verified Flathub listing](https://flathub.org/en/apps/com.bitwarden.desktop), app ID `com.bitwarden.desktop` | `flatpak update` (separate from `pacman -Syu`; no automatic update schedule configured) | Automated system Flatpak install through the system `flathub` remote. Rehearsal VM installed version 2026.10.0 and opened its login screen without sign-in. Flatpak permissions include all devices, network, Wayland/X11, Secret Service, and specific browser/native-messaging paths; review upstream permissions on refresh. GNOME keyring and `libsecret` are installed and active. Vault setup and browser-extension integration remain owner-only and untested. |
| Zoom | [Vendor Arch package](https://zoom.us/download/linux), candidate [zoom](https://aur.archlinux.org/packages/zoom) | Review versioned AUR recipe and rebuild; vendor `pacman -U` is an alternative manual path | Clean rehearsal VM built and installed 7.2.1-1 from pinned recipe `9cf1e9686715d0677db2eb4106c2d59aee6d7ca0`; source SHA-512 passed and the Zoom Workplace window opened. On the later unlocked visual check, a “Zoom quit unexpectedly” report was visible over the Workplace window; root cause is unresolved. Call devices and screen sharing still need live acceptance. Under Wayland, Zoom documents whole-desktop or whiteboard sharing; application-window sharing requires Xorg. |
| Slack | [Vendor Linux instructions](https://slack.com/help/articles/212924728-Download-Slack-for-Linux--beta-), candidate [slack-desktop](https://aur.archlinux.org/packages/slack-desktop) | Review updated AUR recipe and rebuild | Clean rehearsal VM built and installed 4.52.182-1 from pinned recipe `67c43c14906ddc96749f3c9b682bd9f5894d7251`; source BLAKE2 checks passed and the Slack sign-in window opened. Repackages vendor Debian binary; Arch packaging is community maintained. |
| Hyprmon | [Upstream](https://github.com/erans/hyprmon), pinned source build | Review pinned commit and Go module graph, then rebuild | Clean rehearsal VM built commit `32ad27f94f40fd0dd81f982cc8208bb615607202`; `go test ./...` passed and the Hexen Display settings entry opened Hyprmon in Ghostty. Applying/saving a monitor arrangement remains untested. |
| LocalSend | [Official Linux downloads](https://localsend.org/download), official GitHub [1.18.2 x86_64 AppImage](https://github.com/localsend/localsend/releases/download/v1.18.2/LocalSend-1.18.2-linux-x86-64.AppImage) | Desktop role downloads the pinned release with SHA-256 verification | Installed in the VM from the official AppImage; its SHA-256 matched the recorded pin. Version, URL, and hash are in `ansible/roles/desktop/defaults/main.yml`. Upstream also lists `localsend-bin` from AUR; this setup uses the official AppImage and does not run AUR recipes. |

LocalSend is not an official Arch repository package. The desktop role downloads
the upstream x86_64 AppImage with SHA-256 verification and creates a per-user menu
entry. It requires the official `fuse2` runtime included in the desktop role.
LocalSend transfers over the local network; if a firewall is enabled, allow its
configured TCP and UDP ports only on trusted LANs. The default port is 53317;
see the [ArchWiki LocalSend entry](https://wiki.archlinux.org/title/LocalSend).

At the 2026-10-26 VM checkpoint, the refreshed official package databases
contained Neovim, Lazygit, and Obsidian; the manual candidate packages were not
in the official repositories. OBS Studio was added to the automatic official
package role on 2026-10-27. As of that checkpoint, no third-party pacman
repository, Flatpak remote, AUR helper, or downloaded installer script had
been added. The current Bitwarden addition uses the system Flathub remote; no
AUR helper or downloaded installer script is used. A vendor public key was
imported only into the VM build user's GPG keyring for source verification, as
recorded below.

## AUR recipe inspection

The following commits identify the exact recipes inspected, built as the normal
VM user, and installed after archive inspection. They do not assure later
updates or constitute an audit of proprietary application binaries. Maintainer
comments are recipe claims, not independently verified identities. All declared
source checksums passed; 1Password's detached vendor signature also passed.

| Recipe | Inspected commit | Version |
| --- | --- | --- |
| `zen-browser-bin` | `ff5b152a31356577936690ccd32599e851326b85` | 1.23.4b-1 |
| `1password` | `c384584bedaa1ffebd3939d03a52bf4ff48e2bff` | 8.12.42-36 |
| `zoom` | `9cf1e9686715d0677db2eb4106c2d59aee6d7ca0` | 7.2.1-1 |
| `slack-desktop` | `67c43c14906ddc96749f3c9b682bd9f5894d7251` | 4.52.182-1 |

### Zen

The recipe names Luis Vervaet as maintainer. It downloads a versioned binary
tarball from `github.com/zen-browser/desktop/releases`, with SHA-256 hashes for
the x86_64/aarch64 payloads and local launcher, desktop entry, and policies.
No detached upstream signature is declared. Its package function copies into
`/opt/zen-browser-bin`, installs launchers/icons, and uses system dictionaries
and certificate storage. There is no install script.

The inspected `policies.json` disables in-app updates and sets
`DefaultSerialGuardSetting` to 3. Updates therefore depend on rebuilding the
package; those browser-policy changes are part of the review. The executable
desktop entries launch `/opt/zen-browser-bin/zen-bin`; the wrapper is
`/usr/bin/zen-browser`. Do not use an unrelated repository with signature checks
disabled. Browser-extension integration with 1Password must be tested separately.

### 1Password

The recipe downloads a versioned vendor tarball and detached signature from
`downloads.1password.com`. It declares SHA-256 hashes and restricts verification
to fingerprint `3FEF9748469ADBE15DA7CA80AC2D62742012EA22`, matching the vendor's
published Linux signing fingerprint at review time. The vendor's own installation
guide directs Arch users to this AUR package. This does not make the AUR itself
a signed Arch repository.

The package function installs into `/opt/1Password`, installs icons/desktop
integration and a Polkit policy generated from the build host's first ten
four-digit-UID users. It uses shell `eval` to expand a vendor policy template.
This makes the build-host account list relevant: inspect the resulting policy
before installing the package on another machine.

The root-run install script creates a `onepassword` group and makes
`1Password-BrowserSupport` setgid to that group. The build also sets the
`chrome-sandbox` executable to mode 4755. These are intentional privileged
integration helpers and must be inspected in the resulting package. Do not add
the user to the helper group. Uninstall removes the group. During VM validation, the vendor public key was
fingerprint-checked against its official documentation and imported only into
the build user's GPG keyring. The source signature passed. Installation created
the documented helper group/permissions; the desktop user was not added to that
group. The generated Polkit owners list contains only `unix-user:mcuomo`.

The [vendor notes](https://support.1password.com/install-linux/) that sandboxed
Snap/Flatpak distributions lack system-unlock, SSH-agent, and desktop/browser
integration features; that is why native packaging is the candidate here.

### Zoom

The recipe names Gordian Edenhofer and Christian Heusel as maintainers. It
downloads the versioned vendor Arch archive from
`zoom.us/client/7.2.1.5760/zoom_x86_64.pkg.tar.xz`, verifies a SHA-512 checksum,
and copies its `opt` and `usr` trees without preserving upstream ownership.
No detached signature or install script is declared. The vendor supports
manual installation of its Arch archive through `pacman -U`; see its
[Linux instructions](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0063458).
That manual archive does not establish an automatic pacman update source.

The recipe declares X11/PulseAudio/GTK libraries and Mesa among its dependencies.
The desktop role installs PipeWire, WirePlumber,
`xdg-desktop-portal-hyprland`, and selects Hyprland as the ScreenCast portal
backend. These provide the Wayland capture path, but do not by themselves prove
microphone/camera or Zoom screen sharing works. Zoom's current Linux help says a
Wayland session can share the entire desktop or a whiteboard, while sharing one
application window requires Xorg. This setup remains Hyprland/Wayland, so the
supported native Zoom workflow is whole-desktop sharing. Do not install optional
X11 compositors merely because they appear in `optdepends`.

### Slack

The recipe names Oscar Garcia Amor as maintainer. It downloads a versioned
`.deb` from `downloads.slack-edge.com` and checks BLAKE2 hashes for that artifact
and a local desktop-entry patch. No detached signature or install script is
declared. Its package function extracts the Debian data archive, patches the
launcher, adjusts directory permissions, removes bundled `/etc` and irrelevant
documentation, and relocates the license.

The patch changes the launch command to `slack --gtk-version=3 -s` and uses the
themed icon name. Review these flags with desktop testing. `libsecret` is a
dependency, but that alone does not provide an unlocked Secret Service session.
Decide and test the desktop keyring before work sign-in. Do not disable the
Electron sandbox to make an untested desktop launch succeed.

## Manual installation procedure after review

Run as a normal build user in the disposable VM first. Substitute one package
name from the table, clone its exact AUR repository, and inspect all tracked
files. Do not run `makepkg` as root. Inspect recipe updates before rebuilding.

```sh
git clone https://aur.archlinux.org/PACKAGE_NAME.git
cd PACKAGE_NAME
git rev-parse HEAD
git ls-files
less PKGBUILD .SRCINFO
# Read every referenced install script, patch, policy, and launcher too.
makepkg --verifysource
makepkg --syncdeps
pacman -Qip ./ACTUAL_BUILT_PACKAGE.pkg.tar.zst
bsdtar -tvf ./ACTUAL_BUILT_PACKAGE.pkg.tar.zst
sudo pacman -U ./ACTUAL_BUILT_PACKAGE.pkg.tar.zst
```

`makepkg` sources the recipe even for source verification; perform the text
review first. For 1Password, independently compare the vendor key fingerprint
before importing it into the build user's GPG keyring. Do not skip PGP checks.
The package archive suffix may differ from the example; inspect the actual
output rather than assuming its filename. Review any additional AUR dependencies
with the same process. Installing dependencies through pacman should use a
fully updated system; never use a database-only refresh followed by a partial
upgrade.

## Desktop and editor sources

The owner supplied `mykeelium/nvim-config` and requested Base plus additions
from Numen and Arcana. The imported commit is
`e45b8249bfb152c20f9089100ca95f00eeef5ba1`. See
[editor provenance and setup](../config/nvim/README.md) and the
[34-plugin source/commit inventory](../config/nvim/PLUGIN-SOURCES.md).
Only source configuration and lockfiles were copied; the upstream `nvim-data`
cache and machine binaries were excluded. The local host config was not changed.

Plugin-manager bootstrap is pinned to the owner's lockfile. Plugins and build
hooks run as the desktop user. The explicit `setup.lua` step installs 13 grammar
parsers from the pinned Treesitter registry and five tools through Mason:
Lua language server, OmniSharp, gopls, basedpyright, and Ruff. These downloads
use upstream GitHub/PyPI/Go channels and are outside pacman's signature/update
system. Their installed versioned identifiers are recorded in the editor README
and Mason receipts; a plugin lockfile does not pin those tool versions. Normal
editor startup does not automatically install language tools.

The optional desktop role installs official Arch packages. Its complete
common list in `ansible/roles/desktop/defaults/main.yml` includes Hyprland,
Ghostty, Zellij, Waybar, Mako, Nautilus, PipeWire/WirePlumber, portals, lock/idle and
clipboard tools, fonts, and editor dependencies. The install-time launcher
defaults to Walker, using the separately reviewed manual package set; Fuzzel
remains available as an explicit choice. These include Python/pynvim,
Go and Delve, Node/npm, uv, .NET SDK, and the parser/compiler/search tools.
No system-wide pip/npm install is performed. Fonts and runtime dependencies
are explicit package choices rather than downloads hidden in a theme framework.

Walker and Elephant are not selected from official Arch repositories in this
setup. The Walker default uses pinned, reviewed AUR packaging recipes that fetch versioned
upstream Walker/Elephant GitHub sources with SHA-256 checks; see
[`install/manual-apps/walker/`](../install/manual-apps/walker/). Those builds
remain manual and are not updated by `pacman -Syu`. The Fuzzel choice uses the
official `extra/fuzzel` package. The four third-party
applications were installed after the manual validation
below. GUI and work-account integrations remain pending.

## Running .NET Framework applications on Arch

The desktop role installs Arch's signed official [`extra/mono`](https://archlinux.org/packages/extra/x86_64/mono/)
package; it does not use the AUR and Wine is not installed. Mono is a native
Linux implementation rather than Microsoft's Windows-only .NET Framework.
Mono 5.18 added .NET Framework 4.7.2 reference assemblies for targeting, and
the current Arch `mono` package includes its `4.7.2-api` assemblies. It can run
many compatible managed apps directly with `mono app.exe`, but it is not a
complete substitute for Microsoft .NET Framework. The Mono compatibility guide
lists WPF as unimplemented and WCF/ASP.NET support as limited. Rider documents
that it can build .NET Framework projects with MSBuild or Mono's XBuild and can
detect Mono on Linux. The `mono` package includes XBuild. Check each app's Windows-specific API and UI dependencies;
unsupported apps still require Windows. See [the desktop guide](desktop.md#packages-services-and-data).

A full repository refresh on 2026-10-26 resolved an initial mirror 404 for a
`python-dbus` signature; signature checking was never disabled. That full
upgrade updated btrfs-progs, libsoup3, and llvm-libs, with the same kernel version.
The desktop transaction then installed its signed dependencies. Its package
manifest/diff are saved under `/home/mcuomo/hexen-vm-recovery/` in
`packages-after-desktop.txt` and `desktop-package-diff.txt`.


## Manual VM installation evidence, 2026-10-26

The owner requested continued implementation. Manual here means a reviewed,
one-off source/build/inspection/install sequence, not an unattended AUR helper
or Ansible build task. The agent executed those commands in the disposable VM
as the normal build user; root was used only for signed dependency installation
and the final inspected `pacman -U` transaction. No builds ran as root, no
signature checks were bypassed, and no trust prompts were auto-approved.

- Current remote recipe heads matched the recorded reviewed commits.
- All four `makepkg --verifysource` checks passed. 1Password also passed its
  detached OpenPGP check with the independently compared vendor fingerprint.
  Other recipes use hashes and HTTPS without a detached upstream signature.
- Missing official dependencies were installed as dependencies: `mailcap`
  (provides `mime-types`), `dbus-glib`, `ttf-dejavu` (provides `ttf-font`), `libxss`.
- Builds completed without root or recipe-driven sudo. Every archive path and
  uid/gid was inspected; all stored owners were root. The only install script was
  exactly the reviewed `1password.install`. The only privileged archive modes
  were the expected 4755 Chromium sandbox helpers in 1Password and Slack.
- 1Password's build emitted `libfakeroot internal error: payload not recognized`
  during tidying but exited successfully. Archive ownership/mode assertions and
  post-install integrity checks passed; the warning is retained in the build log.
- Root rechecked every artifact SHA-256 before one `pacman -U` transaction.
  The local packages are unsigned AUR builds, not signed Arch packages. The
  1Password *source* signature is a separate trust property.
- `pacman -Qkk` reports zero altered files for Zen, Zoom, and Slack. 1Password's
  only altered file is BrowserSupport: its reviewed install script intentionally
  changes group to `onepassword` and mode to 2755. Its sandbox is root:root 4755;
  Slack's sandbox is root:root 4755. The desktop user remains outside the helper
  group. No new systemd service/autostart unit was found in the inspected archives.

Recipe trees, source artifacts, `verify.log`, `build.log`, and built archives
are retained under `/home/mcuomo/hexen-vm-builds/`. The build manifest is
`verified-packages.json`; a portable record is in
[`install/manual-apps/validation-2026-10-26.json`](../install/manual-apps/validation-2026-10-26.json).
Hashes identify this inspected VM build; generated policy/account content and
build timestamps mean a fresh build can differ. Rebuild and review per target.
Package manifests, transaction/integrity logs, and package diffs are under
`/home/mcuomo/hexen-vm-recovery/`. Snapshot 4 precedes this installation.

## Clean rehearsal VM application pass, 2026-10-28

This pass targets `hexen-rehearsal-20261027`, not the historical VM above.
Packages were built as `mcuomo`; official missing dependencies were installed
through signed pacman repositories. No AUR helper, third-party pacman
repository, or signature bypass was used. The owner created the GNOME keyring;
`gnome-keyring-daemon.service` is active. No account was signed in.

- `1password` 8.12.42-36, recipe commit
  `c384584bedaa1ffebd3939d03a52bf4ff48e2bff`: the vendor source SHA-256 and
  detached signature passed. The primary fingerprint was checked against
  1Password's [published Arch instructions](https://support.1password.com/install-linux/).
  Its package archive and install script were inspected before installation.
  `pacman -Qkk` reports only the expected `BrowserSupport` group/permission
  change (`root:onepassword`, mode 2755); both Electron sandbox helpers are
  `root:root` mode 4755. `mcuomo` is not in the `onepassword` group. Launching
  produced a Hyprland client titled `1Password Crash Reporter`, not the normal
  app welcome screen. A later launch with Chromium GPU acceleration disabled
  (`--disable-gpu`) reached the normal `Welcome — 1Password` window. This is
  evidence of a VM graphics-path interaction, not proof of the exact crash
  cause; the VM has no accelerated virtio GPU. Keep software rendering as a
  diagnostic workaround only, and verify the normal launch path on hardware.
  No account was signed in. The app's native integration also wrote its normal
  browser messaging manifests during launch.
- `slack-desktop` 4.52.182-1, recipe commit
  `67c43c14906ddc96749f3c9b682bd9f5894d7251`: both BLAKE2 source checks passed.
  The archive has no install script; its root-owned Chromium sandbox is mode
  4755. The Slack sign-in window opened. `pacman -Qkk` found no changed files.
- `zoom` 7.2.1-1, recipe commit
  `9cf1e9686715d0677db2eb4106c2d59aee6d7ca0`: its source SHA-512 passed. This
  is Zoom's current Linux build in the [official release notes](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0061222)
  checked 2026-10-28; the listed 7.2.2 is macOS-only. The package has no install
  script or special-permission files. The Zoom Workplace window opened, then a
  “Zoom quit unexpectedly” report was visible over it on the later unlocked
  check. A Zoom Workplace window is currently running after the earlier crash,
  but the crash cause remains unresolved; camera, microphone, meeting and
  sharing are intentionally left for a real-device acceptance pass.
- Hyprmon commit `32ad27f94f40fd0dd81f982cc8208bb615607202` passed
  `go test ./...`, built with Go 1.27.3, and opened in Ghostty from the Hexen
  Display settings command. No monitor arrangement was applied or saved.
- Zed 1.25.3-1 opens in the VM. Its log reports Vulkan adapter initialization
  failure and selects software-emulated `llvmpipe`. The selected
  `vulkan-virtio` package is installed, but the VM's virtio video device has no
  3D acceleration configured. `pacman -Qkk` found no altered Zed files. The
  GPU acceptance requirement remains open; do not infer physical GPU behavior
  from this VM.
- Zen 1.23.4b-1 is the default HTTP/HTTPS handler. The live Hyprland client list
  showed `another test - Google Search — Zen Browser` after the Walker search
  activation. Walker's app matching, `1+1` calculation and Google search result
  were verified in the same VM.

### Bitwarden Flathub follow-up, 2026-10-28

The apps role added Arch `flatpak` 1:1.18.4-2, the system `flathub` remote, and
`com.bitwarden.desktop` version 2026.10.0. Flathub identifies the listing as
verified by Bitwarden Inc. An isolated apps-role run completed with
`ok=4 changed=2 failed=0`; the second run completed with `ok=4 changed=0
failed=0`. The app launched into its login screen and appeared as a mapped
Hyprland window. No account was signed in and no vault was imported.

The app metadata allows network and IPC, Wayland/X11 sockets, all devices, the
Secret Service and specifically listed browser/native-messaging directories.
Its Flatpak does not grant unrestricted home-directory access. The VM has
`libsecret` 0.21.8.2-1 and GNOME keyring 1:51.1-1, with the user keyring service
active. The app log could not create native-messaging sockets under the
non-Flatpak Zen profile, so browser integration is not accepted by this pass.
An autostart portal was also unavailable; no autostart was configured. The
VM's Zoom crash record was left intact. During a later diagnostic pass,
1Password's earlier crash reporter was closed and the app was relaunched with
`--disable-gpu`; it reached its normal welcome window. This narrowed the issue
to the VM graphics path but did not prove the underlying cause. Zoom's saved
crash metadata records SIGSEGV in its own process while calling GLib's
`g_spawn_command_line_sync`; a later Workplace window is running, but the
initial crash has not been explained.

`pacman -Qkk` found zero altered files for Zoom, Slack, Zed and Zen; the sole
1Password difference is the expected helper GID/mode from its install script.
The installed local package archives and Hyprmon binary remain in the VM under
`/home/mcuomo/build/hexen-manual-apps/` and `/home/mcuomo/.local/bin/`. These are
unsigned local AUR builds; review and rebuild them for updates. Outstanding
work: test 1Password's normal GPU-enabled launch on hardware, resolve or scope
Zed's GPU criterion, exercise the browser keybindings and private-session
behavior, test normal lock/reboot behavior, test Bitwarden browser integration
on a supported browser profile, and run the clean provisioning zero-change
check.

The clean VM reports `zen.desktop` for HTTP/HTTPS after installing Zen as its
only browser, and `xdg-open` started the browser with a test URL. Verify the
default handler on machines that already have another browser installed.
On 2026-10-28, the deployed `hexen-desktop browser-private` helper opened a
`Zen Browser Private Browsing` window alongside the existing normal Zen window.
Hyprland reports both Browser and Private browser bindings loaded. This verifies
the helper and target application; an actual physical keypress and private
session browsing behavior remain untested.
1Password/Zen extension integration still needs explicit configuration and
acceptance. Account sign-in is owner-only.
The [vendor custom-browser procedure](https://support.1password.com/additional-browsers/)
and [Zen integration guide](https://docs.zen-browser.app/guides/1password) describe
allowing `zen-bin`; no browser trust allowlist has been changed yet.
