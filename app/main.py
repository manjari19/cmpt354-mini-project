import tkinter as tk
from tkinter import messagebox, ttk

from items import find_item, borrow_item, return_item, donate_item

# Anureet's module to be inserted later
try:
    from events import find_event, register_for_event, volunteer, ask_for_help
    EVENTS_AVAILABLE = True
except ImportError:
    EVENTS_AVAILABLE = False


CATEGORIES = ["print book", "online book", "magazine", "scientific journal", "records"]


def not_implemented():
    messagebox.showinfo("Not available", "This feature isn't wired up yet.")


# Item windows

def open_find_item_window():
    win = tk.Toplevel()
    win.title("Find Item")
    win.geometry("500x400")

    tk.Label(win, text="Search (name or category):").pack(pady=5)
    search_entry = tk.Entry(win, width=40)
    search_entry.pack(pady=5)

    results_box = tk.Listbox(win, width=60, height=15)
    results_box.pack(pady=10)

    def do_search():
        results_box.delete(0, tk.END)
        term = search_entry.get().strip()
        rows = find_item(term)
        if not rows:
            results_box.insert(tk.END, "No available copies found.")
            return
        for row in rows:
            results_box.insert(
                tk.END,
                f"CopyID {row['CopyID']} — {row['Name']} ({row['Category']})"
            )

    tk.Button(win, text="Search", command=do_search).pack(pady=5)


