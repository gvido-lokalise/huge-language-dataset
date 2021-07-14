#!/bin/sh
# Usage: ./parse_json_codes.sh

cat response.json | jq .[].code | sed -e 's/"//g' > supported_lang_codes.txt
