from contextlib import closing
import random
import string
import csv
import itertools as it


numcodes = 300
randseed = 1
length = 10

letters = string.ascii_lowercase
random.seed(randseed)

with open('ticketnames.txt','w') as tickets:
    wr = csv.writer(tickets)
    for item in range(numcodes):
        tickets.write(''.join(it.imap(random.choice, it.repeat(letters, length))))
        tickets.write('\n')
    for i in range(10):
        tickets.write('test%d\n' % i)
