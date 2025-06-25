

import customtkinter as ctk
from tkinter import filedialog, TclError
import time
import pyautogui
import random
from pynput.keyboard import Listener as KeyboardListener, Key
import threading
import json
import sys
import os
import string
import asyncio

# Try to import Discord.py
try:
    import discord
except ImportError:
    discord = None

# Try to import Google AI and Pillow
try:
    import google.generativeai as genai
    from PIL import Image
except ImportError:
    genai = None
    Image = None

# Try to import Windows-specific libraries for capture protection
try:
    import ctypes
    from ctypes import wintypes
    IS_WINDOWS = sys.platform == 'win32'
except ImportError:
    IS_WINDOWS = False

# --- Configuration ---
START_STOP_KEY = Key.f2
HIDE_SHOW_KEY = Key.f6
EXIT_KEY = Key.f8
SETTINGS_FILE = "settings.json"

class ProdigySuiteApp(ctk.CTk):
    # --- MASSIVELY EXPANDED VOCABULARY ---
    # De-duplicated using list(set(...)) to ensure no repeated source words
    START_PHRASES = list(set([
        "HEY", "LISTEN UP", "LOOK HERE", "OI", "YOU THINK YOU'RE TOUGH", "GUESS WHAT", "NEWSFLASH", "PAY ATTENTION", 
        "GET A LOAD OF THIS", "REAL TALK", "CHECK THIS SHIT", "YO", "ATTENTION", "YOU GOT SOMETHING TO SAY?", "LOOK AT ME",
        "COME HERE", "SQUARE UP", "YOU'RE JOKING", "NO SHOT", "DEADASS", "I'M NOT GONNA SUGARCOAT IT"
    ]))
    END_PHRASES = list(set([
        "NOW CRY", "GET GUD", "LMAO", "EZ", "KYS", "DEAL WITH IT", "LOSER", "TAKE THE L", "UR WEAK AS FUCK", "MY BITCH",
        "A FUCKING LOSER", "SO ASS", "DEADASS UR ASS", "BITCHMADE", "SCARED ASS NIGGA", "UR MY PAWN", "GET SHIT ON",
        "U GOT HOED", "UR NOT RELEVANT", "CRY ABOUT IT", "STAY MAD", "RATIO", "SIT DOWN", "GOML", "GG", "EZ CLAP",
        "PACK WATCH", "RIP BOZO", "HOLD THIS L", "SKILL ISSUE", "GET BETTER", "YOU'RE FREE"
    ]))
    BASE_ADJECTIVES = list(set([
        "UGLY", "WEAK", "SLOW", "FUCKING", "STUPID", "RETARDED", "INFURIATED", "ANGRY", "TRASH", "WORTHLESS",
        "PATHETIC", "DOGSHIT", "ASS", "LAME", "CLUELESS", "BRAINDEAD", "PATHETIC", "NASTY", "SHITTY", "UGLY",
        "WEAK", "STUPID", "FILTHY", "BORING", "CRIPPLED", "CROSS EYED", "GREASY", "BROKE", "HOMELESS", "PISSY",
        "SCARED", "CRACKED", "LIMP", "DUSTY", "MUSTY", "RUSTY", "INBRED", "MALNOURISHED", "OBESE"
    ]))
    BASE_NOUNS = list(set([
        "WHORE", "SLUT", "BITCH", "GARBAGE", "DIMWIT", "RETARD", "FAGGOT", "NIGGA", "PUSSY", "SOYBOY", "INCEL", "PEDOPHILE",
        "QUEER", "MONGREL", "DYKE", "BASTARD", "MORON", "ASSHOLE", "CUNT", "FUCKFACE", "PEASANT", "SHITCAN", "LOSER", "NIGGER",
        "DUMBASS", "CLOWN", "PEDO", "MUTT", "GEEK", "SHITTER", "PAWN", "JIT", "NPC", "PLEB", "SCRUB", "DORK", "TARD",
        "PISSBAG", "CUMSLUT", "DOG FUCKER", "TRICK", "HOE"
    ]))
    ACTION_PHRASES = list(set([
        "CRY NOW", "KYS", "SHUT UP", "GET A LIFE", "GO TOUCH GRASS", "LOG OFF", "JUMP OFF A BRIDGE", "SHOOT URSELF",
        "SHUT THE FUCK UP", "ILL SNAP UR NECK", "GET OUT FROM MY CHAT", "DIE TO UR FUCKING LORD", "I OWN YOUR ENTIRE BLOODLINE",
        "FOCUS UP", "ILL RIP UR EAR OFF", "END URSELF", "ILL CHEW UR EYEBALLS OUT", "U SMELL LIKE SHIT", "IM FLAMING YOU",
        "U GOT CUCKED", "UR MOTHER IS POOR", "ILL RIP UR LUNGS OUT", "I ENSLAVED UR ANCESTORS"
    ]))
    BASE_VERBS = list(set([
        "SMACK", "CRUSH", "DOMINATE", "ROAST", "OUTLAST", "BITCH", "STOMP", "GUT", "HUMILIATE", "DESTROY", "FLAME",
        "OWN", "DEMOLISH", "PACK", "SMOKE", "SLAM", "DRAG", "FARM"
    ]))
    LOCATIONS = list(set([
        "IN THE DIRT", "UNDER MY BOOT", "ACROSS THE WASTELAND", "NEAR THE DUMPSTER", "BEHIND THE SHED", "ON THE BATHROOM FLOOR",
        "IN THE GAS CHAMBER", "UNDER THIS THING", "IN THE LOBBY", "BACK TO THE KITCHEN", "IN THE MUD", "IN THE GUTTER"
    ]))
    
    def __init__(self):
        super().__init__()
        if not discord:
            self.title("ERROR")
            ctk.CTkLabel(self, text="Discord.py library not found!\nPlease run 'pip install discord.py' in your terminal.", font=("", 16)).pack(pady=20, padx=20)
            return
        self.messages, self.macro_active, self.ar_bot_running, self.gc_bot_running, self.stop_program = [], False, False, False, False
        
        # AI state variables
        self.ai_model = None
        self.ai_chat = None
        self.attached_image_path = None
        
        self.settings = self.load_settings()
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.start_key_listener()

    def setup_ui(self):
        self.title("Prodigy's Suite")
        self.geometry("600x650"); self.resizable(False, False); ctk.set_appearance_mode("Dark")
        self.configure(fg_color="#0D0D0D"); self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Prodigy's Suite", font=ctk.CTkFont(size=24, weight="bold"), text_color="#00FF7F").grid(row=0, column=0, padx=20, pady=(15, 10))
        self.tab_view = ctk.CTkTabview(self, anchor="w", fg_color="#0D0D0D", border_color="#00FF7F", text_color="#00FF7F",
                                       segmented_button_selected_color="#1A1A1A", segmented_button_selected_hover_color="#2E2E2E")
        self.tab_view.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.tab_view.add("Auto Typer"); self.tab_view.add("AR"); self.tab_view.add("GC Changer"); self.tab_view.add("WordList Gen"); self.tab_view.add("AI Chat")
        self.tab_view.set("Auto Typer")
        self.create_auto_typer_tab(self.tab_view.tab("Auto Typer"))
        self.create_ar_tab(self.tab_view.tab("AR"))
        self.create_gc_changer_tab(self.tab_view.tab("GC Changer"))
        self.create_generator_tab(self.tab_view.tab("WordList Gen"))
        self.create_ai_chat_tab(self.tab_view.tab("AI Chat"))
        self.status_label = ctk.CTkLabel(self, text="Status: Idle.", font=ctk.CTkFont(size=12), text_color="#00FF7F")
        self.status_label.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="w")
        
    def create_auto_typer_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1); s = self.settings
        load_file_button = ctk.CTkButton(tab, text="Load Text File (.txt)", command=self.load_file_from_dialog); load_file_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.file_label = ctk.CTkLabel(tab, text="File: None loaded", wraplength=400); self.file_label.grid(row=1, column=0, padx=10, pady=(0, 10))
        self.wpm_label = ctk.CTkLabel(tab, text=f"Typing Speed (WPM): {s['wpm']}"); self.wpm_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.wpm_slider = ctk.CTkSlider(tab, from_=50, to=1000, number_of_steps=95, command=self.update_wpm_label); self.wpm_slider.set(s['wpm']); self.wpm_slider.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.delay_label = ctk.CTkLabel(tab, text=f"Delay Between Messages (ms): {s['delay_ms']}"); self.delay_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.delay_slider = ctk.CTkSlider(tab, from_=100, to=5000, number_of_steps=49, command=self.update_delay_label); self.delay_slider.set(s['delay_ms']); self.delay_slider.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.hide_checkbox = ctk.CTkCheckBox(tab, text="Hide from Capture (Screenshots/Shares)", command=self.toggle_capture_protection); self.hide_checkbox.grid(row=6, column=0, padx=10, pady=20, sticky="w")
        if not IS_WINDOWS: self.hide_checkbox.configure(state="disabled", text="Hide from Capture (Windows Only)")
        
    def create_ar_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1); s = self.settings['ar_bot']
        ctk.CTkLabel(tab, text="Discord Token:", anchor="w").grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        self.ar_token_entry = ctk.CTkEntry(tab, show="*"); self.ar_token_entry.insert(0, s['token']); self.ar_token_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(tab, text="Target User ID:", anchor="w").grid(row=2, column=0, padx=10, pady=(10,0), sticky="ew")
        self.ar_target_id_entry = ctk.CTkEntry(tab); self.ar_target_id_entry.insert(0, s['target_id']); self.ar_target_id_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(tab, text="Reply Message:", anchor="w").grid(row=4, column=0, padx=10, pady=(10,0), sticky="ew")
        self.ar_reply_entry = ctk.CTkEntry(tab); self.ar_reply_entry.insert(0, s['reply_message']); self.ar_reply_entry.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.ar_button = ctk.CTkButton(tab, text="Start AR Bot", command=self.toggle_ar_bot); self.ar_button.grid(row=6, column=0, padx=10, pady=20, sticky="ew")
        self.ar_status_label = ctk.CTkLabel(tab, text="Status: Idle"); self.ar_status_label.grid(row=7, column=0, padx=10, pady=5)

    def create_gc_changer_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1); s = self.settings['gc_bot']
        ctk.CTkLabel(tab, text="Discord Token:", anchor="w").grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        self.gc_token_entry = ctk.CTkEntry(tab, show="*"); self.gc_token_entry.insert(0, s['token']); self.gc_token_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(tab, text="Group Chat ID:", anchor="w").grid(row=2, column=0, padx=10, pady=(10,0), sticky="ew")
        self.gc_channel_id_entry = ctk.CTkEntry(tab); self.gc_channel_id_entry.insert(0, s['channel_id']); self.gc_channel_id_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(tab, text="Base Name:", anchor="w").grid(row=4, column=0, padx=10, pady=(10,0), sticky="ew")
        self.gc_name_entry = ctk.CTkEntry(tab); self.gc_name_entry.insert(0, s['base_name']); self.gc_name_entry.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.gc_button = ctk.CTkButton(tab, text="Start GC Changer", command=self.toggle_gc_bot); self.gc_button.grid(row=6, column=0, padx=10, pady=20, sticky="ew")
        self.gc_status_label = ctk.CTkLabel(tab, text="Status: Idle. WARNING: VERY HIGH BAN RISK!"); self.gc_status_label.grid(row=7, column=0, padx=10, pady=5)

    def create_generator_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(0, weight=1); s = self.settings['generator']
        scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Generator Settings"); scroll_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew"); scroll_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(scroll_frame, text="Target Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w"); self.gen_name = ctk.CTkEntry(scroll_frame, placeholder_text="Optional"); self.gen_name.insert(0, s['name']); self.gen_name.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.gen_lines_label = ctk.CTkLabel(scroll_frame, text=f"Number of Lines: {s['num_lines']:,}"); self.gen_lines_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        self.gen_lines_slider = ctk.CTkSlider(scroll_frame, from_=100, to=10000, number_of_steps=99, command=lambda v: self.gen_lines_label.configure(text=f"Number of Lines: {int(v):,}")); self.gen_lines_slider.set(s['num_lines']); self.gen_lines_slider.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.gen_start_phrase = ctk.CTkCheckBox(scroll_frame, text="Use Start Phrase"); (self.gen_start_phrase.select() if s['start_phrase'] else None); self.gen_start_phrase.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.gen_end_phrase = ctk.CTkCheckBox(scroll_frame, text="Use End Phrase"); (self.gen_end_phrase.select() if s['end_phrase'] else None); self.gen_end_phrase.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.gen_use_typos = ctk.CTkCheckBox(scroll_frame, text="Enable Typos"); (self.gen_use_typos.select() if s['use_typos'] else None); self.gen_use_typos.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(scroll_frame, text="Text Case:").grid(row=6, column=0, padx=10, pady=5, sticky="w"); self.gen_case = ctk.CTkOptionMenu(scroll_frame, values=['uppercase', 'lowercase', 'mixed']); self.gen_case.set(s['case']); self.gen_case.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(scroll_frame, text="Prefix Symbol:").grid(row=7, column=0, padx=10, pady=5, sticky="w"); self.gen_prefix = ctk.CTkOptionMenu(scroll_frame, values=['none', '#', '+', '-']); self.gen_prefix.set(s['prefix_symbol']); self.gen_prefix.grid(row=7, column=1, padx=10, pady=5, sticky="ew")
        self.gen_button = ctk.CTkButton(tab, text="Generate WordList", command=self.run_generation_thread); self.gen_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.gen_status_label = ctk.CTkLabel(tab, text="Ready to generate."); self.gen_status_label.grid(row=2, column=0, padx=10)

    def create_ai_chat_tab(self, tab):
        if not genai or not Image:
            ctk.CTkLabel(tab, text="Required libraries not found for AI Chat.\nPlease run: pip install google-generativeai pillow", 
                         font=("", 14), text_color="orange", wraplength=450).pack(expand=True, padx=20, pady=20)
            return
        
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(1, weight=1)
        api_frame = ctk.CTkFrame(tab, fg_color="transparent"); api_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew"); api_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(api_frame, text="Google AI API Key:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        self.ai_api_key_entry = ctk.CTkEntry(api_frame, show="*"); self.ai_api_key_entry.insert(0, self.settings['ai_chat']['api_key']); self.ai_api_key_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.ai_set_key_button = ctk.CTkButton(api_frame, text="Set Key & Init", command=self.initialize_ai); self.ai_set_key_button.grid(row=0, column=2, padx=(5, 0), pady=5)
        
        self.chat_frame = ctk.CTkScrollableFrame(tab, label_text="Conversation"); self.chat_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew"); self.chat_frame.grid_columnconfigure(0, weight=1)
        
        input_frame = ctk.CTkFrame(tab); input_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew"); input_frame.grid_columnconfigure(0, weight=1)
        self.ai_prompt_entry = ctk.CTkTextbox(input_frame, height=60); self.ai_prompt_entry.grid(row=0, column=0, rowspan=2, padx=(0,5), pady=5, sticky="ew")
        self.ai_prompt_entry.bind("<Shift-Return>", self.send_ai_prompt_event)
        self.ai_attach_button = ctk.CTkButton(input_frame, text="Attach Image", command=self.attach_image, width=120); self.ai_attach_button.grid(row=0, column=1, padx=5, pady=5, sticky="ne")
        self.ai_send_button = ctk.CTkButton(input_frame, text="Send (Shift+Enter)", command=self.send_ai_prompt, width=120); self.ai_send_button.grid(row=1, column=1, padx=5, pady=5, sticky="se")
        
        self.ai_status_label = ctk.CTkLabel(tab, text="Status: Enter API Key and initialize."); self.ai_status_label.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")
        if self.ai_api_key_entry.get(): self.initialize_ai()

    def load_settings(self):
        defaults = {'wpm': 150, 'delay_ms': 1000, 'theme': 'Dark',
                    'generator': {'name': '', 'num_lines': 1000, 'start_phrase': True, 'end_phrase': True, 
                                  'use_typos': False, 'case': 'uppercase', 'prefix_symbol': 'none'},
                    'ar_bot': {'token': '', 'target_id': '', 'reply_message': 'hi'}, 
                    'gc_bot': {'token': '', 'channel_id': '', 'base_name': ' raided'},
                    'ai_chat': {'api_key': ''}}
        try:
            with open(SETTINGS_FILE, 'r') as f: settings = json.load(f)
            for key, value in defaults.items():
                if key not in settings: settings[key] = value
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                         if sub_key not in settings.get(key, {}): settings[key][sub_key] = sub_value
            return settings
        except (FileNotFoundError, json.JSONDecodeError): return defaults

    def save_settings(self):
        s = self.settings; s['wpm'] = int(self.wpm_slider.get()); s['delay_ms'] = int(self.delay_slider.get()); s['theme'] = ctk.get_appearance_mode()
        s['ar_bot']['token'] = self.ar_token_entry.get(); s['ar_bot']['target_id'] = self.ar_target_id_entry.get(); s['ar_bot']['reply_message'] = self.ar_reply_entry.get()
        s['gc_bot']['token'] = self.gc_token_entry.get(); s['gc_bot']['channel_id'] = self.gc_channel_id_entry.get(); s['gc_bot']['base_name'] = self.gc_name_entry.get()
        s['generator']['name'] = self.gen_name.get(); s['generator']['num_lines'] = int(self.gen_lines_slider.get())
        s['generator']['start_phrase'] = bool(self.gen_start_phrase.get()); s['generator']['end_phrase'] = bool(self.gen_end_phrase.get())
        s['generator']['use_typos'] = bool(self.gen_use_typos.get()); s['generator']['case'] = self.gen_case.get(); s['generator']['prefix_symbol'] = self.gen_prefix.get()
        if genai: s['ai_chat']['api_key'] = self.ai_api_key_entry.get()
        with open(SETTINGS_FILE, 'w') as f: json.dump(s, f, indent=4)

    def load_file_from_dialog(self):
        filepath = filedialog.askopenfilename(title="Select a .txt file", filetypes=(("Text files", "*.txt"),))
        if not filepath: return
        with open(filepath, 'r', encoding='utf-8') as file:
            self.messages = [msg.strip() for msg in file.read().split('\n\n') if msg.strip()]
        self.file_label.configure(text=f"File: {os.path.basename(filepath)}"); self.status_label.configure(text=f"Status: File loaded. Ready.")

    def on_closing(self):
        print("Saving settings and shutting down..."); self.stop_program = True; self.save_settings()
        self.ar_bot_running = False; self.gc_bot_running = False # Signal threads to stop
        if hasattr(self, 'listener'): self.listener.stop()
        self.destroy()

    def start_key_listener(self):
        def listen():
            with KeyboardListener(on_press=self.on_press) as listener: self.listener = listener; listener.join()
        threading.Thread(target=listen, daemon=True).start()

    def on_press(self, key):
        if key == START_STOP_KEY: self.after(0, self.toggle_macro)
        elif key == HIDE_SHOW_KEY: self.after(0, self.deiconify)
        elif key == EXIT_KEY: self.on_closing()

    def update_wpm_label(self,v): self.wpm_label.configure(text=f"Typing Speed (WPM): {int(v)}")
    def update_delay_label(self,v): self.delay_label.configure(text=f"Delay Between Messages (ms): {int(v)}")

    # --- BOT LOGIC (Discord) ---
    def toggle_ar_bot(self):
        if self.ar_bot_running:
            self.ar_bot_running = False; self.ar_button.configure(state="disabled", text="Stopping...")
        else:
            token = self.ar_token_entry.get();
            if not token: self.ar_status_label.configure(text="Error: Token is required."); return
            self.ar_bot_running = True; self.ar_button.configure(text="Stop AR Bot")
            self.ar_status_label.configure(text="Status: Starting...")
            threading.Thread(target=self.run_ar_bot, daemon=True).start()

    def run_ar_bot(self):
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        client = discord.Client(intents=discord.Intents.default(), loop=loop)
        @client.event
        async def on_ready(): self.after(0, self.ar_status_label.configure, {"text": f"Logged in as {client.user.name}"})
        @client.event
        async def on_message(message):
            if not self.ar_bot_running: await client.close(); return
            try:
                if message.author.id == int(self.ar_target_id_entry.get()):
                    await message.channel.send(self.ar_reply_entry.get())
            except (ValueError, discord.errors.HTTPException): pass
        try: client.run(self.ar_token_entry.get())
        except Exception as e: self.after(0, self.ar_status_label.configure, {"text": f"Error: {e}"})
        finally:
            self.ar_bot_running = False
            self.after(0, self.ar_button.configure, {"text": "Start AR Bot", "state": "normal"})
            self.after(0, self.ar_status_label.configure, {"text": "Status: Stopped."})

    def toggle_gc_bot(self):
        if self.gc_bot_running:
            self.gc_bot_running = False; self.gc_button.configure(state="disabled", text="Stopping...")
        else:
            token = self.gc_token_entry.get()
            if not token: self.gc_status_label.configure(text="Error: Token is required."); return
            self.gc_bot_running = True; self.gc_button.configure(text="Stop GC Changer")
            self.gc_status_label.configure(text="Status: Starting...")
            threading.Thread(target=self.run_gc_bot, daemon=True).start()

    def run_gc_bot(self):
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        client = discord.Client(intents=discord.Intents.default(), loop=loop)
        async def name_changer():
            await client.wait_for('ready')
            self.after(0, self.gc_status_label.configure, {"text": f"Logged in as {client.user.name}. Running..."})
            try:
                channel_id = int(self.gc_channel_id_entry.get()); initial_name = self.gc_name_entry.get()
                channel = client.get_channel(channel_id)
                if not channel: self.after(0, self.handle_gc_error, "Channel not found."); await client.close(); return
                count = 1
                while self.gc_bot_running: await channel.edit(name=f'{initial_name} {count}'); count += 1; await asyncio.sleep(0.5)
                await client.close()
            except Exception as e: self.after(0, self.handle_gc_error, str(e)); await client.close()
        try: loop.create_task(name_changer()); client.run(self.gc_token_entry.get())
        except Exception as e: self.after(0, self.handle_gc_error, str(e))
        finally:
            self.gc_bot_running = False
            self.after(0, self.gc_button.configure, {"text": "Start GC Changer", "state": "normal"})
            self.after(0, self.gc_status_label.configure, {"text": "Status: Stopped."})

    def handle_gc_error(self, error_msg):
        self.gc_status_label.configure(text=f"GC Error: {error_msg}")
        self.gc_bot_running = False; self.gc_button.configure(text="Start GC Changer", state="normal")

    # --- WORDLIST GENERATOR LOGIC ---
    def introduce_typos(self, word, typo_probability=0.3):
        if not word or random.random() > typo_probability: return word
        word_list = list(word); typo_type = random.choice(['swap', 'delete', 'insert'])
        if len(word_list) < 2 and typo_type in ['swap', 'delete']: return word
        if typo_type == 'swap':
            idx = random.randint(0, len(word_list) - 2); word_list[idx], word_list[idx+1] = word_list[idx+1], word_list[idx]
        elif typo_type == 'delete': idx = random.randint(0, len(word_list) - 1); del word_list[idx]
        elif typo_type == 'insert': idx = random.randint(0, len(word_list)); char = random.choice(string.ascii_lowercase); word_list.insert(idx, char)
        return ''.join(word_list)
        
    def get_random_part(self, part_list, typo_enabled):
        part = random.choice(part_list)
        return ' '.join(self.introduce_typos(word) for word in part.split()) if typo_enabled else part
        
    def generate_core_phrase(self, typo_enabled):
        adj1 = self.get_random_part(self.BASE_ADJECTIVES, typo_enabled)
        adj2 = self.get_random_part(self.BASE_ADJECTIVES, typo_enabled)
        noun1 = self.get_random_part(self.BASE_NOUNS, typo_enabled)
        verb = self.get_random_part(self.BASE_VERBS, typo_enabled)
        location = self.get_random_part(self.LOCATIONS, typo_enabled)
        action = self.get_random_part(self.ACTION_PHRASES, typo_enabled)
        templates = [f"UR A {adj1} {noun1}",f"{noun1} ass nigga",f"GET {verb}ED {location}",f"{action}",
            f"what a {adj1} {noun1}",f"{adj1} {noun1} {action}",f"you're nothing but a {adj1} {noun1}",
            f"i'll {verb} your {adj1} ass",f"lame ass {noun1} can't even",f"bro is a certified {noun1}",
            f"{noun1.upper()}",f"you are so {adj1} and {adj2}",f"get {verb}ed by me you {noun1}"]
        return random.choice(templates)

    def apply_case(self, text, case_option):
        if case_option == "lowercase": return text.lower()
        if case_option == "mixed": return ''.join(random.choice([c.upper(), c.lower()]) for c in text)
        return text.upper()
        
    def run_generation_thread(self):
        self.gen_button.configure(state="disabled", text="Generating...")
        self.gen_status_label.configure(text="Working...")
        threading.Thread(target=self._generate_wordlist_task, daemon=True).start()

    def _generate_wordlist_task(self):
        s = { 'name': self.gen_name.get(), 'num_lines': int(self.gen_lines_slider.get()), 'start_phrase': bool(self.gen_start_phrase.get()),
              'end_phrase': bool(self.gen_end_phrase.get()), 'use_typos': bool(self.gen_use_typos.get()),
              'case': self.gen_case.get(), 'prefix_symbol': self.gen_prefix.get() }
        all_insults = []
        symbol_prefix = f"{s['prefix_symbol']} " if s['prefix_symbol'] != "none" else ""
        for _ in range(s['num_lines']):
            core_phrase = self.generate_core_phrase(s['use_typos'])
            final_parts = []
            if s['start_phrase']: final_parts.append(self.get_random_part(self.START_PHRASES, s['use_typos']))
            if s['name']: final_parts.append(s['name'])
            final_parts.append(core_phrase)
            if s['end_phrase']: final_parts.append(self.get_random_part(self.END_PHRASES, s['use_typos']))
            full_insult = self.apply_case(" ".join(final_parts), s['case'])
            all_insults.append(f"{symbol_prefix}{full_insult}")
        
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save WordList As...")
        if filepath:
            try:
                with open(filepath, "w", encoding='utf-8') as f: f.write("\n\n".join(all_insults))
                self.after(0, lambda: self.gen_status_label.configure(text=f"Saved {len(all_insults):,} lines to file."))
            except IOError as e: self.after(0, lambda err=e: self.gen_status_label.configure(text=f"Save Error: {err}"))
        else: self.after(0, lambda: self.gen_status_label.configure(text="Save cancelled."))
        self.after(0, lambda: self.gen_button.configure(state="normal", text="Generate WordList"))

    # --- AI CHAT LOGIC ---
    def initialize_ai(self):
        api_key = self.ai_api_key_entry.get()
        if not api_key:
            self.ai_status_label.configure(text="Status: API Key cannot be empty.", text_color="orange")
            return
        try:
            genai.configure(api_key=api_key)
            self.ai_model = genai.GenerativeModel('gemini-1.5-flash')
            self.ai_chat = self.ai_model.start_chat(history=[])
            self.ai_status_label.configure(text="Status: AI Initialized successfully. Ready to chat.", text_color="#00FF7F")
            self.ai_set_key_button.configure(state="disabled"); self.ai_api_key_entry.configure(state="disabled")
            for widget in self.chat_frame.winfo_children(): widget.destroy()
            self.add_message_to_chat("AI", "Hello! How can I assist you today?")
        except Exception as e:
            self.ai_model = None; self.ai_chat = None
            self.ai_status_label.configure(text=f"Status: AI Initialization Failed. Check key or connection.", text_color="red")

    def add_message_to_chat(self, role, text):
        anchor = "w" if role.lower() == "ai" else "e"
        msg_bg_color = "#2b2b2b" if role.lower() == "ai" else "#333333"
        msg_text_color = "#DCE4EE" if role.lower() == "ai" else "#FFFFFF"
        
        msg_textbox = ctk.CTkTextbox(self.chat_frame, fg_color=msg_bg_color, text_color=msg_text_color, wrap="word", font=("", 13), corner_radius=10, border_width=0)
        msg_textbox.insert("1.0", text)
        msg_textbox.configure(state="disabled")
        
        padx = (5, 60) if anchor == 'w' else (60, 5)
        msg_textbox.pack(fill="x", padx=padx, pady=4, anchor=anchor)

        self.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def attach_image(self):
        filepath = filedialog.askopenfilename(title="Select an image", filetypes=(("Image files", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")))
        if not filepath:
            self.attached_image_path = None
            self.ai_status_label.configure(text="Status: Image attachment cancelled.")
            self.ai_attach_button.configure(text="Attach Image")
            return
        self.attached_image_path = filepath
        filename = os.path.basename(filepath)
        self.ai_status_label.configure(text=f"Status: Attached '{filename}'. Ready to send with next prompt.")
        self.ai_attach_button.configure(text=f"Attached: {filename[:10]}...")

    def send_ai_prompt_event(self, event=None):
        self.send_ai_prompt()
        return "break"

    def send_ai_prompt(self):
        prompt_text = self.ai_prompt_entry.get("1.0", "end-1c").strip()
        if not self.ai_chat:
            self.ai_status_label.configure(text="Status: AI not initialized. Please set API key first.", text_color="orange"); return
        if not prompt_text and not self.attached_image_path:
            self.ai_status_label.configure(text="Status: Prompt cannot be empty.", text_color="orange"); return

        self.ai_send_button.configure(state="disabled"); self.ai_prompt_entry.configure(state="disabled")
        display_text = prompt_text
        if self.attached_image_path: display_text = f"[Image: {os.path.basename(self.attached_image_path)}]\n\n{prompt_text}"
        self.add_message_to_chat("User", display_text)

        threading.Thread(target=self._send_ai_prompt_task, args=(prompt_text, self.attached_image_path), daemon=True).start()
        
        self.ai_prompt_entry.delete("1.0", "end"); self.attached_image_path = None
        self.ai_attach_button.configure(text="Attach Image")

    def _send_ai_prompt_task(self, prompt_text, image_path):
        self.after(0, self.ai_status_label.configure, {"text": "Status: AI is thinking..."})
        try:
            content = []
            if image_path: content.append(Image.open(image_path))
            if prompt_text: content.append(prompt_text)
            if not content: raise ValueError("No content to send")
            response = self.ai_chat.send_message(content)
            self.after(0, self._update_ui_with_response, response.text)
        except Exception as e: self.after(0, self._handle_ai_error, str(e))

    def _update_ui_with_response(self, response_text):
        self.add_message_to_chat("AI", response_text)
        self.ai_status_label.configure(text="Status: Ready.", text_color="#00FF7F")
        self.ai_send_button.configure(state="normal"); self.ai_prompt_entry.configure(state="normal")

    def _handle_ai_error(self, error_msg):
        self.add_message_to_chat("AI", f"An error occurred:\n{error_msg}")
        self.ai_status_label.configure(text=f"Status: Error occurred.", text_color="red")
        self.ai_send_button.configure(state="normal"); self.ai_prompt_entry.configure(state="normal")

    # --- AUTO TYPER & MISC ---
    def toggle_capture_protection(self):
        if not IS_WINDOWS: return
        try:
            hwnd = self.winfo_id(); WDA_EXCLUDEFROMCAPTURE = 0x00000011
            SetWindowDisplayAffinity = ctypes.windll.user32.SetWindowDisplayAffinity
            SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]; SetWindowDisplayAffinity.restype = wintypes.BOOL
            if self.hide_checkbox.get() == 1: SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
            else: SetWindowDisplayAffinity(hwnd, 0)
        except Exception as e: self.status_label.configure(text=f"Capture Protection Error: {e}")

    def toggle_macro(self):
        if self.macro_active:
            self.macro_active = False
            self.status_label.configure(text="Status: Auto Typer Stopping...")
        else:
            if not self.messages:
                self.status_label.configure(text="Status: No messages loaded for typer.")
                return
            self.macro_active = True
            self.status_label.configure(text="Status: Auto Typer Running...")
            threading.Thread(target=self.run_macro, daemon=True).start()

    def run_macro(self):
        wpm = self.wpm_slider.get(); char_delay = 60 / (wpm * 5) if wpm > 0 else 0.01
        long_delay_s = self.delay_slider.get() / 1000.0; time.sleep(2)
        while self.macro_active and not self.stop_program:
            if not self.messages: break
            message = random.choice(self.messages); words = message.split(' ')
            for i, word in enumerate(words):
                if not self.macro_active: break
                pyautogui.typewrite(word, interval=char_delay)
                if i < len(words) - 1: pyautogui.press(' ')
            if not self.macro_active: break
            pyautogui.press('enter'); time.sleep(long_delay_s)
        self.macro_active = False
        if not self.stop_program: self.status_label.configure(text="Status: Idle.")

if __name__ == "__main__":
    app = ProdigySuiteApp()
    if discord: app.mainloop()