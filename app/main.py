# main.py
import math
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

from db import cleanup_expired_holds
from items import find_item, borrow_item, return_item, donate_item, place_hold
from events import find_event, register_for_event, volunteer, ask_for_help, list_employees

CATEGORIES = ["Print Book", "Online Book", "Magazine", "Scientific Journal", "Record", "Audiobook", "DVD", "Other"]

# Theme colors
LIGHT = {
    "bg": "#f5f2ed", "header_bg": "#3a2e28", "header_fg": "#ffffff",
    "section_fg": "#8a7a68", "btn_bg": "#e8e3da", "btn_fg": "#2b2420",
    "btn_active": "#d8d0c2",
    "card_bg": "#ffffff", "card_hover": "#f0ebe1", "card_border": "#e8e3da",
    "icon_bg": "#f0ebe1", "icon_fg": "#6b5537", "card_fg": "#2b2420",
    "accent": "#6b5537", "accent_hover": "#5a4730", "toggle_bg": "#2b2420",
}
DARK = {
    "bg": "#1e1e1c", "header_bg": "#000000", "header_fg": "#f5f2ed",
    "section_fg": "#a89f92", "btn_bg": "#332f2a", "btn_fg": "#f5f2ed",
    "btn_active": "#45403a",
    "card_bg": "#2a2622", "card_hover": "#35302a", "card_border": "#3d372f",
    "icon_bg": "#3d372f", "icon_fg": "#c9bba4", "card_fg": "#f5f2ed",
    "accent": "#8a7150", "accent_hover": "#a08561", "toggle_bg": "#000000",
}
theme = {"mode": "light"}


# ---------- Drawing helpers ----------

def rounded_rect(canvas, x1, y1, x2, y2, radius, fill="", outline="", width=1):
    r = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    if r <= 0.5:
        return canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)
    items = []
    if fill:
        items.append(canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=fill))
        items.append(canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline=fill))
        items.append(canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90,
                                        fill=fill, outline=fill, style="pieslice"))
        items.append(canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90,
                                        fill=fill, outline=fill, style="pieslice"))
        items.append(canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90,
                                        fill=fill, outline=fill, style="pieslice"))
        items.append(canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90,
                                        fill=fill, outline=fill, style="pieslice"))
    if outline:
        items.append(canvas.create_line(x1 + r, y1, x2 - r, y1, fill=outline, width=width))
        items.append(canvas.create_line(x1 + r, y2, x2 - r, y2, fill=outline, width=width))
        items.append(canvas.create_line(x1, y1 + r, x1, y2 - r, fill=outline, width=width))
        items.append(canvas.create_line(x2, y1 + r, x2, y2 - r, fill=outline, width=width))
        items.append(canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90,
                                        style="arc", outline=outline, width=width))
        items.append(canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90,
                                        style="arc", outline=outline, width=width))
        items.append(canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90,
                                        style="arc", outline=outline, width=width))
        items.append(canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90,
                                        style="arc", outline=outline, width=width))
    return items


