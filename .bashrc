# Non-interactive shells exit early
case $- in *i*) ;; *) return;; esac

# Homebrew
for b in /home/linuxbrew/.linuxbrew/bin/brew /opt/homebrew/bin/brew /usr/local/bin/brew; do
    [ -x "$b" ] && eval "$("$b" shellenv bash)" && break
done

# History & window
HISTCONTROL=ignoreboth
shopt -s histappend checkwinsize
HISTSIZE=1000
HISTFILESIZE=2000

# Input & terminal
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"
bind 'set show-all-if-ambiguous on'
bind 'TAB:menu-complete'
stty -ixon

# Prompt & xterm title
PS1='\u@\[\e[2m\]\h\[\e[0m\] [\[\e[92;3m\]\D{%H:%M}\[\e[0m\]] \[\e[92m\]>\[\e[0m\] '
case "$TERM" in xterm*|rxvt*) PS1="\[\e]0;\u@\h: \w\a\]$PS1" ;; esac

# Aliases & completion
[ -f ~/.bash_aliases ] && . ~/.bash_aliases
if ! shopt -oq posix; then
    [ -f /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion
    [ -f /etc/bash_completion ] && . /etc/bash_completion
fi

# Paths
export PATH="$PATH:$HOME/.local/bin"

# WSL
if [ -n "$WSL_DISTRO_NAME" ]; then
    export BROWSER="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
    [ -f ~/.c314/bin/activate ] && source ~/.c314/bin/activate
fi
