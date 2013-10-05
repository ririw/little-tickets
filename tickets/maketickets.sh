#!/bin/bash
while read p; do
  echo $p
  qrencode -t PNG -l m -o "codes/qrcode$p.out.png" "http://richardweiss.org/chromatic/ticket?ticket=$p"
  convert -negate -resize 490x490 codes/qrcode$p.out.png codes/qrcode$p.out.png
  convert -gravity center -append ticket.jpg codes/qrcode$p.out.png tickets/codedticket_$p.out.png
done < ticketnames.txt

FILES=./tickets/*
i=1;
j=1;
listfiles="";

for f in $FILES
do
   listfiles="$listfiles $f"
   if [ $i -eq 5 ]
   then
      echo "convert $listfiles +append horizjoins/ticket$j.j1.jpg"
      convert $listfiles \+append horizjoins/ticket$j.j1.jpg
      listfiles=""
      i=0
      j=$(($j + 1))
   fi
   i=$(($i + 1))
done;

FILES=./horizjoins/*
i=1;
j=1;
listfiles="";

for f in $FILES
do
   listfiles="$listfiles $f"
   if [ $i -eq 3 ]
   then
      echo $listfiles
      convert $listfiles -append vertjoins/ticket$j.j1.jpg
      listfiles=""
      i=0
      j=$(($j + 1))
   fi
   i=$(($i + 1))
done;