def draw_icon(canvas, kind, cx, cy, color, bg=None):
    lw = 1.8
    if kind == "search":
        canvas.create_oval(cx - 6, cy - 6, cx + 4, cy + 4, outline=color, width=lw)
        canvas.create_line(cx + 2.5, cy + 2.5, cx + 8, cy + 8, fill=color, width=lw, capstyle="round")
    elif kind == "book":
        canvas.create_line(cx - 9, cy - 6, cx, cy - 4, cx, cy + 7, cx - 9, cy + 5, cx - 9, cy - 6,
                            fill=color, width=lw, joinstyle="round")
        canvas.create_line(cx + 9, cy - 6, cx, cy - 4, cx, cy + 7, cx + 9, cy + 5, cx + 9, cy - 6,
                            fill=color, width=lw, joinstyle="round")
    elif kind == "return":
        r = 7
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r, start=20, extent=150,
                           style="arc", outline=color, width=lw)
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r, start=200, extent=150,
                           style="arc", outline=color, width=lw)
        a1 = math.radians(170)
        x1, y1 = cx + r * math.cos(a1), cy - r * math.sin(a1)
        canvas.create_polygon(x1 - 3.2, y1 - 0.5, x1 + 2.2, y1 - 3.2, x1 + 0.8, y1 + 2.5,
                               fill=color, outline=color)
        a2 = math.radians(350)
        x2, y2 = cx + r * math.cos(a2), cy - r * math.sin(a2)
        canvas.create_polygon(x2 + 3.2, y2 + 0.5, x2 - 2.2, y2 + 3.2, x2 - 0.8, y2 - 2.5,
                               fill=color, outline=color)
    elif kind == "hold":
        canvas.create_polygon(cx - 6, cy - 9, cx - 6, cy + 9, cx, cy + 3, cx + 6, cy + 9, cx + 6, cy - 9,
                               fill="", outline=color, width=lw, joinstyle="round")
    elif kind == "gift":
        canvas.create_rectangle(cx - 8, cy - 2, cx + 8, cy + 8, outline=color, width=lw)
        canvas.create_line(cx - 8, cy - 2, cx + 8, cy - 2, fill=color, width=lw)
        canvas.create_line(cx, cy - 2, cx, cy + 8, fill=color, width=lw)
        canvas.create_arc(cx - 8, cy - 9, cx, cy - 1, start=0, extent=180, style="arc", outline=color, width=lw)
        canvas.create_arc(cx, cy - 9, cx + 8, cy - 1, start=0, extent=180, style="arc", outline=color, width=lw)
    elif kind == "calendar":
        canvas.create_rectangle(cx - 9, cy - 6, cx + 9, cy + 9, outline=color, width=lw)
        canvas.create_line(cx - 9, cy - 1, cx + 9, cy - 1, fill=color, width=lw)
        canvas.create_line(cx - 4, cy - 9, cx - 4, cy -4, fill=color, width=lw, capstyle="round")
        canvas.create_line(cx + 4, cy - 9, cx + 4, cy - 4, fill=color, width=lw, capstyle="round")
    elif kind == "ticket":
        rounded_rect(canvas, cx - 9, cy - 6, cx + 9, cy + 6, 3, outline=color, width=lw, fill="")
        notch = 3.2
        punch = bg if bg else color
        canvas.create_oval(cx - 9 - notch, cy - notch, cx - 9 + notch, cy + notch, fill=punch, outline=punch)
        canvas.create_oval(cx + 9 - notch, cy - notch, cx + 9 + notch, cy + notch, fill=punch, outline=punch)
        canvas.create_line(cx + 2, cy - 4, cx + 2, cy + 4, fill=color, width=lw, dash=(1, 2))
    elif kind == "heart":
        canvas.create_arc(cx - 9, cy - 8, cx - 1, cy, start=0, extent=180,
                           style="arc", outline=color, width=lw)
        canvas.create_arc(cx + 1, cy - 8, cx + 9, cy, start=0, extent=180,
                           style="arc", outline=color, width=lw)
        canvas.create_line(cx - 9, cy - 4, cx, cy + 8, cx + 9, cy - 4,
                            fill=color, width=lw, joinstyle="round", capstyle="round")
    elif kind == "chat":
        canvas.create_rectangle(cx - 9, cy - 7, cx + 9, cy + 4, outline=color, width=lw)
        canvas.create_polygon(cx - 4, cy + 4, cx - 1, cy + 8, cx + 1, cy + 4, fill=color, outline=color)
        canvas.create_text(cx, cy - 1.5, text="?", fill=color, font=("Helvetica", 9, "bold"))
    elif kind == "book_logo":
        canvas.create_line(cx - 8, cy - 8, cx - 8, cy + 8, cx, cy + 6, cx, cy - 6, cx - 8, cy - 8,
                            fill=color, width=1.6, joinstyle="round")
        canvas.create_line(cx + 8, cy - 8, cx + 8, cy + 8, cx, cy + 6, cx, cy - 6, cx + 8, cy - 8,
                            fill=color, width=1.6, joinstyle="round")


