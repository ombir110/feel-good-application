import sqlite3
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label


# ----------- DATABASE SETUP -----------
def init_db():
    conn = sqlite3.connect("feelgood.db")
    cur = conn.cursor()
    # User table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    # Journal table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS journals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood TEXT,
            journal TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def signup_user(username, password):
    try:
        conn = sqlite3.connect("feelgood.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    conn = sqlite3.connect("feelgood.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()
    return user

def save_journal(user_id, mood, journal):
    conn = sqlite3.connect("feelgood.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO journals (user_id, mood, journal) VALUES (?, ?, ?)", (user_id, mood, journal))
    conn.commit()
    conn.close()

def get_quote(mood):
    quotes = {
        "happy": [
            "Keep smiling, it makes people wonder what you're up to!",
            "Happiness is contagious — spread it around!"
        ],
        "sad": [
            "Tough times don’t last, but tough people do.",
            "It's okay to feel sad. Brighter days are ahead."
        ],
        "angry": [
            "Breathe in, breathe out. Let it go.",
            "Anger is one letter short of danger."
        ],
        "stressed": [
            "Slow down. You’re doing just fine.",
            "You’ve survived 100% of your worst days so far."
        ]
    }
    return random.choice(quotes.get(mood.lower(), ["Feel good — you're doing better than you think!"]))

# ----------- SCREENS -----------
class LoginScreen(Screen):
    pass

class HomeScreen(Screen):
    pass

# ----------- MAIN APP -----------
class FeelGoodApp(App):
    def build(self):
        init_db()
        self.user_id = None
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(HomeScreen(name='home'))
        return self.sm

    def show_popup(self, message):
        popup = Popup(title='Notification',
                      content=Label(text=message),
                      size_hint=(None, None),
                      size=(300, 150))
        popup.open()

    def login(self, username, password):
        user = login_user(username, password)
        if user:
            self.user_id = user[0]
            self.sm.current = 'home'
            self.sm.get_screen('home').ids.quote_label.text = ''
        else:
            self.show_popup("Invalid username or password!")

    def signup(self, username, password):
        if signup_user(username, password):
            self.show_popup("Signup successful! Please login.")
        else:
            self.show_popup("Username already exists!")

    def handle_mood(self, mood, journal):
        if not self.user_id:
            self.show_popup("Please login first.")
            return
        if not mood.strip():
            self.show_popup("Please enter your mood.")
            return
        save_journal(self.user_id, mood, journal)
        quote = get_quote(mood)
        self.sm.get_screen('home').ids.quote_label.text = quote

if __name__ == '__main__':
    FeelGoodApp().run()
