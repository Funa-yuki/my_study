#!/bin/bash

count=0
while [ $count -lt 100 ];
do
  curl 'http://localhost:8000/' \
    -H 'Connection: keep-alive' \
    -H 'Cache-Control: max-age=0' \
    -H 'Upgrade-Insecure-Requests: 1' \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36' \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
    -H 'Sec-Fetch-Site: none' \
    -H 'Sec-Fetch-Mode: navigate' \
    -H 'Sec-Fetch-User: ?1' \
    -H 'Sec-Fetch-Dest: document' \
    -H 'Accept-Language: ja,en-US;q=0.9,en;q=0.8' \
    --compressed -s -o /dev/null -w  "%{time_starttransfer}\n"
  [ $count -lt 1000 ]
  count=$(( count + 1 ))
done
