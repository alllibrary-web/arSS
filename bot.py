import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import requests
from bs4 import BeautifulSoup
import json
import os
import threading
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import re
from urllib.parse import urljoin, urlparse, quote
import tempfile
import hashlib
import bencodepy
import base64
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
from contextlib import contextmanager
import csv
import sys
import io
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import math
import webbrowser

# Настройки
BASE_URL = "https://online-fix.me"
SESSION_FILE = "arSS for Hydra_session.json"
CONFIG_FILE = "arSS for Hydra_config.json"
DB_FILE = "arSS for Hydra_database.db"

# Исправление кодировки для Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('pekafix.log', maxBytes=1024*1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class AnimatedBackground:
    """Класс для анимированного фона с частицами"""
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles = []
        self.colors = ['#58a6ff', '#3fb950', '#a371f7', '#f85149', '#ff9b33', '#56d364', '#ec6547']
        self.shapes = ['circle', 'square', 'triangle']
        self.init_particles()
        
    def init_particles(self):
        """Инициализация частиц"""
        for _ in range(25):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 6)
            color = random.choice(self.colors)
            shape = random.choice(self.shapes)
            speed_x = random.uniform(-0.3, 0.3)
            speed_y = random.uniform(-0.3, 0.3)
            
            particle = {
                'x': x, 'y': y, 'size': size, 'color': color,
                'shape': shape, 'speed_x': speed_x, 'speed_y': speed_y, 'id': None
            }
            self.particles.append(particle)
            
    def draw_particles(self):
        """Отрисовка частиц"""
        for particle in self.particles:
            if particle['id']:
                self.canvas.delete(particle['id'])
                
            if particle['shape'] == 'circle':
                particle['id'] = self.canvas.create_oval(
                    particle['x'], particle['y'],
                    particle['x'] + particle['size'],
                    particle['y'] + particle['size'],
                    fill=particle['color'], outline='', width=0
                )
            elif particle['shape'] == 'square':
                particle['id'] = self.canvas.create_rectangle(
                    particle['x'], particle['y'],
                    particle['x'] + particle['size'],
                    particle['y'] + particle['size'],
                    fill=particle['color'], outline='', width=0
                )
            elif particle['shape'] == 'triangle':
                points = [
                    particle['x'], particle['y'],
                    particle['x'] + particle['size'], particle['y'],
                    particle['x'] + particle['size']/2, particle['y'] - particle['size']
                ]
                particle['id'] = self.canvas.create_polygon(
                    points, fill=particle['color'], outline='', width=0
                )
        
    def update_particles(self):
        """Обновление позиций частиц"""
        for particle in self.particles:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            
            # Отскок от границ
            if particle['x'] <= 0 or particle['x'] >= self.width:
                particle['speed_x'] *= -1
            if particle['y'] <= 0 or particle['y'] >= self.height:
                particle['speed_y'] *= -1
            
    def animate(self):
        """Анимация частиц"""
        self.update_particles()
        self.draw_particles()
        self.canvas.after(100, self.animate)

