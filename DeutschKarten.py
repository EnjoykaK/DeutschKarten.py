import tkinter as tk
from tkinter import Tk, simpledialog
import sqlite3
from tkinter import messagebox
from PIL import Image, ImageTk
import os


window = Tk()
window.title("Deutsch-Russisch Karten")
window.configure(bg="violet")
window.geometry("500x500")

icon_path = os.path.join(os.path.dirname(__file__), "icon", "deutschkarten.png")
if os.path.exists(icon_path):
    img = Image.open(icon_path)
    photo = ImageTk.PhotoImage(img)
    window.iconphoto(False, photo)



def verbinden():
   return sqlite3.connect('deutschkarten.db')
def get_next_block_id(limit):
    with verbinden() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(block_id) FROM cards")
        row = cursor.fetchone()
        current_block = row[0] if row[0] is not None else 1
        
        cursor.execute("SELECT COUNT(*) FROM cards WHERE block_id = ?", (current_block,))
        count = cursor.fetchone()[0]
        
        if count >= limit:
            current_block += 1
            block_name = f"Блок {current_block}"
            cursor.execute(
                "INSERT INTO blocks (id, name) VALUES (?, ?);", 
                (current_block, block_name)
            )
            conn.commit()
            
        return current_block

with verbinden() as conn:
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS blocks (
                   id INTEGER PRIMARY KEY,
                   name TEXT,
                   date TEXT
               );
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS cards (
                   id INTEGER PRIMARY KEY,
                   deutsch TEXT,
                   russisch TEXT,
                   block_id INTEGER
               );
                   """)
    cursor.execute("INSERT OR IGNORE INTO blocks (id, name) VALUES (1, 'Блок 1');")
    conn.commit()

def hinzufügen():
    window.lift()
    window.focus_force()
    deutsch = simpledialog.askstring("Deutsch", "Deutsche Wort?", parent = window)
    russisch = simpledialog.askstring("Russisch", "Russische Wort?", parent = window)
    if deutsch and russisch:
        with verbinden() as conn:
            cursor = conn.cursor()
            wörter_limit = 5
            aktueller_block = get_next_block_id(wörter_limit)
            cursor.execute(
                "INSERT INTO cards (deutsch, russisch, block_id) VALUES (?, ?, ?);", (deutsch, russisch, aktueller_block)
            )
        conn.commit()
    with verbinden() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cards WHERE block_id = ?", (aktueller_block,))
        aktueller_count = cursor.fetchone()[0]
    messagebox.showinfo(
        "Успех!", 
        f"Слово '{deutsch}' добавлено в Блок №{aktueller_block}.\n"
        f"Заполнение блока: {aktueller_count} из {wörter_limit}"
    )

def fenster_blöcke_anzeigen():
    blöcke_window = tk.Toplevel(window)
    blöcke_window.title("Meine Blöcke")
    blöcke_window.geometry("300x400")
    
    with verbinden() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM blocks")
        alle_blöcke = cursor.fetchall() 
    if not alle_blöcke:
        lbl = tk.Label(blöcke_window, text="Вы еще не создали ни одного блока.")
        lbl.pack(pady=20)
        return
    for block in alle_blöcke:
        block_id = block[0]
        block_name = block[1]
        frame = tk.Frame(blöcke_window)
        frame.pack(fill="x", padx=10, pady=5)
        lbl_name = tk.Label(frame, text=block_name, font=("Arial", 12))
        lbl_name.pack(side="left")
        btn_öffnen = tk.Button(
            frame, 
            text="Открыть", 
            command=lambda b_id=block_id: fenster_karten_anzeigen(b_id)
        )
        btn_öffnen.pack(side="right")

def fenster_karten_anzeigen(block_id):
    karten_window = tk.Toplevel(window)
    karten_window.title(f"Wörter im Block {block_id}")
    karten_window.geometry("400x500")
    with verbinden() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT deutsch, russisch FROM cards WHERE block_id = ?", (block_id,))
        alle_karten = cursor.fetchall()
        
    if not alle_karten:
        lbl = tk.Label(karten_window, text="В этом блоке пока нет слов.")
        lbl.pack(pady=20)
        return
    for karte in alle_karten:
        de_wort = karte[0]
        ru_wort = karte[1]
        
        row_frame = tk.Frame(karten_window, bd=1, relief="solid", padx=5, pady=5)
        row_frame.pack(fill="x", padx=10, pady=5)
        
        lbl_de = tk.Label(row_frame, text=de_wort, font=("Arial", 11, "bold"), fg="blue")
        lbl_de.pack(side="left")
        
        lbl_trenner = tk.Label(row_frame, text="  ↔  ")
        lbl_trenner.pack(side="left")
        
        lbl_ru = tk.Label(row_frame, text=ru_wort, font=("Arial", 11))
        lbl_ru.pack(side="left")

    btn_train = tk.Button(karten_window, text="Тренировка", bg="green", fg="white")
    btn_train.pack(pady=15)

def clear_database():
    if messagebox.askyesno("Внимание!", "Вы уверены, что хотите удалить все блоки и карточки?"):
        with verbinden() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cards;")
            cursor.execute("DELETE FROM blocks;")
            cursor.execute("INSERT INTO blocks (id, name) VALUES (1, 'Блок 1');")
            
            conn.commit()
            
        messagebox.showinfo("Готово", "База данных успешно очищена! Всё началось с Блока 1.")

btn_add = tk.Button(window, text="Добавить карточку", command=hinzufügen, bg="white")
btn_add.pack(pady=20)
btn_show_blocks = tk.Button(window, text="Посмотреть блоки", command=fenster_blöcke_anzeigen, bg="lightgray")
btn_show_blocks.pack(pady=10)
btn_clear = tk.Button(window, text="Сбросить всё", command=clear_database, bg="red", fg="white")
btn_clear.pack(pady=10)

window.mainloop()