def open_borrow_item_window():
    win = tk.Toplevel()
    win.title("Borrow Item")
    win.geometry("300x200")

    tk.Label(win, text="Member ID:").pack(pady=5)
    member_entry = tk.Entry(win)
    member_entry.pack(pady=5)

    tk.Label(win, text="Copy ID:").pack(pady=5)
    copy_entry = tk.Entry(win)
    copy_entry.pack(pady=5)

    def do_borrow():
        try:
            member_id = int(member_entry.get())
            copy_id = int(copy_entry.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Member ID and Copy ID must be numbers.")
            return
        success, message = borrow_item(member_id, copy_id)
        if success:
            messagebox.showinfo("Success", message)
            win.destroy()
        else:
            messagebox.showerror("Borrow failed", message)

    tk.Button(win, text="Borrow", command=do_borrow).pack(pady=15)


def open_return_item_window():
    win = tk.Toplevel()
    win.title("Return Item")
    win.geometry("300x150")

    tk.Label(win, text="Borrow ID:").pack(pady=5)
    borrow_entry = tk.Entry(win)
    borrow_entry.pack(pady=5)

    def do_return():
        try:
            borrow_id = int(borrow_entry.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Borrow ID must be a number.")
            return
        try:
            return_item(borrow_id)
            messagebox.showinfo("Success", "Item marked as returned.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Return failed", str(e))

    tk.Button(win, text="Return", command=do_return).pack(pady=15)


def open_donate_item_window():
    win = tk.Toplevel()
    win.title("Donate Item")
    win.geometry("350x400")

    fields = {}
    for label in ["Member ID", "Item Name", "Author", "Publisher", "Publication Date (YYYY-MM-DD)"]:
        tk.Label(win, text=label + ":").pack(pady=3)
        entry = tk.Entry(win, width=35)
        entry.pack(pady=3)
        fields[label] = entry

    tk.Label(win, text="Category:").pack(pady=3)
    category_var = tk.StringVar(value=CATEGORIES[0])
    category_menu = ttk.Combobox(win, textvariable=category_var, values=CATEGORIES, state="readonly")
    category_menu.pack(pady=3)

    def do_donate():
        try:
            member_id = int(fields["Member ID"].get())
        except ValueError:
            messagebox.showerror("Invalid input", "Member ID must be a number.")
            return
        try:
            donate_item(
                member_id,
                fields["Item Name"].get(),
                fields["Author"].get(),
                fields["Publisher"].get(),
                fields["Publication Date (YYYY-MM-DD)"].get(),
                category_var.get(),
            )
            messagebox.showinfo("Success", "Donation recorded, thank you!")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Donation failed", str(e))

    tk.Button(win, text="Donate", command=do_donate).pack(pady=15)


# Event windows (needs event.py to be built)
def open_find_event_window():
    if not EVENTS_AVAILABLE:
        not_implemented()
        return
    # TODO 

def open_register_event_window():
    if not EVENTS_AVAILABLE:
        not_implemented()
        return
    # TODO

def open_volunteer_window():
    if not EVENTS_AVAILABLE:
        not_implemented()
        return
    # TODO

def open_ask_for_help_window():
    if not EVENTS_AVAILABLE:
        not_implemented()
        return
    # TODO


# ---------- Main menu ----------

import tkinter as tk
from tkinter import ttk

LIGHT = {
    "bg": "#f5f2ed", "header_bg": "#3a2e28", "header_fg": "#ffffff",
    "section_fg": "#8a7a68", "btn_bg": "#e8e3da", "btn_fg": "#2b2420",
    "btn_active": "#d8d0c2",
}
DARK = {
    "bg": "#1e1e1c", "header_bg": "#000000", "header_fg": "#f5f2ed",
    "section_fg": "#a89f92", "btn_bg": "#332f2a", "btn_fg": "#f5f2ed",
    "btn_active": "#45403a",
}

theme = {"mode": "light"}

def apply_theme(style, root):
    colors = LIGHT if theme["mode"] == "light" else DARK
    root.configure(bg=colors["bg"])
    style.configure("Body.TFrame", background=colors["bg"])
    style.configure("Header.TFrame", background=colors["header_bg"])
    style.configure("Header.TLabel", background=colors["header_bg"], foreground=colors["header_fg"])
    style.configure("Section.TLabel", background=colors["bg"], foreground=colors["section_fg"])
    style.configure("Nav.TButton", background=colors["btn_bg"], foreground=colors["btn_fg"],
                     font=("Helvetica", 12), padding=10, borderwidth=0)
    style.map("Nav.TButton", background=[("active", colors["btn_active"])])
    style.configure("Toggle.TButton", background=colors["header_bg"], foreground=colors["header_fg"],
                     font=("Helvetica", 10), borderwidth=0)
    style.map("Toggle.TButton", background=[("active", colors["header_bg"])])


def main():
    root = tk.Tk()
    root.title("Library Database")
    root.geometry("480x620")
    root.minsize(420, 560)

    style = ttk.Style()
    style.theme_use("clam")

    def toggle_theme():
        theme["mode"] = "dark" if theme["mode"] == "light" else "light"
        toggle_btn.config(text="☀" if theme["mode"] == "dark" else "☾")
        apply_theme(style, root)

    # Header
    header = ttk.Frame(root, style="Header.TFrame", height=90)
    header.pack(fill="x")
    header.pack_propagate(False)

    ttk.Label(header, text="Library Database", style="Header.TLabel",
              font=("Helvetica", 19, "bold")).pack(side="left", padx=25, pady=25)

    toggle_btn = ttk.Button(header, text="☾", style="Toggle.TButton",
                             command=toggle_theme, width=3)
    toggle_btn.pack(side="right", padx=20, pady=25)

    # Body
    body = ttk.Frame(root, style="Body.TFrame")
    body.pack(fill="both", expand=True, padx=35, pady=25)

    def section_label(text):
        ttk.Label(body, text=text, style="Section.TLabel",
                  font=("Helvetica", 10, "bold")).pack(fill="x", pady=(16, 6))

    def nav_button(text, command):
        ttk.Button(body, text=text, style="Nav.TButton", command=command).pack(fill="x", pady=4)

    section_label("▪  ITEMS")
    nav_button("Find Item", open_find_item_window)
    nav_button("Borrow Item", open_borrow_item_window)
    nav_button("Return Item", open_return_item_window)
    nav_button("Donate Item", open_donate_item_window)

    section_label("▪  EVENTS & COMMUNITY")
    nav_button("Find Event", open_find_event_window)
    nav_button("Register for Event", open_register_event_window)
    nav_button("Volunteer", open_volunteer_window)
    nav_button("Ask a Librarian", open_ask_for_help_window)

    apply_theme(style, root)
    root.mainloop()


if __name__ == "__main__":
    main()