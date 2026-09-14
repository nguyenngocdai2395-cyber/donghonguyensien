"""Gia phả dòng họ Nguyễn Siên - Ứng dụng Desktop thuần Python 3.13.

Cập nhật:
1. Tách biệt trường "Năm sinh", "Còn sống" (checkbox) và "Năm mất".
2. Tự động đồng bộ: Điền năm mất -> tự động bỏ tick "Còn sống". Uncheck "Còn sống" hoặc điền năm mất -> viền ô đổi thành màu đen (#000000).
3. Tick "Còn sống" -> viền ô hiển thị màu xanh lá (#2b9a5a).
4. Viền nét đứt khi đang chỉnh sửa/double click, và nét liền sau khi Lưu.
"""
from __future__ import annotations

import copy
import json
import tkinter as tk
from dataclasses import asdict, dataclass
from pathlib import Path
from tkinter import messagebox, ttk
from uuid import uuid4

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "family_desktop.json"
BG_IMAGE_FILE = APP_DIR / "NenGiaPhaHoNguyenSien.jpg"

# Kích thước ô hiển thị (giảm chiều cao xuống 100 để ô lùn hơn)
NODE_W, NODE_H = 180, 100
ROW_GAP, TOP = 150, 60
MIN_X_GAP = NODE_W + 25


@dataclass
class Person:
    id: str
    name: str = "Chua đặt tên"
    gender: str = "Nam"
    alive: bool = True
    born: str = ""
    died: str = ""
    bio: str = ""
    note: str = ""
    generation: int = 1
    x: float = 360.0
    birth_order: int = 1
    is_fixed: bool = False
    wife_order: int | None = None  # Thêm dòng này vào đây
    
@dataclass
class Relationship:
    source: str
    target: str
    kind: str  # 'spouse' hoặc 'parent'
    divorced: bool = False
    wife_order: int = 1


class FamilyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gia phả dòng họ Nguyễn Siên - GiaPhaA")
        self.geometry("1450x850")
        self.minsize(1050, 650)

        self.people: list[Person] = []
        self.relationships: list[Relationship] = []
        self.generations = 8
        self.selected_id: str | None = None
        self.search_keyword: str = ""

        self.drag_id: str | None = None
        self.drag_origin: tuple[float, float] | None = None
        self.pan_origin: tuple[float, float] | None = None
        self.zoom, self.offset_x, self.offset_y = 1.0, 0.0, 0.0

        self.history: list[dict] = []
        self.bg_image_tk = None

        self._make_ui()
        self._load_bg_image()
        self.load_data()

        if not self.people:
            self.init_giapha_a()

        self.bind("<Control-s>", lambda _e: self.save_data())
        self.bind("<Control-z>", lambda _e: self.undo())
        self.bind("<Control-n>", lambda _e: self.add_person())

    def _load_bg_image(self):
        if BG_IMAGE_FILE.exists():
            try:
                self.bg_image_tk = tk.PhotoImage(file=str(BG_IMAGE_FILE))
            except Exception:
                self.bg_image_tk = None

    def init_giapha_a(self):
        self.people.clear()
        self.relationships.clear()

        ids = {k: str(uuid4()) for k in ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N"]}

        # Đời 1
        self.people.append(Person(id=ids["A"], name="A", gender="Nam", generation=1, x=200, is_fixed=True, alive=False, born="1800", died="1860"))
        self.people.append(Person(id=ids["B"], name="B", gender="Nữ", generation=1, x=500, is_fixed=True, alive=False, born="1802", died="1865"))
        self.relationships.append(Relationship(source=ids["A"], target=ids["B"], kind="spouse"))

        # Đời 2
        self.people.append(Person(id=ids["C"], name="C", gender="Nam", generation=2, birth_order=1, x=100, is_fixed=True, alive=False, born="1825", died="1890"))
        self.people.append(Person(id=ids["F"], name="F", gender="Nữ", generation=2, x=340, wife_order=1, is_fixed=True, alive=False, born="1828", died="1895"))
        self.people.append(Person(id=ids["G"], name="G", gender="Nữ", generation=2, x=580, wife_order=2, is_fixed=True, alive=False, born="1830", died="1900"))

        self.people.append(Person(id=ids["D"], name="D", gender="Nữ", generation=2, birth_order=2, x=820, is_fixed=True, alive=False, born="1832", died="1905"))
        self.people.append(Person(id=ids["H"], name="H", gender="Nam", generation=2, x=1060, is_fixed=True, alive=False, born="1830", died="1902"))

        self.people.append(Person(id=ids["E"], name="E", gender="Nam", generation=2, birth_order=3, x=1300, is_fixed=True, alive=False, born="1835", died="1910"))
        self.people.append(Person(id=ids["J"], name="J", gender="Nữ", generation=2, x=1540, is_fixed=True, alive=False, born="1838", died="1912"))

        for child_key in ["C", "D", "E"]:
            self.relationships.append(Relationship(source=ids["A"], target=ids[child_key], kind="parent"))
            self.relationships.append(Relationship(source=ids["B"], target=ids[child_key], kind="parent"))

        self.relationships.append(Relationship(source=ids["C"], target=ids["F"], kind="spouse", wife_order=1))
        self.relationships.append(Relationship(source=ids["C"], target=ids["G"], kind="spouse", wife_order=2))
        self.relationships.append(Relationship(source=ids["H"], target=ids["D"], kind="spouse"))
        self.relationships.append(Relationship(source=ids["E"], target=ids["J"], kind="spouse"))

        # Đời 3
        self.people.append(Person(id=ids["K"], name="K", gender="Nam", generation=3, x=220, is_fixed=True, alive=False, born="1855", died="1920"))
        self.people.append(Person(id=ids["L"], name="L", gender="Nữ", generation=3, x=460, is_fixed=True, alive=False, born="1858", died="1925"))
        self.people.append(Person(id=ids["M"], name="M", gender="Nam", generation=3, x=940, is_fixed=True, alive=False, born="1860", died="1930"))
        self.people.append(Person(id=ids["N"], name="N", gender="Nam", generation=3, x=1420, is_fixed=True, alive=False, born="1865", died="1935"))

        self.relationships.append(Relationship(source=ids["C"], target=ids["K"], kind="parent"))
        self.relationships.append(Relationship(source=ids["F"], target=ids["K"], kind="parent"))

        self.relationships.append(Relationship(source=ids["C"], target=ids["L"], kind="parent"))
        self.relationships.append(Relationship(source=ids["G"], target=ids["L"], kind="parent"))

        self.relationships.append(Relationship(source=ids["D"], target=ids["M"], kind="parent"))
        self.relationships.append(Relationship(source=ids["H"], target=ids["M"], kind="parent"))

        self.relationships.append(Relationship(source=ids["E"], target=ids["N"], kind="parent"))
        self.relationships.append(Relationship(source=ids["J"], target=ids["N"], kind="parent"))

        self.redraw()

    def add_generation(self):
        self.push_undo()
        self.generations += 1
        self.refresh_generation_choices()
        self.redraw()
        self.status.config(text=f"Đã thêm đời mới. Tổng số đời hiện tại: {self.generations}")

    def push_undo(self):
        state = {
            "generations": self.generations,
            "people": copy.deepcopy(self.people),
            "relationships": copy.deepcopy(self.relationships),
            "selected_id": self.selected_id,
        }
        self.history.append(state)
        if len(self.history) > 30:
            self.history.pop(0)

    def undo(self):
        if not self.history:
            self.status.config(text="Không có thao tác nào để hoàn tác.")
            return
        state = self.history.pop()
        self.generations = state["generations"]
        self.people = state["people"]
        self.relationships = state["relationships"]
        self.selected_id = state["selected_id"]

        self.refresh_generation_choices()
        p = self.get_person(self.selected_id) if self.selected_id else None
        if p:
            self.show_person(p)
        else:
            self.clear_form()
        self.redraw()
        self.status.config(text="Đã hoàn tác (Ctrl+Z)")

    def _make_ui(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")

        style.configure("Toolbar.TFrame", background="#12304f")
        style.configure("Title.TLabel", background="#12304f", foreground="white", font=("Segoe UI", 11, "bold"))
        style.configure("Toolbar.TLabel", background="#12304f", foreground="#dbe8f5")
        style.configure("App.TButton", font=("Segoe UI", 9), padding=(5, 3))
        style.configure("Save.TButton", font=("Segoe UI", 9, "bold"), padding=(5, 3))

        toolbar = ttk.Frame(self, padding=(8, 5), style="Toolbar.TFrame")
        toolbar.pack(fill="x")

        ttk.Label(toolbar, text="GIA PHẢ NGUYỄN SIÊN", style="Title.TLabel").pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="+ Thêm đời", command=self.add_generation, style="App.TButton").pack(side="left", padx=2)
        ttk.Button(toolbar, text="+ Thêm ô (Ctrl+N)", command=self.add_person, style="App.TButton").pack(side="left", padx=2)
        ttk.Button(toolbar, text="Hoàn tác (Ctrl+Z)", command=self.undo, style="App.TButton").pack(side="left", padx=2)
        ttk.Button(toolbar, text="Lưu (Ctrl+S)", command=self.save_data, style="Save.TButton").pack(side="left", padx=2)
        ttk.Button(toolbar, text="Vừa khung", command=self.fit_view, style="App.TButton").pack(side="left", padx=2)

        search_frame = ttk.Frame(toolbar, style="Toolbar.TFrame")
        search_frame.pack(side="right", padx=5)

        ttk.Label(search_frame, text="🔍 Tìm tên:", style="Toolbar.TLabel").pack(side="left", padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.on_search_changed())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=18, font=("Segoe UI", 9))
        search_entry.pack(side="left", padx=(0, 2))
        search_entry.bind("<Return>", lambda _e: self.trigger_search())
        ttk.Button(search_frame, text="Tìm", command=self.trigger_search, style="App.TButton").pack(side="left")

        self.status = ttk.Label(toolbar, text="Sẵn sàng", style="Toolbar.TLabel")
        self.status.pack(side="right", padx=10)

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)

        canvas_frame = ttk.Frame(body)
        self.canvas = tk.Canvas(canvas_frame, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Mở khóa & Kéo thả / Sửa", command=self.unlock_selected_for_drag)
        self.context_menu.add_command(label="Xóa ô này", command=self.delete_person)

        self.wire_menu = tk.Menu(self, tearoff=0)
        self.wire_menu.add_command(label="Xóa mối quan hệ này", command=self.delete_selected_wire)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.zoom_at(e.x, e.y, 1.1))
        self.canvas.bind("<Button-5>", lambda e: self.zoom_at(e.x, e.y, 1 / 1.1))
        self.canvas.bind("<Configure>", lambda _e: self.redraw())

        side = ttk.Frame(body, width=190, padding=4)

        body.add(canvas_frame, weight=12)
        body.add(side, weight=0)

        ttk.Label(side, text="THÔNG TIN THÀNH VIÊN", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        self.info_hint = ttk.Label(side, text="Chọn ô sửa (Enter lưu).", wraplength=175, foreground="#596579", font=("Segoe UI", 7))
        self.info_hint.pack(anchor="w", pady=(0, 2))

        self.form = {}
        for label, key in (("Họ tên", "name"), ("Ghi chú (dưới tên)", "note"), ("Năm sinh", "born")):
            ttk.Label(side, text=label, font=("Segoe UI", 8)).pack(anchor="w", pady=(1, 0))
            var = tk.StringVar()
            self.form[key] = var
            entry = ttk.Entry(side, textvariable=var, font=("Segoe UI", 8))
            entry.pack(fill="x")
            entry.bind("<Return>", lambda _e: self.apply_form())

        # Checkbox Còn sống tách biệt
        self.form["alive"] = tk.BooleanVar(value=True)
        self.chk_alive = ttk.Checkbutton(side, text="Còn sống", variable=self.form["alive"])
        self.chk_alive.pack(anchor="w", pady=(2, 0))

        # Trường Năm mất tách biệt
        ttk.Label(side, text="Năm mất", font=("Segoe UI", 8)).pack(anchor="w", pady=(1, 0))
        self.form["died"] = tk.StringVar()
        self.entry_died = ttk.Entry(side, textvariable=self.form["died"], font=("Segoe UI", 8))
        self.entry_died.pack(fill="x")
        self.entry_died.bind("<KeyRelease>", lambda _e: self.on_died_typed())
        self.entry_died.bind("<Return>", lambda _e: self.apply_form())

        ttk.Label(side, text="Giới tính", font=("Segoe UI", 8)).pack(anchor="w", pady=(1, 0))
        self.form["gender"] = tk.StringVar(value="Nam")
        cb_gender = ttk.Combobox(side, textvariable=self.form["gender"], values=("Nam", "Nữ"), state="readonly", font=("Segoe UI", 8))
        cb_gender.pack(fill="x")
        cb_gender.bind("<Return>", lambda _e: self.apply_form())

        ttk.Label(side, text="Đời", font=("Segoe UI", 8)).pack(anchor="w", pady=(1, 0))
        self.form["generation"] = tk.StringVar(value="1")
        self.generation_box = ttk.Combobox(side, textvariable=self.form["generation"], state="readonly", font=("Segoe UI", 8))
        self.generation_box.pack(fill="x")
        self.generation_box.bind("<Return>", lambda _e: self.apply_form())
        self.refresh_generation_choices()

        ttk.Label(side, text="Con thứ", font=("Segoe UI", 8)).pack(anchor="w", pady=(1, 0))
        self.form["birth_order"] = tk.IntVar(value=1)
        sp_order = ttk.Spinbox(side, from_=1, to=30, textvariable=self.form["birth_order"], width=4, font=("Segoe UI", 8))
        sp_order.pack(anchor="w")
        sp_order.bind("<Return>", lambda _e: self.apply_form())

        ttk.Label(side, text="Liên kết:", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(4, 1))
        self.relations_label = ttk.Label(side, text="—", wraplength=175, justify="left", font=("Segoe UI", 7, "italic"), foreground="#2c3e50")
        self.relations_label.pack(anchor="w", pady=(0, 2))

        ttk.Label(side, text="Tiểu sử chi tiết", font=("Segoe UI", 8)).pack(anchor="w", pady=(1, 0))
        self.bio_text = tk.Text(side, height=2, wrap="word", font=("Segoe UI", 8))
        self.bio_text.pack(fill="both", expand=True)

        sub_btns = ttk.Frame(side)
        sub_btns.pack(fill="x", pady=(4, 2))
        ttk.Button(sub_btns, text="Lưu", command=self.apply_form, style="Save.TButton").pack(side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(sub_btns, text="Xóa", command=self.delete_person).pack(side="right", padx=(2, 0))

    def on_died_typed(self):
        val = self.form["died"].get().strip()
        if val:
            self.form["alive"].set(False)

    def on_search_changed(self):
        self.search_keyword = self.search_var.get().strip().lower()
        self.redraw()

    def trigger_search(self):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            return
        matches = [p for p in self.people if keyword in p.name.lower() or keyword in p.note.lower()]
        if matches:
            target = matches[0]
            self.selected_id = target.id
            self.show_person(target)
            cx = target.x + NODE_W / 2
            cy = self.y_of(target.generation) + NODE_H / 2
            self.offset_x = self.canvas.winfo_width() / 2 - cx * self.zoom
            self.offset_y = self.canvas.winfo_height() / 2 - cy * self.zoom
            self.redraw()
            self.status.config(text=f"Đã tìm thấy thành viên: {target.name}")
        else:
            self.status.config(text=f"Không tìm thấy từ khóa: '{keyword}'")

    def clear_form(self):
        self.info_hint.config(text="Chọn ô xem/sửa.")
        for key in ("name", "note", "born", "died"):
            self.form[key].set("")
        self.form["alive"].set(True)
        self.form["gender"].set("Nam")
        self.form["generation"].set("1")
        self.form["birth_order"].set(1)
        self.bio_text.delete("1.0", "end")
        self.relations_label.config(text="—")

    def to_screen(self, x, y):
        return x * self.zoom + self.offset_x, y * self.zoom + self.offset_y

    def to_model(self, x, y):
        return (x - self.offset_x) / self.zoom, (y - self.offset_y) / self.zoom

    def y_of(self, generation):
        return TOP + (generation - 1) * ROW_GAP

    def get_person(self, person_id):
        return next((p for p in self.people if p.id == person_id), None)

    def spouses_of(self, person_id: str) -> list[tuple[Person, Relationship]]:
        res = []
        for r in self.relationships:
            if r.kind == "spouse" and person_id in (r.source, r.target):
                other_id = r.target if r.source == person_id else r.source
                sp = self.get_person(other_id)
                if sp:
                    res.append((sp, r))
        return res

    def parents_of(self, person_id: str) -> list[Person]:
        parent_ids = [r.source for r in self.relationships if r.kind == "parent" and r.target == person_id]
        return [self.get_person(pid) for pid in parent_ids if self.get_person(pid)]

    def is_patrilineal(self, person_id: str) -> bool:
        p = self.get_person(person_id)
        if not p:
            return False
        if p.name == "A" or (p.generation == 1 and p.gender == "Nam"):
            return True
        parents = self.parents_of(person_id)
        for parent in parents:
            if parent.gender == "Nam" and self.is_patrilineal(parent.id):
                return True
        return False

    def is_daughter_of_family(self, person_id: str) -> bool:
        p = self.get_person(person_id)
        if not p or p.gender != "Nữ":
            return False
        parents = self.parents_of(person_id)
        for parent in parents:
            if parent.gender == "Nam" and self.is_patrilineal(parent.id):
                return True
        return False

    def is_spouse_only(self, person_id: str) -> bool:
        p = self.get_person(person_id)
        if not p:
            return False
        if p.generation == 1 and p.name != "A":
            return True
        parents = self.parents_of(person_id)
        if not parents:
            spouses = self.spouses_of(person_id)
            if spouses:
                return True
        return False

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        points = (
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1
        )
        return self.canvas.create_polygon(points, smooth=True, splinesteps=16, **kwargs)

    def draw_bg_image(self):
        if self.bg_image_tk:
            img_id = self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw")
            self.canvas.tag_lower(img_id)

    def redraw(self):
        c = self.canvas
        c.delete("all")
        self.draw_bg_image()

        for generation in range(1, self.generations + 1):
            y = self.y_of(generation)
            sx, sy = self.to_screen(0, y)
            c.create_text(16, sy + 10 * self.zoom, text=f"ĐỜI {generation}", anchor="w", fill="#294b6d", font=("Segoe UI", max(8, int(10 * self.zoom)), "bold"))
            if generation < self.generations:
                separator_y = sy + (NODE_H + (ROW_GAP - NODE_H) / 2) * self.zoom
                c.create_line(16, separator_y, c.winfo_width() - 16, separator_y, fill="#d8e0ea", width=max(1, int(2 * self.zoom)))

        joint_trunks_drawn = set()
        for idx, rel in enumerate(self.relationships):
            a, b = self.get_person(rel.source), self.get_person(rel.target)
            if not a or not b:
                continue

            ax, ay = self.to_screen(a.x + NODE_W / 2, self.y_of(a.generation) + NODE_H / 2)
            bx, by = self.to_screen(b.x + NODE_W / 2, self.y_of(b.generation) + NODE_H / 2)
            line_tags = ("wire", f"rel_{idx}")

            if rel.kind == "spouse":
                is_female_line = (a.name in ("A", "B") and b.name in ("A", "B")) == False and (self.is_daughter_of_family(a.id) or self.is_daughter_of_family(b.id))
                color = "#7f8c8d" if is_female_line else "#e74c3c"
                if a.name in ("A", "B") and b.name in ("A", "B"):
                    color = "#e74c3c"
                dash_style = (7, 4) if rel.divorced else ()
                c.create_line(ax, ay, bx, by, fill=color, width=max(3, int(4 * self.zoom)), dash=dash_style, tags=line_tags)
            else:
                child_top_x = bx
                child_top_y = by - (NODE_H / 2) * self.zoom
                
                line_color = "#e67e22" if self.is_patrilineal(b.id) else "#7f8c8d"
                if a.name in ("A", "B"):
                    line_color = "#e67e22"

                parents = self.parents_of(b.id)
                if len(parents) == 2:
                    p1, p2 = parents[0], parents[1]
                    if a.id > p2.id if p1.id == a.id else a.id > p1.id:
                        continue
                    p1_x, p1_y = self.to_screen(p1.x + NODE_W / 2, self.y_of(p1.generation) + NODE_H / 2)
                    p2_x, p2_y = self.to_screen(p2.x + NODE_W / 2, self.y_of(p2.generation) + NODE_H / 2)

                    start_x, start_y = (p1_x + p2_x) / 2, (p1_y + p2_y) / 2
                    parent_bottom_y = max(p1_y, p2_y) + (NODE_H / 2) * self.zoom
                    trunk_y = parent_bottom_y + 12 * self.zoom

                    union_key = tuple(sorted((p1.id, p2.id)))
                    if union_key not in joint_trunks_drawn:
                        c.create_line(start_x, start_y, start_x, trunk_y, fill=line_color, width=max(2, int(3 * self.zoom)), tags=line_tags)
                        joint_trunks_drawn.add(union_key)
                    c.create_line(start_x, trunk_y, child_top_x, trunk_y, child_top_x, child_top_y, fill=line_color, width=max(2, int(3 * self.zoom)), tags=line_tags)
                else:
                    parent_bottom_x = ax
                    parent_bottom_y = ay + (NODE_H / 2) * self.zoom
                    bend_y = parent_bottom_y + 12 * self.zoom
                    c.create_line(parent_bottom_x, parent_bottom_y, parent_bottom_x, bend_y, child_top_x, bend_y, child_top_x, child_top_y, fill=line_color, width=max(2, int(3 * self.zoom)), tags=line_tags)

        for p in self.people:
            x, y = self.to_screen(p.x, self.y_of(p.generation))
            w, h = NODE_W * self.zoom, NODE_H * self.zoom

            is_matched = bool(self.search_keyword and (self.search_keyword in p.name.lower() or self.search_keyword in p.note.lower()))

            if is_matched:
                fill = "#1b6ca8" if p.gender == "Nam" else "#c73866"
                outline = "#ff0000"
                width = max(4, int(5 * self.zoom))
                text_color = "#ffffff"
                sub_text_color = "#ffeb3b"
                dash = ()
            else:
                fill = "#d6efff" if p.gender == "Nam" else "#ffe0eb"
                outline = "#2b9a5a" if p.alive else "#000000"
                
                if p.id == self.selected_id and not p.is_fixed:
                    dash = (4, 4)
                else:
                    dash = ()

                width = max(3, int(4 * self.zoom)) if p.id == self.selected_id else max(2, int(2 * self.zoom))
                text_color = "#000000"
                sub_text_color = "#536174"

            self.create_rounded_rectangle(x, y, x + w, y + h, 10 * self.zoom, fill=fill, outline=outline, width=width, dash=dash, tags=("node", p.id))
# Dòng 1: Tên, giới tính, thứ bậc
            if p.generation == 1 or self.is_spouse_only(p.id):
                line1 = f"{p.name}, {p.gender.lower()}"
            else:
                order_label = str(p.birth_order)
                if p.birth_order == 1:
                    order_label = "cả"
                else:
                    parents = self.parents_of(p.id)
                    if parents:
                        sibling_ids = set()
                        for pt in parents:
                            for r in self.relationships:
                                if r.kind == "parent" and r.source == pt.id:
                                    sibling_ids.add(r.target)
                        siblings = [self.get_person(sid) for sid in sibling_ids if self.get_person(sid) and self.get_person(sid).generation == p.generation]
                        if siblings:
                            max_order = max(sib.birth_order for sib in siblings)
                            if p.birth_order == max_order and max_order > 1:
                                order_label = "út"
                line1 = f"{p.name}, {p.gender.lower()}, ({order_label})"

            current_y_offset = 6

            # Cỡ chữ tỷ lệ theo self.zoom (giới hạn nhỏ nhất để không bị mất chữ)
            size_name = max(5, int(9 * self.zoom))
            size_sub = max(4, int(8 * self.zoom))
            size_rel = max(4, int(7 * self.zoom))

            # Vẽ dòng 1 (Tên) với font co giãn theo zoom
            t1 = c.create_text(x + w / 2, y + current_y_offset * self.zoom, text=line1, width=w - 10 * self.zoom, anchor="n", fill=text_color, font=("Segoe UI", size_name, "bold"), tags=("node", p.id))
            
            bbox1 = c.bbox(t1)
            if bbox1:
                current_y_offset += (bbox1[3] - bbox1[1]) / self.zoom + 2
            else:
                current_y_offset += 13

            # Hiển thị năm sinh / năm mất
            if p.born or p.died:
                died_part = f" - {p.died}" if p.died else ""
                life_str = f"({p.born}{died_part})"
                t2 = c.create_text(x + w / 2, y + current_y_offset * self.zoom, text=life_str, width=w - 10 * self.zoom, anchor="n", fill=text_color if not is_matched else "#ffffff", font=("Segoe UI", size_sub), tags=("node", p.id))
                
                bbox2 = c.bbox(t2)
                if bbox2:
                    current_y_offset += (bbox2[3] - bbox2[1]) / self.zoom + 2
                else:
                    current_y_offset += 12

            # Ghi chú
            if p.note.strip():
                t3 = c.create_text(x + w / 2, y + current_y_offset * self.zoom, text=p.note.strip(), width=w - 10 * self.zoom, anchor="n", fill="#b71c1c" if not is_matched else "#fff9c4", font=("Segoe UI", size_sub, "italic"), tags=("node", p.id))
                
                bbox3 = c.bbox(t3)
                if bbox3:
                    current_y_offset += (bbox3[3] - bbox3[1]) / self.zoom + 2
                else:
                    current_y_offset += 12

            # Mối quan hệ xung quanh
            rel_text = self.get_card_relation_text(p)
            if rel_text:
                c.create_text(x + 5 * self.zoom, y + current_y_offset * self.zoom, text=rel_text, width=w - 10 * self.zoom, anchor="nw", justify="left", fill=text_color, font=("Segoe UI", size_rel, "italic"), tags=("node", p.id))
    def get_card_relation_text(self, p: Person) -> str:
        lines = []
        spouses = self.spouses_of(p.id)
        if spouses:
            spouse_str = ", ".join(sp[0].name for sp in spouses)
            if p.gender == "Nam":
                lines.append(f"({p.name} chồng {spouse_str};")
            else:
                lines.append(f"({p.name} vợ {spouse_str};")

        children_rels = [r for r in self.relationships if r.kind == "parent" and r.source == p.id]
        if children_rels:
            child_desc = []
            for cr in children_rels:
                child = self.get_person(cr.target)
                if not child:
                    continue
                other_parents = [parent for parent in self.parents_of(child.id) if parent.id != p.id]
                other_str = f" với {other_parents[0].name}" if other_parents else ""
                child_desc.append(f"{child.name}{other_str}")

            role_title = "bố của" if p.gender == "Nam" else "mẹ của"
            lines.append(f"{role_title} {', '.join(child_desc)})")

        return "\n".join(lines)

    def get_panel_relation_text(self, p: Person) -> str:
        lines = []
        parents = self.parents_of(p.id)
        if parents:
            parent_str = " và ".join(pt.name for pt in parents)
            lines.append(f"• Con của {parent_str};")

        spouses = self.spouses_of(p.id)
        if spouses:
            spouse_str = ", ".join(sp[0].name for sp in spouses)
            role = "chồng" if p.gender == "Nam" else "vợ"
            lines.append(f"• Là {role} của {spouse_str};")

        children_rels = [r for r in self.relationships if r.kind == "parent" and r.source == p.id]
        if children_rels:
            child_desc = []
            for cr in children_rels:
                child = self.get_person(cr.target)
                if not child:
                    continue
                other_parents = [parent for parent in self.parents_of(child.id) if parent.id != p.id]
                other_str = f" với {other_parents[0].name}" if other_parents else ""
                child_desc.append(f"{child.name} (con{other_str})")

            role_title = "bố của" if p.gender == "Nam" else "mẹ của"
            lines.append(f"• Là {role_title} {', '.join(child_desc)}")

        return "\n".join(lines) if lines else "Chưa có liên kết."

    def person_at(self, event, exclude_id=None):
        x, y = self.to_model(event.x, event.y)
        for person in reversed(self.people):
            if person.id == exclude_id:
                continue
            top = self.y_of(person.generation)
            if person.x <= x <= person.x + NODE_W and top <= y <= top + NODE_H:
                return person
        return None

    def on_right_click(self, event):
        tags = self.canvas.gettags("current")
        for t in tags:
            if t.startswith("rel_"):
                self.selected_wire_index = int(t.split("_")[1])
                self.wire_menu.post(event.x_root, event.y_root)
                return

        p = self.person_at(event)
        if p:
            self.selected_id = p.id
            self.show_person(p)
            self.redraw()
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected_wire(self):
        if hasattr(self, "selected_wire_index") and 0 <= self.selected_wire_index < len(self.relationships):
            self.push_undo()
            rel = self.relationships[self.selected_wire_index]
            a = self.get_person(rel.source)
            b = self.get_person(rel.target)
            name_a = a.name if a else "?"
            name_b = b.name if b else "?"
            if messagebox.askyesno("Xác nhận xóa liên kết", f"Xóa mối quan hệ giữa '{name_a}' và '{name_b}'?"):
                self.relationships.pop(self.selected_wire_index)
                self.redraw()

    def unlock_selected_for_drag(self):
        if self.selected_id:
            p = self.get_person(self.selected_id)
            if p:
                self.push_undo()
                p.is_fixed = False
                self.show_person(p)
                self.redraw()

    def get_family_subtree(self, person_id: str) -> set[str]:
        subtree = {person_id}
        for sp, _ in self.spouses_of(person_id):
            subtree.add(sp.id)
        
        queue = [person_id]
        while queue:
            curr = queue.pop(0)
            children = [r.target for r in self.relationships if r.kind == "parent" and r.source == curr]
            for ch_id in children:
                if ch_id not in subtree:
                    subtree.add(ch_id)
                    queue.append(ch_id)
                    for sp, _ in self.spouses_of(ch_id):
                        subtree.add(sp.id)
        return subtree

    def on_press(self, event):
        p = self.person_at(event)
        if p:
            self.selected_id = p.id
            self.show_person(p)

            if not p.is_fixed:
                self.drag_id = p.id
                self.drag_origin = self.to_model(event.x, event.y)
                self.drag_subtree = self.get_family_subtree(p.id)
                self.drag_original_positions = {pid: self.get_person(pid).x for pid in self.drag_subtree if self.get_person(pid)}

            self.redraw()
            return
        self.pan_origin = (event.x, event.y)

    def on_motion(self, event):
        if self.drag_id:
            now = self.to_model(event.x, event.y)
            if self.drag_origin:
                for pid in self.drag_subtree:
                    p = self.get_person(pid)
                    if p and pid in self.drag_original_positions:
                        p.x = max(20, self.drag_original_positions[pid] + (now[0] - self.drag_origin[0]))
                self.redraw()
        elif self.pan_origin:
            self.offset_x += event.x - self.pan_origin[0]
            self.offset_y += event.y - self.pan_origin[1]
            self.pan_origin = (event.x, event.y)
            self.redraw()

    def resolve_insertion(self, dragged_person: Person):
        same_gen = sorted([p for p in self.people if p.generation == dragged_person.generation], key=lambda x: x.x)
        
        for i in range(len(same_gen) - 1):
            left = same_gen[i]
            right = same_gen[i + 1]
            if left.id == dragged_person.id or right.id == dragged_person.id:
                continue
            
            if left.x + NODE_W / 2 < dragged_person.x < right.x + NODE_W / 2:
                right.x = left.x + MIN_X_GAP
                dragged_person.x = left.x + MIN_X_GAP / 2
                
                curr_left = right
                for j in range(i + 2, len(same_gen)):
                    nxt = same_gen[j]
                    if nxt.id == dragged_person.id:
                        continue
                    if nxt.x < curr_left.x + MIN_X_GAP:
                        nxt.x = curr_left.x + MIN_X_GAP
                    curr_left = nxt
                break
        
        for other in same_gen:
            if other.id == dragged_person.id:
                continue
            if abs(other.x - dragged_person.x) < NODE_W:
                if dragged_person.x >= other.x:
                    dragged_person.x = other.x + MIN_X_GAP
                else:
                    dragged_person.x = other.x - MIN_X_GAP

        dragged_person.is_fixed = True

    def on_release(self, event):
        if self.drag_id:
            source = self.get_person(self.drag_id)
            target = self.person_at(event, exclude_id=self.drag_id)
            if source and target and source.id != target.id:
                self.ask_relationship(source, target)
            elif source:
                self.resolve_insertion(source)
                self.show_person(source)
                self.redraw()
        self.drag_id = self.drag_origin = self.pan_origin = None

    def ask_relationship(self, source: Person, target: Person):
        dialog = tk.Toplevel(self)
        dialog.title("Thiết lập mối quan hệ")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text=f"Chọn mối quan hệ giữa '{source.name}' và '{target.name}':", padding=14, font=("Segoe UI", 9, "bold")).pack()

        kind = tk.StringVar(value="Vợ")
        for label in ("Vợ", "Chồng", "Con trai", "Con gái"):
            ttk.Radiobutton(dialog, text=f"'{source.name}' là {label} của '{target.name}'", variable=kind, value=label).pack(anchor="w", padx=20, pady=2)

        def confirm():
            self.push_undo()
            self.set_relationship(source, target, kind.get())
            dialog.destroy()

        buttons = ttk.Frame(dialog, padding=10)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Hủy", command=dialog.destroy).pack(side="right", padx=3)
        ttk.Button(buttons, text="Xác nhận", command=confirm).pack(side="right", padx=3)

    def set_relationship(self, source: Person, target: Person, choice: str):
        self.relationships = [r for r in self.relationships if not ({r.source, r.target} == {source.id, target.id})]

        if choice in ("Vợ", "Chồng"):
            source.generation = target.generation
            if choice == "Vợ":
                source.gender = "Nữ"
                self.relationships.append(Relationship(source=target.id, target=source.id, kind="spouse"))
            else:
                source.gender = "Nam"
                self.relationships.append(Relationship(source=source.id, target=target.id, kind="spouse"))
            source.x = target.x + MIN_X_GAP
        else:
            source.gender = "Nam" if choice == "Con trai" else "Nữ"
            source.generation = min(self.generations, target.generation + 1)
            self.relationships.append(Relationship(source=target.id, target=source.id, kind="parent"))

            spouses = self.spouses_of(target.id)
            if spouses:
                self.relationships.append(Relationship(source=spouses[0][0].id, target=source.id, kind="parent"))

        self.resolve_insertion(source)
        self.show_person(source)
        self.redraw()

    def on_double_click(self, event):
        p = self.person_at(event)
        if p:
            self.selected_id = p.id
            self.push_undo()
            p.is_fixed = False
            self.show_person(p)
            self.redraw()
        else:
            self.apply_form()
        return "break"

    def on_wheel(self, event):
        self.zoom_at(event.x, event.y, 1.12 if event.delta > 0 else 1 / 1.12)

    def zoom_at(self, sx, sy, factor):
        mx, my = self.to_model(sx, sy)
        self.zoom = max(0.35, min(2.3, self.zoom * factor))
        self.offset_x, self.offset_y = sx - mx * self.zoom, sy - my * self.zoom
        self.redraw()

    def fit_view(self):
        self.zoom, self.offset_x, self.offset_y = 0.75, 0, 15
        self.redraw()

    def add_person(self):
        self.push_undo()
        target = self.get_person(self.selected_id) if self.selected_id else (self.people[-1] if self.people else None)
        gen = target.generation if target else 1
        
        if target:
            new_x = target.x + MIN_X_GAP
        else:
            cx, cy = self.to_model(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2)
            new_x = cx

        p = Person(id=str(uuid4()), name="Mới", generation=gen, x=new_x, is_fixed=False, alive=True)
        self.people.append(p)
        self.selected_id = p.id
        self.show_person(p)
        self.redraw()
        self.status.config(text="Đã thêm thành viên mới (mở khóa, kéo thả tự do)")

    def delete_person(self):
        if not self.selected_id:
            return
        p = self.get_person(self.selected_id)
        if not p:
            return
        if messagebox.askyesno("Xác nhận xóa", f"Xóa thành viên '{p.name}'?"):
            self.push_undo()
            self.people = [x for x in self.people if x.id != p.id]
            self.relationships = [r for r in self.relationships if p.id not in (r.source, r.target)]
            self.selected_id = None
            self.clear_form()
            self.redraw()

    def show_person(self, p: Person):
        if p.is_fixed:
            self.info_hint.config(text="🔒 Đã chốt. Double-click để sửa.")
        else:
            self.info_hint.config(text="✏️ Mở khóa (kéo thả/sửa).")

        self.form["name"].set(p.name)
        self.form["note"].set(p.note)
        self.form["born"].set(p.born)
        self.form["died"].set(p.died)
        self.form["alive"].set(p.alive)
        self.form["gender"].set(p.gender)
        self.form["generation"].set(str(p.generation))
        self.form["birth_order"].set(p.birth_order)
        self.bio_text.delete("1.0", "end")
        self.bio_text.insert("1.0", p.bio)
        self.relations_label.config(text=self.get_panel_relation_text(p))

    def apply_form(self):
        p = self.get_person(self.selected_id) if self.selected_id else None
        if not p:
            return messagebox.showinfo("Thông báo", "Hãy chọn một ô thành viên trước.")

        self.push_undo()
        p.name = self.form["name"].get().strip() or "Chưa đặt tên"
        p.note = self.form["note"].get().strip()
        p.born = self.form["born"].get().strip()
        p.died = self.form["died"].get().strip()
        p.alive = self.form["alive"].get()

        if p.died:
            p.alive = False
            self.form["alive"].set(False)

        p.gender = self.form["gender"].get()
        p.bio = self.bio_text.get("1.0", "end-1c").strip()
        p.birth_order = max(1, self.form["birth_order"].get())
        p.generation = int(self.form["generation"].get())

        self.resolve_insertion(p)
        p.is_fixed = True
        self.show_person(p)
        self.redraw()
        self.status.config(text="Đã lưu thông tin thành công!")

    def load_data(self):
        if DATA_FILE.exists():
            try:
                raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                self.generations = raw.get("generations", 8)
                self.people = [Person(**x) for x in raw.get("people", [])]
                self.relationships = [Relationship(**x) for x in raw.get("relationships", [])]
            except Exception:
                pass
        
        if not self.people:
            self.init_giapha_a()
        else:
            self.refresh_generation_choices()
            self.redraw()

    def refresh_generation_choices(self):
        if hasattr(self, "generation_box"):
            self.generation_box["values"] = tuple(str(i) for i in range(1, self.generations + 1))

    def save_data(self):
        data = {
            "generations": self.generations,
            "people": [asdict(p) for p in self.people],
            "relationships": [asdict(r) for r in self.relationships],
        }
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.status.config(text="Đã lưu dữ liệu vào file family_desktop.json thành công! (Ctrl+S)")


if __name__ == "__main__":
    FamilyApp().mainloop()
