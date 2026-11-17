# Git shortcuts for interactive Bash sessions.

__uconfig_git_rebase_main() {
    local current_branch
    local main_branch

    if [[ "$#" -ne 0 ]]; then
        printf '%s\n' 'rbmain: does not accept arguments' >&2
        return 2
    fi

    main_branch="$(command git config --get uconfig.mainbranch 2>/dev/null)" || main_branch="main"

    current_branch="$(command git branch --show-current)" || return

    if [[ -z "$current_branch" ]]; then
        printf '%s\n' 'rbmain: not on a branch' >&2
        return 1
    fi

    if [[ "$current_branch" == "$main_branch" ]]; then
        printf 'rbmain: already on %s\n' "$main_branch" >&2
        return 1
    fi

    command git switch "$main_branch" &&
        command git pull --ff-only origin "$main_branch" &&
        command git switch "$current_branch" &&
        command git rebase "$main_branch"
}

git() {
    case "${1-}" in
        ..)
            shift
            command git switch - "$@"
            ;;
        rbmain)
            shift
            __uconfig_git_rebase_main "$@"
            ;;
        *)
            command git "$@"
            ;;
    esac
}

g() {
    git "$@"
}

sub-check() {
    cd bhce || return
    command git status
    if [[ -n "$(command git status --porcelain)" ]]; then
        cd - >/dev/null
        return 1
    fi
    cd - >/dev/null &&
        command git add bhce &&
        command git rebase --continue
}