# ---------- Custom widgets (all Canvas-based, no native button theming) ----------

def make_nav_card(parent, icon_kind, text, command, colors, height=48):
    canvas = tk.Canvas(parent, height=height, bg=colors["bg"], highlightthickness=0, bd=0, cursor="hand2")
    state = {"hover": False}

    def redraw(event=None):
        canvas.delete("all")
        w = canvas.winfo_width()
        if w < 10:
            w = 380
        fill = colors["btn_active"] if state["hover"] else colors["btn_bg"]
        rounded_rect(canvas, 0, 0, w, height, 8, fill=fill, outline="")
        box = 34
        bx1, by1 = 10, (height - box) / 2
        rounded_rect(canvas, bx1, by1, bx1 + box, by1 + box, 8, fill=colors["icon_bg"], outline="")
        draw_icon(canvas, icon_kind, bx1 + box / 2, by1 + box / 2, colors["icon_fg"], bg=colors["icon_bg"])
        canvas.create_text(bx1 + box + 14, height / 2, text=text, anchor="w",
                            font=("Helvetica", 12, "bold"), fill=colors["btn_fg"])

    def on_click(event):
        command()

    def on_enter(event):
        state["hover"] = True
        redraw()

    def on_leave(event):
        state["hover"] = False
        redraw()

    canvas.bind("<Configure>", redraw)
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    return canvas


def make_pill_button(parent, text, command, colors, height=40, width=200, accent=None, fg="white"):
    canvas = tk.Canvas(parent, height=height, bg=colors["bg"], highlightthickness=0, bd=0, cursor="hand2")
    canvas.configure(width=width)
    state = {"hover": False}
    base = accent if accent else colors["accent"]

    def redraw(event=None):
        canvas.delete("all")
        w = canvas.winfo_width()
        if w < 10:
            w = width
        fill = base if not state["hover"] else _darken(base)
        rounded_rect(canvas, 1, 1, w - 1, height - 1, height // 2, fill=fill, outline="")
        canvas.create_text(w / 2, height / 2, text=text, fill=fg, font=("Helvetica", 12, "bold"))

    def on_click(event):
        command()

    def on_enter(event):
        state["hover"] = True
        redraw()

    def on_leave(event):
        state["hover"] = False
        redraw()

    canvas.bind("<Configure>", redraw)
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    return canvas


def _darken(hex_color, amount=0.15):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, int(c * (1 - amount))) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def make_toggle_button(parent, colors, on_click):
    size = 34
    canvas = tk.Canvas(parent, width=size, height=size, bg=colors["header_bg"], highlightthickness=0,
                        bd=0, cursor="hand2")

    def redraw():
        canvas.delete("all")
        canvas.create_oval(1, 1, size - 1, size - 1, fill=colors["toggle_bg"], outline="")
        cx, cy = size / 2, size / 2
        if theme["mode"] == "light":
            canvas.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill=colors["header_fg"], outline="")
            canvas.create_oval(cx - 3.5, cy - 8.5, cx + 10.5, cy + 5.5, fill=colors["toggle_bg"], outline="")
        else:
            canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=colors["header_fg"], outline="")
            for ang in range(0, 360, 45):
                x1 = cx + 7 * math.cos(math.radians(ang))
                y1 = cy + 7 * math.sin(math.radians(ang))
                x2 = cx + 11 * math.cos(math.radians(ang))
                y2 = cy + 11 * math.sin(math.radians(ang))
                canvas.create_line(x1, y1, x2, y2, fill=colors["header_fg"], width=1.6, capstyle="round")

    def handle_click(event):
        on_click()
        redraw()

    canvas.bind("<Button-1>", handle_click)
    redraw()
    return canvas


