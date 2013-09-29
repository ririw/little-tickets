from collections import namedtuple
from contextlib import closing
import logging
import sqlite3
from flask import Flask, render_template, request, abort

app = Flask(__name__, static_folder='./static', static_url_path='/chromatic/static')
app.config['DEBUG'] = True
app.debug = True


def dbconnect():
    db = sqlite3.connect('ticketing.sqlite3')
    db.execute('PRAGMA foreign_keys = ON;')
    return db


def init_db():
    db = dbconnect()
    db.execute('''CREATE TABLE IF NOT EXISTS user (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         extern_id TEXT NOT NULL,
         UNIQUE(extern_id) ON CONFLICT IGNORE)''')
    db.execute('''CREATE TABLE IF NOT EXISTS ticket (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        extern_id TEXT,
        UNIQUE(extern_id) ON CONFLICT IGNORE)''')
    db.execute('''CREATE TABLE IF NOT EXISTS night (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        night DATE,
        UNIQUE(night) ON CONFLICT IGNORE)''')
    db.execute('''CREATE TABLE IF NOT EXISTS sale (
        ticket_id TEXT NOT NULL,
        kind INTEGER NOT NULL,
        night INTEGER NOT NULL,
        seller INTEGER NOT NULL,
        saletime DATETIME NOT NULL,
        cancelled BOOLEAN,
        canceltime DATETIME,
        FOREIGN KEY(ticket_id) REFERENCES ticket(id),
        UNIQUE(ticket_id) ON CONFLICT FAIL,
        FOREIGN KEY(night) REFERENCES night(id),
        FOREIGN KEY(seller) REFERENCES user(id))''')
    db.execute('''INSERT INTO night VALUES (NULL, DATE('2013-10-10'))''')
    db.execute('''INSERT INTO night VALUES (NULL, DATE('2013-10-11'))''')
    db.execute('''INSERT INTO night VALUES (NULL, DATE('2013-10-12'))''')
    db.execute(''' INSERT INTO user VALUES (NULL, 'riri', '123123')''')
    db.executemany("INSERT INTO ticket VALUES (NULL, ?)", (('ticket%d' % d,) for d in range(90)))
    db.commit()


def getuser_fromextern(db, extern_id):
    with db, closing(db.cursor()) as cursor:
        cursor.execute('SELECT id FROM user WHERE extern_id=?', (extern_id,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0]


def getticket_fromextern(db, extern_id):
    with db, closing(db.cursor()) as cursor:
        cursor.execute('SELECT id FROM ticket WHERE extern_id=?', (extern_id,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0]


def issold(db, ticket_id):
    with db, closing(db.cursor()) as cursor:
        cursor.execute('SELECT COUNT(sale.id) FROM sale WHERE sale.ticket_id=? AND cancelled=0', (ticket_id,))


def sellticket(seller, kind, night, ticket):
    db = dbconnect()
    with db, closing(db.cursor()) as cursor:
        seller_id = getuser_fromextern(db, seller)
        ticket_id = getticket_fromextern(db, ticket)
        if ticket_id is not None and issold(db, ticket_id):
            return 'Sold'
        print("User %s is selling ticket %s on night %s as %s" % (seller_id, ticket_id, night, kind))
        if seller_id is None or ticket_id is None:
            return 'Not found'
        else:
            cursor.execute('''INSERT INTO sale VALUES (:ticket_id, :kind, :night, :seller, DATE('now'), false, NULL)''',
                           {'ticket_id': ticket_id, 'kind': kind, 'night': night, 'seller': seller_id})
            return True


def checkuser(user):
    db = dbconnect()
    with db, closing(db.cursor()) as cursor:
        cursor.execute('SELECT COUNT(id) FROM user WHERE extern_id=?', (user,))
        count = cursor.fetchone()[0]
        assert count == 1, "User '%s' is not in db" % user


def getsales():
    db = dbconnect()
    nights = {
        '2013-10-10': 0,
        '2013-10-11': 0,
        '2013-10-12': 0
    }
    with db, closing(db.cursor()) as cursor:
        cursor.execute('''
            SELECT night.night, COUNT(sale.ticket_id) FROM
                night LEFT JOIN
                sale ON sale.night=night.id
            WHERE sale.cancelled = 0 GROUP BY night.night''')
        for night, tickets in cursor:
            nights[night] = tickets
    return [
        ('Thursday', nights['2013-10-10']),
        ('Friday', nights['2013-10-11']),
        ('Saturday', nights['2013-10-12']),
    ]


@app.route('/chromatic/info/<user>')
def showpage(user):
    checkuser(user)
    sales = getsales()
    return render_template('index.html', capacity=30, sales=sales, user=user)


@app.route('/chromatic/sell/<user>', methods=['GET'])
def sell(user):
    return render_template('sell.html', user=user)


@app.route('/chromatic/sellform', methods=['POST'])
def sellform():
    form = request.form
    if 'seller' not in form or 'kind' not in form or 'night' not in form or 'ticketid' not in form:
        return abort(400)
    else:
        kind = form['kind']
        night = form['night']
        ticketid = form['ticketid']
        seller = form['seller']
        if sellticket(seller, kind, night, ticketid):
            print ("Success!")
            return str(True)
        else:
            print ("Fail lol")
            return abort(400)


if __name__ == '__main__':
    init_db()
    app.run()
