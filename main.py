from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
import hashlib
import json
import os
import base64
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import PyPDF2
from docx import Document

VAULT_PATH = "vault_data.enc"
SETTINGS_PATH = "vault_settings.json"

class EncryptionManager:
    @staticmethod
    def derive_key(password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())
    
    @staticmethod
    def encrypt_data(data, password):
        salt = os.urandom(16)
        key = EncryptionManager.derive_key(password, salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        encrypted_package = salt + nonce + ciphertext
        return base64.b64encode(encrypted_package).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data, password):
        try:
            encrypted_package = base64.b64decode(encrypted_data.encode())
            salt = encrypted_package[:16]
            nonce = encrypted_package[16:28]
            ciphertext = encrypted_package[28:]
            key = EncryptionManager.derive_key(password, salt)
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode()
        except Exception:
            return None

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def show_popup(title, message):
    layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
    layout.add_widget(Label(text=message))
    close_button = Button(text='OK', size_hint_y=None, height=40)
    popup = Popup(title=title, content=layout, size_hint=(0.8, 0.4))
    close_button.bind(on_press=popup.dismiss)
    layout.add_widget(close_button)
    popup.open()

def show_pin_prompt(callback, title="Enter PIN"):
    box = BoxLayout(orientation='vertical', padding=10, spacing=10)
    pin_input = TextInput(password=True, multiline=False, hint_text='Enter PIN')
    box.add_widget(pin_input)
    btn = Button(text="Submit", size_hint_y=None, height=40)

    def submit(instance):
        popup.dismiss()
        callback(pin_input.text)

    btn.bind(on_press=submit)
    box.add_widget(btn)
    popup = Popup(title=title, content=box, size_hint=(0.75, 0.4))
    popup.open()

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        device_key = base64.b64encode(os.urandom(32)).decode()
        settings = {
            "vault_locked": False,
            "vault_pin_hash": None,
            "device_key": device_key
        }
        save_settings(settings)
        return settings
    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
            if "device_key" not in settings:
                settings["device_key"] = base64.b64encode(os.urandom(32)).decode()
                save_settings(settings)
            return settings
    except:
        device_key = base64.b64encode(os.urandom(32)).decode()
        return {"vault_locked": False, "vault_pin_hash": None, "device_key": device_key}

def save_settings(settings):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f)

def load_vault(password):
    if not os.path.exists(VAULT_PATH):
        return [], True
    try:
        with open(VAULT_PATH, "r") as f:
            encrypted_data = f.read()
        decrypted = EncryptionManager.decrypt_data(encrypted_data, password)
        if decrypted:
            return json.loads(decrypted), True
        return [], False
    except:
        return [], False

def save_vault(notes, password):
    data = json.dumps(notes)
    encrypted_data = EncryptionManager.encrypt_data(data, password)
    with open(VAULT_PATH, "w") as f:
        f.write(encrypted_data)

class UnlockScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = load_settings()
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='VaultNote', font_size=32))
        
        self.pin_input = TextInput(
            hint_text='Enter Vault PIN',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.pin_input)
        
        unlock_btn = Button(text='Unlock Vault', size_hint_y=None, height=50)
        unlock_btn.bind(on_press=self.unlock_vault)
        layout.add_widget(unlock_btn)
        
        self.add_widget(layout)
    
    def unlock_vault(self, instance):
        if not self.settings.get("vault_locked"):
            self.manager.vault_password = self.settings["device_key"]
            self.manager.current = 'vault'
            return
        
        entered_pin = self.pin_input.text
        if hash_pin(entered_pin) == self.settings.get("vault_pin_hash"):
            self.manager.vault_password = entered_pin
            self.manager.current = 'vault'
        else:
            show_popup("Access Denied", "Incorrect PIN.")
            self.pin_input.text = ""

class VaultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notes = []
        self.selected_index = None

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        settings_btn = Button(text='Vault Settings', size_hint_x=0.7)
        settings_btn.bind(on_press=self.open_vault_settings)
        top_bar.add_widget(settings_btn)
        self.layout.add_widget(top_bar)
        
        self.scroll = ScrollView(size_hint=(1, 0.3))
        self.note_list = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.note_list.bind(minimum_height=self.note_list.setter('height'))
        self.scroll.add_widget(self.note_list)
        self.layout.add_widget(self.scroll)

        self.title_input = TextInput(hint_text="Title", multiline=False, size_hint_y=None, height=50)
        self.content_input = TextInput(hint_text="Content", multiline=True, size_hint_y=0.25)
        self.pin_input = TextInput(hint_text="Document PIN (optional)", password=True, multiline=False, size_hint_y=None, height=50)

        self.layout.add_widget(self.title_input)
        self.layout.add_widget(self.content_input)
        self.layout.add_widget(self.pin_input)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        save_btn = Button(text="Save")
        delete_btn = Button(text="Delete")
        new_btn = Button(text="New")
        import_btn = Button(text="Import")
        export_btn = Button(text="Export")

        save_btn.bind(on_press=self.save_note)
        delete_btn.bind(on_press=self.delete_note)
        new_btn.bind(on_press=self.new_note)
        import_btn.bind(on_press=self.import_file)
        export_btn.bind(on_press=self.export_document)

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(delete_btn)
        btn_layout.add_widget(new_btn)
        btn_layout.add_widget(import_btn)
        btn_layout.add_widget(export_btn)

        self.layout.add_widget(btn_layout)
        self.add_widget(self.layout)

    def on_enter(self):
        vault_password = getattr(self.manager, 'vault_password', None)
        if not vault_password:
            settings = load_settings()
            vault_password = settings["device_key"]
            self.manager.vault_password = vault_password
        
        notes, success = load_vault(vault_password)
        if success:
            self.notes = notes
            self.refresh_note_list()
        else:
            show_popup("Error", "Failed to load vault. Wrong password or corrupted data.")
            self.notes = []
            self.refresh_note_list()

    def refresh_note_list(self):
        self.note_list.clear_widgets()
        for i, note in enumerate(self.notes):
            label = note['title']
            if note.get('locked'):
                label += " 🔒"
            btn = Button(text=label, size_hint_y=None, height=40)
            btn.bind(on_press=lambda instance, idx=i: self.select_note(idx))
            self.note_list.add_widget(btn)

    def select_note(self, index):
        note = self.notes[index]
        if note.get("locked"):
            def check_pin(entered_pin):
                if hash_pin(entered_pin) == note.get("pin_hash"):
                    self.load_note(index)
                else:
                    show_popup("Access Denied", "Incorrect PIN.")
            show_pin_prompt(check_pin, "Enter Document PIN")
        else:
            self.load_note(index)

    def load_note(self, index):
        note = self.notes[index]
        self.selected_index = index
        self.title_input.text = note["title"]
        self.content_input.text = note["content"]
        self.pin_input.text = ""

    def save_note(self, instance):
        title = self.title_input.text.strip()
        content = self.content_input.text.strip()
        pin = self.pin_input.text.strip()
        locked = bool(pin)
        pin_hash = hash_pin(pin) if locked else None

        if not title or not content:
            show_popup("Error", "Title and content cannot be empty.")
            return

        new_note = {
            "title": title,
            "content": content,
            "locked": locked,
            "pin_hash": pin_hash,
            "timestamp": datetime.now().isoformat()
        }

        if self.selected_index is not None:
            self.notes[self.selected_index] = new_note
        else:
            self.notes.append(new_note)

        vault_password = self.manager.vault_password
        save_vault(self.notes, vault_password)
        self.clear_inputs()
        self.refresh_note_list()
        show_popup("Saved", "Document saved successfully.")

    def delete_note(self, instance):
        if self.selected_index is not None:
            del self.notes[self.selected_index]
            vault_password = self.manager.vault_password
            save_vault(self.notes, vault_password)
            self.clear_inputs()
            self.refresh_note_list()
            show_popup("Deleted", "Document deleted.")

    def new_note(self, instance):
        self.selected_index = None
        self.clear_inputs()

    def clear_inputs(self):
        self.title_input.text = ""
        self.content_input.text = ""
        self.pin_input.text = ""

    def import_file(self, instance):
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(filters=['*.txt', '*.pdf', '*.docx', '*.doc'])
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        select_btn = Button(text='Select')
        cancel_btn = Button(text='Cancel')
        
        popup = Popup(title='Import File', content=content, size_hint=(0.9, 0.9))
        
        def select_file(instance):
            if filechooser.selection:
                file_path = filechooser.selection[0]
                self.process_import(file_path)
                popup.dismiss()
        
        def cancel(instance):
            popup.dismiss()
        
        select_btn.bind(on_press=select_file)
        cancel_btn.bind(on_press=cancel)
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def process_import(self, file_path):
        try:
            content = ""
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_ext == '.pdf':
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n"
            elif file_ext in ['.docx', '.doc']:
                doc = Document(file_path)
                content = '\n'.join([para.text for para in doc.paragraphs])
            else:
                show_popup("Error", f"Unsupported file type: {file_ext}")
                return
            
            self.title_input.text = os.path.basename(file_path)
            self.content_input.text = content
            show_popup("Success", "File imported successfully. Add a PIN if needed and click Save.")
        except Exception as e:
            show_popup("Import Error", f"Failed to import file: {str(e)}")
    
    def export_document(self, instance):
        if self.selected_index is None:
            show_popup("Error", "Please select a document to export.")
            return
        
        note = self.notes[self.selected_index]
        
        def do_export(export_pin):
            try:
                export_data = {
                    "title": note["title"],
                    "content": note["content"],
                    "timestamp": note.get("timestamp", datetime.now().isoformat())
                }
                
                encrypted_export = EncryptionManager.encrypt_data(
                    json.dumps(export_data),
                    export_pin
                )
                
                filename = f"{note['title'].replace(' ', '_')}.venc"
                with open(filename, 'w') as f:
                    f.write(encrypted_export)
                
                show_popup("Success", f"Document exported as '{filename}'")
            except Exception as e:
                show_popup("Export Error", f"Failed to export: {str(e)}")
        
        show_pin_prompt(do_export, "Enter PIN for Export Encryption")
    
    def open_vault_settings(self, instance):
        settings = load_settings()
        
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text='Vault Settings', font_size=20, size_hint_y=None, height=40))
        
        pin_input = TextInput(
            hint_text='New Vault PIN (leave empty to remove)',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=50
        )
        box.add_widget(pin_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        save_btn = Button(text='Save')
        cancel_btn = Button(text='Cancel')
        
        popup = Popup(title='Vault Settings', content=box, size_hint=(0.8, 0.5))
        
        def save_settings_callback(instance):
            new_pin = pin_input.text.strip()
            old_password = self.manager.vault_password
            
            if new_pin:
                new_password = new_pin
                settings["vault_locked"] = True
                settings["vault_pin_hash"] = hash_pin(new_pin)
                show_popup("Success", "Vault PIN set successfully.")
            else:
                new_password = settings["device_key"]
                settings["vault_locked"] = False
                settings["vault_pin_hash"] = None
                show_popup("Success", "Vault PIN removed.")
            
            notes, success = load_vault(old_password)
            if success:
                save_vault(notes, new_password)
                self.notes = notes
            
            self.manager.vault_password = new_password
            save_settings(settings)
            popup.dismiss()
        
        def cancel_callback(instance):
            popup.dismiss()
        
        save_btn.bind(on_press=save_settings_callback)
        cancel_btn.bind(on_press=cancel_callback)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        box.add_widget(btn_layout)
        
        popup.open()

class VaultApp(App):
    def build(self):
        sm = ScreenManager()
        settings = load_settings()
        sm.vault_password = settings["device_key"]
        
        if settings.get("vault_locked"):
            sm.add_widget(UnlockScreen(name='unlock'))
            sm.add_widget(VaultScreen(name='vault'))
            sm.current = 'unlock'
        else:
            sm.add_widget(UnlockScreen(name='unlock'))
            sm.add_widget(VaultScreen(name='vault'))
            sm.current = 'vault'
        
        return sm

if __name__ == '__main__':
    VaultApp().run()
