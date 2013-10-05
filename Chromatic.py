from collections import namedtuple
from contextlib import closing
import logging
import sqlite3
from werkzeug.security import generate_password_hash, \
    check_password_hash
from flask import Flask, render_template, request, abort, jsonify, session, redirect, url_for

app = Flask(__name__,
            static_folder='./static',
            static_url_path='/chromatic/static')
app.config['DEBUG'] = True
app.debug = True

app.secret_key = '020c0fa6-ead3-47ac-a068-f23e62211f38-28c4d41e-db63-4601-aa89-f6c1283e1c43'

def dbconnect():
    db = sqlite3.connect('ticketing.sqlite3')
    db.execute('PRAGMA foreign_keys = ON;')
    return db


def init_db():
    db = dbconnect()
    db.execute('''CREATE TABLE IF NOT EXISTS user (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         password TEXT NOT NULL,
         extern_id TEXT NOT NULL,
         UNIQUE(name) ON CONFLICT IGNORE
         UNIQUE(extern_id) ON CONFLICT IGNORE)''')
    db.execute('''CREATE TABLE IF NOT EXISTS ticket (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        extern_id TEXT,
        UNIQUE(extern_id) ON CONFLICT IGNORE)''')
    db.execute('''CREATE TABLE IF NOT EXISTS night (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        night DATE,
        UNIQUE(night) ON CONFLICT IGNORE)''')
    db.execute('''CREATE TABLE IF NOT EXISTS ticketkind (
        id INTEGER,
        descr TEXT,
        UNIQUE(descr) ON CONFLICT IGNORE,
        UNIQUE(id) ON CONFLICT IGNORE)''')
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
        FOREIGN KEY(kind) REFERENCES ticketkind(id),
        FOREIGN KEY(seller) REFERENCES user(id))''')
    db.execute('''INSERT INTO night VALUES (NULL, DATE('2013-10-10'))''')
    db.execute('''INSERT INTO night VALUES (NULL, DATE('2013-10-11'))''')
    db.execute('''INSERT INTO night VALUES (NULL, DATE('2013-10-12'))''')
    db.execute('''INSERT INTO ticketkind VALUES (1, 'Arc')''')
    db.execute('''INSERT INTO ticketkind VALUES (2, 'Circusoc member')''')
    db.execute('''INSERT INTO ticketkind VALUES (3, 'Student')''')
    db.execute('''INSERT INTO ticketkind VALUES (4, 'General admission')''')
    db.execute(''' INSERT INTO user VALUES (NULL, 'riri',
     'sha1$Ka77WPoj$b75d8232fdbd673cc5e663d0837e2b79e23ba83a', '123123')''')       # 'asd'
    db.executemany("INSERT INTO ticket VALUES (NULL, ?)", (('ticket%d' % d,) for d in range(90)))
    with open('ticketnames.txt') as ticketnames:
        db.executemany("INSERT INTO ticket VALUES (NULL, ?)", ((ticketid.strip(),) for ticketid in ticketnames.readlines()))

    db.commit()


def getuser_fromextern(db, extern_id):
    with db, closing(db.cursor()) as cursor:
        cursor.execute('SELECT id FROM user WHERE extern_id=?', (extern_id,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0]

def getuser_fromusername(db, username):
    with db, closing(db.cursor()) as cursor:
        cursor.execute('SELECT id FROM user WHERE name=?', (username,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0]


def getticket_fromextern(db, extern_id):
    with db, closing(db.cursor()) as cursor:
        cursor.execute('SELECT id FROM ticket WHERE extern_id=?', (extern_id,))
        logging.info("Searching for ticket %d", extern_id)
        ticket = cursor.fetchone()
        if ticket is None:
            return None
        else:
            return ticket[0]


def issold(db, ticket_id):
    with db, closing(db.cursor()) as cursor:
        cursor.execute('SELECT COUNT(sale.ticket_id) FROM sale WHERE sale.ticket_id=? AND cancelled=0', (ticket_id,))
        count = cursor.fetchone()[0]
        return count != 0


def sellticket(seller, kind, night, ticket):
    db = dbconnect()
    with db, closing(db.cursor()) as cursor:
        seller_id = getuser_fromusername(db, seller)
        ticket_id = getticket_fromextern(db, ticket)
        if ticket_id is None:
            print "Ticket with id %s is none!" % ticket
            return "Not found"
        if ticket_id is not None and issold(db, ticket_id):
            return 'Sold already!'
        print("User %s is selling ticket %s on night %s as %s" % (seller_id, ticket_id, night, kind))
        if seller_id is None or ticket_id is None:
            return 'Not found'
        else:
            cursor.execute('''INSERT INTO sale VALUES (:ticket_id, :kind, :night, :seller, DATE('now'), 0, NULL)''',
                           {'ticket_id': ticket_id, 'kind': kind, 'night': night, 'seller': seller_id})
            return 'Success'


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


@app.route('/chromatic/info')
def showpage():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    sales = getsales()
    return render_template('index.html', capacity=60, sales=sales, user=user)


@app.route('/chromatic/sell', methods=['GET'])
def sell():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    ticket_id = request.args.get('ticket', None)
    return render_template('sell.html', user=user, ticket_id=ticket_id)




@app.route('/chromatic/sellform', methods=['POST'])
def sellform():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    form = request.form
    if 'kind' not in form or 'night' not in form or 'ticketid' not in form:
        return jsonify({'success': False, 'error': 'Other'})
    else:
        kind = form['kind']
        night = form['night']
        ticketid = form['ticketid']
        result = sellticket(user, kind, night, ticketid)
        if result == 'Success':
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': result})

Ticket = namedtuple('Ticket', ('night', 'descr'))

def get_ticket_info(ticket_id):
    db = dbconnect()
    with db, closing(db.cursor()) as cursor:
        cursor.execute('''
            SELECT n.night, k.descr FROM
                sale s
                    JOIN
                night n ON s.night=n.id
                    JOIN
                ticket t ON s.ticket_id=t.id
                    JOIN
                ticketkind k ON s.kind=k.id WHERE t.extern_id=?''', (ticket_id,))
        ticket = cursor.fetchone()
        print ticket
        if ticket:
            return Ticket._make(ticket)
        else:
            return None


@app.route('/chromatic/ticket', methods=['GET'])
def ticketlink():
    ticket_id = request.args.get('ticket', None)
    if 'user' not in session:
        #return render_template('ticket_info_page.html', ticket_info=get_ticket_info(ticket_id))
        return redirect("https://www.facebook.com/events/209441325890771/")
    else:
        user = session['user']
        ticket_id = request.args.get('ticket', None)
        print ticket_id
        return render_template('sell.html', user=user, ticket_id=ticket_id)


def check_user_credentials(user, password):
    db = dbconnect()
    with db, closing(db.cursor()) as cursor:
        cursor.execute("SELECT password FROM user WHERE name=?", (user,))
        pw = cursor.fetchone()
        if pw is None:
            return False
        else:
            return check_password_hash(pw[0], password)


@app.route('/chromatic/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = request.form
        if 'user' not in form or 'pass' not in form:
            return render_template('login.html', error='Please fill in all fields')
        else:
            logged_in = check_user_credentials(form['user'], form['pass'])
            if logged_in == False:
                return render_template('login.html', error='Username or password incorrect')
            else:
                session['user'] = form['user']
                return redirect(url_for('showpage'))
    else:
        return render_template('login.html', error=None)

@app.route('/chromatic/login', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run()

