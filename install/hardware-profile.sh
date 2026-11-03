# Shared by the interactive first-boot/provisioning wrappers. No system changes.
resolve_hardware_profile() {
  local requested=${1:-} vm_mode=${2:-false}
  local setting="$HOME/.config/hexen/hardware-profile" saved=generic
  if [[ -L $setting || ( -e $setting && ( ! -f $setting || ! -r $setting ) ) ]]; then
    printf 'Refusing unsafe hardware profile setting: %s\n' "$setting" >&2
    return 2
  fi
  if [[ -f $setting ]]; then saved=$(<"$setting"); fi
  case "$saved" in
    generic|xps-14-9440) ;;
    *) printf 'Invalid saved hardware profile: %s\n' "$setting" >&2; return 2 ;;
  esac
  hardware_profile=${requested:-$saved}
  case "$hardware_profile" in
    generic|xps-14-9440) ;;
    *) printf 'Invalid hardware profile: %s\n' "$hardware_profile" >&2; return 2 ;;
  esac
  if [[ $vm_mode == true && $hardware_profile != generic ]]; then
    printf 'The XPS hardware profile cannot be used with --vm.\n' >&2
    return 2
  fi
  if [[ $saved == xps-14-9440 && $hardware_profile != "$saved" ]]; then
    printf 'An installed XPS profile cannot be removed automatically; review its drivers and UWSM files first.\n' >&2
    return 2
  fi
}
