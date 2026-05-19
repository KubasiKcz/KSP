#Nemam tucha co se tu děje, toto je celé AI...
import sys
import subprocess
import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any, Dict, List, Optional, Union

# Auto-install dependencies
try:
    from PIL import Image
except ImportError:
    print("Pillow not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class QSONEditor(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("QSON Editor (KSP Magie)")
        self.geometry("1100x750")
        self.current_file: Optional[str] = None
        self.json_data: Optional[Union[Dict[str, Any], List[Any]]] = None
        self.drag_item: Optional[str] = None
        
        self.setup_ui()
        self.apply_dark_theme()

    def apply_dark_theme(self) -> None:
        style = ttk.Style(self)
        style.theme_use('clam')
        
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        select_bg = "#2a82da"
        
        self.configure(bg=bg_color)
        
        style.configure("Treeview", 
                        background=bg_color, 
                        foreground=fg_color, 
                        fieldbackground=bg_color,
                        borderwidth=0,
                        rowheight=28,
                        font=('Segoe UI', 10))
        style.configure("Treeview.Heading", 
                        background="#3c3f41", 
                        foreground=fg_color, 
                        borderwidth=1,
                        relief="flat",
                        font=('Segoe UI', 10, 'bold'))
        style.map("Treeview", background=[("selected", select_bg)])
        style.configure("TFrame", background=bg_color)
        style.configure("TButton", background="#3c3f41", foreground=fg_color, font=('Segoe UI', 10))
        style.configure("TPanedwindow", background="#1e1e1e")
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TEntry", fieldbackground="#3c3f41", foreground=fg_color, insertcolor=fg_color)
        
    def setup_ui(self) -> None:
        # Menu
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open JSON...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Validate Database 🔍", command=self.validate_database)
        file_menu.add_command(label="Compress Assets 🗜️", command=self.compress_assets)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        
        # PanedWindow
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Levá strana
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=1)
        
        help_label = tk.Label(left_frame, text="💡 Right-click tree to add/delete.", 
                               bg="#2b2b2b", fg="#a9b7c6", font=('Segoe UI', 10, 'italic'))
        help_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 5), anchor="w")
        
        # Button panel at the bottom
        btn_panel = ttk.Frame(left_frame)
        btn_panel.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        validate_btn = tk.Button(btn_panel, text="Validate Database 🔍", command=self.validate_database, 
                                 bg="#e2b714", fg="black", font=('Segoe UI', 10, 'bold'), relief="flat", cursor="hand2")
        validate_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        compress_btn = tk.Button(btn_panel, text="Compress Assets 🗜️", command=self.compress_assets,
                                 bg="#66bb6a", fg="white", font=('Segoe UI', 10, 'bold'), relief="flat", cursor="hand2")
        compress_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        save_btn = tk.Button(btn_panel, text="Save JSON 💾", command=self.save_file, 
                             bg="#2a82da", fg="white", font=('Segoe UI', 10, 'bold'), relief="flat", cursor="hand2")
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        columns = ("Hodnota", "Typ", "RealKey")
        self.tree = ttk.Treeview(left_frame, columns=columns, displaycolumns=())
        self.tree.heading("#0", text="JSON Tree", anchor=tk.W)
        self.tree.column("#0", width=350, minwidth=200)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pravá strana
        self.right_frame = tk.Frame(self.paned, bg="#2b2b2b", padx=20, pady=10)
        self.paned.add(self.right_frame, weight=2)
        
        # Události
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_drag_release)
        
        # Kontextové menu
        self.context_menu = tk.Menu(self, tearoff=0)

    def open_file(self) -> None:
        file_name = filedialog.askopenfilename(
            title="Open JSON", 
            filetypes=(("JSON Files", "*.json"), ("All files", "*.*"))
        )
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            self.current_file = file_name
            self.populate_tree()
            self.title(f"QSON Editor - {os.path.basename(file_name)}")
            self.clear_right_panel()

    def populate_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        if isinstance(self.json_data, dict):
            root_node = self.tree.insert("", tk.END, text="📦 root", values=("{...}", "dict", "root"))
            self._fill_tree(self.json_data, root_node)
            self.tree.item(root_node, open=True)
        elif isinstance(self.json_data, list):
            root_node = self.tree.insert("", tk.END, text="📋 root", values=("[...]", "list", "root"))
            for i, val in enumerate(self.json_data):
                self._fill_item(self.get_list_display_name(val, i), val, root_node)
            self.tree.item(root_node, open=True)

    def get_list_display_name(self, val: Any, index: int) -> str:
        if isinstance(val, dict) and len(val) > 0:
            first_val = list(val.values())[0]
            return f"[{index}] {first_val}"
        return f"[{index}]"

    def _fill_tree(self, data_dict: Dict[str, Any], parent_id: str) -> None:
        keys = list(data_dict.keys())
        if 'children' in keys:
            keys.remove('children')
            keys.append('children')
            
        for key in keys:
            self._fill_item(key, data_dict[key], parent_id)

    def _fill_item(self, key: Union[str, int], value: Any, parent_id: str) -> None:
        emoji = "📄 "
        if isinstance(value, dict):
            t = value.get("type", "")
            emoji = "📁 " if t == "folder" else "🗂️ " if t == "group" else "🔗 " if t == "link" else "📦 "
        elif isinstance(value, list):
            emoji = "📋 "

        display_text = f"{emoji}{key}"

        if isinstance(value, dict):
            node = self.tree.insert(parent_id, tk.END, text=display_text, values=("{...}", "dict", str(key)))
            self._fill_tree(value, node)
            if str(key) == "children":
                self.tree.item(node, open=True)
        elif isinstance(value, list):
            node = self.tree.insert(parent_id, tk.END, text=display_text, values=("[...]", "list", str(key)))
            for i, val in enumerate(value):
                display_name = self.get_list_display_name(val, i)
                self._fill_item(display_name, val, node)
            if str(key) == "children":
                self.tree.item(node, open=True)
        else:
            val_str = str(value) if value is not None else "null"
            type_str = type(value).__name__ if value is not None else "null"
            self.tree.insert(parent_id, tk.END, text=display_text, values=(val_str, type_str, str(key)))

    # --- PRAVÁ STRANA ---
    def clear_right_panel(self) -> None:
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def on_tree_select(self, event: Any) -> None:
        selected = self.tree.selection()
        if not selected:
            return
            
        item_id = selected[0]
        self.clear_right_panel()
            
        values = self.tree.item(item_id, "values")
        val_type = values[1] if values else ""
        title_text = self.tree.item(item_id, "text")
        
        title_label = tk.Label(self.right_frame, text=f"Edit: {title_text}", font=('Segoe UI', 16, 'bold'), bg="#2b2b2b", fg="#e2b714")
        title_label.pack(anchor="w", pady=(0, 20))
        
        self.build_magic_buttons(item_id)
        
        form_frame = tk.Frame(self.right_frame, bg="#2b2b2b")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        if val_type == "dict":
            row = 0
            for child_id in self.tree.get_children(item_id):
                child_text = self.tree.item(child_id, "text")
                child_vals = self.tree.item(child_id, "values")
                child_type = child_vals[1]
                child_val = child_vals[0]
                real_key = child_vals[2] if len(child_vals) > 2 else ""
                
                lbl = tk.Label(form_frame, text=child_text, bg="#2b2b2b", fg="white", font=('Segoe UI', 11))
                lbl.grid(row=row, column=0, sticky="w", pady=8, padx=(0, 15))
                
                if child_type not in ["dict", "list"]:
                    var = tk.StringVar(value=child_val)
                    
                    def make_updater(cid: str, ctype: str, rkey: str) -> Any:
                        def updater(*args: Any, **kwargs: Any) -> None:
                            self.tree.item(cid, values=(var.get(), ctype, rkey))
                            self.update_parent_display_name(cid)
                        return updater
                    
                    var.trace_add("write", make_updater(child_id, child_type, real_key))
                    
                    entry = tk.Entry(form_frame, textvariable=var, width=50, bg="#3c3f41", fg="white", font=('Segoe UI', 11), insertbackground="white", relief="flat")
                    entry.grid(row=row, column=1, sticky="we", pady=8, ipady=4)
                else:
                    lbl2 = tk.Label(form_frame, text="< Expand in tree >", bg="#2b2b2b", fg="#a9b7c6", font=('Segoe UI', 10, 'italic'))
                    lbl2.grid(row=row, column=1, sticky="w", pady=8)
                    
                row += 1
            form_frame.columnconfigure(1, weight=1)
        elif val_type == "list":
            tk.Label(form_frame, text="This is an Array/List. Select its items in the tree to edit them.", bg="#2b2b2b", fg="#a9b7c6", font=('Segoe UI', 11)).pack(anchor="w")
        else:
            # Standalone value
            lbl = tk.Label(form_frame, text="Value:", bg="#2b2b2b", fg="white", font=('Segoe UI', 11))
            lbl.pack(anchor="w", pady=(0, 5))
            
            var = tk.StringVar(value=values[0])
            real_key = values[2] if len(values) > 2 else ""
            
            def single_updater(*args: Any) -> None:
                self.tree.item(item_id, values=(var.get(), val_type, real_key))
                self.update_parent_display_name(item_id)
                
            var.trace_add("write", single_updater)
            entry = tk.Entry(form_frame, textvariable=var, width=50, bg="#3c3f41", fg="white", font=('Segoe UI', 11), insertbackground="white", relief="flat")
            entry.pack(fill=tk.X, ipady=4)

    def update_parent_display_name(self, child_id: str) -> None:
        parent_id = self.tree.parent(child_id)
        if not parent_id: return
        list_id = self.tree.parent(parent_id)
        if not list_id: return
        
        list_vals = self.tree.item(list_id, "values")
        if not list_vals or list_vals[1] != "list": return
        
        display_name = ""
        first_val = ""
        for i, sibling_id in enumerate(self.tree.get_children(parent_id)):
            vals = self.tree.item(sibling_id, "values")
            rkey = vals[2] if len(vals) > 2 else ""
            if i == 0: first_val = vals[0]
            if rkey in ["name", "file"] and not display_name:
                display_name = vals[0]
                
        if not display_name: display_name = first_val
        if not display_name: display_name = "Item"
        
        idx = self.tree.index(parent_id)
        old_text = self.tree.item(parent_id, "text")
        emoji = old_text.split(" ")[0] + " " if old_text.startswith(("📁", "🗂️", "🔗", "📦", "📋", "📄")) else "📦 "
        final_text = f"{emoji}[{idx}] {display_name}"
        self.tree.item(parent_id, text=final_text)

    # --- KSP MAGIE ---
    def build_magic_buttons(self, parent_id: str) -> None:
        has_short = False
        has_file = False
        for child_id in self.tree.get_children(parent_id):
            child_vals = self.tree.item(child_id, "values")
            if len(child_vals) > 2:
                rkey = child_vals[2]
                if rkey == "short": has_short = True
                if rkey == "file": has_file = True
                
        if has_short or has_file:
            magic_frame = tk.Frame(self.right_frame, bg="#2b2b2b")
            magic_frame.pack(fill=tk.X, pady=(0, 20))
            
            tk.Label(magic_frame, text="✨ QSON Tools:", bg="#2b2b2b", fg="#42a5f5", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, padx=(0,15))
            
            btn = tk.Button(magic_frame, text="Upload Thumbnail 🖼️", command=lambda: self.magic_upload_thumbnail(parent_id, is_material=has_file), bg="#42a5f5", fg="white", font=('Segoe UI', 10, 'bold'), relief="flat", cursor="hand2")
            btn.pack(side=tk.LEFT, padx=5, ipady=2, ipadx=5)
            
            if has_file:
                btn2 = tk.Button(magic_frame, text="Upload Material 📄", command=lambda: self.magic_upload_material(parent_id), bg="#66bb6a", fg="white", font=('Segoe UI', 10, 'bold'), relief="flat", cursor="hand2")
                btn2.pack(side=tk.LEFT, padx=5, ipady=2, ipadx=5)

    def magic_upload_thumbnail(self, parent_id: str, is_material: bool = False) -> None:
        base_name: Optional[str] = None
        subject_short: Optional[str] = None
        year_short: Optional[str] = None
        
        if is_material:
            file_val = self.get_child_value(parent_id, "file")
            if not file_val:
                messagebox.showerror("Error", "Materiál musí mít nejprve nahraný soubor (nebo vyplněné 'file'), abychom věděli, jak obrázek pojmenovat!")
                return
            base_name = os.path.splitext(file_val)[0]
            subject_node = self.tree.parent(self.tree.parent(parent_id))
            subject_short = self.get_child_value(subject_node, "short")
            year_node = self.tree.parent(self.tree.parent(subject_node))
            year_short = self.get_child_value(year_node, "short")
        else:
            subject_short = self.get_child_value(parent_id, "short")
            base_name = subject_short
            year_node = self.tree.parent(self.tree.parent(parent_id))
            year_short = self.get_child_value(year_node, "short")
        
        if not subject_short or not year_short or not base_name:
            return
            
        file_path = filedialog.askopenfilename(title="Select image (will be resized to 440x440)", filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if not file_path: return
            
        img: Any = Image.open(file_path)
        img = img.resize((440, 440), Image.Resampling.LANCZOS)
        
        if is_material:
            target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "graphics", "subjects", str(year_short), str(subject_short))
        else:
            target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "graphics", "subjects", str(year_short))
            
        os.makedirs(target_dir, exist_ok=True)
        
        target_file = os.path.join(target_dir, f"{base_name}.png")
        img.save(target_file, "PNG")
        
        messagebox.showinfo("Success", f"Image resized and saved to:\n{target_file}")

    def magic_upload_material(self, parent_id: str) -> None:
        subject_node = self.tree.parent(self.tree.parent(parent_id))
        subject_short = self.get_child_value(subject_node, "short")
        year_node = self.tree.parent(self.tree.parent(subject_node))
        year_short = self.get_child_value(year_node, "short")
        
        if not subject_short or not year_short:
            return
            
        file_path = filedialog.askopenfilename(title="Select material file", filetypes=[("All files", "*.*")])
        if not file_path: return
            
        filename = os.path.basename(file_path)
        
        target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "materials", str(year_short), str(subject_short))
        os.makedirs(target_dir, exist_ok=True)
        
        target_file = os.path.join(target_dir, filename)
        shutil.copy2(file_path, target_file)
        
        self.set_child_value(parent_id, "file", filename)
        self.on_tree_select(None)
        
        messagebox.showinfo("Success", f"File saved to:\n{target_file}\nThe 'file' field was auto-filled!")

    def get_child_value(self, parent_id: str, key_name: str) -> Optional[str]:
        for child_id in self.tree.get_children(parent_id):
            vals = self.tree.item(child_id, "values")
            rkey = vals[2] if len(vals) > 2 else ""
            if rkey == key_name:
                return str(vals[0])
        return None

    def set_child_value(self, parent_id: str, key_name: str, new_value: str) -> None:
        for child_id in self.tree.get_children(parent_id):
            vals = self.tree.item(child_id, "values")
            rkey = vals[2] if len(vals) > 2 else ""
            if rkey == key_name:
                self.tree.item(child_id, values=(new_value, vals[1], rkey))
                return

    # --- KONTEXTOVÉ MENU ---
    def show_context_menu(self, event: Any) -> None:
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.context_menu.delete(0, tk.END)
            
            values = self.tree.item(item_id, "values")
            val_type = values[1] if values else ""
            
            if val_type in ["dict", "list"]:
                self.context_menu.add_command(label="📁 Add KSP Folder", command=lambda: self.add_ksp_node(item_id, "folder"))
                self.context_menu.add_command(label="🗂️ Add KSP Group", command=lambda: self.add_ksp_node(item_id, "group"))
                self.context_menu.add_command(label="🔗 Add KSP Material", command=lambda: self.add_ksp_node(item_id, "link"))
                self.context_menu.add_separator()
                
                self.context_menu.add_command(label="📄 Add Value (Text/Number)", command=lambda: self.add_node(item_id, "new_key", "value", "str"))
                self.context_menu.add_command(label="📦 Add Object {...}", command=lambda: self.add_node(item_id, "new_obj", "{...}", "dict"))
                self.context_menu.add_command(label="📋 Add Array [...]", command=lambda: self.add_node(item_id, "new_list", "[...]", "list"))
                self.context_menu.add_separator()
            
            self.context_menu.add_command(label="❌ Delete selected item", command=lambda: self.delete_node(item_id))
            self.context_menu.post(event.x_root, event.y_root)
        else:
            self.context_menu.delete(0, tk.END)
            root_nodes = self.tree.get_children("")
            if root_nodes:
                self.context_menu.add_command(label="➕ Add to root", command=lambda: self.add_node(root_nodes[0], "new_key", "value", "str"))
            self.context_menu.post(event.x_root, event.y_root)

    def add_node(self, parent_id: str, default_key: str, default_val: str, default_type: str) -> None:
        parent_type = ""
        if parent_id:
            parent_values = self.tree.item(parent_id, "values")
            parent_type = parent_values[1] if parent_values else ""
            
        if parent_type == "list":
            children = self.tree.get_children(parent_id)
            default_key = f"[{len(children)}]"
            
        emoji = "📄 "
        if default_type == "dict": emoji = "📦 "
        elif default_type == "list": emoji = "📋 "
            
        self.tree.insert(parent_id, tk.END, text=f"{emoji}{default_key}", values=(default_val, default_type, default_key))
        if parent_id:
            self.tree.item(parent_id, open=True)

    def add_ksp_node(self, parent_id: str, ksp_type: str) -> None:
        if ksp_type == "folder":
            new_obj = {"name": "Nová Složka", "type": "folder", "short": "new_folder", "tags": "", "children": []}
            emoji = "📁 "
        elif ksp_type == "group":
            new_obj = {"name": "Nová Skupina", "type": "group", "short": "new_group", "tags": "", "children": []}
            emoji = "🗂️ "
        elif ksp_type == "link":
            new_obj = {"name": "Nový Materiál", "type": "link", "icon": "file-pdf", "source": "", "ai": "", "tags": "", "file": ""}
            emoji = "🔗 "
            
        parent_type = ""
        if parent_id:
            parent_values = self.tree.item(parent_id, "values")
            parent_type = parent_values[1] if parent_values else ""
            
        if parent_type == "list":
            children = self.tree.get_children(parent_id)
            default_key = f"[{len(children)}]"
        else:
            default_key = f"new_{ksp_type}"
            
        display_text = f"{emoji}{default_key}"
        node = self.tree.insert(parent_id, tk.END, text=display_text, values=("{...}", "dict", default_key))
        self._fill_tree(new_obj, node)
        
        if parent_id:
            self.tree.item(parent_id, open=True)
            
        children = self.tree.get_children(node)
        if children:
            self.update_parent_display_name(children[0])

    def delete_node(self, item_id: str) -> None:
        self.tree.delete(item_id)
        self.clear_right_panel()

    def save_file(self) -> None:
        if not self.current_file:
            return
            
        root_nodes = self.tree.get_children("")
        if not root_nodes:
            return
            
        visual_root = root_nodes[0]
        root_type = self.tree.item(visual_root, "values")[1]
            
        if root_type == "list":
            new_data: Any = []
            for child_id in self.tree.get_children(visual_root):
                new_data.append(self._reconstruct_value(child_id))
        else:
            new_data = self.reconstruct_json(visual_root)
            
        with open(self.current_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Success", "File was successfully saved.")

    def reconstruct_json(self, parent_id: str) -> Dict[str, Any]:
        result = {}
        for child_id in self.tree.get_children(parent_id):
            values = self.tree.item(child_id, "values")
            key = values[2] if len(values) > 2 else self.tree.item(child_id, "text")
            value = self._reconstruct_value(child_id)
            result[key] = value
        return result

    def _reconstruct_value(self, item_id: str) -> Any:
        values = self.tree.item(item_id, "values")
        val_type = values[1]
        val_str = values[0]
        
        if val_type == "dict":
            return self.reconstruct_json(item_id)
        elif val_type == "list":
            result = []
            for child_id in self.tree.get_children(item_id):
                result.append(self._reconstruct_value(child_id))
            return result
        elif val_type == "int":
            try: return int(val_str)
            except ValueError: return val_str
        elif val_type == "float":
            try: return float(val_str)
            except ValueError: return val_str
        elif val_type == "bool":
            return val_str.lower() == "true"
        elif val_type == "null":
            return None
        else:
            return val_str

    # --- DRAG AND DROP ---
    def on_drag_start(self, event: Any) -> None:
        self.drag_item = self.tree.identify_row(event.y)

    def on_drag_motion(self, event: Any) -> None:
        if not hasattr(self, "drag_item") or not self.drag_item:
            return
        target = self.tree.identify_row(event.y)
        if not target or target == self.drag_item:
            return
            
        drag_parent = self.tree.parent(self.drag_item)
        target_parent = self.tree.parent(target)
        
        if drag_parent == target_parent:
            target_idx = self.tree.index(target)
            self.tree.move(self.drag_item, drag_parent, target_idx)

    def on_drag_release(self, event: Any) -> None:
        if hasattr(self, "drag_item") and self.drag_item:
            parent_id = self.tree.parent(self.drag_item)
            if parent_id:
                self.update_list_indices(parent_id)
            self.drag_item = None

    def update_list_indices(self, parent_id: str) -> None:
        parent_vals = self.tree.item(parent_id, "values")
        if not parent_vals or parent_vals[1] != "list":
            return
            
        for idx, child_id in enumerate(self.tree.get_children(parent_id)):
            display_name = ""
            first_val = ""
            for i, prop_id in enumerate(self.tree.get_children(child_id)):
                vals = self.tree.item(prop_id, "values")
                rkey = vals[2] if len(vals) > 2 else ""
                if i == 0: first_val = vals[0]
                if rkey in ["name", "file"] and not display_name:
                    display_name = vals[0]
                    
            if not display_name: display_name = first_val
            if not display_name: display_name = "Item"
            
            old_text = self.tree.item(child_id, "text")
            emoji = old_text.split(" ")[0] + " " if old_text.startswith(("📁", "🗂️", "🔗", "📦", "📋", "📄")) else "📦 "
            self.tree.item(child_id, text=f"{emoji}[{idx}] {display_name}")

    def get_current_data(self) -> Optional[Any]:
        root_nodes = self.tree.get_children("")
        if not root_nodes:
            return None
            
        visual_root = root_nodes[0]
        root_type = self.tree.item(visual_root, "values")[1]
            
        if root_type == "list":
            new_data = []
            for child_id in self.tree.get_children(visual_root):
                new_data.append(self._reconstruct_value(child_id))
            return new_data
        else:
            return self.reconstruct_json(visual_root)

    def validate_database(self) -> None:
        data = self.get_current_data()
        if data is None:
            messagebox.showinfo("Validátor", "Žádná data k validaci. Otevřete nejprve JSON soubor.")
            return

        errors = []
        
        def check_file(rel_path: str, context: str) -> None:
            clean_path = rel_path.replace('./', '').replace('/', os.sep)
            abs_path = os.path.join(BASE_DIR, clean_path)
            if not os.path.exists(abs_path):
                errors.append(f"❌ Chybí soubor: '{rel_path}'\n   Kontext: {context}")

        def walk(nodes: Any, year_short: Optional[str] = None, subject_short: Optional[str] = None, path_prefix: str = "") -> None:
            if not isinstance(nodes, list):
                return
            for idx, node in enumerate(nodes):
                if not isinstance(node, dict):
                    continue
                name = node.get("name", f"Uzel [{idx}]")
                node_type = node.get("type", "unknown")
                current_path_str = f"{path_prefix} ➔ {name}" if path_prefix else name
                
                curr_year = year_short
                curr_subject = subject_short
                
                if node_type == "folder" and not year_short:
                    curr_year = node.get("short")
                elif node_type in ["folder", "group"] and year_short and not curr_subject and node.get("short"):
                    curr_subject = node.get("short")
                    
                # 1. Zkontroluj explicitly definovaný obrázek
                if "image" in node and node["image"]:
                    if str(node["image"]).startswith("./"):
                        check_file(node["image"], f"Obrázek složky/skupiny '{current_path_str}'")
                elif node_type in ["folder", "group"] and curr_year and curr_subject:
                    # Výchozí obrázek pro předmět
                    img_path = f"./graphics/subjects/{curr_year}/{curr_subject}.png"
                    check_file(img_path, f"Výchozí obrázek předmětu '{current_path_str}'")
                    
                # 2. Zkontroluj materiály (type == link)
                if node_type == "link":
                    file_name = node.get("file")
                    if file_name:
                        # Ověření souboru materiálu
                        if node.get("url"):
                            if str(node["url"]).startswith("./"):
                                check_file(node["url"], f"Odkaz na materiál '{current_path_str}'")
                        elif curr_year and curr_subject:
                            file_path = f"./materials/{curr_year}/{curr_subject}/{file_name}"
                            check_file(file_path, f"Materiál '{current_path_str}'")
                            
                        # Ověření náhledu materiálu
                        if not node.get("image") and curr_year and curr_subject:
                            parts = file_name.split('.')
                            file_name_without_ext = '.'.join(parts[:-1]) if len(parts) > 1 else file_name
                            thumb_path = f"./graphics/subjects/{curr_year}/{curr_subject}/{file_name_without_ext}.png"
                            check_file(thumb_path, f"Náhled materiálu '{current_path_str}'")
                    else:
                        errors.append(f"⚠️ Chybí pole 'file' u materiálu: '{current_path_str}'")
                        
                # 3. Zpracování dětí
                if "children" in node:
                    walk(node["children"], curr_year, curr_subject, current_path_str)

        if isinstance(data, list):
            walk(data)
        elif isinstance(data, dict):
            if "children" in data:
                walk(data["children"])
            else:
                walk([data])
                
        self.show_validation_results(errors)

    def show_validation_results(self, errors: List[str]) -> None:
        win = tk.Toplevel(self)
        win.title("Validátor Databáze")
        win.geometry("700x500")
        win.configure(bg="#2b2b2b")
        win.transient(self)
        win.grab_set()
        
        # Center window
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f'+{x}+{y}')
        
        title_label = tk.Label(win, text="🔍 Výsledky validace databáze", font=('Segoe UI', 14, 'bold'), bg="#2b2b2b", fg="#e2b714")
        title_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        frame = ttk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        txt = tk.Text(frame, wrap=tk.WORD, bg="#1e1e1e", fg="#ffffff", insertbackground="white", font=('Consolas', 10), bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=scrollbar.set)
        
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if not errors:
            txt.insert(tk.END, "🎉 Vše je v naprostém pořádku!\n\nVšechny cesty k souborům v data.json jsou platné a odpovídající soubory fyzicky existují na disku.")
            txt.configure(state=tk.DISABLED)
        else:
            txt.insert(tk.END, f"Nalezeno chyb: {len(errors)}\n\n")
            for err in errors:
                txt.insert(tk.END, err + "\n\n")
            txt.configure(state=tk.DISABLED)
            
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def copy_errors() -> None:
            self.clipboard_clear()
            self.clipboard_append("\n".join(errors))
            messagebox.showinfo("Kopírovat", "Chyby byly zkopírovány do schránky.", parent=win)
            
        if errors:
            copy_btn = tk.Button(btn_frame, text="Kopírovat chyby 📋", command=copy_errors, bg="#2a82da", fg="white", font=('Segoe UI', 10, 'bold'), relief="flat", cursor="hand2")
            copy_btn.pack(side=tk.LEFT, padx=(0, 10))
            
        close_btn = tk.Button(btn_frame, text="Zavřít", command=win.destroy, bg="#3c3f41", fg="white", font=('Segoe UI', 10), relief="flat", cursor="hand2")
        close_btn.pack(side=tk.RIGHT)

    def compress_assets(self) -> None:
        try:
            import pypdf  # type: ignore
        except ImportError:
            self.config(cursor="watch")
            self.update()
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
                import pypdf  # type: ignore
            except Exception as e:
                messagebox.showerror("Chyba", f"Nepodařilo se nainstalovat knihovnu 'pypdf' pro kompresi PDF:\n{e}")
                self.config(cursor="")
                return
            finally:
                self.config(cursor="")

        if not messagebox.askyesno("Komprese", "Chcete spustit kompresi všech souborů v adresářích 'materials/' a 'graphics/'?\nTato operace může trvat několik desítek sekund a upraví soubory přímo na disku."):
            return

        self.config(cursor="watch")
        self.update()

        total_saved_bytes = 0
        processed_count = 0
        log_lines = []

        materials_dir = os.path.join(BASE_DIR, "materials")
        graphics_dir = os.path.join(BASE_DIR, "graphics")

        files_to_process = []
        for root, dirs, files in os.walk(materials_dir):
            for file in files:
                files_to_process.append(os.path.join(root, file))
        for root, dirs, files in os.walk(graphics_dir):
            for file in files:
                files_to_process.append(os.path.join(root, file))

        for file_path in files_to_process:
            ext = os.path.splitext(file_path)[1].lower()
            orig_size = os.path.getsize(file_path)
            
            if ext == ".pdf":
                try:
                    reader = pypdf.PdfReader(file_path)
                    writer = pypdf.PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    for page in writer.pages:
                        page.compress_content_streams(level=9)
                    
                    temp_path = file_path + ".tmp"
                    with open(temp_path, "wb") as f:
                        writer.write(f)
                    
                    new_size = os.path.getsize(temp_path)
                    if new_size < orig_size:
                        os.replace(temp_path, file_path)
                        saved = orig_size - new_size
                        total_saved_bytes += saved
                        processed_count += 1
                        log_lines.append(f"📄 PDF: {os.path.relpath(file_path, BASE_DIR)}\n   Ušetřeno: {saved / 1024:.1f} KB ({orig_size / 1024:.1f} KB -> {new_size / 1024:.1f} KB)")
                    else:
                        os.remove(temp_path)
                except Exception as e:
                    pass
                    
            elif ext in [".png", ".jpg", ".jpeg"]:
                try:
                    img: Any = Image.open(file_path)
                    resized = False
                    
                    if "graphics" in file_path and ("subjects" in file_path or "folder" in file_path):
                        if img.width > 440 or img.height > 440:
                            img = img.resize((440, 440), Image.Resampling.LANCZOS)
                            resized = True
                    
                    temp_path = file_path + ".tmp"
                    if ext == ".png":
                        img.save(temp_path, "PNG", optimize=True)
                    else:
                        img.save(temp_path, "JPEG", optimize=True, quality=85)
                        
                    new_size = os.path.getsize(temp_path)
                    if new_size < orig_size or resized:
                        os.replace(temp_path, file_path)
                        saved = orig_size - new_size
                        if saved > 0:
                            total_saved_bytes += saved
                        processed_count += 1
                        action_str = "Zmenšeno a kompresováno" if resized else "Kompresováno"
                        log_lines.append(f"🖼️ Obrázek: {os.path.relpath(file_path, BASE_DIR)}\n   {action_str}: ušetřeno {max(0, saved) / 1024:.1f} KB ({orig_size / 1024:.1f} KB -> {new_size / 1024:.1f} KB)")
                    else:
                        os.remove(temp_path)
                except Exception as e:
                    pass

        self.config(cursor="")
        self.show_compression_results(processed_count, total_saved_bytes, log_lines)

    def show_compression_results(self, count: int, saved_bytes: int, log_lines: List[str]) -> None:
        win = tk.Toplevel(self)
        win.title("Výsledky komprese")
        win.geometry("700x500")
        win.configure(bg="#2b2b2b")
        win.transient(self)
        win.grab_set()
        
        # Center window
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f'+{x}+{y}')
        
        title_label = tk.Label(win, text="🗜️ Výsledky komprese souborů", font=('Segoe UI', 14, 'bold'), bg="#2b2b2b", fg="#66bb6a")
        title_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        frame = ttk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        txt = tk.Text(frame, wrap=tk.WORD, bg="#1e1e1e", fg="#ffffff", insertbackground="white", font=('Consolas', 10), bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=scrollbar.set)
        
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if count == 0:
            txt.insert(tk.END, "Všechny soubory jsou již maximálně kompresované. Žádné úspory místa nebyly nalezeny.")
        else:
            txt.insert(tk.END, f"Úspěšně kompresováno souborů: {count}\nCelková úspora: {saved_bytes / (1024*1024):.2f} MB ({saved_bytes / 1024:.1f} KB)\n\nDetailní výpis:\n\n")
            txt.insert(tk.END, "\n\n".join(log_lines))
            
        txt.configure(state=tk.DISABLED)
        
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        close_btn = tk.Button(btn_frame, text="Zavřít", command=win.destroy, bg="#3c3f41", fg="white", font=('Segoe UI', 10), relief="flat", cursor="hand2")
        close_btn.pack(side=tk.RIGHT)

if __name__ == "__main__":
    app = QSONEditor()
    app.mainloop()
