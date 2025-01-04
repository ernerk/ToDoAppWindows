import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime, timedelta
from win10toast import ToastNotifier
import threading
import time
import re

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yapılacaklar")
        self.root.geometry("900x650")
        
        # Tema seçenekleri
        self.themes = {
            "light": {
                "bg": "#FFFFFF",  # Ana arka plan beyaz
                "panel_bg": "#FFFFFF",  # Panel arka planı
                "sidebar_bg": "#F5F6F7",  # Sol panel arka planı
                "text": "#202020",  # Ana yazı rengi
                "text_secondary": "#666666",  # İkincil yazı rengi
                "accent": "#2564CF",  # Windows mavi
                "accent_hover": "#1B4B9E",  # Koyu mavi (hover için)
                "success": "#3BB143",  # Yeşil
                "warning": "#FDB515",  # Sarı
                "danger": "#E81123",  # Windows kırmızı
                "border": "#E5E5E5",  # Çerçeve rengi
                "hover": "#EDF2F7",  # Hover efekti için renk
                "selected": "#E1EFFF"  # Seçili buton için renk
            },
            "dark": {
                "bg": "#1F1F1F",  # Koyu arka plan
                "panel_bg": "#2D2D2D",  # Panel arka planı
                "sidebar_bg": "#252526",  # Sol panel arka planı
                "text": "#FFFFFF",  # Beyaz yazı
                "text_secondary": "#CCCCCC",  # Gri yazı
                "accent": "#0078D4",  # Windows mavi
                "accent_hover": "#106EBE",  # Koyu mavi
                "success": "#13A10E",  # Yeşil
                "warning": "#FDB515",  # Sarı
                "danger": "#E81123",  # Kırmızı
                "border": "#404040",  # Çerçeve rengi
                "hover": "#3E3E40",  # Hover efekti için renk
                "selected": "#094771"  # Seçili buton için renk
            }
        }
        
        # Aktif tema
        self.current_theme = "light"
        self.colors = self.themes[self.current_theme]
        
        # Tema değiştirme butonu
        self.theme_button = ttk.Button(self.root, 
                                     text="🌙" if self.current_theme == "light" else "☀️",
                                     command=self.toggle_theme,
                                     style="Theme.TButton")
        self.theme_button.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")
        
        self.root.configure(bg=self.colors["bg"])
        
        # Ana frame
        self.main_frame = ttk.Frame(self.root, padding="0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel
        self.left_panel = ttk.Frame(self.main_frame, style="LeftPanel.TFrame", padding=0)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        # Sol panel başlık
        ttk.Label(self.left_panel, 
                 text="📝 Yapılacaklar",
                 style="Title.TLabel",
                 font=('Segoe UI', 16, 'bold'),
                 background=self.colors["sidebar_bg"]).pack(anchor=tk.W, pady=(10, 20), padx=10)
        
        # Kategori butonları için frame
        self.categories_frame = ttk.Frame(self.left_panel, style="LeftPanel.TFrame")
        self.categories_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Kategori butonları
        self.current_category = "my_day"  # Aktif kategori
        self.category_buttons = {}  # Butonları saklamak için
        
        categories = [
            ("☀️ Günüm", "my_day"),
            ("⭐ Önemli", "important"),
            ("📅 Planlanan", "planned"),
            ("📋 Görevler", "tasks"),
            ("🏠 Ev", "home"),
            ("💼 İş", "work"),
            ("🛒 Alışveriş", "shopping")
        ]
        
        # Her kategori için buton oluştur
        for text, command in categories:
            btn = ttk.Button(self.left_panel, 
                           text=text, 
                           style="SidebarButton.TButton",
                           command=lambda c=command, t=text: self.change_category(c, t))
            btn.pack(fill=tk.X, padx=0, pady=0)
            self.category_buttons[command] = btn
        
        # Sağ panel
        self.right_panel = ttk.Frame(self.main_frame, style="RightPanel.TFrame", padding="20")
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Sağ panel içeriği - Başlık ve Arama
        self.header_frame = ttk.Frame(self.right_panel, style="RightPanel.TFrame")
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Başlık
        self.title_label = ttk.Label(self.header_frame,
                                   text="☀️Günüm",
                                   style="Title.TLabel",
                                   font=('Segoe UI', 24, 'bold'),
                                   background=self.colors["bg"])
        self.title_label.pack(side=tk.LEFT, padx=0)
        
        # Arama alanı
        self.search_frame = ttk.Frame(self.header_frame, style="Search.TFrame")
        self.search_frame.pack(side=tk.RIGHT)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame,
                                    textvariable=self.search_var,
                                    style="Custom.TEntry",
                                    width=30)
        self.search_entry.insert(0, "🔍 Ara")
        self.search_entry.pack(side=tk.RIGHT, padx=5)
        
        # Görev ekleme alanı
        self.add_task_frame = ttk.Frame(self.right_panel, style="AddTask.TFrame", padding=10)
        self.add_task_frame.pack(fill=tk.X, pady=10)
        
        self.task_var = tk.StringVar()
        self.task_entry = ttk.Entry(self.add_task_frame,
                                  textvariable=self.task_var,
                                  style="Custom.TEntry",
                                  width=50)
        self.task_entry.insert(0, "➕ Görev ekle")
        self.task_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Ekle butonu
        self.add_button = ttk.Button(self.add_task_frame,
                                   text="➕",
                                   command=self.add_task,
                                   style="Add.TButton",
                                   width=3)
        self.add_button.pack(side=tk.RIGHT, padx=5)
        
        # Ekle butonu stili
        style = ttk.Style()
        style.configure("Add.TButton",
                       padding=(5, 5),
                       font=('Segoe UI', 12),
                       background=self.colors["bg"],
                       foreground=self.colors["text"])
        
        # Buton stili
        style.configure("Custom.TButton",
                       padding=(10, 5),
                       font=('Segoe UI', 10),
                       background=self.colors["accent"],
                       foreground=self.colors["text"])
        
        style.map("Custom.TButton",
                 background=[("active", self.colors["accent_hover"])],
                 foreground=[("active", self.colors["text"])])
        
        # Placeholder text işlevselliği
        self.task_entry.bind('<FocusIn>', self.on_entry_click)
        self.task_entry.bind('<FocusOut>', self.on_focus_out)
        self.task_entry.bind('<Return>', lambda e: self.add_task())  # Enter tuşu ile görev ekleme
        
        # Görev listesi ve detay paneli için frame
        self.content_frame = ttk.Frame(self.right_panel, style="RightPanel.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Görev listesi frame
        self.tasks_frame = ttk.Frame(self.content_frame, style="Tasks.TFrame")
        self.tasks_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Görev listesi
        self.tree = ttk.Treeview(self.tasks_frame,
                                columns=("Görev", "Kategori", "Öncelik", "Tarih"),
                                show="headings",
                                style="Custom.Treeview")
        
        # Sütun başlıkları ve genişlikleri
        columns = {
            "Görev": 300,      # Görev sütunu daha geniş
            "Kategori": 150,   # Kategori için yeterli genişlik
            "Öncelik": 100,    # Öncelik için yeterli genişlik
            "Tarih": 100       # Tarih için sabit genişlik
        }
        
        for col, width in columns.items():
            self.tree.heading(col, text=col, anchor="w")  # Başlıkları sola hizala (west)
            self.tree.column(col, width=width, anchor="w")  # İçeriği sola hizala
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tasks_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Butonlar için frame
        self.buttons_frame = ttk.Frame(self.tasks_frame, style="Tasks.TFrame", padding=10)
        self.buttons_frame.pack(fill=tk.X, pady=10)
        
        # Tamamla butonu
        self.complete_btn = ttk.Button(self.buttons_frame,
                                     text="✓ Tamamlandı",
                                     command=self.complete_selected_task,
                                     style="Action.TButton",
                                     width=15)
        self.complete_btn.pack(side=tk.LEFT, padx=5)
        
        # Düzenle butonu
        self.edit_btn = ttk.Button(self.buttons_frame,
                                 text="✏️ Düzenle",
                                 command=self.edit_selected_task,
                                 style="Action.TButton",
                                 width=15)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Sil butonu
        self.delete_btn = ttk.Button(self.buttons_frame,
                                   text="🗑️ Sil",
                                   command=self.delete_selected_task,
                                   style="Action.TButton",
                                   width=15)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Başlangıçta butonları devre dışı bırak
        self.complete_btn.state(['disabled'])
        self.edit_btn.state(['disabled'])
        self.delete_btn.state(['disabled'])
        
        # Buton stili
        style = ttk.Style()
        style.configure("Action.TButton",
                       padding=5,
                       font=('Segoe UI', 10))
        
        # Detay paneli
        self.detail_frame = ttk.Frame(self.content_frame, style="Detail.TFrame", padding=10)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Detay paneli başlık
        self.detail_title = ttk.Label(self.detail_frame, 
                                    text="Görev Detayları",
                                    font=('Segoe UI', 12, 'bold'),
                                    style="Detail.TLabel")
        self.detail_title.pack(anchor=tk.W, pady=(0, 10))
        
        # Detay paneli içerik
        self.detail_text = ttk.Label(self.detail_frame,
                                   text="Bir görev seçin",
                                   wraplength=200,
                                   style="Detail.TLabel")
        self.detail_text.pack(anchor=tk.W)
        
        # Detay paneli stili
        style.configure("Detail.TFrame",
                       background=self.colors["panel_bg"])
        style.configure("Detail.TLabel",
                       background=self.colors["panel_bg"],
                       foreground=self.colors["text"])
        
        # Görev seçildiğinde detayları göster
        self.tree.bind('<<TreeviewSelect>>', self.on_task_select)
        
        # Veri dosyası
        self.data_file = "todos.json"
        self.todos = self.load_todos()
        
        # Görevleri yükle
        self.update_task_list()
        
        self.editing_index = None  # Düzenleme modu için index
        
        # Bildirim nesnesi
        self.toaster = ToastNotifier()
        
        # Hatırlatıcı thread'i başlat
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()
        
        # Sürükle-bırak için değişkenler
        self.drag_source = None
        self.drag_data = None
        
        # Sürükle-bırak bağlantıları
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_drag_release)
        
        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        
        # Panel stilleri
        style.configure("LeftPanel.TFrame",
                       background=self.colors["sidebar_bg"],
                       relief="flat")
        
        style.configure("RightPanel.TFrame",
                       background=self.colors["bg"],
                       relief="flat")
        
        # Buton stilleri
        style.configure("SidebarButton.TButton",
                       padding=(10, 8, 10, 8),
                       font=('Segoe UI', 10),
                       background=self.colors["sidebar_bg"],
                       foreground=self.colors["text"],
                       borderwidth=0,
                       relief="flat",
                       anchor="w",  # Sola hizalama
                       width=25)
        
        style.map("SidebarButton.TButton",
                 background=[("active", self.colors["hover"]),
                           ("selected", self.colors["selected"])],
                 foreground=[("active", self.colors["accent"]),
                           ("selected", self.colors["accent"])])
        
        # Entry stilleri
        style.configure("Custom.TEntry",
                       fieldbackground=self.colors["panel_bg"],
                       foreground=self.colors["text"],
                       insertcolor=self.colors["text"],
                       borderwidth=0,
                       relief="flat")
        
        # Treeview stilleri
        style.configure("Custom.Treeview",
                       background=self.colors["panel_bg"],
                       foreground=self.colors["text"],
                       fieldbackground=self.colors["panel_bg"],
                       font=('Segoe UI', 10),
                       rowheight=30,
                       borderwidth=0,
                       relief="flat")
        
        style.configure("Custom.Treeview.Heading",
                       background=self.colors["panel_bg"],
                       foreground=self.colors["text"],
                       font=('Segoe UI', 10, 'bold'),
                       relief="flat")
        
        # Buton stilleri
        style.configure("Success.TButton",
                       padding=(10, 5),
                       font=('Segoe UI', 10),
                       background=self.colors["success"],
                       foreground="white")
        
        style.configure("Danger.TButton",
                       padding=(10, 5),
                       font=('Segoe UI', 10),
                       background=self.colors["danger"],
                       foreground="white")
        
        style.map("Success.TButton",
                 background=[("active", self.colors["success"])])
        
        style.map("Danger.TButton",
                 background=[("active", self.colors["danger"])])
    
    def load_todos(self):
        """Görevleri yükle"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            messagebox.showerror("Hata", f"Görevler yüklenirken bir hata oluştu: {str(e)}")
        return []
    
    def save_todos(self):
        """Görevleri kaydet"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Hata", f"Görevler kaydedilirken bir hata oluştu: {str(e)}")
    
    def add_task(self):
        """Yeni görev ekle"""
        task_text = self.task_var.get().strip()
        if task_text and task_text != "➕ Görev ekle":
            # Görev detayları penceresini aç
            self.show_task_details_window()
            # Giriş alanını temizle
            self.task_var.set("")
            self.task_entry.insert(0, "➕ Görev ekle")
            self.task_entry.configure(foreground=self.colors["text_secondary"])
    
    def show_task_details_window(self, edit_mode=False, task_index=None):
        """Görev detayları penceresini göster"""
        details_window = tk.Toplevel(self.root)
        details_window.title("Görev Detayları")
        details_window.geometry("400x500")
        details_window.configure(bg=self.colors["bg"])
        details_window.resizable(False, False)
        
        # Frame
        frame = ttk.Frame(details_window, style="Custom.TFrame", padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Görev adı
        ttk.Label(frame, text="Görev Adı:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0,5))
        task_entry = ttk.Entry(frame, width=40, style="Custom.TEntry")
        task_entry.insert(0, self.task_var.get() if not edit_mode else self.todos[task_index]["task"])
        task_entry.pack(fill=tk.X, pady=(0,15))
        
        # Açıklama
        ttk.Label(frame, text="Açıklama:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0,5))
        description_text = tk.Text(frame, height=4, width=40, bg=self.colors["panel_bg"], 
                                 fg=self.colors["text"], relief="flat")
        if edit_mode and "description" in self.todos[task_index]:
            description_text.insert("1.0", self.todos[task_index]["description"])
        description_text.pack(fill=tk.X, pady=(0,15))
        
        # Kategori seçimi
        ttk.Label(frame, text="Kategori:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0,5))
        categories = ["📋 Görevler", "☀️ Günüm", "⭐ Önemli", "📅 Planlanan", "🏠 Ev", "💼 İş", "🛒 Alışveriş"]
        category_var = tk.StringVar(value=categories[0] if not edit_mode else self.todos[task_index]["category"])
        category_combo = ttk.Combobox(frame, textvariable=category_var, values=categories, state="readonly")
        category_combo.pack(fill=tk.X, pady=(0,15))
        
        # Öncelik seçimi
        ttk.Label(frame, text="Öncelik:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0,5))
        priority_var = tk.StringVar(value="Orta" if not edit_mode else self.todos[task_index]["priority"])
        
        for text, value in [("🔴 Yüksek", "Yüksek"), ("🟡 Orta", "Orta"), ("🟢 Düşük", "Düşük")]:
            ttk.Radiobutton(frame, text=text, value=value, variable=priority_var).pack(anchor=tk.W)
        
        # Tarih seçimi
        ttk.Label(frame, text="Tarih:", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(15,5))
        due_date = DateEntry(frame, width=20, background=self.colors["accent"],
                           foreground=self.colors["text"], date_pattern='dd/mm/yyyy')
        if edit_mode:
            due_date.set_date(datetime.strptime(self.todos[task_index]["due_date"], "%d/%m/%Y").date())
        due_date.pack(fill=tk.X, pady=(0,15))
        
        # Butonlar için frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(20,0))
        
        def save_task():
            task_dict = {
                "task": task_entry.get().strip(),
                "description": description_text.get("1.0", tk.END).strip(),
                "category": category_var.get(),
                "priority": priority_var.get(),
                "due_date": due_date.get(),
                "completed": False if not edit_mode else self.todos[task_index]["completed"]
            }
            
            if edit_mode:
                self.todos[task_index] = task_dict
            else:
                self.todos.append(task_dict)
            
            self.save_todos()
            self.update_task_list()
            details_window.destroy()
        
        # İptal butonu
        ttk.Button(button_frame, 
                  text="❌ İptal", 
                  command=details_window.destroy,
                  style="Danger.TButton",
                  width=15).pack(side=tk.LEFT, padx=5)
        
        # Kaydet butonu
        ttk.Button(button_frame, 
                  text="💾 Kaydet",
                  command=save_task,
                  style="Success.TButton",
                  width=15).pack(side=tk.RIGHT, padx=5)
        
        # Pencereyi ortala
        details_window.transient(self.root)
        details_window.grab_set()
        self.root.wait_window(details_window)
    
    def edit_task(self, item):
        """Görevi düzenle"""
        try:
            index = list(self.tree.get_children()).index(item)
            self.task_var.set(self.todos[index]["task"])
            self.show_task_details_window(edit_mode=True, task_index=index)
        except Exception as e:
            messagebox.showerror("Hata", f"Görev düzenlenirken bir hata oluştu: {str(e)}")
    
    def delete_task(self, item):
        """Görevi sil"""
        try:
            if messagebox.askyesno("Onay", "Bu görevi silmek istediğinizden emin misiniz?"):
                # Seçili görevin indeksini bul
                selected_task = self.tree.item(item)["values"][0]  # Görev adını al
                
                # Görev listesinde bu görevi bul ve sil
                for i, task in enumerate(self.todos):
                    if task["task"] == selected_task:
                        del self.todos[i]
                        # Değişiklikleri kaydet
                        self.save_todos()
                        # Listeyi güncelle
                        self.update_task_list()
                        break
        except Exception as e:
            messagebox.showerror("Hata", f"Görev silinirken bir hata oluştu: {str(e)}")
    
    def toggle_complete(self, item):
        """Görevi tamamlandı/tamamlanmadı olarak işaretle"""
        try:
            # Seçili görevin değerlerini al
            task_values = self.tree.item(item)["values"]
            task_name = task_values[0]  # Görev adı
            task_category = task_values[1]  # Kategori
            task_priority = task_values[2].split(" ")[1]  # Öncelik (emoji'yi kaldır)
            task_due_date = task_values[3]  # Tarih
            
            # Görev listesinde bu görevi bul
            for task in self.todos:
                if (task["task"] == task_name and 
                    task["category"] == task_category and 
                    task["priority"] == task_priority and 
                    task["due_date"] == task_due_date):
                    # Görevin durumunu değiştir
                    task["completed"] = not task["completed"]
                    # Değişiklikleri kaydet
                    self.save_todos()
                    # Listeyi güncelle
                    self.update_task_list()
                    break
        except Exception as e:
            messagebox.showerror("Hata", f"Görev tamamlanırken bir hata oluştu: {str(e)}")
    
    def search_tasks(self, *args):
        self.update_task_list()
    
    def update_task_list(self):
        """Görev listesini güncelle"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_var.get().lower()
        if search_term == "🔍 ara":
            search_term = ""
        
        # Tamamlanmamış ve tamamlanmış görevleri ayır
        active_tasks = []
        completed_tasks = []
        
        for task in self.todos:
            # Kategori filtreleme
            if self.current_category == "my_day" and task["category"] != "☀️ Günüm":
                continue
            elif self.current_category == "important" and task["category"] != "⭐ Önemli":
                continue
            elif self.current_category == "planned" and task["category"] != "📅 Planlanan":
                continue
            elif self.current_category == "tasks" and task["category"] != "📋 Görevler":
                continue
            elif self.current_category == "home" and task["category"] != "🏠 Ev":
                continue
            elif self.current_category == "work" and task["category"] != "💼 İş":
                continue
            elif self.current_category == "shopping" and task["category"] != "🛒 Alışveriş":
                continue
            
            # Arama filtreleme
            if search_term and search_term not in task["task"].lower():
                continue
            
            if task["completed"]:
                completed_tasks.append(task)
            else:
                active_tasks.append(task)
        
        # Önce aktif görevleri göster
        self._insert_tasks(active_tasks)
        
        # Tamamlanan görevler başlığı
        if completed_tasks:
            separator = self.tree.insert("", tk.END, values=("✓ Tamamlanan Görevler", "", "", "", ""))
            self.tree.tag_configure("separator", font=('Segoe UI', 10, 'bold'))
            self.tree.item(separator, tags=("separator",))
            
            # Tamamlanan görevleri göster
            self._insert_tasks(completed_tasks)
    
    def _insert_tasks(self, tasks):
        """Görevleri listeye ekle"""
        priority_icons = {
            "Yüksek": "🔴",
            "Orta": "🟡",
            "Düşük": "🟢"
        }
        
        for task in tasks:
            priority_text = f"{priority_icons[task['priority']]} {task['priority']}"
            
            values = (
                task["task"],
                task["category"],
                priority_text,
                task["due_date"]
            )
            
            item = self.tree.insert("", tk.END, values=values)
            
            # Tamamlanan görevlerin stilini ayarla
            if task["completed"]:
                self.tree.tag_configure("completed", 
                                      foreground="#A0A0A0",  # Gri yazı rengi
                                      font=('Segoe UI', 10, 'overstrike'))  # Üstü çizili
                self.tree.item(item, tags=("completed",))
            else:
                # Önceliğe göre renklendirme
                priority_colors = {
                    "Yüksek": "#FF4757",
                    "Orta": "#6C5CE7",
                    "Düşük": "#00B894"
                }
                self.tree.tag_configure(f"priority_{task['priority'].lower()}", 
                                      foreground=priority_colors[task['priority']])
                self.tree.item(item, tags=(f"priority_{task['priority'].lower()}",))
        
        # Seçili öğe varsa butonları aktif et
        selection = self.tree.selection()
        if selection:
            self.complete_btn.state(['!disabled'])
            self.edit_btn.state(['!disabled'])
            self.delete_btn.state(['!disabled'])
        else:
            self.complete_btn.state(['disabled'])
            self.edit_btn.state(['disabled'])
            self.delete_btn.state(['disabled'])
    
    def on_hover(self, event):
        """Butonların üzerine gelindiğinde simgeleri değiştir"""
        pass
    
    def handle_button_click(self, event):
        """Butonlara tıklandığında işlem yap"""
        pass
    
    def on_entry_click(self, event):
        """Entry'ye tıklandığında placeholder'ı temizle"""
        if self.task_entry.get() == "➕ Görev ekle":
            self.task_entry.delete(0, tk.END)
            self.task_entry.configure(foreground=self.colors["text"])

    def on_focus_out(self, event):
        """Entry'den çıkıldığında boşsa placeholder'ı geri getir"""
        if not self.task_entry.get():
            self.task_entry.insert(0, "➕ Görev ekle")
            self.task_entry.configure(foreground=self.colors["text_secondary"])

    def show_context_menu(self, event):
        """Sağ tık menüsünü göster"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def change_category(self, category, title):
        """Kategori değiştir"""
        # Eski seçili butonu normal hale getir
        if hasattr(self, 'current_category'):
            self.category_buttons[self.current_category].state(['!selected'])
        
        # Yeni butonu seçili yap
        self.current_category = category
        self.category_buttons[category].state(['selected'])
        
        # Başlığı güncelle
        for widget in self.header_frame.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.configure(text=title)
        
        # Görevleri filtrele ve güncelle
        self.update_task_list()
    
    def check_reminders(self):
        """Hatırlatıcıları kontrol et"""
        while True:
            current_time = datetime.now()
            for task in self.todos:
                if task.get("reminder") and not task["completed"]:
                    task_time = datetime.strptime(f"{task['due_date']} {task['reminder_time']}", 
                                                "%d/%m/%Y %H:%M")
                    if current_time >= task_time and current_time <= task_time + timedelta(minutes=1):
                        self.show_notification(task["task"])
            time.sleep(60)  # Her dakika kontrol et
    
    def show_notification(self, task_title):
        """Windows bildirimi göster"""
        self.toaster.show_toast(
            "Yapılacak Görev Hatırlatıcısı",
            f"Görev: {task_title}",
            duration=10,
            threaded=True
        )

    def on_drag_start(self, event):
        """Sürükleme başladığında"""
        selection = self.tree.selection()
        if selection:
            # Seçili öğenin koordinatlarını al
            x, y = event.x, event.y
            item = self.tree.identify_row(y)
            if item in selection:
                self.drag_source = item
                self.drag_data = self.tree.item(item)["values"]
    
    def on_drag_motion(self, event):
        """Sürükleme devam ederken"""
        if self.drag_source:
            # İmlecin üzerinde olduğu öğeyi belirle
            target = self.tree.identify_row(event.y)
            if target:
                # Hedef öğeyi vurgula
                self.tree.selection_set(target)
    
    def on_drag_release(self, event):
        """Sürükleme bittiğinde"""
        if self.drag_source:
            target = self.tree.identify_row(event.y)
            if target and target != self.drag_source:
                # Öğelerin indekslerini al
                source_index = self.tree.index(self.drag_source)
                target_index = self.tree.index(target)
                
                # Todos listesinde öğeleri yer değiştir
                self.todos.insert(target_index, self.todos.pop(source_index))
                
                # Değişiklikleri kaydet ve listeyi güncelle
                self.save_todos()
                self.update_task_list()
            
            # Sürükleme verilerini temizle
            self.drag_source = None
            self.drag_data = None

    def toggle_theme(self):
        """Temayı değiştir"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.colors = self.themes[self.current_theme]
        
        # Tema butonunu güncelle
        self.theme_button.configure(text="🌙" if self.current_theme == "light" else "☀️")
        
        # Renkleri güncelle
        self.root.configure(bg=self.colors["bg"])
        
        # Başlık rengini güncelle
        self.title_label.configure(background=self.colors["bg"])
        
        # Stil güncellemeleri
        style = ttk.Style()
        
        # Başlık stili
        style.configure("Title.TLabel",
                       background=self.colors["bg"],
                       foreground=self.colors["text"])
        
        # Panel stilleri
        style.configure("LeftPanel.TFrame",
                       background=self.colors["sidebar_bg"],
                       relief="flat")
        
        style.configure("RightPanel.TFrame",
                       background=self.colors["bg"],
                       relief="flat")
        
        # Buton stilleri
        style.configure("SidebarButton.TButton",
                       padding=(10, 8, 10, 8),
                       font=('Segoe UI', 10),
                       background=self.colors["sidebar_bg"],
                       foreground=self.colors["text"],
                       borderwidth=0,
                       relief="flat",
                       anchor="w",  # Sola hizalama
                       width=25)
        
        style.map("SidebarButton.TButton",
                 background=[("active", self.colors["hover"]),
                           ("selected", self.colors["selected"])],
                 foreground=[("active", self.colors["accent"]),
                           ("selected", self.colors["accent"])])
        
        # Entry stilleri
        style.configure("Custom.TEntry",
                       fieldbackground=self.colors["panel_bg"],
                       foreground=self.colors["text"],
                       insertcolor=self.colors["text"],
                       borderwidth=0,
                       relief="flat")
        
        # Treeview stilleri
        style.configure("Custom.Treeview",
                       background=self.colors["panel_bg"],
                       foreground=self.colors["text"],
                       fieldbackground=self.colors["panel_bg"],
                       font=('Segoe UI', 10),
                       rowheight=30,
                       borderwidth=0,
                       relief="flat")
        
        style.configure("Custom.Treeview.Heading",
                       background=self.colors["panel_bg"],
                       foreground=self.colors["text"],
                       font=('Segoe UI', 10, 'bold'),
                       relief="flat")
        
        # Buton stilleri
        style.configure("Success.TButton",
                       padding=(10, 5),
                       font=('Segoe UI', 10),
                       background=self.colors["success"],
                       foreground="white")
        
        style.configure("Danger.TButton",
                       padding=(10, 5),
                       font=('Segoe UI', 10),
                       background=self.colors["danger"],
                       foreground="white")
        
        style.map("Success.TButton",
                 background=[("active", self.colors["success"])])
        
        style.map("Danger.TButton",
                 background=[("active", self.colors["danger"])])
        
        # Görev listesini güncelle
        self.update_task_list()

    def show_task_details(self, event):
        """Seçili görevin detaylarını göster"""
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            task = self.todos[index]
            
            # Detay metnini hazırla
            details = []
            if "description" in task and task["description"].strip():
                details.append(f"📝 Açıklama:\n{task['description']}\n")
            
            details.extend([
                f"📅 Tarih: {task['due_date']}",
                f"⚡ Öncelik: {task['priority']}",
                f"📂 Kategori: {task['category']}"
            ])
            
            # Detayları göster
            self.detail_text.configure(text="\n\n".join(details))

    def on_task_select(self, event):
        """Görev seçildiğinde butonları aktif/pasif yap"""
        selection = self.tree.selection()
        if selection:
            self.complete_btn.state(['!disabled'])
            self.edit_btn.state(['!disabled'])
            self.delete_btn.state(['!disabled'])
            
            # Seçili görevin detaylarını göster
            self.show_task_details(event)
        else:
            self.complete_btn.state(['disabled'])
            self.edit_btn.state(['disabled'])
            self.delete_btn.state(['disabled'])

    def complete_selected_task(self):
        """Seçili görevi tamamla/tamamlanmadı olarak işaretle"""
        selection = self.tree.selection()
        if selection:
            self.toggle_complete(selection[0])
    
    def edit_selected_task(self):
        """Seçili görevi düzenle"""
        selection = self.tree.selection()
        if selection:
            self.edit_task(selection[0])
    
    def delete_selected_task(self):
        """Seçili görevi sil"""
        selection = self.tree.selection()
        if selection:
            self.delete_task(selection[0])

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop() 