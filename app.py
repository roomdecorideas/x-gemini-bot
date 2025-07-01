# app.py
from flask import Flask, render_template, request, redirect, url_for
import os
# Anda akan menambahkan logika penjadwalan di sini nanti

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_settings():
    # Simpan data dari form ke sebuah file atau database
    with open('settings.conf', 'w') as f:
        f.write(f"X_ACCOUNTS={request.form['x_accounts']}\n")
        f.write(f"GEMINI_KEYS={request.form['gemini_keys']}\n")
        f.write(f"SCHEDULE_TIMES={request.form['schedule_times']}\n")
        f.write(f"CUSTOM_LINK={request.form['custom_link']}\n")

    # Di aplikasi nyata, Anda akan memuat ulang penjadwal di sini
    print("Pengaturan disimpan! Harap restart aplikasi untuk menerapkan jadwal baru.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
