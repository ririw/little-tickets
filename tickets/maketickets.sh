#!/bin/bash

while read p; do
  echo $p
  qrencode --foreground=FFFFFF --background=000000 -t PNG -l m -o "codes/qrcode$p.out.png" "http://richardweiss.org/chromatic/ticket?ticket=$p"
  convert -resize 450x450 codes/qrcode$p.out.png -fill white -undercolor '#00000080' -font LMMonoLt10-Bold -pointsize 30 -gravity south -annotate +0+5 $p codes/qrcode$p.out.png
  convert -gravity center ticket.jpg codes/qrcode$p.out.png -append tickets/coded_$p.out.png
done < ticketnames.txt

FILES=./tickets/*
i=1;
j=1;
listfiles="";

for f in $FILES
do
   if ( echo $f | grep -q 'ticket' )
   then
      listfiles="$listfiles $f"
      if [ $i -eq 5 ]
      then
         ticketname=`printf '%02d' $j`
         echo "convert $listfiles +append horizjoins/ticket$ticketname.j1.jpg"
         convert $listfiles \+append horizjoins/ticket$ticketname.j1.jpg
         listfiles=""
         i=0
         j=$(($j + 1))
      fi
      i=$(($i + 1))
   fi;
done;
ticketname=`printf '%02d' $j`
echo "convert $listfiles +append horizjoins/ticket$ticketname.j1.jpg"
convert $listfiles \+append horizjoins/ticket$ticketname.j1.jpg
listfiles=""
i=0
j=$(($j + 1))




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
      ticketname=`printf '%02d' $j`
      convert $listfiles -append vertjoins/ticket$ticketname.j1.pdf
      listfiles=""
      i=0
      j=$(($j + 1))
   fi
   i=$(($i + 1))
done;

echo $listfiles
ticketname=`printf '%02d' $j`
convert $listfiles -append vertjoins/ticket$ticketname.j1.pdf
listfiles=""
i=0
j=$(($j + 1))

gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=alltickets.pdf vertjoins/*