# ---------- Themed popup helpers ----------

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

    win.focus_force()

    return win, body, colors

def themed_label(parent, text, colors):
    return tk.Label(parent, text=text, font=("Helvetica", 11),
                     bg=colors["bg"], fg=colors["btn_fg"])

def themed_entry(parent, colors, width=28):
    return tk.Entry(parent, width=width, font=("Helvetica", 11),
                     bg=colors["btn_bg"], fg=colors["btn_fg"],
                     insertbackground=colors["btn_fg"], relief="flat",
                     borderwidth=0, highlightthickness=1,
                     highlightbackground=colors["card_border"], highlightcolor=colors["accent"])

def themed_button(parent, text, command, colors, accent=None, width=None):
    return make_pill_button(parent, text, command, colors, accent=accent, width=width or 260)

def show_dialog(parent, kind, title, message):
    """kind: 'success' or 'error' — themed replacement for tkinter.messagebox"""
    colors = LIGHT if theme["mode"] == "light" else DARK
    accent = "#2e7d32" if kind == "success" else "#b3261e"

    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.geometry("360x210")
    dlg.configure(bg=colors["bg"])
    dlg.resizable(False, False)
    dlg.transient(parent)
    dlg.grab_set()

    tk.Frame(dlg, bg=accent, height=6).pack(fill="x")
    tk.Label(dlg, text=title, font=("Helvetica", 13, "bold"),
              bg=colors["bg"], fg=accent).pack(pady=(18, 6))
    tk.Label(dlg, text=message, font=("Helvetica", 10), bg=colors["bg"],
              fg=colors["btn_fg"], wraplength=300, justify="center").pack(pady=6, padx=15)
    make_pill_button(dlg, "OK", dlg.destroy, colors, accent=accent, width=120).pack(pady=15)

    dlg.after(50, dlg.focus_force)
    dlg.wait_window()

def open_find_item_window():
    win, body, colors = themed_toplevel("Find Item", 500, 520)

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
                f"ItemID {row['ItemID']} / CopyID {row['CopyID']} - {row['Name']} by {row['Author']} ({row['Status']})"
            )

    win.bind("<Return>", lambda event: do_search())
    themed_button(body, "Search", do_search, colors, width=450).pack(fill="x")

def open_borrow_item_window():
    win, body, colors = themed_toplevel("Borrow Item", 360, 300)

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

    win.bind("<Return>", lambda event: do_borrow())
    themed_button(body, "Borrow", do_borrow, colors, width=310).pack(fill="x")

def open_return_item_window():
    win, body, colors = themed_toplevel("Return Item", 340, 260)

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

    win.bind("<Return>", lambda event: do_return())
    themed_button(body, "Return", do_return, colors, width=290).pack(fill="x")

def open_place_hold_window():
    win, body, colors = themed_toplevel("Place Hold", 360, 300)

    themed_label(body, "Member ID:", colors).pack(pady=(5, 3), anchor="w")
    member_entry = themed_entry(body, colors)
    member_entry.pack(pady=(0, 10), fill="x")
    member_entry.focus_set()

    themed_label(body, "Item ID:", colors).pack(pady=(5, 3), anchor="w")
    item_entry = themed_entry(body, colors)
    item_entry.pack(pady=(0, 15), fill="x")

    def do_hold():
        try:
            member_id = int(member_entry.get())
            item_id = int(item_entry.get())
        except ValueError:
            show_dialog(win, "error", "Invalid Input", "Member ID and Item ID must be numbers.")
            return
        success, message = place_hold(member_id, item_id)
        if success:
            show_dialog(win, "success", "Success", message)
            win.destroy()
        else:
            show_dialog(win, "error", "Hold Failed", message)

    win.bind("<Return>", lambda event: do_hold())
    themed_button(body, "Place Hold", do_hold, colors, width=310).pack(fill="x")

