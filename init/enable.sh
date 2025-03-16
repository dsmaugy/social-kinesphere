#!/bin/bash

host=$(whoami)

mkdir -p ~/.config/systemd/user

ln -s ~/social-kinesphere/init/$host.service ~/.config/systemd/user/void.service
systemctl --user daemon-reload
systemctl --user enable void.service
# systemctl --user start void.service
