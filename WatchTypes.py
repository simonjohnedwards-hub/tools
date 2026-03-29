import tkinter as tk
from tkinter import messagebox
import json

# Load the JSON data
with open("WatchTypes.json", "r", encoding="utf-8") as f:
    watch_data = json.load(f)

# Create a lookup dictionary for quick access
part_number_lookup = {watch["partNumber"]: watch for watch in watch_data}

# Define the lookup function
def lookup_part():
    part_number = entry.get().strip()
    result = part_number_lookup.get(part_number)
    if result:
        name = result["name"]
        additional_names = result["additionalNames"]
        additional_names_str = "\n".join(additional_names) if additional_names else "None"
        result_text.set(f"Name: {name}\nAdditional Names:\n{additional_names_str}")
    else:
        result_text.set("Part number not found.")

# Setup the GUI
root = tk.Tk()
root.title("Garmin Watch Lookup")

tk.Label(root, text="Enter Part Number:").grid(row=0, column=0, padx=10, pady=10)
entry = tk.Entry(root, width=30)
entry.grid(row=0, column=1, padx=10, pady=10)

tk.Button(root, text="Lookup", command=lookup_part).grid(row=0, column=2, padx=10, pady=10)

result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify="left", anchor="w")
result_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="w")

root.mainloop()