#!/bin/bash

rm controls_meross_device.txt

find ./FHEM -type f \( -name "*.pm" -or -name "*.py" \) -print0 | while IFS= read -r -d '' f;
  do
   echo "DEL ${f}" >> controls_meross_device.txt
   out="$(date -d "@$( stat -c '%Y' $f )" +'%F_%T') $(stat -c%s $f) ${f}"
   echo "UPD ${out//.\//}" >> controls_meross_device.txt
done

# CHANGED file
echo "FHEM MEROSS_DEVICE last changes:" > CHANGED
echo $(date +"%Y-%m-%d") >> CHANGED
echo " - $(git log -1 --pretty=%B)" >> CHANGED