class ModernGameParser:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 PEKAR.fix PRO - Ultimate Game Parser")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0d1117')
        
        # Создание анимированного фона
        self.setup_animated_background()
        
        # Главный контейнер поверх фона
        self.main_container = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_container.place(relwidth=1, relheight=1)
        
        # Центрирование окна
        self.center_window()
        
        # Инициализация переменных
        self.session = requests.Session()
        self.driver = None
        self.logged_in = False
        self.selenium_logged_in = False
        self.games_data = []
        self.max_games = 10000
        self.config = self.load_config()
        self.stats = {
            'games_found': 0,
            'torrents_found': 0,
            'magnets_created': 0,
            'errors': 0
        }
        
        # Настройка ограничителя запросов
        self.request_semaphore = threading.Semaphore(3)
        self.last_request_time = 0
        self.min_request_interval = 0.5
        
        # Переменные для умного скролла
        self.auto_scroll_enabled = True
        self.user_scrolled_up = False
        
        # Инициализация БД
        self.init_database()
        
        # Настройка сессии
        self.setup_session()
        
        # Создание интерфейса
        self.setup_modern_ui()
        
        # Загрузка сессии
        self.load_session()
        
        self.safe_log("🎯 PEKAR.fix PRO инициализирован")

    def setup_animated_background(self):
        """Настройка анимированного фона"""
        self.bg_canvas = tk.Canvas(self.root, bg='#0d1117', highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)
        
        # Запуск анимации частиц
        self.background = AnimatedBackground(self.bg_canvas, 1400, 900)
        self.root.after(1000, self.background.animate)

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{1400}x{900}+{x}+{y}')

    def setup_modern_ui(self):
        """Создание современного интерфейса"""
        # Стили
        self.setup_styles()
        
        # Верхняя панель
        self.create_header()
        
        # Разделитель
        separator = ttk.Separator(self.main_container, orient='horizontal')
        separator.pack(fill=tk.X, pady=10, padx=20)
        
        # Панель вкладок
        self.create_tabs()
        
        # Статус бар
        self.create_status_bar()

    def setup_styles(self):
        """Настройка современных стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Темная цветовая схема
        bg_color = '#0d1117'
        card_bg = '#161b22'
        accent_color = '#58a6ff'
        text_color = '#c9d1d9'
        muted_text = '#8b949e'
        
        # Основные стили
        style.configure('Dark.TFrame', background=bg_color)
        style.configure('Card.TFrame', background=card_bg, relief='flat', borderwidth=1)
        
        # Стили для текста
        style.configure('Title.TLabel', background=bg_color, foreground=accent_color, 
                       font=('Segoe UI', 20, 'bold'))
        style.configure('Subtitle.TLabel', background=bg_color, foreground=muted_text, 
                       font=('Segoe UI', 11))
        style.configure('Dark.TLabel', background=bg_color, foreground=text_color, 
                       font=('Segoe UI', 10))
        style.configure('Accent.TLabel', background=bg_color, foreground='#3fb950', 
                       font=('Segoe UI', 10, 'bold'))
        
        # Стили для кнопок
        style.configure('Accent.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       background='#21262d',
                       foreground=text_color,
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='#30363d')
        
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 9),
                       background=card_bg,
                       foreground=muted_text,
                       borderwidth=0)
        
        # Стили для Treeview
        style.configure('Modern.Treeview',
            background=card_bg,
            foreground=text_color,
            fieldbackground=card_bg,
            font=('Segoe UI', 9),
            borderwidth=0,
            relief='flat'
        )
        style.configure('Modern.Treeview.Heading',
            background='#21262d',
            foreground=accent_color,
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            borderwidth=0
        )
        
        # Стили для Progressbar
        style.configure('Custom.Horizontal.TProgressbar',
            background='#238636',
            troughcolor=card_bg,
            borderwidth=0
        )
        
        # Стили для Notebook (вкладки)
        style.configure('Modern.TNotebook',
            background=bg_color,
            borderwidth=0
        )
        style.configure('Modern.TNotebook.Tab',
            background=card_bg,
            foreground=muted_text,
            padding=[20, 8],
            font=('Segoe UI', 10)
        )
        style.map('Modern.TNotebook.Tab',
            background=[('selected', '#21262d')],
            foreground=[('selected', accent_color)]
        )
        
        style.map('Modern.Treeview', 
                 background=[('selected', '#1f6feb')])
        style.map('Accent.TButton', 
                 background=[('active', '#30363d'), ('pressed', '#484f58')])
        style.map('Secondary.TButton', 
                 background=[('active', '#21262d'), ('pressed', '#30363d')])

    def create_header(self):
        """Создание заголовка"""
        header_frame = ttk.Frame(self.main_container, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        # Левая часть - логотип и название
        title_frame = ttk.Frame(header_frame, style='Dark.TFrame')
        title_frame.pack(side=tk.LEFT)
        
        # Логотип с эмодзи
        logo_label = ttk.Label(title_frame, text="🎮", style='Title.TLabel', font=('Segoe UI', 24))
        logo_label.pack(side=tk.LEFT)
        
        # Текст заголовка
        text_frame = ttk.Frame(title_frame, style='Dark.TFrame')
        text_frame.pack(side=tk.LEFT, padx=(15, 0))
        
        ttk.Label(text_frame, text="PEKAR.fix", style='Title.TLabel').pack(anchor='w')
        ttk.Label(text_frame, text="PRO | Ultimate Game Parser", style='Subtitle.TLabel').pack(anchor='w')
        
        # Правая часть - кнопки управления
        control_frame = ttk.Frame(header_frame, style='Dark.TFrame')
        control_frame.pack(side=tk.RIGHT)
        
        controls = [
            ("🔐 Авторизация", self.login),
            ("🔄 Обновить", self.refresh_data),
            ("⚙️ Настройки", self.show_settings),
            ("📊 Статистика", self.show_stats),
            ("🔄 Торренты", self.update_torrents),
            ("🦊 Авто-торренты", self.selenium_torrent_search),
            ("➕ Ручная игра", self.manual_game_add),
            ("❓ Помощь", self.show_help)
        ]
        
        for text, command in controls:
            btn = ttk.Button(control_frame, text=text, command=command, style='Secondary.TButton')
            btn.pack(side=tk.LEFT, padx=(8, 0))

    def create_tabs(self):
        """Создание системы вкладок"""
        tab_control = ttk.Notebook(self.main_container, style='Modern.TNotebook')
        tab_control.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # Вкладка парсера
        self.parser_tab = ttk.Frame(tab_control, style='Dark.TFrame')
        tab_control.add(self.parser_tab, text='🎯 Парсер')
        self.setup_parser_tab()
        
        # Вкладка базы данных
        self.database_tab = ttk.Frame(tab_control, style='Dark.TFrame')
        tab_control.add(self.database_tab, text='🗃️ База данных')
        self.setup_database_tab()
        
        # Вкладка мониторинга
        self.monitor_tab = ttk.Frame(tab_control, style='Dark.TFrame')
        tab_control.add(self.monitor_tab, text='📡 Мониторинг')
        self.setup_monitor_tab()

    def setup_parser_tab(self):
        """Настройка вкладки парсера"""
        # Основной контейнер
        main_frame = ttk.Frame(self.parser_tab, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Панель управления
        control_frame = ttk.Frame(main_frame, style='Card.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        control_inner = ttk.Frame(control_frame, style='Card.TFrame')
        control_inner.pack(padx=20, pady=15)
        
        # Основные действия
        action_frame = ttk.Frame(control_inner, style='Card.TFrame')
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        actions = [
            ("🎮 Найти игры", self.start_game_search),
            ("📥 Найти торренты", self.start_torrent_search),
            ("🧲 Создать магнеты", self.start_magnet_creation),
            ("✏️ Ручная версия", self.manual_version_input),
            ("🔗 Ручной торрент", self.manual_torrent_input)
        ]
        
        for text, command in actions:
            btn = ttk.Button(action_frame, text=text, command=command, style='Accent.TButton')
            btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Панель экспорта
        export_frame = ttk.Frame(control_inner, style='Card.TFrame')
        export_frame.pack(fill=tk.X)
        
        ttk.Label(export_frame, text="Экспорт:", style='Dark.TLabel').pack(side=tk.LEFT)
        
        ttk.Button(export_frame, text="📤 JSON", command=self.export_json, style='Secondary.TButton').pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(export_frame, text="📋 CSV", command=self.export_csv, style='Secondary.TButton').pack(side=tk.LEFT, padx=(5, 0))
        
        # Панель поиска и настроек
        search_frame = ttk.Frame(main_frame, style='Card.TFrame')
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        search_inner = ttk.Frame(search_frame, style='Card.TFrame')
        search_inner.pack(padx=20, pady=15)
        
        # Поиск
        search_row = ttk.Frame(search_inner, style='Card.TFrame')
        search_row.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_row, text="🔍 Поиск:", style='Dark.TLabel').pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(10, 5))
        search_entry.bind('<KeyRelease>', self.search_games)
        
        ttk.Button(search_row, text="Очистить", command=self.clear_search, style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Настройки
        settings_row = ttk.Frame(search_inner, style='Card.TFrame')
        settings_row.pack(fill=tk.X)
        
        # Максимальное количество игр
        ttk.Label(settings_row, text="Макс. игр:", style='Dark.TLabel').pack(side=tk.LEFT)
        self.max_games_var = tk.StringVar(value=str(self.max_games))
        max_games_spinbox = ttk.Spinbox(settings_row, from_=1, to=99999, width=8, 
                                      textvariable=self.max_games_var)
        max_games_spinbox.pack(side=tk.LEFT, padx=(10, 20))
        max_games_spinbox.bind('<Return>', lambda e: self.update_max_games())
        max_games_spinbox.bind('<FocusOut>', lambda e: self.update_max_games())
        
        # Ограничение запросов
        ttk.Label(settings_row, text="Запросов/сек:", style='Dark.TLabel').pack(side=tk.LEFT)
        self.requests_per_second_var = tk.StringVar(value="3")
        requests_spinbox = ttk.Spinbox(settings_row, from_=1, to=10, width=3,
                                     textvariable=self.requests_per_second_var)
        requests_spinbox.pack(side=tk.LEFT, padx=(10, 20))
        
        # Диапазон страниц
        ttk.Label(settings_row, text="Страницы:", style='Dark.TLabel').pack(side=tk.LEFT)
        self.start_page_var = tk.StringVar(value="1")
        start_spinbox = ttk.Spinbox(settings_row, from_=1, to=82, width=5,
                                  textvariable=self.start_page_var)
        start_spinbox.pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Label(settings_row, text="-", style='Dark.TLabel').pack(side=tk.LEFT)
        self.end_page_var = tk.StringVar(value="5")
        end_spinbox = ttk.Spinbox(settings_row, from_=1, to=82, width=5,
                                textvariable=self.end_page_var)
        end_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(settings_row, text="📄 Все страницы", command=self.parse_all_pages, style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Сортировка
        sort_frame = ttk.Frame(search_inner, style='Card.TFrame')
        sort_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(sort_frame, text="Сортировка:", style='Dark.TLabel').pack(side=tk.LEFT)
        
        self.sort_var = tk.StringVar(value="id")
        sort_options = [
            ("ID", "id"),
            ("Название А-Я", "title_asc"),
            ("Название Я-А", "title_desc"),
            ("Вес (правильно)", "size_correct"),
            ("Версия Any", "any_version"),
            ("Без торрентов", "no_torrents")
        ]
        
        for text, value in sort_options:
            ttk.Radiobutton(sort_frame, text=text, variable=self.sort_var, 
                           value=value, command=self.apply_sorting,
                           style='Dark.TLabel').pack(side=tk.LEFT, padx=(10, 0))
        
        # Прогресс-бар
        progress_frame = ttk.Frame(main_frame, style='Card.TFrame')
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        progress_inner = ttk.Frame(progress_frame, style='Card.TFrame')
        progress_inner.pack(padx=20, pady=15)
        
        ttk.Label(progress_inner, text="Прогресс:", style='Dark.TLabel').pack(side=tk.LEFT)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_inner, variable=self.progress_var, 
                                          maximum=100, style='Custom.Horizontal.TProgressbar')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        self.progress_label = ttk.Label(progress_inner, text="0%", style='Accent.TLabel')
        self.progress_label.pack(side=tk.LEFT)
        
        # Таблица с играми
        table_frame = ttk.Frame(main_frame, style='Card.TFrame')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        table_inner = ttk.Frame(table_frame, style='Card.TFrame')
        table_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        columns = ("ID", "Название", "Версия", "Торрент", "Магнет", "Размер", "Статус", "Обновлено")
        self.tree = ttk.Treeview(table_inner, columns=columns, show="headings", 
                               style='Modern.Treeview', height=18)
        
        # Настройка колонок
        column_config = {
            "ID": 60, "Название": 350, "Версия": 80, "Торрент": 100, 
            "Магнет": 120, "Размер": 100, "Статус": 150, "Обновлено": 150
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_config.get(col, 100))
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_inner, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Контекстное меню
        self.setup_context_menu()

    def setup_database_tab(self):
        """Настройка вкладки базы данных"""
        main_frame = ttk.Frame(self.database_tab, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Статистика БД
        stats_frame = ttk.Frame(main_frame, style='Card.TFrame')
        stats_frame.pack(fill=tk.X, pady=(0, 30))
        
        stats_inner = ttk.Frame(stats_frame, style='Card.TFrame')
        stats_inner.pack(padx=20, pady=20)
        
        ttk.Label(stats_inner, text="📊 Статистика базы данных", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 20))
        
        stats_cards = [
            ("🎮", "Всего игр:", "total_games", "#58a6ff"),
            ("📥", "С торрентами:", "with_torrents", "#3fb950"),
            ("🧲", "С магнетами:", "with_magnets", "#a371f7"),
            ("❌", "Ошибок:", "errors", "#f85149")
        ]
        
        cards_frame = ttk.Frame(stats_inner, style='Card.TFrame')
        cards_frame.pack(fill=tk.X)
        
        for i, (emoji, label, key, color) in enumerate(stats_cards):
            card = ttk.Frame(cards_frame, style='Card.TFrame')
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
            
            card_inner = ttk.Frame(card, style='Card.TFrame')
            card_inner.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
            
            # Эмодзи и текст
            text_frame = ttk.Frame(card_inner, style='Card.TFrame')
            text_frame.pack(fill=tk.X)
            
            ttk.Label(text_frame, text=emoji, style='Dark.TLabel', font=('Segoe UI', 14)).pack(side=tk.LEFT)
            ttk.Label(text_frame, text=label, style='Dark.TLabel', font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(5, 0))
            
            # Значение
            label_var = tk.StringVar(value="0")
            setattr(self, f"{key}_var", label_var)
            value_label = ttk.Label(card_inner, textvariable=label_var, 
                                  style='Dark.TLabel', 
                                  font=('Segoe UI', 24, 'bold'),
                                  foreground=color)
            value_label.pack(pady=(10, 0))

    def setup_monitor_tab(self):
        """Настройка вкладки мониторинга"""
        main_frame = ttk.Frame(self.monitor_tab, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Панель управления логом
        log_control_frame = ttk.Frame(main_frame, style='Card.TFrame')
        log_control_frame.pack(fill=tk.X, pady=(0, 15))
        
        log_control_inner = ttk.Frame(log_control_frame, style='Card.TFrame')
        log_control_inner.pack(padx=20, pady=15)
        
        ttk.Label(log_control_inner, text="📝 Лог выполнения в реальном времени", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        ttk.Button(log_control_inner, text="📋 Копировать лог", command=self.copy_log, style='Secondary.TButton').pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(log_control_inner, text="🧹 Очистить лог", command=self.clear_log, style='Secondary.TButton').pack(side=tk.RIGHT)
        
        # Текстовое поле лога
        log_frame = ttk.Frame(main_frame, style='Card.TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_inner = ttk.Frame(log_frame, style='Card.TFrame')
        log_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_inner, 
            wrap=tk.WORD, 
            bg='#161b22', 
            fg='#c9d1d9',
            insertbackground='#c9d1d9',
            font=('Consolas', 9),
            relief='flat',
            borderwidth=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.log_text.config(state=tk.DISABLED)
        
        # Настройка умного автоскролла
        self.setup_log_autoscroll()
        
        # Контекстное меню для лога
        self.log_context_menu = tk.Menu(self.root, tearoff=0, bg='#161b22', fg='#c9d1d9', font=('Segoe UI', 9))
        self.log_context_menu.add_command(label="📋 Копировать", command=self.copy_log_selection)
        self.log_context_menu.add_command(label="📋 Копировать всё", command=self.copy_log)
        self.log_context_menu.add_separator()
        self.log_context_menu.add_command(label="🧹 Очистить", command=self.clear_log)
        
        self.log_text.bind("<Button-3>", self.show_log_context_menu)

    def setup_log_autoscroll(self):
        """Настройка умного автоскролла для лога"""
        self.auto_scroll_enabled = True
        self.user_scrolled_up = False
        
        # Привязка событий для отслеживания действий пользователя
        self.log_text.bind("<MouseWheel>", self.on_log_scroll)
        self.log_text.bind("<Button-1>", self.on_log_click)
        self.log_text.bind("<KeyPress>", self.on_log_keypress)
        
    def on_log_scroll(self, event):
        """Обработка скролла мыши в логе"""
        self.check_scroll_position()
        
    def on_log_click(self, event):
        """Обработка клика в логе"""
        self.check_scroll_position()
        
    def on_log_keypress(self, event):
        """Обработка нажатия клавиш в логе"""
        self.check_scroll_position()
        
    def check_scroll_position(self):
        """Проверка позиции скролла для определения, находится ли пользователь внизу"""
        try:
            # Получаем текущую позицию скролла
            self.log_text.update_idletasks()
            first_visible = self.log_text.yview()[0]
            
            # Если пользователь прокрутил вверх более чем на 5% от конца
            if first_visible < 0.95:
                self.user_scrolled_up = True
            else:
                self.user_scrolled_up = False
        except:
            pass

    def create_status_bar(self):
        """Создание статус бара"""
        status_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        status_inner = ttk.Frame(status_frame, style='Card.TFrame')
        status_inner.pack(padx=15, pady=10)
        
        self.status_var = tk.StringVar(value="🟢 Готов к работе")
        status_label = ttk.Label(status_inner, textvariable=self.status_var, style='Dark.TLabel')
        status_label.pack(side=tk.LEFT)
        
        conn_status = "🔴 Не авторизован"
        self.conn_var = tk.StringVar(value=conn_status)
        conn_label = ttk.Label(status_inner, textvariable=self.conn_var, style='Dark.TLabel')
        conn_label.pack(side=tk.RIGHT)

    def setup_context_menu(self):
        """Настройка контекстного меню для таблицы"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#161b22', fg='#c9d1d9', font=('Segoe UI', 9))
        self.context_menu.add_command(label="🌐 Открыть в браузере", command=self.open_in_browser)
        self.context_menu.add_command(label="📋 Копировать название", command=self.copy_game_name)
        self.context_menu.add_command(label="🔗 Копировать URL", command=self.copy_game_url)
        self.context_menu.add_command(label="🧲 Копировать магнет", command=self.copy_magnet)
        self.context_menu.add_command(label="🔄 Обновить игру", command=self.refresh_game)
        self.context_menu.add_command(label="✏️ Ввести версию вручную", command=self.manual_version_for_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Удалить игру", command=self.delete_game)
        
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def show_log_context_menu(self, event):
        """Показать контекстное меню для лога"""
        self.log_context_menu.post(event.x_root, event.y_root)

    def copy_log_selection(self):
        """Копировать выделенный текст в логе"""
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.safe_log("📋 Выделенный текст скопирован из лога")
        except:
            self.copy_log()

    def copy_log(self):
        """Копировать весь лог"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(log_content)
            self.safe_log("📋 Весь лог скопирован в буфер")
        except Exception as e:
            self.safe_log(f"❌ Ошибка копирования лога: {e}")

    def clear_log(self):
        """Очистить лог"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.safe_log("🧹 Лог очищен")

    def search_games(self, event=None):
        """Поиск игр по названию"""
        search_text = self.search_var.get().lower()
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, version, torrent_url, magnet_url, file_size, status, updated_at FROM games ORDER BY id ASC")
            all_games = cursor.fetchall()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for game in all_games:
            if search_text in game[1].lower():
                # Исправляем отображение версии - убираем ссылки
                game_values = list(game)
                if game_values[2] and (game_values[2].startswith('http') or len(game_values[2]) > 50):
                    game_values[2] = "Не найдена"
                self.tree.insert("", tk.END, values=game_values)

    def clear_search(self):
        """Очистить поиск"""
        self.search_var.set("")
        self.load_games_from_db()

    def update_max_games(self):
        """Обновление максимального количества игр"""
        try:
            self.max_games = int(self.max_games_var.get())
            self.safe_log(f"🔧 Максимальное количество игр установлено: {self.max_games}")
        except ValueError:
            self.max_games = 10000
            self.max_games_var.set("10000")

    def parse_all_pages(self):
        """Парсинг всех страниц (1-82)"""
        self.start_page_var.set("1")
        self.end_page_var.set("82")
        self.start_game_search()

    def apply_sorting(self):
        """Применение сортировки"""
        sort_type = self.sort_var.get()
        self.load_games_from_db(sort_type)

    def open_in_browser(self):
        """Открыть страницу игры в браузере"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            game_id = item['values'][0]
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT url FROM games WHERE id = ?", (game_id,))
                result = cursor.fetchone()
                if result:
                    webbrowser.open(result[0])
                    self.safe_log("🌐 Открываю страницу в браузере")

    def init_database(self):
        """Инициализация базы данных"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE,
                    torrent_url TEXT,
                    magnet_url TEXT,
                    file_size TEXT,
                    status TEXT,
                    page INTEGER,
                    version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY,
                    cookies TEXT,
                    headers TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def load_config(self):
        """Загрузка конфигурации"""
        default_config = {
            'max_threads': 3,
            'request_delay': 1,
            'timeout': 30,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'auto_save': True
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
        except Exception as e:
            logging.error(f"Ошибка загрузки конфига: {e}")
        
        return default_config

    def save_config(self):
        """Сохранение конфигурации"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Ошибка сохранения конфига: {e}")

    def setup_session(self):
        """Настройка сессии"""
        self.session.headers.update({
            'User-Agent': self.config['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def load_session(self):
        """Загрузка сессии из БД"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT cookies, headers FROM sessions ORDER BY id DESC LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    cookies = json.loads(result[0])
                    headers = json.loads(result[1])
                    
                    self.session.cookies.update(cookies)
                    self.session.headers.update(headers)
                    self.logged_in = True
                    self.conn_var.set("🟢 Авторизован")
                    self.safe_log("✅ Сессия загружена из БД")
                    return True
        except Exception as e:
            logging.error(f"Ошибка загрузки сессии: {e}")
        
        return False

    def save_session(self):
        """Сохранение сессии в БД"""
        try:
            cookies = json.dumps(dict(self.session.cookies))
            headers = json.dumps(dict(self.session.headers))
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO sessions (id, cookies, headers) 
                    VALUES (1, ?, ?)
                ''', (cookies, headers))
                conn.commit()
                
            self.safe_log("💾 Сессия сохранена в БД")
            return True
        except Exception as e:
            logging.error(f"Ошибка сохранения сессии: {e}")
            return False

    def login(self):
        """Авторизация на сайте"""
        def login_thread():
            self.safe_log("🔐 Начинаем авторизацию...")
            
            if self.check_session_valid():
                self.safe_log("✅ Используем существующую сессию")
                self.logged_in = True
                self.conn_var.set("🟢 Авторизован")
                return
            
            if not self.selenium_login():
                self.safe_log("❌ Ошибка авторизации")
                return
            
            self.logged_in = True
            self.conn_var.set("🟢 Авторизован")
            self.save_session()
            self.safe_log("✅ Авторизация успешна!")
        
        threading.Thread(target=login_thread, daemon=True).start()

    def selenium_login(self):
        """Авторизация через Selenium"""
        try:
            self.safe_log("🦊 Запускаем браузер...")
            
            options = Options()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1200,800")
            
            try:
                from webdriver_manager.firefox import GeckoDriverManager
                service = Service(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
            except ImportError:
                self.driver = webdriver.Firefox(options=options)
            
            self.driver.get(BASE_URL)
            
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.safe_log("🔍 Ищем форму авторизации...")
            time.sleep(2)
            
            login_links = [
                "//a[contains(text(), 'Вход')]",
                "//a[contains(text(), 'Войти')]",
                "//a[contains(text(), 'Login')]",
                "//a[contains(@href, 'login')]",
            ]
            
            for link_selector in login_links:
                try:
                    login_link = self.driver.find_element(By.XPATH, link_selector)
                    self.safe_log(f"🔗 Найдена ссылка входа: {link_selector}")
                    login_link.click()
                    time.sleep(3)
                    break
                except:
                    continue
            
            username_selectors = [
                "//input[@name='login_name']",
                "//input[@name='username']", 
            ]
            
            password_selectors = [
                "//input[@name='login_password']",
                "//input[@name='password']",
            ]
            
            username_field = None
            password_field = None
            
            for selector in username_selectors:
                try:
                    username_field = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
                    
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if not username_field or not password_field:
                self.safe_log("❌ Не удалось найти поля для ввода")
                self.driver.quit()
                return False
            
            username_field.clear()
            username_field.send_keys("имя")
            time.sleep(0.5)
            
            password_field.clear() 
            password_field.send_keys("пароль")
            time.sleep(0.5)
            
            password_field.send_keys(Keys.RETURN)
            time.sleep(5)
            
            if "peka_r" in self.driver.page_source.lower():
                self.safe_log("✅ Авторизация в браузере успешна")
                
                selenium_cookies = self.driver.get_cookies()
                for cookie in selenium_cookies:
                    self.session.cookies.set(
                        cookie['name'],
                        cookie['value'],
                        domain=cookie.get('domain', '.online-fix.me')
                    )
                
                self.selenium_logged_in = True
                self.driver.quit()
                return True
            else:
                self.safe_log("❌ Ошибка авторизации в браузере")
                self.driver.quit()
                return False
                    
        except Exception as e:
            self.safe_log(f"❌ Ошибка Selenium: {e}")
            if self.driver:
                self.driver.quit()
            return False

    def check_session_valid(self):
        """Проверка валидности сессии"""
        try:
            response = self.session.get(BASE_URL, timeout=10)
            return "peka_r" in response.text
        except:
            return False

    def refresh_data(self):
        """Обновить данные"""
        self.load_games_from_db()
        self.safe_log("🔄 Данные обновлены")

    def show_settings(self):
        """Показать настройки"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Настройки ограничения запросов")
        settings_window.geometry("400x200")
        settings_window.configure(bg='#0d1117')
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        main_frame = ttk.Frame(settings_window, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="⚙️ Настройки ограничения запросов", style='Title.TLabel').pack(pady=(0, 20))
        
        # Настройка количества запросов в секунду
        requests_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        requests_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(requests_frame, text="Макс. запросов в секунду:", style='Dark.TLabel').pack(side=tk.LEFT)
        requests_var = tk.StringVar(value=self.requests_per_second_var.get())
        requests_spinbox = ttk.Spinbox(requests_frame, from_=1, to=10, width=5, textvariable=requests_var)
        requests_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Настройка интервала между запросами
        interval_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        interval_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(interval_frame, text="Интервал между запросами (сек):", style='Dark.TLabel').pack(side=tk.LEFT)
        interval_var = tk.StringVar(value=str(self.min_request_interval))
        interval_spinbox = ttk.Spinbox(interval_frame, from_=0.1, to=5.0, increment=0.1, width=5, textvariable=interval_var)
        interval_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        def save_settings():
            try:
                requests_per_sec = int(requests_var.get())
                interval = float(interval_var.get())
                
                self.requests_per_second_var.set(str(requests_per_sec))
                self.min_request_interval = interval
                self.request_semaphore = threading.Semaphore(requests_per_sec)
                
                self.safe_log(f"⚙️ Настройки обновлены: {requests_per_sec} запр/сек, интервал {interval} сек")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числовые значения")
        
        ttk.Button(main_frame, text="💾 Сохранить", command=save_settings, style='Accent.TButton').pack(pady=20)

    def show_stats(self):
        """Показать статистику"""
        stats_text = f"""
📊 Статистика PEKAR.fix PRO:

🎮 Всего игр: {getattr(self, 'total_games_var', tk.StringVar(value='0')).get()}
📥 С торрентами: {getattr(self, 'with_torrents_var', tk.StringVar(value='0')).get()} 
🧲 С магнетами: {getattr(self, 'with_magnets_var', tk.StringVar(value='0')).get()}
❌ Ошибок: {getattr(self, 'errors_var', tk.StringVar(value='0')).get()}

💾 База данных: {DB_FILE}
🔐 Статус: {"🟢 Авторизован" if self.logged_in else "🔴 Не авторизован"}
        """
        messagebox.showinfo("📊 Статистика", stats_text)

    def show_help(self):
        """Показать помощь"""
        help_text = """
🎮 PEKAR.fix PRO - Помощь

🔐 Авторизация - войти на online-fix.me
🎮 Найти игры - парсинг списка игр (всех 82 страниц)
📥 Найти торренты - поиск .torrent файлов
🧲 Создать магнеты - конвертация в magnet-ссылки
🔄 Обновить торренты - проверка обновлений версий
🦊 Авто-торренты - поиск торрентов через браузер для игр без торрентов
➕ Ручная игра - добавление игры вручную по URL
✏️ Ручная версия - ввод версии вручную
🔗 Ручной торрент - ввод ссылки на торрент вручную
📤 Экспорт - сохранение результатов

⚙️ Настройки - настройка ограничения запросов

💡 Советы:
- Используйте правый клик для быстрых действий
- Данные автоматически сохраняются в БД
- Логи сохраняются в pekafix.log
- Кнопка "Все страницы" для парсинга всех 82 страниц
- Поиск по названию в таблице работает в реальном времени
- Настройте ограничение запросов чтобы избежать ошибки 429
- "Авто-торренты" использует видимый браузер для поиска сложных торрентов
- "Ручная игра" позволяет добавить игры, которые не нашлись автоматически
        """
        messagebox.showinfo("❓ Помощь", help_text)

    def manual_game_add(self):
        """Добавление игры вручную по URL"""
        game_url = simpledialog.askstring(
            "➕ Добавить игру вручную", 
            "Введите URL игры с online-fix.me:",
            parent=self.root
        )
        
        if not game_url:
            return
            
        if not game_url.startswith('http'):
            messagebox.showerror("Ошибка", "Введите корректный URL")
            return
        
        def add_thread():
            try:
                self.safe_log(f"➕ Добавляем игру вручную: {game_url}")
                
                response = self.safe_get(game_url, timeout=30)
                if response.status_code != 200:
                    self.safe_log(f"❌ Ошибка загрузки страницы: {response.status_code}")
                    return
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Ищем заголовок игры
                title_elem = soup.find('h1', class_='title')
                if not title_elem:
                    # Пробуем другие селекторы для заголовка
                    title_elem = soup.find('h1') or soup.find('title')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    # Очищаем заголовок от лишнего
                    if ' - ' in title:
                        title = title.split(' - ')[0]
                    if ' | ' in title:
                        title = title.split(' | ')[0]
                    
                    self.safe_log(f"📋 Найдено название: {title}")
                    
                    # Сохраняем игру в БД
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM games WHERE url = ?", (game_url,))
                        existing = cursor.fetchone()
                        
                        if not existing:
                            cursor.execute('''
                                INSERT INTO games (title, url, status, page)
                                VALUES (?, ?, ?, ?)
                            ''', (title, game_url, 'Добавлена вручную', 0))
                            conn.commit()
                            self.safe_log(f"✅ Игра добавлена: {title}")
                            
                            # Пытаемся сразу найти торрент
                            cursor.execute("SELECT id FROM games WHERE url = ?", (game_url,))
                            game_id = cursor.fetchone()[0]
                            
                            torrent_url, magnet, version, game_size = self.generate_torrent_and_magnet(game_url, title)
                            
                            if torrent_url:
                                self.update_game_torrent(game_id, torrent_url)
                                if version:
                                    self.update_game_version(game_id, version)
                                if game_size:
                                    self.update_game_size(game_id, game_size)
                                if magnet:
                                    self.update_game_magnet(game_id, magnet)
                                self.safe_log(f"✅ Торрент найден для ручной игры: {title}")
                            else:
                                self.safe_log(f"❌ Торрент не найден для ручной игры: {title}")
                        else:
                            self.safe_log("ℹ️ Игра уже есть в базе")
                    
                    self.load_games_from_db()
                else:
                    self.safe_log("❌ Не удалось определить название игры")
                    
            except Exception as e:
                self.safe_log(f"❌ Ошибка добавления игры: {e}")
        
        threading.Thread(target=add_thread, daemon=True).start()

    def selenium_torrent_search(self):
        """Автоматический поиск торрентов через Selenium для игр без торрентов"""
        def selenium_search_thread():
            self.safe_log("🦊 Запускаем автоматический поиск торрентов через браузер...")
            
            games = self.get_games_without_torrents()
            
            if not games:
                self.safe_log("ℹ️ Нет игр без торрентов для обработки")
                return
            
            self.safe_log(f"🔍 Обрабатываем {len(games)} игр через браузер...")
            
            total = len(games)
            successful = 0
            
            # Запускаем браузер
            try:
                options = Options()
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1200,800")
                
                try:
                    from webdriver_manager.firefox import GeckoDriverManager
                    service = Service(GeckoDriverManager().install())
                    driver = webdriver.Firefox(service=service, options=options)
                except ImportError:
                    driver = webdriver.Firefox(options=options)
                
                # Сначала авторизуемся в браузере
                self.safe_log("🔐 Выполняем авторизацию в браузере...")
                driver.get(BASE_URL)
                time.sleep(3)
                
                # Ищем и заполняем форму авторизации
                login_links = [
                    "//a[contains(text(), 'Вход')]",
                    "//a[contains(text(), 'Войти')]",
                    "//a[contains(text(), 'Login')]",
                    "//a[contains(@href, 'login')]",
                ]
                
                for link_selector in login_links:
                    try:
                        login_link = driver.find_element(By.XPATH, link_selector)
                        self.safe_log(f"🔗 Найдена ссылка входа: {link_selector}")
                        login_link.click()
                        time.sleep(3)
                        break
                    except:
                        continue
                
                username_selectors = ["//input[@name='login_name']", "//input[@name='username']"]
                password_selectors = ["//input[@name='login_password']", "//input[@name='password']"]
                
                username_field = None
                password_field = None
                
                for selector in username_selectors:
                    try:
                        username_field = driver.find_element(By.XPATH, selector)
                        break
                    except:
                        continue
                        
                for selector in password_selectors:
                    try:
                        password_field = driver.find_element(By.XPATH, selector)
                        break
                    except:
                        continue
                
                if username_field and password_field:
                    username_field.clear()
                    username_field.send_keys("имя")
                    time.sleep(0.5)
                    
                    password_field.clear() 
                    password_field.send_keys("пароль")
                    time.sleep(0.5)
                    
                    password_field.send_keys(Keys.RETURN)
                    time.sleep(5)
                    
                    if "peka_r" in driver.page_source.lower():
                        self.safe_log("✅ Авторизация в браузере успешна")
                    else:
                        self.safe_log("❌ Ошибка авторизации в браузере")
                        driver.quit()
                        return
                else:
                    self.safe_log("❌ Не удалось найти поля для авторизации")
                    driver.quit()
                    return

                # Теперь ищем торренты для каждой игры
                for i, game in enumerate(games):
                    game_id, title, game_url = game
                    self.update_progress(i * 100 / total, 100, f"Браузер: {title[:50]}...")
                    
                    self.safe_log(f"🌐 Переходим на страницу: {title}")
                    
                    try:
                        driver.get(game_url)
                        time.sleep(3)
                        
                        # Прокручиваем страницу чтобы все элементы загрузились
                        self.safe_log("📜 Прокручиваем страницу игры...")
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        
                        # Ищем кнопку "Скачать торрент" (игнорируем magnet-ссылки)
                        self.safe_log("🔍 Ищем кнопку 'Скачать торрент'...")
                        
                        download_button_selectors = [
                            "//a[contains(text(), 'Скачать торрент')]",
                            "//a[contains(text(), 'скачать торрент')]",
                            "//a[contains(text(), 'Download torrent')]",
                            "//a[contains(text(), 'download torrent')]",
                        ]
                        
                        download_button = None
                        for selector in download_button_selectors:
                            try:
                                elements = driver.find_elements(By.XPATH, selector)
                                for element in elements:
                                    href = element.get_attribute('href')
                                    # Игнорируем magnet-ссылки, ищем только те, что ведут на страницу загрузки
                                    if href and not href.startswith('magnet:'):
                                        download_button = element
                                        self.safe_log(f"🔗 Найдена кнопка загрузки: {selector}")
                                        break
                                if download_button:
                                    break
                            except:
                                continue
                        
                        if download_button:
                            # Кликаем на кнопку загрузки
                            self.safe_log("🖱️ Кликаем на кнопку загрузки...")
                            driver.execute_script("arguments[0].click();", download_button)
                            time.sleep(3)
                            
                            # Ждем загрузки новой страницы
                            current_url = driver.current_url
                            self.safe_log(f"📄 Перешли на страницу: {current_url}")
                            
                            # На новой странице ищем ссылку с .torrent
                            self.safe_log("🔍 Ищем .torrent ссылку на странице загрузки...")
                            
                            torrent_link = None
                            torrent_selectors = [
                                "//a[contains(@href, '.torrent')]",
                                "//a[contains(text(), '.torrent')]",
                            ]
                            
                            for selector in torrent_selectors:
                                try:
                                    elements = driver.find_elements(By.XPATH, selector)
                                    for element in elements:
                                        href = element.get_attribute('href')
                                        if href and '.torrent' in href and not href.startswith('magnet:'):
                                            torrent_link = href
                                            self.safe_log(f"🔗 Найдена .torrent ссылка: {href}")
                                            break
                                    if torrent_link:
                                        break
                                except:
                                    continue
                            
                            if torrent_link:
                                # Обрабатываем найденную .torrent ссылку
                                torrent_url, magnet, version, game_size = self.process_torrent_from_url(torrent_link, game_url, title)
                                
                                if torrent_url:
                                    self.update_game_torrent(game_id, torrent_url)
                                    self.update_game_version(game_id, version if version else "auto_selenium")
                                    if game_size:
                                        self.update_game_size(game_id, game_size)
                                    
                                    if magnet:
                                        self.update_game_magnet(game_id, magnet)
                                    
                                    self.safe_log(f"✅ Торрент найден через браузер для: {title}")
                                    successful += 1
                                else:
                                    self.safe_log(f"❌ Не удалось обработать торрент для: {title}")
                            else:
                                self.safe_log(f"❌ Не удалось найти .torrent ссылку на странице загрузки для: {title}")
                        else:
                            self.safe_log(f"❌ Не удалось найти кнопку загрузки для: {title}")
                        
                    except Exception as e:
                        self.safe_log(f"❌ Ошибка обработки игры {title}: {e}")
                        import traceback
                        self.safe_log(f"🔍 Детали ошибки: {traceback.format_exc()}")
                    
                    time.sleep(2)  # Задержка между играми
                
                driver.quit()
                
            except Exception as e:
                self.safe_log(f"❌ Ошибка в автоматическом поиске: {e}")
                if 'driver' in locals():
                    driver.quit()
            
            self.update_progress(100, 100, "Автоматический поиск завершен")
            self.load_games_from_db()
            self.safe_log(f"✅ Автоматический поиск завершен. Успешно: {successful}/{total}")
        
        threading.Thread(target=selenium_search_thread, daemon=True).start()

    def update_torrents(self):
        """Обновление торрентов (псевдоним для обратной совместимости)"""
        self.start_torrent_search()

    def rate_limited_request(self, method, *args, **kwargs):
        """Ограничение количества запросов"""
        with self.request_semaphore:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            
            if time_since_last_request < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last_request
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
            return method(*args, **kwargs)

    def safe_get(self, url, **kwargs):
        """Безопасный GET запрос с ограничением"""
        return self.rate_limited_request(self.session.get, url, **kwargs)

    def clean_game_title(self, title):
        """Очистка названия игры с сохранением специальных символов"""
        # Убираем "по сети" и другие ненужные слова
        remove_words = ['по сети', 'repack', 'steam', 'rip', 'free', 'download', 'torrent']
        
        # Сохраняем все буквы, цифры, пробелы и специальные символы: ! . - _ ( ) [ ] { }
        clean_title = re.sub(r'[^a-zA-Z0-9\s!\.\-_\(\)\[\]\{\}]', '', title)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        
        words = clean_title.split()
        filtered_words = []
        
        for word in words:
            if word.lower() not in remove_words:
                filtered_words.append(word)
        
        return ' '.join(filtered_words)

    def format_game_title_with_version(self, title, version):
        """Форматирование названия игры с версией"""
        clean_title = self.clean_game_title(title)
        
        if not version or version.lower() == 'any':
            return clean_title
        
        # Проверяем, связана ли версия с build
        if 'build' in version.lower():
            formatted_version = f"[build {version.replace('build', '').replace('Build', '').strip()}]"
        else:
            formatted_version = f"[{version}]"
        
        return f"{clean_title} {formatted_version}"

    def format_version_for_display(self, version):
        """Форматирование версии для отображения в таблице"""
        if not version:
            return ""
        
        if version.lower() == 'any':
            return "any"
        
        # Проверяем, связана ли версия с build
        if 'build' in version.lower():
            return f"build {version.replace('build', '').replace('Build', '').strip()}"
        
        return version

    def parse_size_to_bytes(self, size_str):
        """Конвертация размера в байты для правильной сортировки"""
        if not size_str or size_str == "Неизвестно" or size_str == "Ошибка":
            return 0
            
        try:
            size_str = size_str.upper().replace(' ', '')
            if 'GB' in size_str:
                return float(size_str.replace('GB', '')) * 1024 * 1024 * 1024
            elif 'MB' in size_str:
                return float(size_str.replace('MB', '')) * 1024 * 1024
            elif 'KB' in size_str:
                return float(size_str.replace('KB', '')) * 1024
            else:
                return float(size_str)
        except:
            return 0

    def generate_torrent_filename(self, clean_title, version, file_type="standard"):
        """Генерация имени файла торрента с правильным форматированием"""
        # Заменяем пробелы на точки для имени файла, но сохраняем специальные символы
        filename_title = clean_title.replace(' ', '.')
        
        # Убираем лишние точки (но сохраняем точки в аббревиатурах типа S.P.A.T.)
        filename_title = re.sub(r'\.{2,}', '.', filename_title)
        
        if file_type == "any":
            return f"{filename_title}-OFME.torrent"
        elif file_type == "dedicated_server":
            return f"{filename_title}.Dedicated.Server.v{version}-OFME.torrent"
        elif file_type == "build":
            return f"{filename_title}.Build.{version}-OFME.torrent"
        else:
            return f"{filename_title}.v{version}-OFME.torrent"

    def generate_torrent_url(self, clean_title, filename):
        """Генерация URL торрента с правильным кодированием"""
        # URL-кодируем название для пути, сохраняя специальные символы
        url_title = quote(clean_title)
        
        # Формируем полный URL
        torrent_url = f"https://uploads.online-fix.me:2053/torrents/{url_title}/{filename}"
        return torrent_url

    def extract_game_size(self, torrent_content):
        """Извлечение размера игры из торрент-файла"""
        try:
            torrent_dict = bencodepy.decode(torrent_content)
            info = torrent_dict.get(b'info', {})
            
            total_size = 0
            
            # Проверяем структуру торрента
            if b'files' in info:
                # Мультифайловый торрент
                for file_info in info[b'files']:
                    total_size += file_info.get(b'length', 0)
            else:
                # Однофайловый торрент
                total_size = info.get(b'length', 0)
            
            # Конвертируем в читаемый формат
            if total_size > 0:
                if total_size >= 1024**3:  # GB
                    size_str = f"{total_size / (1024**3):.2f} GB"
                elif total_size >= 1024**2:  # MB
                    size_str = f"{total_size / (1024**2):.2f} MB"
                else:
                    size_str = f"{total_size / 1024:.2f} KB"
                
                self.safe_log(f"💾 Размер из торрента: {size_str}")
                return size_str
            
            return "Неизвестно"
        except Exception as e:
            self.safe_log(f"❌ Ошибка извлечения размера из торрента: {e}")
            return "Ошибка"

    def extract_game_version(self, soup):
        """Извлечение версии игры"""
        try:
            page_text = soup.get_text()
            
            # Паттерны для поиска версии
            version_patterns = [
                (r'Версия игры:\s*v?(\d+(?:\.\d+)*(?:[a-z]\d*)?)', "Версия игры"),
                (r'Версия игры:\s*(any)', "Any версия"),
                (r'Build[:\s]+(\d+(?:\.\d+)*)', "Build"),
                (r'Version[:\s]+v?(\d+(?:\.\d+)*(?:[a-z]\d*)?)', "Version"),
            ]
            
            for pattern, pattern_name in version_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    version = match.group(1).strip()
                    if version.lower() == 'any' or '.' in version or len(version) >= 2:
                        self.safe_log(f"📋 Найдена версия ({pattern_name}): {version}")
                        return version
            
            self.safe_log("⚠️ Версия игры не найдена на странице")
            return None
                
        except Exception as e:
            self.safe_log(f"❌ Ошибка извлечения версии: {e}")
            return None

    def clean_magnet_url(self, magnet_url):
        """Очистка magnet-ссылки до основной части"""
        if magnet_url and magnet_url.startswith('magnet:'):
            # Оставляем только часть до &dn= (основная информация о хэше)
            parts = magnet_url.split('&', 1)
            if len(parts) > 0:
                return parts[0]  # magnet:?xt=urn:btih:96860667290a5950c7881ae81648ecd33f2edd5c
        return magnet_url

    def torrent_content_to_magnet(self, torrent_content):
        """Конвертация в магнет (упрощенная версия)"""
        try:
            torrent_dict = bencodepy.decode(torrent_content)
            info = torrent_dict[b'info']
            info_encoded = bencodepy.encode(info)
            
            info_hash = hashlib.sha1(info_encoded).hexdigest()
            
            # Только основная часть magnet-ссылки
            magnet = f"magnet:?xt=urn:btih:{info_hash}"
            
            return magnet
            
        except Exception as e:
            self.safe_log(f"❌ Ошибка создания магнета: {e}")
            return None

    def generate_torrent_and_magnet(self, game_url, game_title, manual_version=None):
        """Генерация торрента и магнета с правильным форматированием названий"""
        try:
            self.safe_log(f"🔍 Генерируем торрент для: {game_title}")
            
            response = self.safe_get(game_url)
            if response.status_code != 200:
                self.safe_log(f"❌ Ошибка загрузки страницы: {response.status_code}")
                return None, None, None, None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if manual_version:
                version = manual_version
                self.safe_log(f"📋 Используем ручную версию: {version}")
            else:
                version = self.extract_game_version(soup)
                if not version:
                    self.safe_log("❌ Не удалось извлечь версию игры")
                    return None, None, None, None
            
            # Очищаем название с сохранением специальных символов
            clean_title = self.clean_game_title(game_title)
            self.safe_log(f"🔧 Очищенное название: {clean_title}")
            
            # Обработка версии "any"
            if version.lower() == 'any':
                attempts = [
                    {"type": "любая версия", "file_type": "any"},
                ]
            else:
                attempts = [
                    {"type": "стандартный", "file_type": "standard"},
                    {"type": "с Dedicated Server", "file_type": "dedicated_server"},
                    {"type": "с Build", "file_type": "build"},
                ]
            
            for attempt in attempts:
                self.safe_log(f"🔄 Попытка {attempt['type']}...")
                
                # Генерируем имя файла с правильным форматированием
                filename = self.generate_torrent_filename(clean_title, version, attempt['file_type'])
                
                # Генерируем URL с правильным кодированием
                torrent_url = self.generate_torrent_url(clean_title, filename)
                
                self.safe_log(f"🔗 Сгенерирован URL: {torrent_url}")
                
                headers = {
                    'Referer': game_url,
                    'User-Agent': self.config['user_agent']
                }
                
                torrent_response = self.safe_get(torrent_url, headers=headers, timeout=30)
                
                if torrent_response.status_code == 200:
                    content = torrent_response.content
                    if content.startswith(b'd8:announce') or len(content) > 100:
                        # Извлекаем размер из торрента
                        game_size = self.extract_game_size(content)
                        magnet = self.torrent_content_to_magnet(content)
                        if magnet:
                            self.safe_log(f"✅ Торрент найден ({attempt['type']}) и преобразован в магнет")
                            return torrent_url, magnet, version, game_size
                        else:
                            self.safe_log(f"❌ Не удалось создать магнет-ссылку для {attempt['type']}")
                            return torrent_url, None, version, game_size
            
            self.safe_log("❌ Все попытки скачать торрент провалились")
            return None, None, version, None
                
        except Exception as e:
            self.safe_log(f"❌ Ошибка генерации торрента: {e}")
            return None, None, None, None

    def process_torrent_from_url(self, torrent_url, game_url, game_title):
        """Обработка торрента по прямой ссылке"""
        try:
            self.safe_log(f"🔗 Обрабатываем торрент по ссылке: {torrent_url}")
            
            headers = {
                'Referer': game_url,
                'User-Agent': self.config['user_agent']
            }
            
            torrent_response = self.safe_get(torrent_url, headers=headers, timeout=30)
            
            if torrent_response.status_code == 200:
                content = torrent_response.content
                if content.startswith(b'd8:announce') or len(content) > 100:
                    # Извлекаем размер из торрента
                    game_size = self.extract_game_size(content)
                    magnet = self.torrent_content_to_magnet(content)
                    
                    if magnet:
                        self.safe_log("✅ Торрент обработан и преобразован в магнет")
                        return torrent_url, magnet, "manual", game_size
                    else:
                        self.safe_log("❌ Не удалось создать магнет-ссылку")
                        return torrent_url, None, "manual", game_size
                else:
                    self.safe_log("❌ Получен некорректный торрент-файл")
                    return None, None, None, None
            else:
                self.safe_log(f"❌ Ошибка загрузки торрента: {torrent_response.status_code}")
                return None, None, None, None
                
        except Exception as e:
            self.safe_log(f"❌ Ошибка обработки торрента: {e}")
            return None, None, None, None

    def start_game_search(self):
        """Поиск игр"""
        if not self.logged_in:
            messagebox.showwarning("Ошибка", "Сначала выполните авторизацию!")
            return
        
        def search_thread():
            try:
                start_page = int(self.start_page_var.get())
                end_page = int(self.end_page_var.get())
                
                if start_page > end_page:
                    messagebox.showerror("Ошибка", "Начальная страница не может быть больше конечной")
                    return
                
                if start_page < 1 or start_page > 82 or end_page < 1 or end_page > 82:
                    messagebox.showerror("Ошибка", "Номер страницы должен быть от 1 до 82")
                    return
                
                self.safe_log(f"🎮 Ищем игры на страницах {start_page}-{end_page}...")
                
                all_games = []
                total_pages = end_page - start_page + 1
                games_found = 0
                
                for page_num in range(start_page, end_page + 1):
                    self.safe_log(f"📄 Обрабатываем страницу {page_num}/{end_page}...")
                    self.update_progress((page_num - start_page) * 100 / total_pages, 100, f"Страница {page_num}/{end_page}...")
                    
                    if page_num == 1:
                        url = BASE_URL
                    else:
                        url = f"{BASE_URL}/page/{page_num}/"
                    
                    try:
                        response = self.safe_get(url, timeout=30)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            articles = soup.find_all('article', class_='news')
                            
                            page_games = 0
                            for article in articles:
                                try:
                                    title_elem = article.find('h2', class_='title')
                                    link_elem = article.find('a', class_='big-link')
                                    
                                    if title_elem and link_elem:
                                        title = title_elem.get_text(strip=True)
                                        game_url = urljoin(BASE_URL, link_elem.get('href'))
                                        
                                        if '/games/' in game_url:
                                            game_data = {
                                                'title': title,
                                                'url': game_url,
                                                'page': page_num,
                                                'status': 'Найдена'
                                            }
                                            all_games.append(game_data)
                                            games_found += 1
                                            page_games += 1
                                            
                                            if games_found >= self.max_games:
                                                self.safe_log(f"🔧 Достигнут лимит в {self.max_games} игр")
                                                break
                                except Exception as e:
                                    self.safe_log(f"⚠️ Ошибка обработки статьи: {e}")
                                    continue
                            
                            self.safe_log(f"✅ На странице {page_num} найдено {page_games} игр (всего: {games_found})")
                            
                            if games_found >= self.max_games:
                                break
                                
                        else:
                            self.safe_log(f"❌ Ошибка загрузки страницы {page_num}: {response.status_code}")
                    except Exception as e:
                        self.safe_log(f"❌ Ошибка обработки страницы {page_num}: {e}")
                    
                    time.sleep(1)
                
                if all_games:
                    self.save_games_to_db(all_games)
                    self.load_games_from_db()
                    self.safe_log(f"✅ Всего найдено {len(all_games)} игр на {total_pages} страницах")
                else:
                    self.safe_log("❌ Игры не найдены на указанных страницах")
                
                self.update_progress(100, 100, "Поиск завершен")
                
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный номер страницы")
            except Exception as e:
                self.safe_log(f"❌ Ошибка поиска игр: {e}")
                traceback.print_exc()
        
        threading.Thread(target=search_thread, daemon=True).start()

    def save_games_to_db(self, games):
        """Сохранение игр в БД без дубликатов"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                saved_count = 0
                skipped_count = 0
                
                for game in games:
                    cursor.execute("SELECT id FROM games WHERE url = ?", (game['url'],))
                    existing = cursor.fetchone()
                    
                    if not existing:
                        cursor.execute('''
                            INSERT INTO games (title, url, page, status)
                            VALUES (?, ?, ?, ?)
                        ''', (game['title'], game['url'], game['page'], game['status']))
                        saved_count += 1
                    else:
                        skipped_count += 1
                
                conn.commit()
                self.safe_log(f"💾 Сохранено {saved_count} новых игр, пропущено дубликатов: {skipped_count}")
        except Exception as e:
            logging.error(f"Ошибка сохранения в БД: {e}")
            self.safe_log(f"❌ Ошибка сохранения в БД: {e}")

    def load_games_from_db(self, sort_type="id"):
        """Загрузка игр из БД с сортировкой"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Определяем порядок сортировки
                if sort_type == "id":
                    order_by = "id ASC"
                elif sort_type == "title_asc":
                    order_by = "title ASC"
                elif sort_type == "title_desc":
                    order_by = "title DESC"
                elif sort_type == "size":
                    # Старая сортировка по тексту (неправильная)
                    order_by = "file_size DESC"
                elif sort_type == "size_correct":
                    # Новая правильная сортировка по размеру в байтах
                    order_by = """
                        CASE 
                            WHEN file_size LIKE '%GB%' THEN CAST(REPLACE(file_size, ' GB', '') AS REAL) * 1073741824
                            WHEN file_size LIKE '%MB%' THEN CAST(REPLACE(file_size, ' MB', '') AS REAL) * 1048576
                            WHEN file_size LIKE '%KB%' THEN CAST(REPLACE(file_size, ' KB', '') AS REAL) * 1024
                            ELSE 0
                        END DESC
                    """
                elif sort_type == "any_version":
                    order_by = "CASE WHEN version = 'any' THEN 0 ELSE 1 END, id ASC"
                elif sort_type == "no_torrents":
                    order_by = "CASE WHEN torrent_url IS NULL THEN 0 ELSE 1 END, id ASC"
                else:
                    order_by = "id ASC"
                
                cursor.execute(f"SELECT id, title, version, torrent_url, magnet_url, file_size, status, updated_at FROM games ORDER BY {order_by}")
                rows = cursor.fetchall()
                
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                self.safe_log(f"📊 Загружено {len(rows)} игр из БД (сортировка: {sort_type})")
                
                for row in rows:
                    row_values = list(row)
                    
                    # Форматируем версию для отображения
                    if row_values[2]:
                        row_values[2] = self.format_version_for_display(row_values[2])
                    
                    # Форматируем название с версией для экспорта
                    formatted_title = self.format_game_title_with_version(row_values[1], row_values[2])
                    row_values[1] = formatted_title
                    
                    self.tree.insert("", tk.END, values=row_values)
                
                self.update_stats()
                
        except Exception as e:
            logging.error(f"Ошибка загрузки из БД: {e}")
            self.safe_log(f"❌ Ошибка загрузки из БД: {e}")

    def update_stats(self):
        """Обновление статистики"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM games")
                total_games = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM games WHERE torrent_url IS NOT NULL")
                with_torrents = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM games WHERE magnet_url IS NOT NULL")
                with_magnets = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM games WHERE status LIKE '%Ошибка%'")
                errors = cursor.fetchone()[0]
            
            if hasattr(self, 'total_games_var'):
                self.total_games_var.set(str(total_games))
            if hasattr(self, 'with_torrents_var'):
                self.with_torrents_var.set(str(with_torrents))
            if hasattr(self, 'with_magnets_var'):
                self.with_magnets_var.set(str(with_magnets))
            if hasattr(self, 'errors_var'):
                self.errors_var.set(str(errors))
        except Exception as e:
            logging.error(f"Ошибка обновления статистики: {e}")

    def safe_log(self, message):
        """Безопасное логирование с умным автоскроллом"""
        clean_message = re.sub(r'[^\w\s\-_.,!?@#$%^&*()+=:;\"\'<>/\\|]', '', message)
        logging.info(clean_message)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        def update_log():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, formatted_message + "\n")
            
            # Автоскролл только если пользователь не прокрутил вверх
            if not self.user_scrolled_up:
                self.log_text.see(tk.END)
            
            self.log_text.config(state=tk.DISABLED)
            self.status_var.set(message)
        
        self.root.after(0, update_log)

    def update_progress(self, current, total, message):
        """Обновление прогресса"""
        progress = min(current, 100)
        
        def update():
            self.progress_var.set(progress)
            self.progress_label.config(text=f"{progress:.1f}%")
            self.status_var.set(message)
        
        self.root.after(0, update)

    def process_single_torrent(self, game):
        """Обработка одной игры для поиска торрента"""
        game_id, title, game_url = game
        try:
            torrent_url, magnet, version, game_size = self.generate_torrent_and_magnet(game_url, title)
            
            if torrent_url:
                self.update_game_torrent(game_id, torrent_url)
                if version:
                    self.update_game_version(game_id, version)
                if game_size:
                    self.update_game_size(game_id, game_size)
                
                if magnet:
                    self.update_game_magnet(game_id, magnet)
                
                return (True, title, "Успешно")
            else:
                # Если версия найдена, но торрент нет - сохраняем версию
                if version:
                    self.update_game_version(game_id, version)
                    self.update_game_status(game_id, "Версия найдена, торрент отсутствует")
                    return (False, title, "Версия найдена, торрент отсутствует")
                else:
                    self.update_game_status(game_id, "Торрент не найден")
                    return (False, title, "Торрент не найден")
        except Exception as e:
            self.update_game_status(game_id, f"Ошибка: {str(e)}")
            return (False, title, f"Ошибка: {str(e)}")

    def start_torrent_search(self):
        """Поиск торрентов для ВСЕХ игр"""
        if not self.logged_in:
            messagebox.showwarning("Ошибка", "Сначала выполните авторизацию!")
            return
        
        def search_thread():
            self.safe_log("📥 Начинаем параллельный поиск торрентов...")
            
            games = self.get_games_without_torrents()
            
            if not games:
                self.safe_log("ℹ️ Все игры уже имеют торренты")
                return
            
            self.safe_log(f"🔍 Обрабатываем {len(games)} игр параллельно...")
            
            total = len(games)
            successful = 0
            processed = 0
            
            max_workers = min(5, int(self.requests_per_second_var.get()))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_game = {executor.submit(self.process_single_torrent, game): game for game in games}
                
                for future in as_completed(future_to_game):
                    game = future_to_game[future]
                    processed += 1
                    
                    try:
                        success, title, message = future.result()
                        if success:
                            self.safe_log(f"✅ [{processed}/{total}] {title[:50]}")
                            successful += 1
                        else:
                            self.safe_log(f"❌ [{processed}/{total}] {title[:50]}: {message}")
                    except Exception as e:
                        self.safe_log(f"❌ [{processed}/{total}] Ошибка: {e}")
                    
                    self.update_progress(processed * 100 / total, 100, f"Обработано: {processed}/{total}")
            
            self.update_progress(100, 100, "Поиск завершен")
            self.load_games_from_db()
            self.safe_log(f"✅ Поиск торрентов завершен. Успешно: {successful}/{total}")
        
        threading.Thread(target=search_thread, daemon=True).start()

    def start_magnet_creation(self):
        """Создание магнетов для ВСЕХ игр с торрентами"""
        if not self.logged_in:
            messagebox.showwarning("Ошибка", "Сначала выполните авторизацию!")
            return
        
        def magnet_thread():
            self.safe_log("🧲 Начинаем создание магнет-ссылок...")
            
            games = self.get_games_with_torrents()
            
            if not games:
                self.safe_log("ℹ️ Нет игр с торрентами для обработки")
                return
            
            self.safe_log(f"🔧 Обрабатываем {len(games)} торрентов...")
            
            total = len(games)
            successful = 0
            
            for i, game in enumerate(games):
                game_id, title, game_url, torrent_url = game
                self.update_progress(i * 100 / total, 100, f"Создание магнета: {title[:50]}...")
                
                if torrent_url:
                    headers = {
                        'Referer': game_url,
                        'User-Agent': self.config['user_agent']
                    }
                    
                    try:
                        torrent_response = self.safe_get(torrent_url, headers=headers, timeout=30)
                        if torrent_response.status_code == 200:
                            magnet = self.torrent_content_to_magnet(torrent_response.content)
                            if magnet:
                                self.update_game_magnet(game_id, magnet)
                                self.safe_log(f"✅ Создан магнет для: {title}")
                                successful += 1
                            else:
                                self.safe_log(f"❌ Ошибка создания магнета для: {title}")
                        else:
                            self.safe_log(f"❌ Ошибка загрузки торрента: {torrent_response.status_code}")
                    except Exception as e:
                        self.safe_log(f"❌ Ошибка при создании магнета: {e}")
                
                time.sleep(self.min_request_interval)
            
            self.update_progress(100, 100, "Создание магнетов завершено")
            self.load_games_from_db()
            self.safe_log(f"✅ Создание магнет-ссылок завершено. Успешно: {successful}/{total}")
        
        threading.Thread(target=magnet_thread, daemon=True).start()

    def manual_version_input(self):
        """Ручной ввод версии"""
        if not self.logged_in:
            messagebox.showwarning("Ошибка", "Сначала выполните авторизацию!")
            return
        
        def input_thread():
            games = self.get_games_without_torrents()
            
            if not games:
                self.safe_log("ℹ️ Нет игр без торрентов для обработки")
                return
            
            self.safe_log(f"✏️ Ручной ввод версии для {len(games)} игр...")
            
            for i, game in enumerate(games):
                game_id, title, game_url = game
                self.update_progress(i * 100 / len(games), 100, f"Ручной ввод: {title[:50]}...")
                
                version = simpledialog.askstring(
                    "Ручной ввод версии", 
                    f"Введите версию для игры:\n{title}",
                    parent=self.root
                )
                
                if version:
                    self.safe_log(f"✏️ Ручная версия для {title}: {version}")
                    
                    torrent_url, magnet, _, game_size = self.generate_torrent_and_magnet(game_url, title, version)
                    
                    if torrent_url:
                        self.update_game_torrent(game_id, torrent_url)
                        self.update_game_version(game_id, version)
                        if game_size:
                            self.update_game_size(game_id, game_size)
                        self.safe_log(f"✅ Торрент найден с ручной версией для: {title}")
                        
                        if magnet:
                            self.update_game_magnet(game_id, magnet)
                            self.safe_log(f"✅ Создан магнет для: {title}")
                    else:
                        self.safe_log(f"❌ Не удалось найти торрент с ручной версией для: {title}")
                else:
                    self.safe_log(f"⏭️ Пропущена игра: {title}")
                    break
            
            self.update_progress(100, 100, "Ручной ввод завершен")
            self.load_games_from_db()
            self.safe_log("✅ Ручной ввод версий завершен")
        
        threading.Thread(target=input_thread, daemon=True).start()

    def manual_torrent_input(self):
        """Ручной ввод ссылки на торрент"""
        if not self.logged_in:
            messagebox.showwarning("Ошибка", "Сначала выполните авторизацию!")
            return
        
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите игру из списка!")
            return
        
        item = self.tree.item(selected[0])
        game_id = item['values'][0]
        title = item['values'][1]
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM games WHERE id = ?", (game_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Ошибка", "Не удалось найти URL игры")
                return
            game_url = result[0]
        
        torrent_url = simpledialog.askstring(
            "Ручной ввод торрента", 
            f"Введите прямую ссылку на торрент для игры:\n{title}",
            parent=self.root
        )
        
        if torrent_url:
            self.safe_log(f"🔗 Ручная ссылка на торрент для {title}: {torrent_url}")
            
            torrent_url, magnet, version, game_size = self.process_torrent_from_url(torrent_url, game_url, title)
            
            if torrent_url:
                self.update_game_torrent(game_id, torrent_url)
                self.update_game_version(game_id, version if version else "manual")
                if game_size:
                    self.update_game_size(game_id, game_size)
                self.safe_log(f"✅ Торрент обработан для: {title}")
                
                if magnet:
                    self.update_game_magnet(game_id, magnet)
                    self.safe_log(f"✅ Создан магнет для: {title}")
                
                self.load_games_from_db()
            else:
                self.safe_log(f"❌ Не удалось обработать торрент для: {title}")

    def manual_version_for_selected(self):
        """Ручной ввод версии для выбранной игры"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите игру из списка!")
            return
        
        item = self.tree.item(selected[0])
        game_id = item['values'][0]
        title = item['values'][1]
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM games WHERE id = ?", (game_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Ошибка", "Не удалось найти URL игры")
                return
            game_url = result[0]
        
        version = simpledialog.askstring(
            "Ручной ввод версии", 
            f"Введите версию для игры:\n{title}",
            parent=self.root
        )
        
        if version:
            self.safe_log(f"✏️ Ручная версия для {title}: {version}")
            
            torrent_url, magnet, _, game_size = self.generate_torrent_and_magnet(game_url, title, version)
            
            if torrent_url:
                self.update_game_torrent(game_id, torrent_url)
                self.update_game_version(game_id, version)
                if game_size:
                    self.update_game_size(game_id, game_size)
                self.safe_log(f"✅ Торрент найден с ручной версией для: {title}")
                
                if magnet:
                    self.update_game_magnet(game_id, magnet)
                    self.safe_log(f"✅ Создан магнет для: {title}")
                
                self.load_games_from_db()
            else:
                self.safe_log(f"❌ Не удалось найти торрент с ручной версией для: {title}")

    def get_game_version(self, game_id):
        """Получение версии игры из БД"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM games WHERE id = ?", (game_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def update_game_version(self, game_id, version):
        """Обновление версии игры в БД"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE games SET version = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (version, game_id)
                )
                conn.commit()
        except sqlite3.OperationalError as e:
            self.safe_log(f"❌ Ошибка обновления версии: {e}")

    def update_game_size(self, game_id, size):
        """Обновление размера игры в БД"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE games SET file_size = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (size, game_id)
                )
                conn.commit()
        except sqlite3.OperationalError as e:
            self.safe_log(f"❌ Ошибка обновления размера: {e}")

    def get_all_games_with_torrents(self):
        """Получение всех игр с торрентами"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, url, torrent_url FROM games WHERE torrent_url IS NOT NULL ORDER BY id ASC")
            return cursor.fetchall()

    def get_games_without_torrents(self):
        """Получение игр без торрентов"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, url FROM games WHERE torrent_url IS NULL ORDER BY id ASC")
            return cursor.fetchall()

    def get_games_with_torrents(self):
        """Получение игр с торрентами но без магнетов"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, url, torrent_url FROM games WHERE torrent_url IS NOT NULL AND magnet_url IS NULL ORDER BY id ASC")
            return cursor.fetchall()

    def update_game_torrent(self, game_id, torrent_url):
        """Обновление торрента для игры"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE games SET torrent_url = ?, status = 'Торрент найден', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (torrent_url, game_id)
            )
            conn.commit()

    def update_game_magnet(self, game_id, magnet_url):
        """Обновление магнета для игры (с очисткой)"""
        clean_magnet = self.clean_magnet_url(magnet_url)
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE games SET magnet_url = ?, status = 'Готово', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (clean_magnet, game_id)
            )
            conn.commit()

    def update_game_status(self, game_id, status):
        """Обновление статуса игры"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE games SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, game_id)
            )
            conn.commit()

    def export_json(self):
        """Экспорт в JSON с очищенными magnet-ссылками и форматированными названиями"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT title, version, magnet_url, file_size, created_at FROM games WHERE magnet_url IS NOT NULL ORDER BY id ASC")
                games = cursor.fetchall()
                
                export_data = {
                    "name": "PEKAR.fix Games Collection",
                    "downloads": []
                }
                
                for game in games:
                    original_title, version, magnet_url, file_size, created_at = game
                    
                    # Форматируем название с версией
                    formatted_title = self.format_game_title_with_version(original_title, version)
                    
                    # Очищаем magnet-ссылку
                    clean_magnet = self.clean_magnet_url(magnet_url)
                    
                    if created_at:
                        upload_date = created_at.replace(' ', 'T') + '.000Z'
                    else:
                        upload_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
                    
                    if not file_size:
                        file_size = "Unknown"
                    
                    download_item = {
                        "title": formatted_title,
                        "uris": [clean_magnet],
                        "fileSize": file_size,
                        "uploadDate": upload_date
                    }
                    export_data["downloads"].append(download_item)
                
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json")]
                )
                
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                    self.safe_log(f"✅ Данные экспортированы в: {filename}")
                    
        except Exception as e:
            self.safe_log(f"❌ Ошибка экспорта JSON: {e}")

    def export_csv(self):
        """Экспорт в CSV с форматированными названиями"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT title, version, magnet_url, file_size, status FROM games WHERE magnet_url IS NOT NULL ORDER BY id ASC")
                games = cursor.fetchall()
                
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv")]
                )
                
                if filename:
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Название', 'Magnet-ссылка', 'Размер', 'Статус', 'Версия'])
                        
                        for game in games:
                            original_title, version, magnet_url, file_size, status = game
                            formatted_title = self.format_game_title_with_version(original_title, version)
                            writer.writerow([formatted_title, magnet_url, file_size, status, version])
                    
                    self.safe_log(f"✅ Данные экспортированы в: {filename}")
                    
        except Exception as e:
            self.safe_log(f"❌ Ошибка экспорта CSV: {e}")

    def copy_game_name(self):
        """Копировать название игры"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.root.clipboard_clear()
            self.root.clipboard_append(item['values'][1])
            self.safe_log("📋 Название скопировано")

    def copy_game_url(self):
        """Копировать URL игры"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            game_id = item['values'][0]
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT url FROM games WHERE id = ?", (game_id,))
                result = cursor.fetchone()
                if result:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(result[0])
                    self.safe_log("🔗 URL скопирован")

    def copy_magnet(self):
        """Копировать магнет-ссылку"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            if len(item['values']) > 3:
                magnet = item['values'][3]
                if magnet and magnet.startswith('magnet:'):
                    self.root.clipboard_clear()
                    self.root.clipboard_append(magnet)
                    self.safe_log("🧲 Magnet-ссылка скопирована")
                else:
                    self.safe_log("❌ Magnet-ссылка не найдена")
            else:
                self.safe_log("❌ Magnet-ссылка не найдена")

    def refresh_game(self):
        """Обновить игру"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.safe_log(f"🔄 Обновляем игру: {item['values'][1]}")

    def delete_game(self):
        """Удалить игру"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            game_id = item['values'][0]
            
            if messagebox.askyesno("Подтверждение", f"Удалить игру '{item['values'][1]}'?"):
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
                    conn.commit()
                
                self.load_games_from_db()
                self.safe_log("🗑️ Игра удалена")

def main():
    root = tk.Tk()
    app = ModernGameParser(root)
    root.mainloop()

if __name__ == "__main__":
    main()

