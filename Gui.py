from tkinter import Tk, Frame, Scrollbar, Label, Listbox, Entry, Button, messagebox, StringVar
import socket
import threading
import datetime
import pyodbc


def database():
    def login_t():
        login()

    def login():
        username = username_entry.get()
        password = password_entry.get()
        login_button.config(text="Logowanie...", bg='grey', state='disabled')
        base.update()
        try:
            conn = pyodbc.connect('Driver={SQL SERVER};' +
                                  'Server=ZALMAN;' +
                                  'Database=app;' +
                                  'Trusted_Connection=True;')
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM users WHERE Username = '{username}' AND PasswordHash COLLATE Latin1_General_CS_AS = '{password}'")

            if cursor.fetchone():

                messagebox.showinfo("Success", "Zalogowano pomyślnie!")
                base.destroy()
                main()

            else:
                messagebox.showerror("Error", "Błędny login lub hasło!")
                login_button.config(text="Zaloguj", bg="#4CAF50", state='normal')

            cursor.close()
            conn.close()
        except Exception as e:
            print(e)

    base = Tk()
    base.title("Login")
    base.geometry("400x250")
    base.configure(bg="#f0f0f0")

    title_label = Label(base, text="Logowanie", font=("Arial", 24), bg="#f0f0f0")
    title_label.pack(pady=10)

    # Pole na nazwę użytkownika
    username_frame = Frame(base, bg="#f0f0f0")
    username_frame.pack(pady=5)
    Label(username_frame, text="Login:", bg="#f0f0f0", font=("Arial", 12)).pack(side='left')
    username_entry = Entry(username_frame, font=("Arial", 12))
    username_entry.pack(side='right')

    # Pole na hasło
    password_frame = Frame(base, bg="#f0f0f0")
    password_frame.pack(pady=5)
    Label(password_frame, text="Hasło:", bg="#f0f0f0", font=("Arial", 12)).pack(side='left')
    password_entry = Entry(password_frame, show="*", font=("Arial", 12))
    password_entry.pack(side='right')

    # Przycisk logowania
    login_button = Button(base, text="Zaloguj", font=("Arial", 12), command=login_t, bg="#4CAF50", fg="white", padx=20,
                          pady=5)
    login_button.pack(pady=10)

    # Pole do wyświetlania statusu logowania
    login_status = Label(base, text="", font=("Arial", 12), bg="#f0f0f0")
    login_status.pack()

    base.mainloop()


def main():
    global client_socket, is_Connected
    is_Connected = False

    def time_():
        czas = datetime.datetime.now()
        time_label.config(text=czas.strftime("%H:%M"))
        root.after(1000, time_)

    def disconnect():
        global is_Connected, client_socket
        if is_Connected:
            message = f'{username_entry.get()} DISCONNECTED'
            client_socket.send(message.encode())
            client_socket.close()
            chat_listbox.delete(0, 'end')
            connection_info.config(text="DISCONNECTED", fg="red")
            messagebox.showinfo("Disconnected from server", "You have been disconnected from the server")
        else:
            messagebox.showerror("Error", "Please connect first!")

    def send(event=None):
        global client_socket, is_Connected
        if is_Connected:
            message = f"{message_entry.get()}"
            if not message.isspace() and message:
                chat_listbox.insert('end', f"{username_entry.get()}: {message}")
                client_socket.send(message.encode())
                print(message)
                message_entry.delete(0, 'end')
            else:
                messagebox.showinfo("Error", "Type Something!")
        else:
            messagebox.showerror("Error", "Please connect first!")

    def connect_th():
        chat_listbox.delete(0, 'end')
        threading.Thread(target=connect).start()

    def connect():
        global is_Connected, client_socket
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = '192.168.0.139'
            port = 12345
            if username_entry.get():
                connection_info.config(text="CONNECTING...", fg="gray")
                client_socket.connect((host, port))
                client_socket.send(username_entry.get().encode())
                is_Connected = True

                connection_info.config(text="CONNECTED", fg="green")
                messagebox.showinfo("Connected to server", "You have been connected to the server")

                messages_th(client_socket)
            else:
                messagebox.showerror("Error", "Please enter a username!")
                connection_info.config(text="NOT CONNECTED", fg="red")
        except Exception as e:
            connection_info.config(text="NOT CONNECTED", fg="red")
            messagebox.showerror("Error", "Something went wrong. Please try again later. \n Error:" + str(e))

    def messages_th(client_socket):
        receive_thread = threading.Thread(target=receive_message(client_socket))
        receive_thread.start()

    def receive_message(client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode()
                chat_listbox.insert('end', data)
            except Exception as e:
                print("Błąd:", e)
                break

    global sock, chat_listbox, message_entry, username_entry

    root = Tk()
    root.title("Chat App")
    root.resizable(False, False)
    root.geometry("900x500")

    bg_color = "#f0f0f0"
    button_color = "#4CAF50"
    button_text_color = "white"

    root.configure(bg=bg_color)

    frame_menu = Frame(root, bg=bg_color, bd=10)
    frame_menu.pack(side='left', fill='y')

    frame_chat = Frame(root, bg=bg_color, bd=10)
    frame_chat.pack(expand=True, fill='both')

    frame_notes = Frame(root, bg=bg_color, bd=10)
    frame_notes.pack(side='right', fill='y')

    Label(frame_menu, text="Connection Menu:", bg=bg_color, fg="blue", font=("Arial", 12, "bold")).pack(side='top',
                                                                                                        padx=5, pady=5)
    connect_button = Button(frame_menu, text="Connect", command=connect_th, bg=button_color, fg=button_text_color,
                            font=("Arial", 10, "bold"))
    connect_button.pack(padx=5, pady=5)
    disconnect_button = Button(frame_menu, text="Disconnect", command=disconnect, bg=button_color, fg=button_text_color,
                               font=("Arial", 10, "bold"))
    disconnect_button.pack(padx=5, pady=5)
    Label(frame_menu, text="Username:", bg=bg_color, fg="blue", font=("Arial", 12, "bold")).pack(padx=5, pady=5)
    username_entry = Entry(frame_menu, width=20)
    username_entry.pack(padx=5, pady=5)

    Label(frame_chat, text="Chat:", bg=bg_color, fg="blue", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5,
                                                                                             pady=5, sticky="w")
    chat_listbox = Listbox(frame_chat, height=18, width=35, font=("Arial", 12))
    chat_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
    scrollbar = Scrollbar(frame_chat, command=chat_listbox.yview)
    scrollbar.grid(row=1, column=2, sticky='ns')
    chat_listbox.config(yscrollcommand=scrollbar.set)

    Label(frame_chat, text="Message:", bg=bg_color, fg="blue", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=5,
                                                                                                pady=5, sticky="w")
    message_entry = Entry(frame_chat, width=60)
    message_entry.grid(row=3, column=0, padx=5, pady=5)
    send_button = Button(frame_chat, text="Send", command=send, bg=button_color, fg=button_text_color,
                         font=("Arial", 10, "bold"))
    send_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    message_entry.bind("<Return>", send)

    connection_info = Label(frame_chat, text="NOT CONNECTED", fg="red", font=("Arial", 20, "bold"))
    connection_info.place(x=140, y=1)

    time_label = Label(frame_chat, text="Time", font=("Arial", 20))
    time_label.place(x=560, y=1)

    time_()
    root.mainloop()


if __name__ == "__main__":
    database()
