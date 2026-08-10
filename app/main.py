# main.py
import tkinter as tk
from tkinter import ttk

from items import find_item, borrow_item, return_item, donate_item

# insert events module later
try:
    from events import find_event, register_for_event, volunteer, ask_for_help
    EVENTS_AVAILABLE = True
except ImportError:
    EVENTS_AVAILABLE = False


CATEGORIES = ["Print Book", "Online Book", "Magazine", "Scientific Journal", "Record", "Audiobook", "DVD", "Other"]


# Theme colors
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


# Shared themed widget helpers (used by every popup window below)

def themed_toplevel(title, width=380, height=280):
    colors = LIGHT if theme["mode"] == "light" else DARK
    win = tk.Toplevel()
    win.title(title)
    win.geometry(f"{width}x{height}")
    win.configure(bg=colors["bg"])
    win.resizable(False, False)

    header = tk.Frame(win, bg=colors["header_bg"], height=55)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text=title, font=("Helvetica", 14, "bold"),
              bg=colors["header_bg"], fg=colors["header_fg"]).pack(pady=15)

    body = tk.Frame(win, bg=colors["bg"])
    body.pack(fill="both", expand=True, padx=25, pady=20)
    return win, body, colors


def themed_label(parent, text, colors):
    return tk.Label(parent, text=text, font=("Helvetica", 11),
                     bg=colors["bg"], fg=colors["btn_fg"])


def themed_entry(parent, colors, width=28):
    return tk.Entry(parent, width=width, font=("Helvetica", 11),
                     bg=colors["btn_bg"], fg=colors["btn_fg"],
                     insertbackground=colors["btn_fg"], relief="flat")


def themed_button(parent, text, command, colors):
    return tk.Button(parent, text=text, command=command,
                      font=("Helvetica", 11, "bold"), bg=colors["btn_bg"],
                      fg=colors["btn_fg"], activebackground=colors["btn_active"],
                      relief="flat", cursor="hand2", height=1)


def show_dialog(parent, kind, title, message):
    """kind: 'success' or 'error' — themed replacement for tkinter.messagebox"""
    colors = LIGHT if theme["mode"] == "light" else DARK
    accent = "#2e7d32" if kind == "success" else "#b3261e"

    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.geometry("360x200")
    dlg.configure(bg=colors["bg"])
    dlg.resizable(False, False)
    dlg.transient(parent)
    dlg.grab_set()

    style = ttk.Style(dlg)
    style.theme_use("clam")
    style.configure("Dialog.TButton", background=accent, foreground="white",
                     font=("Helvetica", 10, "bold"), borderwidth=0)
    style.map("Dialog.TButton", background=[("active", accent)])

    tk.Frame(dlg, bg=accent, height=6).pack(fill="x")
    tk.Label(dlg, text=title, font=("Helvetica", 13, "bold"),
              bg=colors["bg"], fg=accent).pack(pady=(18, 6))
    tk.Label(dlg, text=message, font=("Helvetica", 10), bg=colors["bg"],
              fg=colors["btn_fg"], wraplength=300, justify="center").pack(pady=6, padx=15)
    ttk.Button(dlg, text="OK", command=dlg.destroy, style="Dialog.TButton",
               width=10, cursor="hand2").pack(pady=15)

    dlg.wait_window()


def not_implemented():
    show_dialog(None, "error", "Not Available", "This feature isn't wired up yet.")


# Item windows

def open_find_item_window():
    win, body, colors = themed_toplevel("Find Item", 500, 440)

    themed_label(body, "Search (name or category):", colors).pack(pady=(0, 6), anchor="w")
    search_entry = themed_entry(body, colors, width=40)
    search_entry.pack(pady=(0, 10), fill="x")

    results_box = tk.Listbox(body, width=58, height=15, bg=colors["btn_bg"],
                               fg=colors["btn_fg"], relief="flat",
                               selectbackground=colors["btn_active"], font=("Helvetica", 10))
    results_box.pack(pady=(0, 10), fill="both", expand=True)

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
                f"CopyID {row['CopyID']} — {row['Name']} by {row['Author']} ({row['Category']})"
            )

    themed_button(body, "Search", do_search, colors).pack(fill="x")


