import tkinter as tk
from tkinter import filedialog, messagebox
from difflib import SequenceMatcher
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

# Create a ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

# Asynchronous file loading function
async def load_file_or_display_contents(entry, text_widget):
    file_path = entry.get()
    if not file_path:
        file_path = filedialog.askopenfilename()

    if file_path:
        entry.delete(0, tk.END)
        entry.insert(tk.END, file_path)

        loop = asyncio.get_event_loop()
        try:
            # Read file content asynchronously
            text = await loop.run_in_executor(executor, read_file, file_path)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, text)

            # Inform the user the file was successfully loaded
            print(f"File {file_path} is successfully loaded")

        except UnicodeDecodeError:
            # Handle decoding errors
            print(f"Unable to load file {file_path} due to a decoding error")

# Synchronous function to read files
def read_file(file_path):
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Failed to read file {file_path} with all tried encodings")

# Asynchronous text comparison function
async def compare_text(text1, text2):
    loop = asyncio.get_event_loop()
    similarity_percentage, diff = await loop.run_in_executor(
        executor, compute_similarity, text1, text2
    )
    return similarity_percentage, diff

# Function to compute similarity
def compute_similarity(text1, text2):
    d = SequenceMatcher(None, text1, text2)
    similarity_ratio = d.ratio()
    similarity_percentage = int(similarity_ratio * 100)
    diff = list(d.get_opcodes())
    return similarity_percentage, diff

# Asynchronous function to show similarity
async def show_similarity():
    text1 = text_textbox1.get(1.0, tk.END)
    text2 = text_textbox2.get(1.0, tk.END)
    similarity_percentage, diff = await compare_text(text1, text2)
    text_textbox_diff.delete(1.0, tk.END)
    text_textbox_diff.insert(tk.END, f"Similarity: {similarity_percentage}%")

    # Highlight similar text
    highlight_similar_text(diff)

# Highlighting function for similar text
def highlight_similar_text(diff):
    text_textbox1.tag_remove("same", "1.0", tk.END)
    text_textbox2.tag_remove("same", "1.0", tk.END)
    for opcode in diff:
        tag = opcode[0]
        start1 = opcode[1]
        end1 = opcode[2]
        start2 = opcode[3]
        end2 = opcode[4]

        if tag == "equal":
            text_textbox1.tag_add("same", f"1.0+{start1}c", f"1.0+{end1}c")
            text_textbox2.tag_add("same", f"1.0+{start2}c", f"1.0+{end2}c")

# Create the tkinter GUI
root = tk.Tk()
root.title("Text Comparison Tool")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Text widgets and labels
text_label1 = tk.Label(frame, text="Text 1:")
text_label1.grid(row=0, column=0, padx=5, pady=5)
text_textbox1 = tk.Text(frame, wrap=tk.WORD, width=40, height=10)
text_textbox1.grid(row=0, column=1, padx=5, pady=5)

text_label2 = tk.Label(frame, text="Text 2:")
text_label2.grid(row=0, column=2, padx=5, pady=5)
text_textbox2 = tk.Text(frame, wrap=tk.WORD, width=40, height=10)
text_textbox2.grid(row=0, column=3, padx=5, pady=5)

# Entry widgets and buttons
file_entry1 = tk.Entry(frame, width=50)
file_entry1.grid(row=1, column=2, columnspan=2, padx=5, pady=5)

load_button1 = tk.Button(frame, text="Load File 1", command=lambda: asyncio.run(load_file_or_display_contents(file_entry1, text_textbox1)))
load_button1.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

file_entry2 = tk.Entry(frame, width=50)
file_entry2.grid(row=2, column=2, columnspan=2, padx=5, pady=5)

load_button2 = tk.Button(frame, text="Load File 2", command=lambda: asyncio.run(load_file_or_display_contents(file_entry2, text_textbox2)))
load_button2.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

# Compare button
compare_button = tk.Button(root, text="Compare", command=lambda: asyncio.run(show_similarity()))
compare_button.pack(pady=5)

# Text widget for displaying similarity percentage
text_textbox_diff = tk.Text(root, wrap=tk.WORD, width=80, height=1)
text_textbox_diff.pack(padx=10, pady=10)

# Configure tags for highlighting similar text
text_textbox1.tag_configure("same", foreground="red", background="lightyellow")
text_textbox2.tag_configure("same", foreground="red", background="lightyellow")

# Run the main event loop
root.mainloop()


