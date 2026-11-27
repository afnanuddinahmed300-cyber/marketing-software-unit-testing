def bank_action(action):
    try:
        amt = float(amount_entry.get())
        if amt <= 0:
            raise ValueError("Amount must be positive")

        if action == "Withdraw":
            if balance < amt:
                raise ValueError("Insufficient funds")

        confirm = messagebox.askyesno(
            "Confirm",
            f"Are you sure you want to {action.lower()} {amt:.2f} coins?"
        )
        if not confirm:
            return

        if action == "Deposit":
            cursor.execute(
                "UPDATE users SET coins = coins + ? WHERE username = ?",
                (amt, self.logged_in_user)
            )
        elif action == "Withdraw":
            cursor.execute(
                "UPDATE users SET coins = coins - ? WHERE username = ?",
                (amt, self.logged_in_user)
            )
        elif action == "Loan":
            cursor.execute(
                "UPDATE users SET coins = coins + ? WHERE username = ?",
                (amt, self.logged_in_user)
            )

        cursor.execute("""
            INSERT INTO transactions (username, type, amount)
            VALUES (?, ?, ?)
        """, (self.logged_in_user, action.lower(), amt))

        conn.commit()
        SoundManager.play("transaction")
        messagebox.showinfo(
            "Success",
            f"{action} of {amt:.2f} coins completed!"
        )
        self.show_bank()

    except ValueError as e:
        SoundManager.play("error")
        messagebox.showerror("Error", str(e))
    except Exception as e:
        SoundManager.play("error")
        messagebox.showerror("Error", f"Transaction failed: {str(e)}")
