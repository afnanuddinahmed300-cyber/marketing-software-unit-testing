def save_note():
    note = entry_var.get().strip()
    if note:
        cursor.execute("""
            INSERT INTO calendar (username, log_date, note)
            VALUES (?, ?, ?)
        """, (self.logged_in_user, today, note))
        conn.commit()
        SoundManager.play("success")
        messagebox.showinfo("Saved", "Note saved for today!")
        self.show_calendar()
