# agent firejail
fj() {
  local provider="${1:-codex}"

  case "$provider" in
  codex)
    if (( $# > 0 )); then shift; fi
    CODEX_DIR="$HOME/.codex" \
      /home/mcuomo/source/repos/jhop-heap/scripts/codex.sh \
      --bin-dir /usr/local/go \
      --bin-dir /usr/local/go/bin \
      "$PWD" "$@"
    ;;
  opencode | opencodeai)
    shift
    OPENCODE_DIR="$HOME/.opencode" \
      /home/mcuomo/source/repos/jhop-heap/scripts/opencodeai.sh \
      --bin-dir /usr/local/go \
      --bin-dir /usr/local/go/bin \
      "$PWD" "$@"
    ;;
  *)
    CODEX_DIR="$HOME/.codex" \
      /home/mcuomo/source/repos/jhop-heap/scripts/codex.sh \
      --bin-dir /usr/local/go \
      --bin-dir /usr/local/go/bin \
      "$PWD" "$@"
    ;;
  esac
}
