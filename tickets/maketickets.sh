while read p; do
  echo $p
  qrencode -t PNG -l m -o "codes/qrcode$p.out.png" "http://richardweiss.org/chromatic/ticket?ticket=$p"
  convert -resize 300x300 codes/qrcode$p.out.png codes/qrcode$p.out.png
  convert -gravity center -append ticket_l.png codes/qrcode$p.out.png tickets/codedticket_$p.out.png
done < ticketnames.txt

convert +append tickets/codedticket_* tickets.png
