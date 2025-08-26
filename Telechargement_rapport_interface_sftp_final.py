import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import paramiko
import os
from pathlib import Path

# === Paramètres ===
KHOST = "151.80.119.52"
KPORT = 22

# === Connexion SFTP pour lister les fichiers ===
def ListServerFiles(_host, _port, _username, _password, _remote_dir):
    try:
        _transport = paramiko.Transport((_host, _port))
        _transport.connect(username=_username, password=_password)
        _sftp = paramiko.SFTPClient.from_transport(_transport)

        _files = _sftp.listdir(_remote_dir)

        _sftp.close()
        _transport.close()
        return _files

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la connexion : {e}")
        return []

# === Fonction de téléchargement d'un fichier ===
def DownloadFile(_host, _port, _username, _password, _remote_dir, _local_dir, _filename):
    try:
        _transport = paramiko.Transport((_host, _port))
        _transport.connect(username=_username, password=_password)
        _sftp = paramiko.SFTPClient.from_transport(_transport)

        if not os.path.exists(_local_dir):
            os.makedirs(_local_dir)

        _remote_file = os.path.join(_remote_dir, _filename)
        _local_file = os.path.join(_local_dir, _filename)
        _sftp.get(_remote_file, _local_file)

        _sftp.close()
        _transport.close()
        messagebox.showinfo("Succès", f"Fichier '{_filename}' téléchargé avec succès !")

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du téléchargement : {e}")

# === Fonction de téléchargement de tous les fichiers ===
def DownloadAllFiles(_host, _port, _username, _password, _remote_dir, _local_dir, _files, _progressbar):
    try:
        _transport = paramiko.Transport((_host, _port))
        _transport.connect(username=_username, password=_password)
        _sftp = paramiko.SFTPClient.from_transport(_transport)

        if not os.path.exists(_local_dir):
            os.makedirs(_local_dir)

        total = len(_files)
        for idx, filename in enumerate(_files, start=1):
            remote_file = os.path.join(_remote_dir, filename)
            local_file = os.path.join(_local_dir, filename)
            _sftp.get(remote_file, local_file)

            _progressbar["value"] = (idx / total) * 100
            _progressbar.update()

        _sftp.close()
        _transport.close()
        messagebox.showinfo("Succès", "Tous les fichiers ont été téléchargés avec succès !")

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du téléchargement : {e}")

# === Interface graphique ===
def LaunchGui():
    def load_files():
        nonlocal _files
        _username = _entry_username.get()
        _password = _entry_password.get()

        if not _username or not _password:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs.")
            return

        _remote_dir = f"/home/{_username}/DownloadUserData/"
        _files = ListServerFiles(KHOST, KPORT, _username, _password, _remote_dir)
        if _files:
            _combo_files["values"] = _files
            _combo_files.current(0)

    def DownloadSelected():
        _username = _entry_username.get()
        _password = _entry_password.get()
        _filename = _combo_files.get()

        if not _username or not _password or not _filename:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs et sélectionner un fichier.")
            return

        _remote_dir = f"/home/{_username}/DownloadUserData/"
        DownloadFile(KHOST, KPORT, _username, _password, _remote_dir, _selected_dir.get(), _filename)

    def DownloadAll():
        _username = _entry_username.get()
        _password = _entry_password.get()

        if not _username or not _password or not _files:
            messagebox.showwarning("Attention", "Veuillez charger les fichiers et remplir les champs d'identifiants.")
            return

        _remote_dir = f"/home/{_username}/DownloadUserData/"
        DownloadAllFiles(KHOST, KPORT, _username, _password, _remote_dir, _selected_dir.get(), _files, progressbar)

    def BrowseFolder():
        _folder = filedialog.askdirectory()
        if _folder:
            _selected_dir.set(_folder)

    _files = []

    _root = tk.Tk()
    _root.title("Téléchargement de rapports BOROBO")

    # === Ligne Nom d'utilisateur ===
    _frame_user = tk.Frame(_root)
    _frame_user.grid(row=0, column=0, columnspan=3, pady=2, sticky="w")
    tk.Label(_frame_user, text="Nom d'utilisateur :", width=18, anchor="e").pack(side="left")
    _entry_username = tk.Entry(_frame_user)
    _entry_username.pack(side="left", padx=5)

    # === Ligne Mot de passe ===
    _frame_pass = tk.Frame(_root)
    _frame_pass.grid(row=1, column=0, columnspan=3, pady=2, sticky="w")
    tk.Label(_frame_pass, text="Mot de passe :", width=18, anchor="e").pack(side="left")
    _entry_password = tk.Entry(_frame_pass, show="*")
    _entry_password.pack(side="left", padx=5)

    _show_password = tk.BooleanVar(value=False)

    def TogglePassword():
        if _show_password.get():
            _entry_password.config(show="*")
            _btn_eye.config(text="👁️")
            _show_password.set(False)
        else:
            _entry_password.config(show="")
            _btn_eye.config(text="🙈")
            _show_password.set(True)

    _btn_eye = tk.Button(_frame_pass, text="👁️", command=TogglePassword, padx=5)
    _btn_eye.pack(side="left")

    # === Sélecteur de dossier ===
    _selected_dir = tk.StringVar(value=os.path.join(str(Path.home()), "Desktop", "Borobo_rapports"))

    _frame_folder = tk.Frame(_root)
    _frame_folder.grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=5)
    tk.Label(_frame_folder, text="Dossier de destination :", width=18, anchor="e").pack(side="left")
    _entry_folder = tk.Entry(_frame_folder, textvariable=_selected_dir, width=40)
    _entry_folder.pack(side="left", padx=5)
    tk.Button(_frame_folder, text="Parcourir", command=BrowseFolder).pack(side="left")

    # === Autres widgets ===
    tk.Button(_root, text="Charger les rapports", command=load_files).grid(row=3, columnspan=3, pady=5)

    tk.Label(_root, text="Sélectionner un rapport :").grid(row=4, columnspan=3)
    _combo_files = ttk.Combobox(_root, state="readonly", width=60)
    _combo_files.grid(row=5, columnspan=3, padx=10, pady=5)

    tk.Button(_root, text="Télécharger le rapport sélectionné", command=DownloadSelected).grid(row=6, columnspan=3, pady=5)
    tk.Button(_root, text="Télécharger tous les rapports", command=DownloadAll).grid(row=7, columnspan=3, pady=5)

    progressbar = ttk.Progressbar(_root, orient="horizontal", mode="determinate", length=300)
    progressbar.grid(row=8, columnspan=3, pady=10)

    _root.mainloop()

if __name__ == "__main__":
    LaunchGui()
