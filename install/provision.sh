#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage: install/provision.sh [--vm] [--help]

Provision this Arch Linux installation with the repository's system and desktop
configuration. Run it as the account that should own the desktop configuration,
not as root. It does not partition disks or run Archinstall.

--vm leaves libvirt's default network unmanaged to avoid a nested NAT subnet
collision. It still provisions the desktop, libvirt sockets, and storage pool.
EOF
}

vm_mode=false
while (( $# )); do
  case "$1" in
    --vm) vm_mode=true ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
  shift
done

if (( EUID == 0 )); then
  printf 'Run this script as your regular desktop account, not root.\n' >&2
  exit 1
fi

if [[ ! -f /etc/arch-release ]]; then
  printf 'This provisioning entrypoint supports Arch Linux only.\n' >&2
  exit 1
fi

if [[ ! -t 0 ]]; then
  printf 'Run this script from an interactive terminal.\n' >&2
  exit 1
fi

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
desktop_user="$(id -un)"
network_summary='It starts the standard libvirt NAT network and default VM storage pool.'
if [[ $vm_mode == true ]]; then
  network_summary='VM mode leaves libvirt networks unmanaged and configures the default VM storage pool.'
fi

if ! command -v ansible-playbook >/dev/null 2>&1 || ! command -v ansible-galaxy >/dev/null 2>&1; then
  cat >&2 <<'EOF'
Ansible is not installed. First update the Arch system and install Ansible:

  sudo pacman -Syu ansible

Reboot if the update replaced the kernel or other components that need a restart,
then run this script again.
EOF
  exit 1
fi

cat <<EOF
This will provision the local Arch installation for user: ${desktop_user}
Repository: ${repo_root}

It audits the existing boot setup, installs declared system and desktop packages,
enables configured services, creates root Snapper configuration, and links the
repository's desktop and Neovim configuration into that user's home directory.
This includes OpenVPN/NetworkManager support and a virt-manager QEMU/KVM host.
${network_summary}
Ansible will ask for sudo authorization when required.

It does not partition disks, change encryption, or install the manually reviewed
Zen, 1Password, Zoom, and Slack packages. Bitwarden Desktop is installed by the
apps role from Flathub. Keep this repository at its current path after
provisioning because the desktop configuration links point here.
EOF

read -r -p 'Continue? [y/N] ' answer
case "$answer" in
  y|Y|yes|YES) ;;
  *)
    printf 'Provisioning cancelled.\n'
    exit 0
    ;;
esac

read -r -p 'Desktop launcher [walker/fuzzel] (default: walker): ' launcher_choice
desktop_launcher="${launcher_choice:-walker}"
case "$desktop_launcher" in
  fuzzel|walker) ;;
  *)
    printf 'Invalid launcher choice: %s. Choose fuzzel or walker.\n' "$desktop_launcher" >&2
    exit 2
    ;;
esac

if [[ $desktop_launcher == walker ]]; then
  walker_packages=(walker elephant elephant-desktopapplications elephant-files elephant-runner elephant-calc elephant-websearch elephant-providerlist)
  if ! pacman -Q "${walker_packages[@]}" >/dev/null 2>&1; then
    cat >&2 <<'EOF'
Walker was selected, but its reviewed manual packages are not installed.
Follow install/manual-apps/walker/README.md, install the pinned packages, then
run this provisioner again and choose Walker. No AUR helper or repository is
used by this script.
EOF
    exit 1
  fi
  for executable in walker elephant; do
    if ! command -v "$executable" >/dev/null 2>&1; then
      printf 'Walker executable is missing from PATH: %s\n' "$executable" >&2
      printf 'Follow install/manual-apps/walker/README.md and rerun provisioning.\n' >&2
      exit 1
    fi
  done
  for provider in desktopapplications files runner calc providerlist; do
    if [[ ! -f "/usr/lib/elephant/${provider}.so" ]]; then
      printf 'Walker provider is missing: /usr/lib/elephant/%s.so\n' "$provider" >&2
      printf 'Follow install/manual-apps/walker/README.md and rerun provisioning.\n' >&2
      exit 1
    fi
  done
fi

export ANSIBLE_CONFIG="${repo_root}/ansible/ansible.cfg"
extra_vars=(-e "desktop_user=${desktop_user} desktop_launcher=${desktop_launcher}")
if [[ $vm_mode == true ]]; then
  extra_vars+=(-e desktop_libvirt_manage_default_network=false)
  extra_vars+=(-e '{"desktop_vulkan_driver_packages":["vulkan-virtio"]}')
fi

ansible-galaxy collection install -r "${repo_root}/ansible/requirements.yml"
ansible-playbook --syntax-check \
  -i "${repo_root}/ansible/inventory/localhost.yml" \
  "${repo_root}/ansible/playbook.yml" \
  "${extra_vars[@]}"
ansible-playbook \
  -i "${repo_root}/ansible/inventory/localhost.yml" \
  "${repo_root}/ansible/playbook.yml" \
  "${extra_vars[@]}" \
  --ask-become-pass