def open_donate_item_window():
    win, body, colors = themed_toplevel("Donate Item", 420, 560)

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

    themed_button(body, "Donate", do_donate, colors, width=350).pack(fill="x")

# Event Windows
def open_find_event_window():
    win, body, colors = themed_toplevel("Find Event", 540, 520)

    themed_label(body, "Search (title or type):", colors).pack(pady=(0, 6), anchor="w")
    search_entry = themed_entry(body, colors, width=40)
    search_entry.pack(pady=(0, 10), fill="x")
    search_entry.focus_set()

    results_box = tk.Listbox(body, width=62, height=15, bg=colors["btn_bg"],
                               fg=colors["btn_fg"], relief="flat",
                               selectbackground=colors["btn_active"], font=("Helvetica", 10))
    results_box.pack(pady=(0, 10), fill="both", expand=True)

    def do_search():
        results_box.delete(0, tk.END)
        rows = find_event(search_entry.get().strip())
        if not rows:
            results_box.insert(tk.END, "No events found.")
            return
        for row in rows:
            seats = "Full" if row["SeatsLeft"] <= 0 else f"{row['SeatsLeft']} seats left"
            results_box.insert(tk.END, f"Event {row['EventID']}: {row['Title']} ({row['Type']})")
            results_box.insert(tk.END, f"    {row['Date']}  {row['StartTime']}-{row['EndTime']}"
                                       f"  Ages {row['RecommendedMinAge']}+  {seats}")

    win.bind("<Return>", lambda event: do_search())
    themed_button(body, "Search", do_search, colors, width=490).pack(fill="x")

def open_register_event_window():
    win, body, colors = themed_toplevel("Register for Event", 360, 310)

    themed_label(body, "Member ID:", colors).pack(pady=(5, 3), anchor="w")
    member_entry = themed_entry(body, colors)
    member_entry.pack(pady=(0, 10), fill="x")
    member_entry.focus_set()

    themed_label(body, "Event ID:", colors).pack(pady=(5, 3), anchor="w")
    event_entry = themed_entry(body, colors)
    event_entry.pack(pady=(0, 15), fill="x")

    def do_register():
        try:
            member_id = int(member_entry.get())
            event_id = int(event_entry.get())
        except ValueError:
            show_dialog(win, "error", "Invalid Input", "Member ID and Event ID must be numbers.")
            return
        success, message = register_for_event(member_id, event_id)
        if success:
            show_dialog(win, "success", "Success", message)
            win.destroy()
        else:
            show_dialog(win, "error", "Registration Failed", message)

    win.bind("<Return>", lambda event: do_register())
    themed_button(body, "Register", do_register, colors, width=310).pack(fill="x")

def open_volunteer_window():
    win, body, colors = themed_toplevel("Volunteer", 390, 400)

    themed_label(body, "Member ID:", colors).pack(pady=(5, 3), anchor="w")
    member_entry = themed_entry(body, colors, width=32)
    member_entry.pack(pady=(0, 10), fill="x")
    member_entry.focus_set()

    themed_label(body, "Event ID (leave blank to just sign up):", colors).pack(pady=(5, 3), anchor="w")
    event_entry = themed_entry(body, colors, width=32)
    event_entry.pack(pady=(0, 10), fill="x")

    themed_label(body, "Role at the event:", colors).pack(pady=(5, 3), anchor="w")
    role_entry = themed_entry(body, colors, width=32)
    role_entry.pack(pady=(0, 15), fill="x")

    def do_volunteer():
        try:
            member_id = int(member_entry.get())
            event_id = int(event_entry.get()) if event_entry.get().strip() else None
        except ValueError:
            show_dialog(win, "error", "Invalid Input", "Member ID and Event ID must be numbers.")
            return
        role = role_entry.get().strip()
        if event_id and not role:
            show_dialog(win, "error", "Invalid Input", "Please enter a role for the event.")
            return
        success, message = volunteer(member_id, event_id, role)
        if success:
            show_dialog(win, "success", "Success", message)
            win.destroy()
        else:
            show_dialog(win, "error", "Volunteer Failed", message)

    win.bind("<Return>", lambda event: do_volunteer())
    themed_button(body, "Volunteer", do_volunteer, colors, width=340).pack(fill="x")

