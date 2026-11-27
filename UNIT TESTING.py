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
        cursor.executemany(
            "INSERT INTO news (title, content, posted_by) VALUES (?, ?, ?)",
            sample_news
        )
        conn.commit()

initialize_database()
