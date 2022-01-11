#!/bin/bash
rm controls_meross_device.txt

while IFS= read -r -d '' FILE
do
    TIME=$(git log --pretty=format:%cd -n 1 --date=iso -- "$FILE")
    TIME=$(TZ=Europe/Berlin date -d "$TIME" +%Y-%m-%d_%H:%M:%S)
    FILESIZE=$(stat -c%s "$FILE")
	FILE=$(echo "$FILE"  | cut -c 3-)
	printf "UPD %s %-7d %s\n" "$TIME" "$FILESIZE" "$FILE"  >> controls_meross_device.txt
done <   <(find . \( -name "*.pm" -o -name "*.txt" -o -name "*.svg" \) -print0 | sort -z -g)

# CHANGED file
echo "MEROSS DEVICE last changes:" > CHANGED
echo $(date +"%Y-%m-%d") >> CHANGED
git log -n 10 --reverse --pretty="format:- %s" >> CHANGED