def open_ask_for_help_window():
    win, body, colors = themed_toplevel("Ask a Librarian", 420, 460)

    themed_label(body, "Member ID:", colors).pack(pady=(5, 3), anchor="w")
    member_entry = themed_entry(body, colors, width=34)
    member_entry.pack(pady=(0, 10), fill="x")
    member_entry.focus_set()

    themed_label(body, "Librarian:", colors).pack(pady=(5, 3), anchor="w")
    employees = list_employees()
    labels = [f"{row['EmployeeID']}: {row['Name']}" for row in employees]
    employee_var = tk.StringVar(value=labels[0])
    ttk.Combobox(body, textvariable=employee_var, values=labels,
                 state="readonly").pack(fill="x", pady=(0, 10))

    themed_label(body, "How can we help?", colors).pack(pady=(5, 3), anchor="w")
    request_box = tk.Text(body, height=6, bg=colors["btn_bg"], fg=colors["btn_fg"],
                          insertbackground=colors["btn_fg"], relief="flat",
                          font=("Helvetica", 10), wrap="word")
    request_box.pack(fill="both", expand=True, pady=(0, 15))

    def do_ask():
        try:
            member_id = int(member_entry.get())
        except ValueError:
            show_dialog(win, "error", "Invalid Input", "Member ID must be a number.")
            return
        request_text = request_box.get("1.0", tk.END).strip()
        if not request_text:
            show_dialog(win, "error", "Invalid Input", "Please describe what you need help with.")
            return
        employee_id = int(employee_var.get().split(":")[0])
        success, message = ask_for_help(member_id, employee_id, request_text)
        if success:
            show_dialog(win, "success", "Request Sent", message)
            win.destroy()
        else:
            show_dialog(win, "error", "Request Failed", message)

    themed_button(body, "Send Request", do_ask, colors, width=350).pack(fill="x")

def _activate_macos_app():
    if sys.platform == "darwin":
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to set frontmost of '
            'the first process whose unix id is {} to true'.format(os.getpid())
        ])

