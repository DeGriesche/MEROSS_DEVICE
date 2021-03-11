#!/bin/bash

rm controls_meross_device.txt
find ./FHEM -type f \( ! -iname ".*" \) -print0 | while IFS= read -r -d '' f;
  do
   echo "DEL ${f}" >> controls_meross_device.txt
   out="UPD "$(stat -f "%Sm" -t "%Y-%m-%d_%T" $f)" "$(stat -f%z $f)" ${f}"
   echo ${out//.\//} >> controls_meross_device.txt
done

# CHANGED file
echo "FHEM MEROSS_DEVICE last changes:" > CHANGED
echo $(date +"%Y-%m-%d") >> CHANGED
echo " - $(git log -1 --pretty=%B)" >> CHANGED