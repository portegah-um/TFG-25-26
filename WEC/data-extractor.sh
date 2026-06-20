#!/bin/bash

for i in {1..10};
do
    python3 WEC-data-extract.py Results/$i.json
done