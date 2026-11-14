# wsl things, only required for my work machine
cdw() { local d=`wslpath "$1"`; cd "$d"; }
alias beep="powershell.exe '[console]::beep(261.6,700)'"
alias bods-proj="cd ~/Testing/BODS/ && pwd"

# Scripts
alias restrict_gtfs="~/.bash_scripts/restrict_gtfs.py"
alias create_map="~/.bash_scripts/create_map.py"
alias gis_layer_inventory="~/.bash_scripts/gis_layer_inventory.py"
alias agg_to_gpkg="~/.bash_scripts/agg_to_gpkg.py"

# Jupyter (obsolete, I use marimo now)
alias jpnb="jupyter notebook"
alias nohup-jpnb="nohup jupyter notebook > /tmp/jpnb.log 2>&1 &"
alias ipynb-clean="jupyter nbconvert --clear-output --inplace *ipynb"

# General
alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias la='ls -alh'
watchLog() {
  # Watch a logfile
  watch -n3 "tail -n30 /tmp/$1.log"
}
catLog() {
  # cat a logfile for grep
  cat "/tmp/$1.log"
}
alias rem="sudo mount -a"
alias ka="kill $(jobs -p)"
# alias dockerStart="sudo echo 'Enter Permissions: '; sudo dockerd > ~/.dockerd.log 2>&1 &"
# alias dockerCVAT="(cd ~/GitHub/cvat; sudo docker exec -it cvat_server > ~/.CVAT.log 2>&1) &"
alias dockerStart="sudo dockerd > /tmp/dockerd.log 2>&1 &"

# Other aliases
[ -f ~/.aws/.bash_aliases ] && . ~/.aws/.bash_aliases
