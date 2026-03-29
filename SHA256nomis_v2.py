import tkinter as tk
from tkinter import messagebox
import hmac
import hashlib
import base64

def hmac_sha256_hex_base64(message: str, key: str):
    message_bytes = message.encode('utf-8')
    key_bytes = key.encode('utf-8')
    hmac_digest = hmac.new(key_bytes, message_bytes, hashlib.sha256).digest()
    return hmac_digest.hex(), base64.b64encode(hmac_digest).decode('utf-8')

def on_generate():
    msg = message_input.get()
    k = key_input.get()
    if not msg or not k:
        messagebox.showwarning("Missing Input", "Please enter both a message and a key.")
        return
    hex_result, b64_result = hmac_sha256_hex_base64(msg, k)
    hex_output.configure(state='normal')
    b64_output.configure(state='normal')
    hex_output.delete(0, tk.END)
    b64_output.delete(0, tk.END)
    hex_output.insert(0, hex_result)
    b64_output.insert(0, b64_result)
    hex_output.configure(state='readonly')
    b64_output.configure(state='readonly')

# GUI setup
root = tk.Tk()
root.title("HMAC-SHA256 Generator")

tk.Label(root, text="Message:").pack(pady=2)
message_input = tk.Entry(root, width=60)
message_input.pack(padx=10)

tk.Label(root, text="Key (default: 'nomis'):").pack(pady=2)
key_input = tk.Entry(root, width=60, show="*")
key_input.insert(0, "nomis")  # Set default key
key_input.pack(padx=10)

tk.Button(root, text="Generate HMAC", command=on_generate).pack(pady=10)

tk.Label(root, text="Hex Output:").pack(pady=(10,0))
hex_output = tk.Entry(root, width=80, state='readonly')
hex_output.pack(padx=10)

tk.Label(root, text="Base64 Output:").pack(pady=(10,0))
b64_output = tk.Entry(root, width=80, state='readonly')
b64_output.pack(padx=10)

root.mainloop()