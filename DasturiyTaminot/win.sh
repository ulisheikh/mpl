xfconf-query -c xfce4-keyboard-shortcuts -p "/xfwm4/custom/<Super>Left" -n -t string -s "tile_left_key" && \
xfconf-query -c xfce4-keyboard-shortcuts -p "/xfwm4/custom/<Super>Right" -n -t string -s "tile_right_key" && \
xfwm4 --replace &
