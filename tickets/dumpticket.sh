rm ticketnames.txt
touch ticketnames.txt
for ((i = 1; i <= 300; i++)); do
    uuidgen >> ticketnames.txt
done;
