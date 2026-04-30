import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd

app = Flask(__name__)

# Chemin absolu pour éviter les erreurs d'écriture sur Railway
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'agro_data.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS collectes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  culture TEXT, prix REAL, humidite INTEGER, 
                  meteo TEXT, zone TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    # On utilise un try/except pour éviter que l'app crash si la table est vide
    try:
        df = pd.read_sql_query("SELECT * FROM collectes", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    
    stats = {"total": 0, "prix_moyen": 0}
    if not df.empty:
        stats['total'] = len(df)
        stats['prix_moyen'] = round(df['prix'].mean(), 2)
        
    return render_template('index.html', stats=stats, data=df.to_dict(orient='records'))

@app.route('/collecte', methods=['POST'])
def collecte():
    culture = request.form.get('culture')
    prix = float(request.form.get('prix', 0))
    humidite = request.form.get('humidite', 0)
    meteo = request.form.get('meteo')
    zone = request.form.get('zone')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO collectes (culture, prix, humidite, meteo, zone) VALUES (?,?,?,?,?)',
              (culture, prix, humidite, meteo, zone))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    # TRÈS IMPORTANT : Railway définit son propre PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
