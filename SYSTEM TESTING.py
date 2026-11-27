def upload():
    name = name_var.get().strip()
    price = price_var.get().strip()
    desc = desc_entry.get("1.0", tk.END).strip()
    img = img_path.get()

    try:
        price_val = float(price)
        if not name or price_val <= 0:
            raise ValueError("Invalid name or price")

        cursor.execute("""
            INSERT INTO products (name, price, description, image_path, seller)
            VALUES (?, ?, ?, ?, ?)
        """, (name, price_val, desc, img, self.logged_in_user))

        conn.commit()
        SoundManager.play("success")
        messagebox.showinfo("Uploaded", "Product added successfully!")
        self.show_market()
    except ValueError as e:
        SoundManager.play("error")
        messagebox.showerror("Error", "Please enter a valid price (positive number)")
    except Exception as e:
        SoundManager.play("error")
        messagebox.showerror("Error", f"Failed to upload product: {str(e)}")
