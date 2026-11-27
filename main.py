import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import random
import calendar
import datetime
import time
import winsound  # Replacement for pygame sound
import os

# Folder next to the EXE for persistent data
APP_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Path to database
DB_PATH = os.path.join(APP_FOLDER, "mydatabase.db")

# Path to images folder
IMAGES_FOLDER = os.path.join(APP_FOLDER, "images")

# Make sure images folder exists
os.makedirs(IMAGES_FOLDER, exist_ok=True)
import sqlite3




ASSETS_DIR = "assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
# Create assets directory if it doesn't exist
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)
# === SQLite Database Connection ===
conn = sqlite3.connect("treasure_island.db", check_same_thread=False)
cursor = conn.cursor()
# === Sound Manager ===
class SoundManager:
    sounds = {
        "success": os.path.join(SOUNDS_DIR, "success.wav"),
        "error": os.path.join(SOUNDS_DIR, "error.wav"),
        "transaction": os.path.join(SOUNDS_DIR, "transaction.wav")
    }
    @staticmethod
    def play(name):
        path = SoundManager.sounds.get(name)
        if path and os.path.exists(path):
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                pass
        else:
            # Fallback system sounds
            if name == "success":
                winsound.Beep(1000, 200)
            elif name == "error":
                winsound.Beep(500, 500)
class ImageManager:
    @staticmethod
    def load(image_path, size=(100, 100)):
        try:
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path)
            else:
                # Create a placeholder image if none exists
                placeholder_path = os.path.join(IMAGES_DIR, "placeholder.png")
                if not os.path.exists(placeholder_path):
                    img = Image.new('RGB', size, color=(200, 200, 200))
                    img.save(placeholder_path)
                img = Image.open(placeholder_path)
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Image loading error: {e}")
            # Return a blank image if all else fails
            img = Image.new('RGB', size, color=(200, 200, 200))
            return ImageTk.PhotoImage(img)
def initialize_database():
    tables = [
        """CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            email TEXT,
            coins REAL DEFAULT 100,
            level INTEGER DEFAULT 1
        )""",
        """CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            theme TEXT,
            sound_enabled INTEGER,
            animations_enabled INTEGER
        )""",
        """CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            description TEXT,
            image_path TEXT,
            seller TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            sent_time TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS postcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            amount REAL,
            log_date TEXT,
            is_message INTEGER DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            posted_by TEXT,
            posted_on TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            type TEXT,
            amount REAL,
            date TEXT DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            log_date TEXT,
            note TEXT
        )"""
    ]
    
    for table in tables:
        cursor.execute(table)    
    cursor.execute("SELECT COUNT(*) FROM news")
    if cursor.fetchone()[0] == 0:
        sample_news = [
            ("Welcome to Treasure Island!", "Start your adventure by exploring the market and meeting other players.", "System"),
            ("New Update Available", "The bank feature has been improved with better transaction tracking.", "Admin"),
            ("Island Event Coming Soon", "Prepare for the annual treasure hunt event next month!", "Event Team")
        ]
        cursor.executemany("INSERT INTO news (title, content, posted_by) VALUES (?, ?, ?)", sample_news)
        conn.commit()
