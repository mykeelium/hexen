# Walker manual package setup

Walker is an optional install-time launcher choice. It needs Walker, Elephant,
and six Elephant providers before provisioning can select it. The exact recipe
commits and upstream source hashes are in [`sources.lock`](sources.lock).

The recipes are community-maintained AUR `PKGBUILD`s; the recipes inspected here
fetch versioned source archives from the upstream Walker and Elephant GitHub
projects and verify them with SHA-256. The recipe revisions listed in the lock
file contain no install scripts. They build Walker with Cargo and Elephant and
its providers with Go, then stage the binary, plugins, and upstream license.
That review applies to those exact commits only. Review every recipe and source
again before updating.

Provisioning does not clone recipes, build packages, or add a pacman repository.
Build as the regular desktop user and install the exact inspected archives
yourself. Do not use an AUR helper or run `makepkg` as root.

## Build and inspect

Start from a fully updated Arch installation. The base setup supplies
`base-devel`; Walker's source build additionally needs Cargo, Go, and the
declared official dependencies. `makepkg --syncdeps` resolves official
dependencies such as `gtk4-layer-shell`, `poppler-glib`, `cairo`, `fd`, and
`libqalculate`. Recheck these against the current recipe and system before
building.

Clone each recipe and check out the exact commit from `sources.lock`:

```sh
mkdir -p "$HOME/build/hexen-walker"
cd "$HOME/build/hexen-walker"

git clone https://aur.archlinux.org/walker.git
git -C walker checkout a801f3cc3be208a8cd188b2072087af1a413aecf

git clone https://aur.archlinux.org/elephant.git
git -C elephant checkout fa4ae49703d0f1a2b47d3a93f0a373fb404aff39

git clone https://aur.archlinux.org/elephant-desktopapplications.git
git -C elephant-desktopapplications checkout fec5937952dc3f320cef9741b401478aa26e5a57

git clone https://aur.archlinux.org/elephant-files.git
git -C elephant-files checkout 2088f75f6ff637c339c55ec01a1bbd36ae6b8ffa

git clone https://aur.archlinux.org/elephant-runner.git
git -C elephant-runner checkout 01254600069cdadc8317af9416f50e3b68b7b76e

git clone https://aur.archlinux.org/elephant-calc.git
git -C elephant-calc checkout 5c2979c6790aeb19c686f19147e63e37b67c73ed

git clone https://aur.archlinux.org/elephant-websearch.git
git -C elephant-websearch checkout 8c76e2deaf63cd7800702a160bdffae5972a1842

git clone https://aur.archlinux.org/elephant-providerlist.git
git -C elephant-providerlist checkout 96ce4305a7b8a217f348890fc66410af7cedec02
```

Inspect every checked-out `PKGBUILD` and `.SRCINFO` before running it. Confirm
the source URLs and hashes match `sources.lock`, and inspect changes if the
selected commits differ. Then verify and build each recipe as your normal user:

```sh
for package in walker elephant elephant-desktopapplications elephant-files elephant-runner elephant-calc elephant-websearch elephant-providerlist; do
  (
    cd "$package"
    git status --short
    git rev-parse HEAD
    sed -n '1,240p' PKGBUILD
    cat .SRCINFO
    makepkg --verifysource
    makepkg --syncdeps
  )
done
```

When adding web search to an existing installation, rebuild Elephant and all
its providers together with the same Go toolchain; matching release numbers
alone do not guarantee Go plugin compatibility.

Before installation, inspect each generated archive's package metadata, file
list, ownership, modes, and SHA-256. Confirm the providers install only their
plugin under `/usr/lib/elephant/` and the expected license files; Walker also
installs its binary and default theme/config assets. The reviewed recipes have
no install scripts. Install only the eight exact archives produced by the
builds, in one explicit transaction:

```sh
sudo pacman -U \
  ./walker/walker-2.17.2-1-ARCH.pkg.tar.zst \
  ./elephant/elephant-2.22.1-1-ARCH.pkg.tar.zst \
  ./elephant-desktopapplications/elephant-desktopapplications-2.22.1-1-ARCH.pkg.tar.zst \
  ./elephant-files/elephant-files-2.22.1-1-ARCH.pkg.tar.zst \
  ./elephant-runner/elephant-runner-2.22.1-1-ARCH.pkg.tar.zst \
  ./elephant-calc/elephant-calc-2.22.1-1-ARCH.pkg.tar.zst \
  ./elephant-websearch/elephant-websearch-2.22.1-1-ARCH.pkg.tar.zst \
  ./elephant-providerlist/elephant-providerlist-2.22.1-1-ARCH.pkg.tar.zst
```

Replace `ARCH` with the actual architecture suffix and use the exact filenames
reported by `makepkg`; do not assume the examples match a later package release.
Review pacman's transaction before accepting it. Re-run provisioning and choose
Walker after installation. Standard `pacman -Syu` does not update these manual
packages. Updates require review of recipe changes and new upstream source
hashes, source verification, a normal-user build, archive inspection, and an
explicit pacman install.

This pins the packaging inputs and verifies the fetched source archives; it
does not promise bit-for-bit reproducible build output or pin Arch's rolling
runtime dependencies.
