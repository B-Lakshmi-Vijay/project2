import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from datetime import datetime, timedelta

class TimeTrackerApp(App):
    def build(self):
        self.conn = sqlite3.connect('time_tracker.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS login_db
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             login_time TIMESTAMP,
                             logout_time TIMESTAMP DEFAULT NULL,
                             reason TEXT DEFAULT ' ')''')
        
        self.main_layout = BoxLayout(orientation='vertical')
        
        self.login_button = Button(text="Log In")
        self.login_button.bind(on_press=self.log_in)
        
        self.logout_button = Button(text="Log Out")
        self.logout_button.bind(on_press=self.log_out)
        
        self.compute_button = Button(text="Compute Total Time")
        self.compute_button.bind(on_press=self.compute_today_total_time)
        
        self.result_label = Label(text="Total Time: ")
        self.weekstats_button = Button(text = "Show this Week's Statistics")
        self.weekstats_button.bind(on_press=self.compute_week_stats)
        self.weekresult_label = Label(text="Total Time: ", font_size = 12)

        self.main_layout.add_widget(self.login_button)
        self.main_layout.add_widget(self.logout_button)
        self.main_layout.add_widget(self.compute_button)
        self.main_layout.add_widget(self.result_label)
        self.main_layout.add_widget(self.weekstats_button)
        self.main_layout.add_widget(self.weekresult_label)
          
        return self.main_layout
    
    def log_in(self, instance):
        current_time = datetime.now()
        print(current_time)
        InsertQuery = """INSERT INTO login_db (login_time) VALUES (?)"""
        self.cursor.execute(InsertQuery, (current_time,))
        self.conn.commit()
        print(f"Logged in at {current_time}")
    
    def log_out(self, instance):
        current_time = datetime.now()
        self.cursor.execute("UPDATE login_db SET logout_time=?, reason=? WHERE logout_time IS NULL",
                            (current_time, "Reason for logout"))
        self.conn.commit()
        print(f"Logged out at {current_time}")
    
    def compute_today_total_time(self, instance):
      #  self.cursor.execute("SELECT login_time, logout_time FROM login_db WHERE logout_time IS NOT NULL")
        query = "SELECT login_time, logout_time FROM login_db WHERE DATE(login_time) = ?"
        self.cursor.execute(query, (datetime.now().date(),))

        rows = self.cursor.fetchall()
        total_time = 0
        
        for row in rows:
            login_time, logout_time = map(datetime.fromisoformat, row)
         #   print(login_time)
          #  print(logout_time)
         #   print(type(row[0]))
   
            time_difference = logout_time - login_time
            total_time += time_difference.total_seconds()
        #print(total_time)    
        
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        
        self.result_label.text = f"Total Time: {hours} hours, {minutes} minutes, {seconds} seconds"

    def compute_week_stats(self, instance):
        
        statistics = {}
        today = datetime.now().date()

        for _ in range(7):
            previous_day = today - timedelta(days=0)
            login_times, logout_times = self.retrieve_times_for_day(previous_day)
            total_time = self.compute_total_time(login_times, logout_times)
            statistics[previous_day] = total_time
            today -= timedelta(days=1)
            ps =""
        for date, total_time in statistics.items():
            temp =f"{date}: Total Time: { int(total_time // 3600)}  hours {int((total_time % 3600) // 60)}"
            ps += f"{temp}  minutes'\n'"

        self.weekresult_label.text = ps

    def retrieve_times_for_day(self, date):
        query = "SELECT login_time, logout_time FROM login_db WHERE DATE(login_time) = ?"
        self.cursor.execute(query, (date,))
        rows = self.cursor.fetchall()

        login_times = [datetime.fromisoformat(row[0]) for row in rows]
        logout_times = [datetime.fromisoformat(row[1]) for row in rows if row[1] is not None]

        return login_times, logout_times

    def compute_total_time(self, login_times, logout_times):
        total_time = 0
        for login_time, logout_time in zip(login_times, logout_times):
            time_difference = logout_time - login_time
            total_time += time_difference.total_seconds()
        return total_time

    def close_connection(self):
        self.conn.close()

    def on_stop(self):
        self.conn.close()

if __name__ == "__main__":
    TimeTrackerApp().run()
