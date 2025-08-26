#!/bin/bash

userJETSON_NBR="user$JETSON_NBR"

LOCAL_DIR="$HOME/Documents/borobo_document/borobo_script/Script"
REMOTE_DIR="/home/$userJETSON_NBR/script"

# === Créer le dossier local s'il n'existe pas ===
mkdir -p "$LOCAL_DIR"

# === Écrire l'heure dans le fichier last_seen.txt (heure française) ===
TZ="Europe/Paris" date +"%Y-%m-%dT%H:%M:%S%z" > "$LOCAL_DIR/last_seen.txt"

# === Envoyer le fichier via rsync ===
rsync -avz "$LOCAL_DIR/last_seen.txt" "$userJETSON_NBR@$SERVER_IP:$REMOTE_DIR/"

