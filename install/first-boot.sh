#!/usr/bin/env bash
# Run as the newly installed regular user, from a permanent Hexen checkout.
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
trap 'printf "\nSetup stopped. Read the error above, correct it, then rerun this command. Your terminal remains open.\n" >&2' ERR
usage() {
  printf 'Usage: ./install/first-boot.sh [--vm] [--hardware generic|xps-14-9440]\nRun from a permanent checkout as your regular Arch account.\n'
}
vm_mode=false
hardware_profile=''
while (( $# )); do
  case "$1" in
    --help|-h) (( $# == 1 )) || { usage >&2; exit 2; }; usage; exit 0 ;;
    --vm) [[ $vm_mode == false ]] || { usage >&2; exit 2; }; vm_mode=true ;;
    --hardware) (( $# >= 2 )) || { usage >&2; exit 2; }; hardware_profile=$2; shift ;;
    *) usage >&2; exit 2 ;;
  esac
  shift
done
source "$root/install/hardware-profile.sh"
resolve_hardware_profile "$hardware_profile" "$vm_mode"
provision_args=()
[[ $vm_mode == false ]] || provision_args+=(--vm)
[[ $hardware_profile == generic ]] || provision_args+=(--hardware "$hardware_profile")
if [[ $hardware_profile != generic ]]; then
  python3 "$root/install/hardware.py" --profile "$hardware_profile"
fi
[[ $EUID != 0 && -f /etc/arch-release && -t 0 ]] || { printf 'Run as your regular user in an interactive terminal on installed Arch.\n' >&2; exit 1; }
[[ ! -d /run/archiso ]] || { printf 'Reboot into the installed system first.\n' >&2; exit 1; }
if [[ $vm_mode == true ]] && ! systemd-detect-virt --vm --quiet; then
  printf 'VM mode was requested, but this is not identified as a VM. Run inside the target VM.\n' >&2
  exit 1
fi
printf 'Hexen first-boot setup for %s\nCheckout: %s\nKeep this checkout here; configuration links will refer to it.\n' "$(id -un)" "$root"
read -r -p 'Desktop launcher [walker/fuzzel] (default: walker): ' launcher_choice
launcher=${launcher_choice:-walker}
case "$launcher" in
  walker|fuzzel) ;;
  *) printf 'Invalid launcher choice: %s. Choose walker or fuzzel.\n' "$launcher" >&2; exit 2 ;;
esac
printf 'This updates Arch and installs Git, Ansible and Firefox. Each retry can update Arch again.\n'
if [[ $launcher == walker ]]; then
  printf 'Walker setup also installs build tools, Go and Rust and asks you to review third-party recipes.\n'
fi
printf 'Sudo asks for your account password. Ansible calls the same password the BECOME password.\n'
read -r -p 'Install prerequisites and continue? [y/N] ' answer
[[ $answer == y || $answer == Y ]] || { printf 'Setup cancelled.\n'; exit 3; }
prerequisites=(git ansible firefox less pipewire-jack noto-fonts)
if [[ $hardware_profile != generic ]]; then
  hardware_packages_text=$(python3 "$root/install/hardware.py" --profile "$hardware_profile" --packages)
  read -r -a hardware_packages <<< "$hardware_packages_text"
  prerequisites+=("${hardware_packages[@]}")
fi
if [[ $launcher == walker ]]; then
  prerequisites+=(base-devel go rust fd libqalculate gtk4-layer-shell poppler-glib cairo gobject-introspection protobuf)
fi
sudo pacman -Syu --needed "${prerequisites[@]}"
if [[ $launcher == walker ]]; then
  walker_packages=(walker elephant elephant-desktopapplications elephant-files elephant-runner elephant-calc elephant-websearch elephant-providerlist)
  reuse=n
  if pacman -Q "${walker_packages[@]}"; then
    printf 'All Walker components are already installed. Check their versions above and only reuse builds you trust.\n'
    read -r -p 'Reuse these installed Walker packages and continue provisioning? [y/N] ' reuse
  fi
  if [[ $reuse != y && $reuse != Y ]]; then
    python3 "$root/install/manual-apps/walker/setup.py"
  fi
fi
if "$root/install/provision.sh" "${provision_args[@]}" --launcher "$launcher"; then
  :
else
  status=$?
  if (( status == 3 )); then
    printf 'Setup cancelled during provisioning.\n' >&2
  else
    printf 'Provisioning failed; correct the error and rerun setup.\n' >&2
  fi
  exit "$status"
fi
python3 "$root/install/health.py"
printf '\nSetup completed.\n'
if [[ $hardware_profile != generic ]]; then
  printf 'XPS graphics configuration installed. Reboot before checking NVIDIA, MST displays and KVM switching. Physical acceptance is still required.\n'
fi
