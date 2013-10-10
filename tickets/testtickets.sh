#!/bin/bash

#while read p; do
  #echo $p
  #qrencode -t PNG -l m -o "codes/qrcode$p.out.png" "http://richardweiss.org/chromatic/ticket?ticket=$p"
  #convert -negate -resize 490x490 codes/qrcode$p.out.png codes/qrcode$p.out.png
  #convert -gravity center -append ticket.jpg codes/qrcode$p.out.png tickets/coded_$p.out.png
#done < ticketnames.txt

FILES=./tickets/*
i=1;
j=1;
listfiles="";

for f in $FILES
do
   echo $f | grep 'test'

   if ( echo $f | grep -q 'test' )
   then
      listfiles="$listfiles $f"
      if [ $i -eq 5 ]
      then
         echo "convert $listfiles +append test_horizjoins/ticket$j.j1.jpg"
         convert $listfiles \+append test_horizjoins/ticket$j.j1.jpg
         listfiles=""
         i=0
         j=$(($j + 1))
      fi
      i=$(($i + 1))
   fi;
done;

echo "convert $listfiles +append test_horizjoins/ticket$j.j1.jpg"
convert $listfiles \+append test_horizjoins/ticket$j.j1.jpg
listfiles=""
i=0
j=$(($j + 1))





FILES=./test_horizjoins/*
i=1;
j=1;
listfiles="";

for f in $FILES
do
   listfiles="$listfiles $f"
   if [ $i -eq 3 ]
   then
      echo $listfiles
      convert $listfiles -append test_vertjoins/ticket$j.j1.pdf
      listfiles=""
      i=0
      j=$(($j + 1))
   fi
   i=$(($i + 1))
done;
echo $listfiles
convert $listfiles -append test_vertjoins/ticket$j.j1.pdf
listfiles=""
i=0
j=$(($j + 1))


gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=alltesttickets.pdf test_vertjoin/*