initialize_database()
class GameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏝️ Treasure Island Game ++")
        self.root.geometry("1024x700")
        self.root.minsize(800, 600)
        self.center_window()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.fonts = {
            "title": ("Georgia", 24, "bold"),
            "section": ("Georgia", 16, "bold"),
            "text": ("Georgia", 12),
            "small": ("Georgia", 10)
        }
        self.color_schemes = {
            "default": {
                "bg": "#f0f0f0",
                "fg": "#333333",
                "accent": "#2a9df4",
                "button_bg": "#e0e0e0",
                "button_fg": "#000000",
                "frame_bg": "#ffffff",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000"
            },
            "treasure_theme": {
                "bg": "#fff8e1",
                "fg": "#4e342e",
                "accent": "#d4af37",
                "button_bg": "#ffe082",
                "button_fg": "#4e342e",
                "frame_bg": "#fff3e0",
                "entry_bg": "#fffde7",
                "entry_fg": "#3e2723"
            },
            "market": {
                "bg": "#e1f5fe",
                "fg": "#01579b",
                "accent": "#039be5",
                "button_bg": "#b3e5fc",
                "button_fg": "#01579b",
                "frame_bg": "#e1f5fe",
                "entry_bg": "#ffffff",
                "entry_fg": "#01579b"
            },
            "messages": {
                "bg": "#f3e5f5",
                "fg": "#4a148c",
                "accent": "#9c27b0",
                "button_bg": "#ce93d8",
                "button_fg": "#4a148c",
                "frame_bg": "#f8bbd0",
                "entry_bg": "#ffffff",
                "entry_fg": "#4a148c"
            }
        }
        self.current_theme = "default"
        self.root.configure(bg=self.color_schemes[self.current_theme]["bg"])
        self.content_frame = tk.Frame(self.root, bg=self.color_schemes[self.current_theme]["bg"])
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.current_page = None
        self.logged_in_user = None
        self.show_login()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    def on_close(self):
        conn.close()
        self.root.destroy()
    def apply_theme(self, theme_name):
        if theme_name in self.color_schemes:
            self.current_theme = theme_name
            self.root.configure(bg=self.color_schemes[self.current_theme]["bg"])
    def clear_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    def create_fancy_frame(self, parent=None, title=None, subtitle=None, theme=None):
        if parent is None:
            parent = self.content_frame
        theme = theme or self.current_theme
        frame = tk.Frame(parent, bg=self.color_schemes[theme]["frame_bg"], padx=10, pady=10)        
        if title:
            title_label = tk.Label(frame, text=title, font=self.fonts["title"],
                     fg=self.color_schemes[theme]["accent"], bg=self.color_schemes[theme]["frame_bg"])
            title_label.pack(pady=(10, 0))            
        if subtitle:
            subtitle_label = tk.Label(frame, text=subtitle, font=self.fonts["text"],
                     fg=self.color_schemes[theme]["fg"], bg=self.color_schemes[theme]["frame_bg"])
            subtitle_label.pack(pady=(0, 10))            
        return frame
    def create_fancy_button(self, parent, text, command, bg=None, fg=None, emoji=None, width=None):
        theme = self.color_schemes[self.current_theme]
        bg = bg or theme["button_bg"]
        fg = fg or theme["button_fg"]        
        btn_text = f"{emoji or ''} {text}" if emoji else text
        btn = tk.Button(parent, text=btn_text, font=self.fonts["text"],
                        bg=bg, fg=fg, command=command, relief="raised", bd=2,
                        padx=10, pady=5, width=width)
        btn.bind("<Enter>", lambda e: btn.config(bg=self.lighten_color(bg)))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn    
    def lighten_color(self, color, factor=0.2):
        """Lighten a color by a given factor (0-1)"""
        try:
            rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            lighter = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
            return '#%02x%02x%02x' % lighter
        except:
            return color
    def show_login(self):
        self.clear_frame()
        self.apply_theme("default")
        frame = self.create_fancy_frame(title="🔐 Login", subtitle="Enter your adventurer name to begin")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        tk.Label(frame, text="Username:", font=self.fonts["text"], 
                 bg=self.color_schemes["default"]["frame_bg"]).pack(pady=(10, 5))
        self.login_entry = tk.Entry(frame, font=self.fonts["text"], width=30)
        self.login_entry.pack(pady=5)
        self.login_entry.focus_set()
        tk.Label(frame, text="Password:", font=self.fonts["text"], 
                 bg=self.color_schemes["default"]["frame_bg"]).pack(pady=(10, 5))
        self.password_entry = tk.Entry(frame, font=self.fonts["text"], show="*", width=30)
        self.password_entry.pack(pady=5)
        def login():
            username = self.login_entry.get().strip()
            password = self.password_entry.get().strip()  # In a real app, you'd hash this            
            if not username:
                SoundManager.play("error")
                messagebox.showerror("Error", "Username cannot be empty")
                return                
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user:
                self.logged_in_user = username
                SoundManager.play("success")
                self.show_dashboard()
            else:
                SoundManager.play("error")
                if messagebox.askyesno("User Not Found", "Username not found. Would you like to register?"):
                    self.show_register(prefilled_username=username)
        btn_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        btn_frame.pack(pady=20)        
        self.create_fancy_button(btn_frame, "Login", login, emoji="✅").pack(side="left", padx=10)
        self.create_fancy_button(btn_frame, "Register", self.show_register, emoji="📝").pack(side="left", padx=10)    
        self.root.bind('<Return>', lambda event: login())
    def show_register(self, prefilled_username=None):
        self.clear_frame()
        self.apply_theme("default")
        frame = self.create_fancy_frame(title="📝 Create New Account", subtitle="Register as a new adventurer")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        tk.Label(frame, text="Choose Username:", font=self.fonts["text"], 
                 fg=self.color_schemes["default"]["fg"],
                 bg=self.color_schemes["default"]["frame_bg"]).pack(pady=(10, 5))
        username_entry = tk.Entry(frame, font=self.fonts["text"], 
                                 bg=self.color_schemes["default"]["entry_bg"],
                                 fg=self.color_schemes["default"]["entry_fg"])
        username_entry.pack(pady=5)        
        if prefilled_username:
            username_entry.insert(0, prefilled_username)
        tk.Label(frame, text="Choose Password:", font=self.fonts["text"], 
                 fg=self.color_schemes["default"]["fg"],
                 bg=self.color_schemes["default"]["frame_bg"]).pack(pady=(10, 5))
        password_entry = tk.Entry(frame, font=self.fonts["text"], show="*",
                                 bg=self.color_schemes["default"]["entry_bg"],
                                 fg=self.color_schemes["default"]["entry_fg"])
        password_entry.pack(pady=5)
        tk.Label(frame, text="Confirm Password:", font=self.fonts["text"], 
                 fg=self.color_schemes["default"]["fg"],
                 bg=self.color_schemes["default"]["frame_bg"]).pack(pady=(10, 5))
        confirm_password_entry = tk.Entry(frame, font=self.fonts["text"], show="*",
                                        bg=self.color_schemes["default"]["entry_bg"],
                                        fg=self.color_schemes["default"]["entry_fg"])
        confirm_password_entry.pack(pady=5)
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
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                SoundManager.play("error")
                messagebox.showerror("Error", "Username already exists")
                return
            cursor.execute("INSERT INTO users (username, password, coins, level) VALUES (?, ?, 100.0, 1)", 
                          (username, password))
            cursor.execute("INSERT INTO user_settings (username, theme, sound_enabled, animations_enabled) VALUES (?, 'default', 1, 1)", 
                          (username,))
            conn.commit()            
            SoundManager.play("success")
            messagebox.showinfo("Success", "Account created! Logging in...")
            self.logged_in_user = username
            self.show_dashboard()
        btn_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        btn_frame.pack(pady=20)        
        self.create_fancy_button(btn_frame, "Register", register, emoji="✅").pack(side="left", padx=10)
        self.create_fancy_button(btn_frame, "Back", self.show_login, emoji="🔙").pack(side="left", padx=10)
    def show_dashboard(self):
        self.clear_frame()
        self.apply_theme("treasure_theme")
        frame = self.create_fancy_frame(title=f"🏝️ Welcome, {self.logged_in_user}!", subtitle="Your Island Dashboard")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        cursor.execute("SELECT coins, level FROM users WHERE username = ?", (self.logged_in_user,))
        data = cursor.fetchone()
        coins, level = data if data else (0, 1)
        stats_frame = tk.Frame(frame, bg=self.color_schemes["treasure_theme"]["frame_bg"])
        stats_frame.pack(pady=10)        
        tk.Label(stats_frame, text=f"💰 Coins: {coins:.2f}", font=self.fonts["text"],
                 fg="#d4af37", bg=self.color_schemes["treasure_theme"]["frame_bg"]).pack(side="left", padx=10)
        tk.Label(stats_frame, text=f"🎚️ Level: {level}", font=self.fonts["text"],
                 fg=self.color_schemes["treasure_theme"]["accent"], 
                 bg=self.color_schemes["treasure_theme"]["frame_bg"]).pack(side="left", padx=10)
        nav_frame = tk.Frame(frame, bg=self.color_schemes["treasure_theme"]["frame_bg"])
        nav_frame.pack(pady=20)
        self.create_fancy_button(nav_frame, "🏪 Market", self.show_market, width=15).grid(row=0, column=0, padx=10, pady=5)
        self.create_fancy_button(nav_frame, "💼 Bank", self.show_bank, width=15).grid(row=0, column=1, padx=10, pady=5)
        self.create_fancy_button(nav_frame, "🗓️ Calendar", self.show_calendar, width=15).grid(row=0, column=2, padx=10, pady=5)
        self.create_fancy_button(nav_frame, "📨 Messages", self.show_inbox, width=15).grid(row=1, column=0, padx=10, pady=5)
        self.create_fancy_button(nav_frame, "🧾 Postcards", self.show_postcards, width=15).grid(row=1, column=1, padx=10, pady=5)
        self.create_fancy_button(nav_frame, "📰 News", self.show_news, width=15).grid(row=1, column=2, padx=10, pady=5)
        self.create_fancy_button(nav_frame, "👤 Users", self.show_registered_users, width=15).grid(row=2, column=0, padx=10, pady=5)
        self.create_fancy_button(nav_frame, "⚙️ Settings", self.show_settings, width=15).grid(row=2, column=1, padx=10, pady=5)
        self.create_fancy_button(nav_frame, "🚪 Logout", self.logout_user, width=15).grid(row=2, column=2, padx=10, pady=5)
        msg = f"🎉 Ready to sail, {self.logged_in_user}? Explore the island now!"
        self.animate_banner(frame, msg)
    def animate_banner(self, parent, text):
        banner_label = tk.Label(parent, text="", font=self.fonts["text"],
                                fg=self.color_schemes["treasure_theme"]["fg"],
                                bg=self.color_schemes["treasure_theme"]["frame_bg"])
        banner_label.pack(pady=(10, 20))
        def animate(i=0):
            if i <= len(text):
                banner_label.config(text=text[:i])
                self.root.after(50, animate, i+1)
        animate()
    def logout_user(self):
        self.logged_in_user = None
        self.show_login()
    def show_market(self):
        self.clear_frame()
        self.apply_theme("market")
        frame = self.create_fancy_frame(title="🏪 Island Market", subtitle="Buy or Sell Exotic Goods", theme="market")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        canvas = tk.Canvas(frame, bg=self.color_schemes["market"]["frame_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.color_schemes["market"]["frame_bg"])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        cursor.execute("SELECT id, name, price, description, image_path, seller FROM products ORDER BY id DESC")
        products = cursor.fetchall()
        if not products:
            tk.Label(scrollable_frame, text="No products available in the market yet!", 
                     font=self.fonts["text"], bg=self.color_schemes["market"]["frame_bg"]).pack(pady=20)
        else:
            for pid, name, price, desc, img_path, seller in products:
                card = self.create_fancy_frame(scrollable_frame, theme="market")
                card.pack(padx=10, pady=5, fill="x")
                img = ImageManager.load(img_path, size=(80, 80))
                if img:
                    img_label = tk.Label(card, image=img, bg=self.color_schemes["market"]["frame_bg"])
                    img_label.image = img  # Keep reference
                    img_label.pack(side="left", padx=5)
                details = tk.Frame(card, bg=self.color_schemes["market"]["frame_bg"])
                details.pack(side="left", padx=10, fill="x", expand=True)
                tk.Label(details, text=name, font=self.fonts["section"],
                         fg=self.color_schemes["market"]["accent"],
                         bg=self.color_schemes["market"]["frame_bg"]).pack(anchor="w")
                tk.Label(details, text=f"💰 {price:.2f} coins",
                         font=self.fonts["text"],
                         fg=self.color_schemes["market"]["fg"],
                         bg=self.color_schemes["market"]["frame_bg"]).pack(anchor="w")

                tk.Label(details, text=desc, font=self.fonts["small"],
                         fg=self.color_schemes["market"]["fg"],
                         bg=self.color_schemes["market"]["frame_bg"], wraplength=400, justify="left").pack(anchor="w")

                tk.Label(details, text=f"Sold by: {seller}", font=self.fonts["small"],
                         fg="#666666", bg=self.color_schemes["market"]["frame_bg"]).pack(anchor="w")
                action_frame = tk.Frame(card, bg=self.color_schemes["market"]["frame_bg"])
                action_frame.pack(side="right", padx=10)
                def buy_product(pid=pid, price=price, seller=seller, name=name):
                    buyer = self.logged_in_user
                    if buyer == seller:
                        messagebox.showinfo("Oops", "You can't buy your own item!")
                        return                        
                    cursor.execute("SELECT coins FROM users WHERE username = ?", (buyer,))
                    balance = cursor.fetchone()[0]                    
                    if balance < price:
                        SoundManager.play("error")
                        messagebox.showerror("Insufficient Coins", "You do not have enough coins!")
                        return                        
                    if not messagebox.askyesno("Confirm Purchase", f"Buy '{name}' for {price:.2f} coins?"):
                        return                        
                    cursor.execute("UPDATE users SET coins = coins - ? WHERE username = ?", (price, buyer))
                    cursor.execute("UPDATE users SET coins = coins + ? WHERE username = ?", (price, seller))
                    cursor.execute("DELETE FROM products WHERE id = ?", (pid,))                    
                    cursor.execute("""
                        INSERT INTO postcards (username, message, amount, log_date, is_message) 
                        VALUES (?, ?, ?, ?, 0)
                    """, (seller, f"{buyer} bought your product: {name}", price, datetime.datetime.now().strftime("%Y-%m-%d")))                    
                    cursor.execute("""
                        INSERT INTO transactions (username, type, amount) 
                        VALUES (?, ?, ?)
                    """, (buyer, "purchase", price))                    
                    conn.commit()
                    SoundManager.play("transaction")
                    messagebox.showinfo("Success", f"You bought {name}!")
                    self.show_market()
                buy_btn = tk.Button(action_frame, text="🛒 Buy", command=buy_product,
                                  font=self.fonts["text"], bg="#a5d6a7", fg="#1b5e20",
                                  padx=10, pady=3)
                buy_btn.pack(pady=5)
                def message_seller(seller=seller):
                    self.show_message_dialog(sender=self.logged_in_user, receiver=seller)
                if self.logged_in_user != seller:
                    msg_btn = tk.Button(action_frame, text="✉️ Message", command=message_seller,
                                     font=self.fonts["small"], bg="#ffccbc", fg="#bf360c",
                                     padx=5, pady=2)
                    msg_btn.pack()
        btn_frame = tk.Frame(frame, bg=self.color_schemes["market"]["frame_bg"])
        btn_frame.pack(pady=10)        
        self.create_fancy_button(btn_frame, "📤 Upload Product", self.show_upload_form, emoji="📷").pack(side="left", padx=10)
        self.create_fancy_button(btn_frame, "🔙 Back", self.show_dashboard, emoji="🏠").pack(side="left", padx=10)
    def show_upload_form(self):
        self.clear_frame()
        self.apply_theme("market")
        frame = self.create_fancy_frame(title="📤 Upload Product", subtitle="Add your goods to the marketplace", theme="market")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        name_var = tk.StringVar()
        price_var = tk.StringVar()
        desc_var = tk.StringVar()
        img_path = tk.StringVar()
        tk.Label(frame, text="Product Name:", font=self.fonts["text"], 
                 bg=self.color_schemes["market"]["frame_bg"]).pack(pady=(5, 0))
        tk.Entry(frame, textvariable=name_var, font=self.fonts["text"]).pack(pady=5)
        tk.Label(frame, text="Price:", font=self.fonts["text"], 
                 bg=self.color_schemes["market"]["frame_bg"]).pack(pady=(5, 0))
        tk.Entry(frame, textvariable=price_var, font=self.fonts["text"]).pack(pady=5)
        tk.Label(frame, text="Description:", font=self.fonts["text"], 
                 bg=self.color_schemes["market"]["frame_bg"]).pack(pady=(5, 0))
        desc_entry = tk.Text(frame, font=self.fonts["text"], height=4, width=40)
        desc_entry.pack(pady=5)
        img_preview = tk.Label(frame, bg=self.color_schemes["market"]["frame_bg"])
        img_preview.pack(pady=5)
        def browse_image():
            path = filedialog.askopenfilename(
                initialdir=os.path.expanduser("~"),
                title="Select Product Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
            )
            if path:
                img_path.set(path)
                try:
                    img = Image.open(path)
                    img.thumbnail((150, 150))
                    photo = ImageTk.PhotoImage(img)
                    img_preview.config(image=photo)
                    img_preview.image = photo  # Keep reference
                except Exception as e:
                    messagebox.showerror("Error", f"Could not load image: {e}")
        browse_btn = tk.Button(frame, text="Browse Image", command=browse_image,
                              font=self.fonts["text"], bg="#b3e5fc", fg="#01579b")
        browse_btn.pack(pady=5)        
        tk.Label(frame, textvariable=img_path, font=self.fonts["small"], 
                 bg=self.color_schemes["market"]["frame_bg"]).pack()
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
        btn_frame = tk.Frame(frame, bg=self.color_schemes["market"]["frame_bg"])
        btn_frame.pack(pady=20)        
        self.create_fancy_button(btn_frame, "Upload", upload, emoji="✅").pack(side="left", padx=10)
        self.create_fancy_button(btn_frame, "Cancel", self.show_market, emoji="❌").pack(side="left", padx=10)
    def show_inbox(self):
        self.clear_frame()
        self.apply_theme("messages")
        frame = self.create_fancy_frame(title="📨 Inbox", subtitle="Messages from other users", theme="messages")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        cursor.execute("""
            SELECT id, sender, message, sent_time 
            FROM messages 
            WHERE receiver = ? 
            ORDER BY sent_time DESC
        """, (self.logged_in_user,))
        messages = cursor.fetchall()
        if not messages:
            tk.Label(frame, text="No messages yet!", font=self.fonts["text"], 
                     bg=self.color_schemes["messages"]["frame_bg"]).pack(pady=20)
        else:
            for msg_id, sender, msg, sent in messages:
                card = self.create_fancy_frame(frame, theme="messages")
                card.pack(pady=5, padx=10, fill="x")                
                header_frame = tk.Frame(card, bg=self.color_schemes["messages"]["frame_bg"])
                header_frame.pack(fill="x")                
                tk.Label(header_frame, text=f"From: {sender}", font=self.fonts["text"], 
                         bg=self.color_schemes["messages"]["frame_bg"]).pack(side="left")
                
                tk.Label(header_frame, text=f"Sent: {sent}", font=self.fonts["small"], 
                         bg=self.color_schemes["messages"]["frame_bg"], fg="#888").pack(side="right")                
                tk.Label(card, text=msg, font=self.fonts["small"], 
                         bg=self.color_schemes["messages"]["frame_bg"], 
                         wraplength=500, justify="left").pack(anchor="w", padx=10, pady=5)                
                btn_frame = tk.Frame(card, bg=self.color_schemes["messages"]["frame_bg"])
                btn_frame.pack(anchor="e", pady=5)        
                tk.Button(btn_frame, text="✉️ Reply", 
                          command=lambda s=sender: self.show_message_dialog(self.logged_in_user, s),
                          font=self.fonts["small"], bg="#ba68c8", fg="white").pack(side="left", padx=5)                
                tk.Button(btn_frame, text="🗑️ Delete", 
                          command=lambda mid=msg_id: self.delete_message(mid),
                          font=self.fonts["small"], bg="#f06292", fg="white").pack(side="left", padx=5)
        btn_frame = tk.Frame(frame, bg=self.color_schemes["messages"]["frame_bg"])
        btn_frame.pack(pady=10)        
        self.create_fancy_button(btn_frame, "✏️ New Message", 
                               lambda: self.show_message_dialog(self.logged_in_user, ""), 
                               emoji="✏️").pack(side="left", padx=10)
        self.create_fancy_button(btn_frame, "🔙 Back", self.show_dashboard, emoji="🏠").pack(side="left", padx=10)
    def delete_message(self, msg_id):
        if messagebox.askyesno("Confirm", "Delete this message?"):
            cursor.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
            conn.commit()
            SoundManager.play("success")
            self.show_inbox()
    def show_message_dialog(self, sender, receiver=None):
        top = tk.Toplevel(self.root)
        top.title("New Message" if not receiver else f"Message to {receiver}")
        top.geometry("500x400")
        top.resizable(False, False)
        top.configure(bg="#f8bbd0")        
        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f'+{x}+{y}')
        if not receiver:
            tk.Label(top, text="To:", font=self.fonts["text"], bg="#f8bbd0").pack(pady=(10, 5))            
            cursor.execute("SELECT username FROM users WHERE username != ? ORDER BY username", (sender,))
            users = [row[0] for row in cursor.fetchall()]            
            receiver_var = tk.StringVar()
            receiver_combo = ttk.Combobox(top, textvariable=receiver_var, values=users, state="readonly")
            receiver_combo.pack(pady=5)
            if users:
                receiver_combo.current(0)
        else:
            receiver_var = tk.StringVar(value=receiver)
            tk.Label(top, text=f"To: {receiver}", font=self.fonts["text"], bg="#f8bbd0").pack(pady=(10, 5))
        tk.Label(top, text="Message:", font=self.fonts["text"], bg="#f8bbd0").pack(pady=(10, 5))
        msg_entry = tk.Text(top, height=10, font=self.fonts["text"], wrap="word")
        msg_entry.pack(padx=10, pady=10, fill="both", expand=True)
        def send():
            recv = receiver_var.get()
            msg = msg_entry.get("1.0", tk.END).strip()            
            if not recv:
                messagebox.showerror("Error", "Please select a recipient")
                return                
            if not msg:
                messagebox.showerror("Error", "Message cannot be empty")
                return                
            cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", 
                         (sender, recv, msg))
            conn.commit()
            SoundManager.play("success")
            messagebox.showinfo("Sent", "Message sent!")
            top.destroy()
            self.show_inbox()
        btn_frame = tk.Frame(top, bg="#f8bbd0")
        btn_frame.pack(pady=10)        
        tk.Button(btn_frame, text="✉️ Send", command=send, 
                 font=self.fonts["text"], bg="#ce93d8", fg="#4a148c",
                 padx=15, pady=5).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", command=top.destroy, 
                 font=self.fonts["text"], bg="#f8bbd0", fg="#4a148c",
                 padx=15, pady=5).pack(side="left", padx=10)
    def show_bank(self):
        self.clear_frame()
        self.apply_theme("default")
        frame = self.create_fancy_frame(title="💼 Island Bank", subtitle="Manage your finances", theme="default")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        cursor.execute("SELECT coins FROM users WHERE username = ?", (self.logged_in_user,))
        balance = cursor.fetchone()[0]
        balance_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        balance_frame.pack(pady=20)        
        tk.Label(balance_frame, text="Current Balance:", font=self.fonts["section"], 
                 bg=self.color_schemes["default"]["frame_bg"]).pack(side="left", padx=10)
        tk.Label(balance_frame, text=f"💰 {balance:.2f} coins", font=self.fonts["section"],
                 fg="#2e7d32", bg=self.color_schemes["default"]["frame_bg"]).pack(side="left")
        form_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        form_frame.pack(pady=20)        
        tk.Label(form_frame, text="Amount:", font=self.fonts["text"], 
                 bg=self.color_schemes["default"]["frame_bg"]).grid(row=0, column=0, padx=5, pady=5)
        amount_entry = tk.Entry(form_frame, font=self.fonts["text"])
        amount_entry.grid(row=0, column=1, padx=5, pady=5)
        btn_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        btn_frame.pack(pady=20)        
        def bank_action(action):
            try:
                amt = float(amount_entry.get())
                if amt <= 0:
                    raise ValueError("Amount must be positive")                    
                if action == "Withdraw":
                    if balance < amt:
                        raise ValueError("Insufficient funds")                        
                confirm = messagebox.askyesno("Confirm", 
                    f"Are you sure you want to {action.lower()} {amt:.2f} coins?")
                if not confirm:
                    return                    
                if action == "Deposit":
                    cursor.execute("UPDATE users SET coins = coins + ? WHERE username = ?", 
                                 (amt, self.logged_in_user))
                elif action == "Withdraw":
                    cursor.execute("UPDATE users SET coins = coins - ? WHERE username = ?", 
                                 (amt, self.logged_in_user))
                elif action == "Loan":
                    cursor.execute("UPDATE users SET coins = coins + ? WHERE username = ?", 
                                 (amt, self.logged_in_user))                    
                cursor.execute("""
                    INSERT INTO transactions (username, type, amount) 
                    VALUES (?, ?, ?)
                """, (self.logged_in_user, action.lower(), amt))                
                conn.commit()
                SoundManager.play("transaction")
                messagebox.showinfo("Success", f"{action} of {amt:.2f} coins completed!")
                self.show_bank()
            except ValueError as e:
                SoundManager.play("error")
                messagebox.showerror("Error", str(e))
            except Exception as e:
                SoundManager.play("error")
                messagebox.showerror("Error", f"Transaction failed: {str(e)}")
        tk.Button(btn_frame, text="Deposit", command=lambda: bank_action("Deposit"), 
                 font=self.fonts["text"], bg="#a5d6a7", fg="#1b5e20",
                 padx=15, pady=5).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Withdraw", command=lambda: bank_action("Withdraw"), 
                 font=self.fonts["text"], bg="#ffe082", fg="#e65100",
                 padx=15, pady=5).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Loan", command=lambda: bank_action("Loan"), 
                 font=self.fonts["text"], bg="#ffab91", fg="#b71c1c",
                 padx=15, pady=5).grid(row=0, column=2, padx=10)
        history_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        history_frame.pack(pady=20, fill="x")        
        tk.Label(history_frame, text="Transaction History:", font=self.fonts["section"], 
                 bg=self.color_schemes["default"]["frame_bg"]).pack(anchor="w")        
        cursor.execute("""
            SELECT type, amount, date 
            FROM transactions 
            WHERE username = ? 
            ORDER BY date DESC 
            LIMIT 10
        """, (self.logged_in_user,))
        transactions = cursor.fetchall()        
        if not transactions:
            tk.Label(history_frame, text="No transactions yet", font=self.fonts["small"], 
                     bg=self.color_schemes["default"]["frame_bg"], fg="#666").pack(anchor="w")
        else:
            for t_type, amount, date in transactions:
                tk.Label(history_frame, 
                         text=f"{date}: {t_type.capitalize()} of {amount:.2f} coins",
                         font=self.fonts["small"], 
                         bg=self.color_schemes["default"]["frame_bg"]).pack(anchor="w")
        self.create_fancy_button(frame, "🔙 Back", self.show_dashboard).pack(pady=10)
    def show_postcards(self):
        self.clear_frame()
        self.apply_theme("treasure_theme")
        frame = self.create_fancy_frame(title="🧾 Postcards", subtitle="Logs of trades & messages", theme="treasure_theme")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        cursor.execute("""
            SELECT message, amount, log_date 
            FROM postcards 
            WHERE username = ? 
            ORDER BY log_date DESC
        """, (self.logged_in_user,))
        logs = cursor.fetchall()
        if not logs:
            tk.Label(frame, text="No postcards found!", font=self.fonts["text"], 
                     bg=self.color_schemes["treasure_theme"]["frame_bg"]).pack(pady=20)
        else:
            for msg, amt, date in logs:
                log_frame = self.create_fancy_frame(frame, theme="treasure_theme")
                log_frame.pack(padx=10, pady=5, fill="x")                
                tk.Label(log_frame, text=msg, font=self.fonts["text"], 
                         bg=self.color_schemes["treasure_theme"]["frame_bg"]).pack(anchor="w", padx=10)                
                tk.Label(log_frame, text=f"Amount: {amt:.2f} | Date: {date}", 
                         font=self.fonts["small"],
                         bg=self.color_schemes["treasure_theme"]["frame_bg"], fg="#777").pack(anchor="e", padx=10)
        self.create_fancy_button(frame, "🔙 Back", self.show_dashboard).pack(pady=10)
    def show_calendar(self):
        self.clear_frame()
        self.apply_theme("default")
        frame = self.create_fancy_frame(title="🗓️ Calendar", subtitle="Track your island journey", theme="default")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        today = datetime.date.today().strftime("%Y-%m-%d")
        entry_var = tk.StringVar()
        tk.Label(frame, text=f"Today is: {today}", font=self.fonts["text"], 
                 bg=self.color_schemes["default"]["frame_bg"]).pack(pady=10)
        tk.Label(frame, text="Add Note for Today:", font=self.fonts["text"], 
                 bg=self.color_schemes["default"]["frame_bg"]).pack(pady=(10, 5))
        tk.Entry(frame, textvariable=entry_var, font=self.fonts["text"]).pack(pady=5)
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

        self.create_fancy_button(frame, "💾 Save Note", save_note).pack(pady=10)
        tk.Label(frame, text="📘 Past Logs", font=self.fonts["section"], 
                 bg=self.color_schemes["default"]["frame_bg"]).pack(pady=10)
        cursor.execute("""
            SELECT log_date, note 
            FROM calendar 
            WHERE username = ? 
            ORDER BY log_date DESC
        """, (self.logged_in_user,))
        logs = cursor.fetchall()        
        if not logs:
            tk.Label(frame, text="No logs yet", font=self.fonts["small"], 
                     bg=self.color_schemes["default"]["frame_bg"], fg="#666").pack()
        else:
            for date, note in logs:
                log_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
                log_frame.pack(fill="x", padx=20, pady=5)                
                tk.Label(log_frame, text=date, font=self.fonts["small"], 
                         bg=self.color_schemes["default"]["frame_bg"], width=12, anchor="w").pack(side="left")
                tk.Label(log_frame, text=note, font=self.fonts["small"], 
                         bg=self.color_schemes["default"]["frame_bg"], wraplength=400, justify="left").pack(side="left")
        self.create_fancy_button(frame, "🔙 Back", self.show_dashboard).pack(pady=10)
    def show_news(self):
        self.clear_frame()
        self.apply_theme("default")
        frame = self.create_fancy_frame(title="📰 Island News", subtitle="Announcements and Updates", theme="default")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        cursor.execute("""
            SELECT title, content, posted_on, posted_by 
            FROM news 
            ORDER BY posted_on DESC
        """)
        news_items = cursor.fetchall()
        if not news_items:
            tk.Label(frame, text="No news available.", font=self.fonts["text"], 
                     bg=self.color_schemes["default"]["frame_bg"]).pack(pady=20)
        else:
            for headline, body, date, author in news_items:
                post_frame = self.create_fancy_frame(frame, theme="default")
                post_frame.pack(fill="x", padx=10, pady=5)
                header_frame = tk.Frame(post_frame, bg=self.color_schemes["default"]["frame_bg"])
                header_frame.pack(fill="x")                
                tk.Label(header_frame, text=headline, font=self.fonts["section"], 
                         bg=self.color_schemes["default"]["frame_bg"]).pack(side="left")
                tk.Label(header_frame, text=f"Posted: {date} by {author}", font=self.fonts["small"], 
                         bg=self.color_schemes["default"]["frame_bg"], fg="#888").pack(side="right")
                tk.Label(post_frame, text=body, font=self.fonts["small"], 
                         bg=self.color_schemes["default"]["frame_bg"], wraplength=600, justify="left").pack(anchor="w", padx=10)
        self.create_fancy_button(frame, "🔙 Back", self.show_dashboard).pack(pady=10)
    def show_registered_users(self):
        self.clear_frame()
        self.apply_theme("default")
        frame = self.create_fancy_frame(title="👤 Registered Users", subtitle="Meet other island adventurers", theme="default")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        cursor.execute("""
            SELECT username, coins, level 
            FROM users 
            WHERE username != ? 
            ORDER BY level DESC, coins DESC
        """, (self.logged_in_user,))
        users = cursor.fetchall()
        if not users:
            tk.Label(frame, text="No other users found!", font=self.fonts["text"], 
                     bg=self.color_schemes["default"]["frame_bg"]).pack(pady=20)
        else:
            tree = ttk.Treeview(frame, columns=("username", "coins", "level"), show="headings")
            tree.heading("username", text="Username")
            tree.heading("coins", text="Coins")
            tree.heading("level", text="Level")
            style = ttk.Style()
            style.configure("Treeview", font=self.fonts["small"], rowheight=25)
            style.configure("Treeview.Heading", font=self.fonts["text"])            
            for user in users:
                tree.insert("", "end", values=user)            
            tree.pack(fill="both", expand=True, padx=10, pady=10)
            def message_selected_user():
                selected = tree.focus()
                if selected:
                    user_data = tree.item(selected, "values")
                    self.show_message_dialog(self.logged_in_user, user_data[0])            
            btn_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
            btn_frame.pack(pady=10)            
            self.create_fancy_button(btn_frame, "✉️ Message Selected", message_selected_user).pack(side="left", padx=10)
        self.create_fancy_button(frame, "🔙 Back", self.show_dashboard).pack(pady=10)
    def show_settings(self):
        self.clear_frame()
        self.apply_theme("default")
        frame = self.create_fancy_frame(title="⚙️ Settings", subtitle="Customize your experience", theme="default")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        cursor.execute("""
            SELECT theme, sound_enabled, animations_enabled 
            FROM user_settings 
            WHERE username = ?
        """, (self.logged_in_user,))
        result = cursor.fetchone()        
        current_theme = result[0] if result else "default"
        current_sound = result[1] if result else 1
        current_animation = result[2] if result else 1
        self.settings_theme_var = tk.StringVar(value=current_theme)
        self.settings_sound_var = tk.IntVar(value=current_sound)
        self.settings_animation_var = tk.IntVar(value=current_animation)
        theme_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        theme_frame.pack(fill="x", pady=5)        
        tk.Label(theme_frame, text="Theme:", font=self.fonts["text"], 
                 bg=self.color_schemes["default"]["frame_bg"]).pack(side="left", padx=10)        
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.settings_theme_var,
                                 values=list(self.color_schemes.keys()), state="readonly")
        theme_combo.pack(side="left")
        sound_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        sound_frame.pack(fill="x", pady=5)        
        tk.Checkbutton(sound_frame, text="Enable Sound", variable=self.settings_sound_var,
                      font=self.fonts["text"], bg=self.color_schemes["default"]["frame_bg"],
                      command=lambda: SoundManager.play("success") if self.settings_sound_var.get() else None).pack(anchor="w", padx=10)
        anim_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        anim_frame.pack(fill="x", pady=5)
        
        tk.Checkbutton(anim_frame, text="Enable Animations", variable=self.settings_animation_var,
                      font=self.fonts["text"], bg=self.color_schemes["default"]["frame_bg"]).pack(anchor="w", padx=10)
        def save_settings():
            cursor.execute("""
                UPDATE user_settings 
                SET theme = ?, sound_enabled = ?, animations_enabled = ? 
                WHERE username = ?
            """, (
                self.settings_theme_var.get(), 
                self.settings_sound_var.get(), 
                self.settings_animation_var.get(), 
                self.logged_in_user
            ))
            conn.commit()
            SoundManager.play("success")
            messagebox.showinfo("Saved", "Settings updated!")
            self.apply_theme(self.settings_theme_var.get())
            self.show_dashboard()
        btn_frame = tk.Frame(frame, bg=self.color_schemes["default"]["frame_bg"])
        btn_frame.pack(pady=20)        
        self.create_fancy_button(btn_frame, "💾 Save Settings", save_settings).pack(side="left", padx=10)
        self.create_fancy_button(btn_frame, "🔙 Back", self.show_dashboard).pack(side="left", padx=10)
if __name__ == "__main__":
    root = tk.Tk()
    app = GameUI(root)
    root.mainloop()
    conn.close()