# Main Menu
def main():
    cleanup_expired_holds()

    root = tk.Tk()
    root.configure(bg=LIGHT["bg"])
    root.after(100, _activate_macos_app)
    root.title("Library Database")
    root.geometry("500x780")
    root.minsize(460, 760)

    def redraw_all():
        colors = LIGHT if theme["mode"] == "light" else DARK
        root.configure(bg=colors["bg"])
        header.configure(bg=colors["header_bg"])
        header_left.configure(bg=colors["header_bg"])
        logo_canvas.configure(bg=colors["header_bg"])
        logo_canvas.delete("all")
        draw_icon(logo_canvas, "book_logo", 13, 13, colors["header_fg"])
        title_label.configure(bg=colors["header_bg"], fg=colors["header_fg"])
        body.configure(bg=colors["bg"])
        items_label.configure(bg=colors["bg"], fg=colors["section_fg"])
        events_label.configure(bg=colors["bg"], fg=colors["section_fg"])
        items_frame.configure(bg=colors["bg"])
        events_frame.configure(bg=colors["bg"])
        for card in cards:
            card.destroy()
        cards.clear()
        build_cards(colors)
        toggle_canvas.configure(bg=colors["header_bg"])
        toggle_redraw()

    def toggle_theme():
        theme["mode"] = "dark" if theme["mode"] == "light" else "light"
        redraw_all()

    header = tk.Frame(root, bg=LIGHT["header_bg"], height=90)
    header.pack(fill="x")
    header.pack_propagate(False)

    header_left = tk.Frame(header, bg=LIGHT["header_bg"])
    header_left.pack(side="left", padx=25, pady=25)
    logo_canvas = tk.Canvas(header_left, width=26, height=26, bg=LIGHT["header_bg"],
                             highlightthickness=0, bd=0)
    logo_canvas.pack(side="left", padx=(0, 10))
    draw_icon(logo_canvas, "book_logo", 13, 13, LIGHT["header_fg"])
    title_label = tk.Label(header_left, text="Library Database", font=("Helvetica", 19, "bold"),
                            bg=LIGHT["header_bg"], fg=LIGHT["header_fg"])
    title_label.pack(side="left")

    toggle_canvas = make_toggle_button(header, LIGHT, toggle_theme)
    toggle_canvas.pack(side="right", padx=20, pady=25)

    def toggle_redraw():
        colors = LIGHT if theme["mode"] == "light" else DARK
        toggle_canvas.delete("all")
        size = 34
        toggle_canvas.create_oval(1, 1, size - 1, size - 1, fill=colors["toggle_bg"], outline="")
        cx, cy = size / 2, size / 2
        if theme["mode"] == "light":
            toggle_canvas.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill=colors["header_fg"], outline="")
            toggle_canvas.create_oval(cx - 3.5, cy - 8.5, cx + 10.5, cy + 5.5, fill=colors["toggle_bg"], outline="")
        else:
            toggle_canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=colors["header_fg"], outline="")
            for ang in range(0, 360, 45):
                x1 = cx + 7 * math.cos(math.radians(ang))
                y1 = cy + 7 * math.sin(math.radians(ang))
                x2 = cx + 11 * math.cos(math.radians(ang))
                y2 = cy + 11 * math.sin(math.radians(ang))
                toggle_canvas.create_line(x1, y1, x2, y2, fill=colors["header_fg"], width=1.6, capstyle="round")

    body = tk.Frame(root, bg=LIGHT["bg"])
    body.pack(fill="both", expand=True, padx=24, pady=22)

    items_label = tk.Label(body, text="ITEMS", font=("Helvetica", 10, "bold"),
                            bg=LIGHT["bg"], fg=LIGHT["section_fg"], anchor="w")
    items_label.pack(fill="x", pady=(0, 8))

    items_frame = tk.Frame(body, bg=LIGHT["bg"])
    items_frame.pack(fill="x")

    events_label = tk.Label(body, text="EVENTS & COMMUNITY", font=("Helvetica", 10, "bold"),
                             bg=LIGHT["bg"], fg=LIGHT["section_fg"], anchor="w")
    events_label.pack(fill="x", pady=(20, 8))

    events_frame = tk.Frame(body, bg=LIGHT["bg"])
    events_frame.pack(fill="x")

    cards = []

    def build_cards(colors):
        item_specs = [
            ("search", "Find Item", open_find_item_window),
            ("book", "Borrow Item", open_borrow_item_window),
            ("return", "Return Item", open_return_item_window),
            ("hold", "Place Hold", open_place_hold_window),
            ("gift", "Donate Item", open_donate_item_window),
        ]
        event_specs = [
            ("calendar", "Find Event", open_find_event_window),
            ("ticket", "Register for Event", open_register_event_window),
            ("heart", "Volunteer", open_volunteer_window),
            ("chat", "Ask a Librarian", open_ask_for_help_window),
        ]
        for icon_kind, text, command in item_specs:
            card = make_nav_card(items_frame, icon_kind, text, command, colors)
            card.pack(fill="x", pady=4)
            cards.append(card)
        for icon_kind, text, command in event_specs:
            card = make_nav_card(events_frame, icon_kind, text, command, colors)
            card.pack(fill="x", pady=4)
            cards.append(card)

    build_cards(LIGHT)

    root.mainloop()

if __name__ == "__main__":
    main()