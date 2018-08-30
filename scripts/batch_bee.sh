#!/bin/bash
cd /home/alex/Dropbox/Work/Bee/Models/MushroomBody/paper_version//scripts/
echo 'python world_DMTS.py' &
echo $PWD &
python world_DMTS.py &
cd ~/git/SpineML_2_BRAHMS
BRAHMS_NS=~/git/SpineML_2_BRAHMS/Namespace/ SYSTEMML_INSTALL_PATH= PATH=/home/alex/bin:/home/alex/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/brahms/bin:. ./convert_script_s2b -w ~/git/SpineML_2_BRAHMS -m /home/alex/Dropbox/Work/Bee/Models/MushroomBody/paper_version//model/ -e 0 -o /home/alex/outtemp//bee123/
