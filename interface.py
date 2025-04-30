import tkinter as tk
from tkinter import scrolledtext
from chat import get_bot_response

# 🎬 Window setup
window = tk.Tk()
window.title("🎬 CineMate - Movie Chatbot")
window.geometry("520x600")
window.configure(bg="#1e1e1e")  # dark background

# 📝 Chat log with scroll
chat_log = scrolledtext.ScrolledText(window, wrap=tk.WORD, state='disabled', font=("Segoe UI", 11))
chat_log.configure(bg="#2b2b2b", fg="white", padx=10, pady=10)
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# 🖊️ Input frame
input_frame = tk.Frame(window, bg="#1e1e1e")
input_frame.pack(padx=10, pady=10, fill=tk.X)

entry = tk.Entry(input_frame, font=("Segoe UI", 12), bg="#333333", fg="white", insertbackground="white", relief=tk.FLAT)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=6)


def send_message(event=None):
    user_input = entry.get()
    if not user_input.strip():
        return
    entry.delete(0, tk.END)

    # Show user's message
    chat_log.config(state='normal')
    chat_log.insert(tk.END, f"You: {user_input}\n", "user")

    # Get bot's response
    response = get_bot_response(user_input)
    chat_log.insert(tk.END, f"CineMate: {response}\n\n", "bot")
    chat_log.config(state='disabled')
    chat_log.yview(tk.END)


# 💬 Style tags
chat_log.tag_config("user", foreground="#4dd0e1", font=("Segoe UI", 11, "bold"))
chat_log.tag_config("bot", foreground="#a5d6a7", font=("Segoe UI", 11))

# 📤 Send button
send_button = tk.Button(input_frame, text="Send", command=send_message, bg="#4dd0e1", fg="black",
                        font=("Segoe UI", 10, "bold"), padx=15, pady=5, relief=tk.FLAT)
send_button.pack(side=tk.RIGHT)

# Pressing Enter sends message
window.bind("<Return>", send_message)

# 🎬 Launch app
window.mainloop()