def open_borrow_item_window():
    win, body, colors = themed_toplevel("Borrow Item", 360, 260)

    themed_label(body, "Member ID:", colors).pack(pady=(5, 3), anchor="w")
    member_entry = themed_entry(body, colors)
    member_entry.pack(pady=(0, 10), fill="x")

    themed_label(body, "Copy ID:", colors).pack(pady=(5, 3), anchor="w")
    copy_entry = themed_entry(body, colors)
    copy_entry.pack(pady=(0, 15), fill="x")

    def do_borrow():
        try:
            member_id = int(member_entry.get())
            copy_id = int(copy_entry.get())
        except ValueError:
            show_dialog(win, "error", "Invalid Input", "Member ID and Copy ID must be numbers.")
            return
        success, message = borrow_item(member_id, copy_id)
        if success:
            show_dialog(win, "success", "Success", message)
            win.destroy()
        else:
            show_dialog(win, "error", "Borrow Failed", message)

    themed_button(body, "Borrow", do_borrow, colors).pack(fill="x")


def open_return_item_window():
    win, body, colors = themed_toplevel("Return Item", 340, 220)

    themed_label(body, "Borrow ID:", colors).pack(pady=(10, 3), anchor="w")
    borrow_entry = themed_entry(body, colors)
    borrow_entry.pack(pady=(0, 15), fill="x")

    def do_return():
        try:
            borrow_id = int(borrow_entry.get())
        except ValueError:
            show_dialog(win, "error", "Invalid Input", "Borrow ID must be a number.")
            return
        success, message = return_item(borrow_id)
        if success:
            show_dialog(win, "success", "Success", message)
            win.destroy()
        else:
            show_dialog(win, "error", "Return Failed", message)

    themed_button(body, "Return", do_return, colors).pack(fill="x")


def open_donate_item_window():
    win, body, colors = themed_toplevel("Donate Item", 400, 480)

    fields = {}
    for label in ["Member ID", "Item Name", "Author", "Publisher", "Publication Date (YYYY-MM-DD)"]:
        themed_label(body, label + ":", colors).pack(pady=(8, 3), anchor="w")
        entry = themed_entry(body, colors, width=35)
        entry.pack(fill="x")
        fields[label] = entry

    themed_label(body, "Category:", colors).pack(pady=(8, 3), anchor="w")
    category_var = tk.StringVar(value=CATEGORIES[0])
    category_menu = ttk.Combobox(body, textvariable=category_var, values=CATEGORIES, state="readonly")
    category_menu.pack(fill="x", pady=(0, 15))

    def do_donate():
        try:
            member_id = int(fields["Member ID"].get())
        except ValueError:
            show_dialog(win, "error", "Invalid Input", "Member ID must be a number.")
            return
        success, message = donate_item(
            member_id,
            fields["Item Name"].get(),
            fields["Author"].get(),
            fields["Publisher"].get(),
            fields["Publication Date (YYYY-MM-DD)"].get(),
            category_var.get(),
        )
        if success:
            show_dialog(win, "success", "Success", message)
            win.destroy()
        else:
            show_dialog(win, "error", "Donation Failed", message)

    themed_button(body, "Donate", do_donate, colors).pack(fill="x")


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


# Main Menu

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

    header = ttk.Frame(root, style="Header.TFrame", height=90)
    header.pack(fill="x")
    header.pack_propagate(False)

    ttk.Label(header, text="Library Database", style="Header.TLabel",
              font=("Helvetica", 19, "bold")).pack(side="left", padx=25, pady=25)

    toggle_btn = ttk.Button(header, text="☾", style="Toggle.TButton",
                             command=toggle_theme, width=3)
    toggle_btn.pack(side="right", padx=20, pady=25)

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