#!/bin/bash

count=1
cat $1 | while read line
do
	echo "analysing website: '$line'"
	website-evidence-collector collect $line -o dummy/ 2> /dev/null
	echo "done, cleaning up"
	mv dummy/inspection.json Results/$count.json
	rm -rf dummy/
	((count++))
	sleep 5
done
rm -rf output/
