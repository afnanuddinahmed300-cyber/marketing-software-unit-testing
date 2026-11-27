def register():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    confirm_password = confirm_password_entry.get().strip()

    if not username:
        SoundManager.play("error")
        messagebox.showerror("Error", "Username cannot be empty")
        return

    if not password:
        SoundManager.play("error")
        messagebox.showerror("Error", "Password cannot be empty")
        return

    if password != confirm_password:
        SoundManager.play("error")
        messagebox.showerror("Error", "Passwords do not match")
        return

    cursor.execute(
        "SELECT username FROM users WHERE username = ?",
        (username,)
    )

    if cursor.fetchone():
        SoundManager.play("error")
        messagebox.showerror("Error", "Username already exists")
        return

    cursor.execute(
        "INSERT INTO users (username, password, coins, level) VALUES (?, ?, 100.0, 1)",
        (username, password)
    )

    cursor.execute(
        "INSERT INTO user_settings (username, theme, sound_enabled, animations_enabled) VALUES (?, 'default', 1, 1)",
        (username,)
    )

    conn.commit()

    SoundManager.play("success")
    messagebox.showinfo("Success", "Account created! Logging in...")
    self.logged_in_user = username
    self.show_dashboard()
