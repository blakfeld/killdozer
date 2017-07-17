#!/usr/bin/env bash

set -eu

declare -r venv_path=../venv
declare -r killdozer_user=killdozer
declare -r killdozer_install_path=/opt/killdozer

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $(id -u) -ne 0 ]]; then
   echo "This script must be run as root!"
   exit 1
fi

mkdir /var/log/killdozer
chmod 755 /var/log/killdozer

# Prepare the OS
apt-get update
apt-get install -y  libyaml-dev \
                    libpython2.7-dev \
                    python-virtualenv \
                    libpython-dev \
                    python3-dev \
                    rsync \
                    vim \
                    tmux \
                    supervisor

set +e
id -u $killdozer_user
if [[ $? -ne 0 ]]; then
    useradd $killdozer_user
fi
set -e
chown -R $killdozer_user:$killdozer_user $killdozer_install_path
chown -R $killdozer_user:$killdozer_user /var/log/killdozer

(
    cd "$script_path"

    mkdir -p /etc/killdozer || true
    cp ../conf/config.yml /etc/killdozer/config.yml
    ## GET VERSION OF RPi.GPIO!!!!

    ## Create Virtualenv
    if [[ ! -d $venv_path ]]; then
        virtualenv $venv_path
    fi

    $venv_path/bin/pip install -r ../requirements.txt

    ## Copy over supervisor conf.
    cp killdozer_supervisord.conf /etc/supervisor/conf.d/killdozer.conf
    supervisorctl reread
    supervisorctl update
)

exit 0
