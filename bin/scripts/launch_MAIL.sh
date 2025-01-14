#!/bin/bash
# This file is part of Open-Capture.

# Open-Capture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Open-Capture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Open-Capture. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.

# @dev : Nathan Cheval <nathan.cheval@outlook.fr>

script="MAIL"
# Made 14 char for name, to have the same layout in log as OC application
# Made 31 char for filename, to have the same layout in log as OC application
spaces="              "
name="$script.sh"
name=${name:0:14}${spaces:0:$((14-${#name}))}

spaces="                               "
scriptName="launch_$script.sh"
scriptName=${scriptName:0:31}${spaces:0:$((31-${#scriptName}))}

OCPath="/var/www/html/opencaptureforinvoices/"
config_file="$OCPath"/instance/config.ini
config_mail_file="$OCPath"/instance/config/mail.ini
logFile="$OCPath"/bin/data/log/OCForInvoices.log
PID=/tmp/securite-$script-$$.pid

if ! test -e $PID;
then
  touch $PID
  echo $$ > $PID

  # Retrieve all the processes and launch them instead of copy/paste X lines
  while read -r process ; do
    if [ "$process" != '[GLOBAL]' ];
    then
      process_name="${process//[][]/}"
      python3 "$OCPath"/launch_worker_mail.py -c "$config_file" -cm "$config_mail_file" --process "$process_name"
    fi
  done < <(grep -o '^\[[^][]*]' "$config_mail_file")

  rm -f $PID
else
  echo "[$name] [$scriptName] $(date +"%d-%m-%Y %T") WARNING MAIL capture is already active : PID exists : $PID" >> "$logFile"
fi

