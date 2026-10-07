from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('khair.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        category TEXT,
        target_amount INTEGER,
        collected_amount INTEGER DEFAULT 0,
        image TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER,
        donor_name TEXT,
        amount INTEGER,
        created_at TEXT
    )''')
    c.execute("SELECT COUNT(*) FROM cases")
    if c.fetchone()[0] == 0:
        sample_cases = [
            ('سارة - 7 سنوات', 'يتيمة محتاجة عملية قلب عاجلة', 'orphans', 20000, 12000, '👧'),
            ('محمد - 60 سنة', 'مسكين محتاج علاج سكري', 'poor', 5000, 2000, '👴'),
            ('عائلة في غزة', 'أسرة فقدت منزلها', 'gaza', 50000, 30000, '🇵🇸'),
            ('عرايس محتاجة', 'مساعدة عرايس غير قادرات', 'brides', 15000, 8000, '💍'),
        ]
        for case in sample_cases:
            c.execute('''INSERT INTO cases 
                (title, description, category, target_amount, collected_amount, image, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (*case, datetime.now().isoformat()))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('khair.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cases ORDER BY id DESC')
    cases = c.fetchall()
    conn.close()
    return render_template('index.html', cases=cases)

@app.route('/case/<int:case_id>')
def case_detail(case_id):
    conn = sqlite3.connect('khair.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cases WHERE id = ?', (case_id,))
    case = c.fetchone()
    conn.close()
    return render_template('case.html', case=case)

@app.route('/donate/<int:case_id>', methods=['POST'])
def donate(case_id):
    donor_name = request.form.get('donor_name', 'متبرع')
    amount = int(request.form.get('amount', 0))
    conn = sqlite3.connect('khair.db')
    c = conn.cursor()
    c.execute('''INSERT INTO donations (case_id, donor_name, amount, created_at)
                 VALUES (?, ?, ?, ?)''',
              (case_id, donor_name, amount, datetime.now().isoformat()))
    c.execute('''UPDATE cases SET collected_amount = collected_amount + ?
                 WHERE id = ?''', (amount, case_id))
    conn.commit()
    conn.close()
    return redirect(url_for('case_detail', case_id=case_id))

@app.route('/category/<cat>')
def category(cat):
    conn = sqlite3.connect('khair.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cases WHERE category = ?', (cat,))
    cases = c.fetchall()
    conn.close()
    return render_template('index.html', cases=cases, category=cat)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
