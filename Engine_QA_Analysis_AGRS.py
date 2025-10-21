# %% [markdown]
#  # **ENGINE WAKTU APLIKASI PUPUK 2025**

# %% [markdown]
#  ## 1. Imports and Setup

# %%
# Standard Libraries
import sys
import os
import datetime
import traceback
import random
import json
import io

# Third-Party Libraries
import pandas as pd
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from tkinter import filedialog
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import webbrowser
import tempfile

# GUI Libraries
import tkinter as tk
from tkinter import ttk, messagebox, StringVar
from tkcalendar import Calendar
from PIL import Image, ImageTk
import fitz

# %% [markdown]
#  ## 2. Configuration and Constants

# %%
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# %%
# --- Authentication ---
JSON_PATH = resource_path('enginewaktuaplikasipemupukan-03e33861bae9.json')
# SHEET_URL = "https://docs.google.com/spreadsheets/d/1yCrPTPT6xVMEAYs7d31Vya0GhxQ_AySbfg-CXD7UaMw/edit?usp=sharing"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1I0dkJq30JSM-sUaGUhd0eZiAdeuVjI7Ls4rNLWd6bbE/edit?usp=sharing"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SPLASH_IMAGE = resource_path('bgqa.png')
PANCARAN_LOGO = resource_path("Logo_Pancaran_Agro-removebg-preview.ico")
COMPANY_LOGO = resource_path("Logo_TDK.png")
PHOTO_FOLDER_ID = "1_OgkeR2Iooh9dyoIC6gskIYnJnt8qyJ6"
PDF_REJECTED_FOLDER_ID = "1GqFyobGO6UfFYHy4pqCNuQfX21DtU4RC"
PDF_APPROVED_FOLDER_ID = "1C36T73QJxDNMJsZJR_WsHgv4GlPp-60o"
PDF_PROCESSED_FOLDER_ID = "1ksjnPFekcrxb4-6NNr7bdyNBMzHTqtfT"
APPROVED_LOGO = resource_path("Approved.png")
DONE_LOGO = resource_path("Done.png")

# --- Sheets ---
SHEET_NAMES_INPUT = ["Input - Production", "Input - Nursery", "Input - Chemist", "Input - Fertilizer"]
SHEET_NAMES_OUTPUT = ["Output - Production", "Output - Nursery", "Output - Chemist", "Output - Fertilizer"]
SHEET_NAMES_OUTPUT_WEIGHT = ["Output (Weight) - Production", "Output (Weight) - Nursery", "Output (Weight) - Chemist", "Output (Weight) - Fertilizer"]

ESTATE_OPTIONS = ["Inti", "Plasma"]
DAY_IN_MONTH = 30
DATABASE_IDENTIFIER = ["Blok", "Panen Rotasi", "Tanggal Periksa", "Divisi", "Estate", "DivisiLabel", "Total", "Jenis Pupuk", "Dosis / Pokok", "Tanggal Pemupukan", "Jenis Chemist", "Dosis / Knapsack", "Tanggal Semprot"]
TABLE_COLUMNS = ("Parameter", "Score", "Nilai", "Keterangan")
PDF_TABLE_COLUMNS = ("Title", "Date Modified")

# Production
BRONDOLAN_TINGGAL_OPTIONS = [
    "< 0,5 butir/pkk",
    "> 0,5 - 0,6 butir/pkk",
    "> 0,6 - 0,75 butir/pkk",
    "> 0,75 - 1 butir/pkk",
    "> 1 butir/pkk"]

BUAH_TINGGAL_TPH_OPTIONS = [
    "0 jjg", 
    "> 0 - 0,2 jjg", 
    "> 0,2 - 0,4 jjg", 
    "> 0,4 - 0,6 jjg", 
    "> 0,6 jjg"]

BRONDOLAN_TINGGAL_TPH_OPTIONS = [
    "< 5 butir", 
    "> 5 - 7 butir", 
    "> 7 - 10 butir", 
    "> 10 - 12 butir", 
    "> 12 butir"]

# Nursery
TITI_PANEN_OPTIONS = [
    "Rasio standar, permanen, kondisi baik", 
    "Rasio standar, semi permanen, kondisi baik", 
    "Rasio kurang standar, semi permanen, kondisi baik", 
    "Rasio kurang standar, semi permanen, kondisi rusak", 
    "Tidak ada sama sekali"]

JALAN_JEMBATAN_OPTIONS = [
    "Jalan rata (tidak lubang/rel), jembatan permanen", 
    "Jalan kondisi sedang, jembatan permanen", 
    "Jalan rusak sebagian, jembatan rusak sebagian", 
    "Jalan dominan rusak, jembatan rusak", 
    "Jalan rusak parah, jembatan rusak parah"]

PEILSCALE_OPTIONS = [
    "> -30cm, kondisi baik, update", 
    "-30cm sampai -20cm, kondisi sedang, update", 
    "-20cm sampai -10cm, kondisi sedang, update", 
    "-10cm sampai 0cm, kondisi rusak, update", 
    "> 0cm, kondisi rusak, tidak update"]

BENEFICIAL_PLANT_OPTIONS = [
    "Semua ruas jalan terdapat tanaman rasio 10m2/ha", 
    "Salah satu MR atau CR saja, populasi sesuai rasio", 
    "Salah satu MR atau CR saja, populasi < rasio", 
    "Salah satu MR atau CR , jarang dan tidak terawat", 
    "Tidak dijumpai tanaman sama sekali"]

BARN_OWL_OPTIONS = [
    "Rasio gupon <40 ha, Ada burung hantu,  gupon aktif, kondisi baik, sensus rutin", 
    "Ada burung hantu,  gupon aktif, kondisi baik, sensus rutin", 
    "Ada atau tidak ada burung hantu,  gupon aktif, kondisi baik atau rusak, sensus jarang", 
    "Tidak ada burung hantu, ada gupon, kondisi baik atau rusak, sensus jarang", 
    "Tidak ada burung hantu, tidak ada gupon, sensus tidak"]

# Fertilizer
CARA_APLIKASI_OPTIONS = [
    "> 95%",
    "85% - < 95%",
    "75% - < 85%",
    "65% - < 75%",
    "< 65%"]

KESESUAIAN_DOSIS_ALAT_TABUR_OPTIONS = [
    "> 95%",
    "90% - < 95%",
    "85% - < 90%",
    "80% - < 85%",
    "< 80%"]

TENAGA_PEMUPUK_OPTIONS = [
    "Organisasi tetap, training rutin",
    "Organisasi tetap, tetapi training tidak rutin",
    "Organisasi tidak tetap, training rutin",
    "Organisasi tidak tetap, training tidak rutin",
    "Organisasi tidak tetap, tidak ada training"]

SUPERVISI_OPTIONS = [
    "Lengkap",
    "Ada semua, kecuali tidak ada Assistant / Mandor 1",
    "Ada semua, kecuali tidak ada Assistant & Security",
    "Ada semua, kecuali tidak ada Assistant & Mandor",
    "Tidak ada sama sekali supervisi"]

PEMERIKSAAN_ANCAK_PEMUPUKAN_OPTIONS = [
    "100%",
    "95% - < 100%",
    "90% - < 95%",
    "85% - < 90%",
    "< 85%"]

JADWAL_PEMUPUKAN_OPTIONS = [
    "Sesuai bulan rekomendasi",
    "Terlambat / maju 1 bulan",
    "Terlambat / maju 2 bulan",
    "Terlambat / maju 3 bulan",
    "Terlambat / maju > 3 bulan"]

APD_PEKERJA_OPTIONS = [
    "Lengkap",
    "Kurang dari 1 item",
    "Kurang dari 2 item",
    "Kurang dari 3 item",
    "Tidak ada APD"]

FISIK_PUPUK_OPTIONS = [
    "Tekstur baik, kondisi kering",
    "Tekstur baik, sebagian menggumpal",
    "Tekstur kurang baik, sebagian menggumpal",
    "Tekstur tidak baik, sebagian menggumpal",
    "Tekstur tidak baik, semua menggumpal"]

PELETAKAN_PUPUK_OPTIONS = [
    "Di TPP / dalam blok, dekat piringan",
    "Dalam blok, jauh dari piringan",
    "Di badan jalan sebagian",
    "Semua diletak di badan jalan",
    "Masuk ke parit jalan"]

PUPUK_TERCECER_OPTIONS = [
    "0%",
    "> 0% - 1%",
    "> 1% - 2%",
    "> 2% - 3%",
    "> 3%"]

PENGEMBALIAN_KARUNG_OPTIONS = [
    "Rapi, gulungan 10 lembar, dikumpul pada hari H",
    "Rapi, gulungan kurang sesuai, dikumpul pada H+1",
    "Kurang rapi, gulungan kurang sesuai, dikumpul pada H+1",
    "Kurang rapi, gulungan kurang sesuai, dikumpul pada H+2",
    "Tidak rapi, gulungan tidak sesuai, dikumpul > H+2"]

# Chemist
KONDISI_ALAT_SEMPROT_OPTIONS = [
    "100%",
    "95% - < 100%",
    "90% - < 95%",
    "85% - < 90%",
    "< 85%"]


KESERAGAMAN_NOZEL_OPTIONS = [
    "100%",
    "95% - < 100%",
    "90% - < 95%",
    "85% - < 90%",
    "< 85%"]

DOSIS_KNAPSACK_OPTIONS = [
    "> 100%",
    "97,5% - < 100%",
    "95% - < 97,5%",
    "92,5% - < 95%",
    "< 92,5%"]

BAHAN_HERBISIDA_OPTIONS = [
    "Sesuai gulma sasaran, jumlah yang dibawa sesuai kebutuhan",
    "Kurang sesuai gulma sasaran, jumlah yang dibawa sesuai kebutuhan",
    "Sesuai gulma sasaran, jumlah yang dibawa tidak sesuai kebutuhan",
    "Kurang sesuai gulma sasaran, jumlah tidak sesuai kebutuhan",
    "Tidak sesuai gulma sasaran, jumlah tidak sesuai"]

PENGENDALIAN_GULMA_OPTIONS = [
    "Terdapat RKB/ RKH, sesuai program rotasi",
    "Terdapat RKB/ RKH, kurang sesuai program rotasi",
    "Terdapat RKB/ RKH, tidak sesuai program rotasi",
    "Tidak terdapat RKB/ RKH, sesuai program rotasi",
    "Tidak terdapat RKB/ RKH, tidak sesuai program rotasi"]

PENGGUNAAN_HK_OPTIONS = [
    "95% - 100%",
    "90% - < 95%",
    "85% - < 90%",
    "80% - < 85%",
    "< 80% atau > 100%"]

APD_PEKERJA_CHEMIST_OPTIONS = [
    "Lengkap",
    "Kurang dari 1 item",
    "Kurang dari 2 item",
    "Kurang dari 3 item",
    "Lebih dari 4 item"]

KOTAK_P3K_OPTIONS = [
    "Lengkap dan dibawa mandor",
    "Kurang dari 1 item, dibawa mandor",
    "Kurang dari 2 item, dibawa mandor",
    "Kurang dari 3 item, tidak dibawa mandor",
    "Tidak ada sama sekali"]

KARTU_PENGAMBILAN_PENCAMPURAN_BAHAN_OPTIONS = [
    "Kartu lengkap dan update",
    "Kartu lengkap, terlambat 1 hari",
    "Kartu lengkap, terlambat > 2 hari",
    "Kartu tidak lengkap, terlambat 1 hari",
    "Kartu dan monitoring tidak ada"]

KALIBRASI_ALAT_NOZEL_OPTIONS = [
    "Rutin dan tercatat",
    "Rutin, tidak tercatat",
    "Kurang rutin, tercatat",
    "Tidak rutin, tercatat",
    "Tidak pernah"]

GELAS_UKUR_PERKAKAS_PERBAIKAN_ALAT_SEMPROT_OPTIONS = [
    "Gelas ukur terkalibrasi, alat perbaikan lengkap",
    "Gelas ukur terkalibrasi, alat perbaikan tidak lengkap",
    "Gelas ukur tidak terkalibrasi, alat perbaikan lengkap",
    "Gelas ukur tidak terkalibrasi, alat perbaikan tidak lengkap",
    "Tidak membawa alat takaran dan alat perbaikan"]

PELETAKAN_ALAT_SEMPROT_OPTIONS = [
    "Semua alat dan tercatat",
    "Semua alat, tidak tercatat",
    "Sebagian alat saja dan tercatat",
    "Sebagian alat saja, tidak tercatat",
    "Tidak ada gudang dan pencatatan"]

APD_PEKERJA_RANK = [
    "Lengkap",
    "Kurang dari 1 item",
    "Kurang dari 2 item",
    "Kurang dari 3 item",
    "Tidak ada APD"]

YEARLY_WEIGHT_PRODUCTION = {
    "Pencapaian Produksi": {"2025": "20%", "2026": "18%", "2027": "15%"},
    "Kualitas Panen - TBS Tertinggal": {"2025": "15%", "2026": "13%", "2027": "12%"},
    "Kualitas Panen - LF Tertinggal": {"2025": "15%", "2026": "13%", "2027": "12%"},
    "Kualitas Transport - Jjg di TPH": {"2025": "5%", "2026": "8%", "2027": "4%"},
    "Kualitas Transport - LF di TPH": {"2025": "10%", "2026": "8%", "2027": "4%"},
    "Rotasi Panen": {"2025": "15%", "2026": "13%", "2027": "12%"},
    "Restan": {"2025": "8%", "2026": "10%", "2027": "10%"},
    "Pemakaian Jaring/Terpal": {"2025": "3%", "2026": "5%", "2027": "5%"},
    "Kualitas Panen - TBS Busuk Tinggal": {"2025": "10%", "2026": "13%", "2027": "12%"},
    "Produktivitas Pemanen": {"2025": "0%", "2026": "7%", "2027": "4%"},
    "Administrasi Panen": {"2025": "0%", "2026": "5%", "2027": "5%"},
    "Kualitas TBS": {"2025": "0%", "2026": "0%", "2027": "12%"},
    "Muatan Overload": {"2025": "0%", "2026": "0%", "2027": "5%"},
}

YEARLY_WEIGHT_NURSERY = {
    "Kondisi Circle, Path dan TPH": {"2025": "20%", "2026": "18%", "2027": "15%"},
    "Kondisi Gawangan": {"2025": "18%", "2026": "15%", "2027": "12%"},
    "Titi Panen": {"2025": "8%", "2026": "10%", "2027": "10%"},
    "Jalan & Jembatan": {"2025": "8%", "2026": "10%", "2027": "10%"},
    "Pruning dan Sanitasi": {"2025": "18%", "2026": "15%", "2027": "15%"},
    "Susunan Pelepah": {"2025": "10%", "2026": "10%", "2027": "8%"},
    "Hama Penyakit": {"2025": "10%", "2026": "10%", "2027": "10%"},
    "Beneficial Plant": {"2025": "3%", "2026": "3%", "2027": "5%"},
    "Peilscale": {"2025": "5%", "2026": "5%", "2027": "5%"},
    "Cover Crop (Neprolepis sp.)": {"2025": "0%", "2026": "2%", "2027": "5%"},
    "Barn Owl": {"2025": "0%", "2026": "2%", "2027": "5%"},
}

YEARLY_WEIGHT_FERTILIZER = {
    "Pokok Tidak Terpupuk": {"2025": "20%", "2026": "18%", "2027": "18%"},
    "Kondisi Piringan / Gawangan": {"2025": "15%", "2026": "15%", "2027": "15%"},
    "Cara Aplikasi": {"2025": "12%", "2026": "10%", "2027": "10%"},
    "Keseragaman Alat Tabur": {"2025": "12%", "2026": "10%", "2027": "10%"},
    "Kesesuaian Dosis Alat Tabur": {"2025": "10%", "2026": "10%", "2027": "10%"},
    "Tenaga Pemupuk": {"2025": "5%", "2026": "5%", "2027": "5%"},
    "Supervisi": {"2025": "6%", "2026": "5%", "2027": "5%"},
    "Terdapat Pemeriksaan Ancak Pemupukan": {"2025": "5%", "2026": "5%", "2027": "5%"},
    "Jadwal Pemupukan": {"2025": "5%", "2026": "5%", "2027": "5%"},
    "APD Pekerja": {"2025": "5%", "2026": "5%", "2027": "5%"},
    "Fisik Pupuk": {"2025": "5%", "2026": "3%", "2027": "3%"},
    "Peletakan Pupuk": {"2025": "0%", "2026": "3%", "2027": "3%"},
    "Pupuk Tercecer": {"2025": "0%", "2026": "3%", "2027": "3%"},
    "Pengembalian Karung": {"2025": "0%", "2026": "3%", "2027": "3%"},
}

YEARLY_WEIGHT_CHEMIST = {
    "Kematian Gulma": {"2025": "22%", "2026": "22%", "2027": "20%"},
    "Pokok Tersemprot": {"2025": "5%", "2026": "5%", "2027": "5%"},
    "Bahan Herbisida yang Dibawa ke Ancak": {"2025": "10%", "2026": "10%", "2027": "10%"},
    "Kondisi Alat Semprot": {"2025": "10%", "2026": "10%", "2027": "10%"},
    "Keseragaman Nozel": {"2025": "10%", "2026": "8%", "2027": "8%"},
    "Dosis per Knapsack Sesuai Standar Kalibrasi": {"2025": "7%", "2026": "7%", "2027": "7%"},
    "Program Pengendalian Gulma": {"2025": "7%", "2026": "7%", "2027": "7%"},
    "Penggunaan HK Sesuai Norma Pekerjaan": {"2025": "7%", "2026": "7%", "2027": "7%"},
    "APD Pekerja": {"2025": "5%", "2026": "5%", "2027": "5%"},
    "Kotak P3K Isi Lengkap dan Dibawa Oleh Mandor": {"2025": "0%", "2026": "4%", "2027": "5%"},
    "Terdapat Kartu Pengambilan dan Pencampuran Bahan": {"2025": "5%", "2026": "4%", "2027": "4%"},
    "Terdapat Kalibrasi Alat dan Nozel": {"2025": "5%", "2026": "4%", "2027": "4%"},
    "Membawa Gelas Ukur & Perkakas Perbaikan Alat Semprot": {"2025": "5%", "2026": "5%", "2027": "5%"},
    "Peletakan Alat Semprot": {"2025": "2%", "2026": "2%", "2027": "3%"},
}

QA_TYPE = ["QA Produksi", "QA Perawatan", "QA Pemupukan", "QA Chemist"]

AVAILABLE_YEAR = ["2025", "2026", "2027"]

FERTILIZER_TYPE = ["NPK 13", "NPK 15", "NPK 12", "Dolomite", "Urea", "MOP", "HGFB", "CuSO4", "Zincop Chelated", "Kieserite", "RP", "Kaptan", "TSP"]

# --- Timezone ---
CURRENT_TIMEZONE = pytz.timezone('Asia/Jakarta')

photos_data = []  # list of {"path": ..., "note": ..., "widgets": ...}
pdf_data = []

# %% [markdown]
#  ## 3. Utility Functions

# %%
# --- Styling and Misc ---
BORDER_LINE = "=" * 80
PRIMARY_BUTTON_COLOR = "#4CAF50"  # Green
SECONDARY_BUTTON_COLOR = "#2196F3"  # Blue
MAIN_MENU_BUTTON_COLOR = "#f44336"  # Red
EXIT_BUTTON_COLOR = "#f44336" # Red
TEXT_COLOR = "#000000" # Black
BUTTON_TEXT_COLOR = "#ffffff"  # White

# %%
def format_datetime(dt):
    if isinstance(dt, (datetime.datetime, datetime.date)):
         if dt:
             return dt.strftime('%d/%m/%Y')
    return '' 

# %%
def format_datetimehour(dt):
    if isinstance(dt, datetime.datetime):
         if dt:
             return dt.strftime('%d/%m/%Y %H:%M:%S')
    return ''

# %%
def set_username():
    global username, username_var
    if username_var:
        username = username_var.get()

# %%
def is_valid_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# %%
def make_label(parent, text, row, column=0, font=("Arial", 12), fg=None, **kwargs):
    lbl = tk.Label(parent, text=text, font=font, fg=fg, **kwargs)
    lbl.grid(row=row, column=column, padx=10, pady=5, sticky="ew")
    return lbl

# %%
def make_entry(parent, row, column=0, font=("Arial", 10), width=None, textvariable=None, **kwargs):
    ent = tk.Entry(parent, font=font, textvariable=textvariable, **kwargs)
    if width:
        ent.config(width=width)
    ent.grid(row=row, column=column, padx=10, pady=5, sticky="ew")
    return ent

# %%
def make_combobox(parent, values, row, column=0, font=("Arial", 10), width=30, state="readonly", textvariable=None, **kwargs):
    if textvariable is None:
        textvariable = tk.StringVar()
    cb = ttk.Combobox(parent, values=values, textvariable=textvariable, font=font, width=width, state=state, **kwargs)
    cb.grid(row=row, column=column, padx=10, pady=5, sticky="ew")
    return cb, textvariable

# %%
def make_button(parent, text, row, column=0, command=None, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, **kwargs):
    btn = tk.Button(parent, text=text, command=command, font=font, bg=bg, fg=fg, **kwargs)
    btn.grid(row=row, column=column, padx=10, pady=10, sticky="ew")
    return btn

# %%
def get_available_estate_list(df_mobile_input):
    global available_estate_list, \
        entry_tanggal_qa_terakhir

    tanggal_str = entry_tanggal_qa_terakhir.get().strip()

    if tanggal_str == "":
        available_blok_list = ["None"]
        print("Invalid input for date")
        update_blok_combobox()
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except ValueError:
        available_estate_list = ["None"]
        print("Invalid date format")
        update_estate_combobox()
        return

    # Konversi kolom ke datetime.date (bukan datetime64)
    df_mobile_input['Tanggal'] = pd.to_datetime(df_mobile_input['Tanggal'], errors='coerce').dt.date

    # Filter dengan tipe yang sama
    filtered_df = df_mobile_input[df_mobile_input['Tanggal'] == tanggal_dt]

    # Extract unique blok list
    available_estate_list = sorted(filtered_df['Kebun'].dropna().unique().tolist())
    print("Available Estate List updated:", available_estate_list)

    # Update the combobox with the new blok list
    update_estate_combobox()

# %%
def get_available_divisi_list(df_mobile_input):
    global available_divisi_list, \
        entry_tanggal_qa_terakhir, selected_estate

    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate_str = selected_estate.get().strip()

    if tanggal_str == "" or estate_str == "None":
        available_blok_list = ["None"]
        print("Invalid input for date or estate")
        update_blok_combobox()
        return
    
    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except ValueError:
        available_divisi_list = ["None"]
        print("Invalid date format")
        update_divisi_combobox()
        return

    # Konversi kolom ke datetime.date (bukan datetime64)
    df_mobile_input['Tanggal'] = pd.to_datetime(df_mobile_input['Tanggal'], errors='coerce').dt.date

    # Filter dengan tipe yang sama
    filtered_df = df_mobile_input[(df_mobile_input['Tanggal'] == tanggal_dt) & (df_mobile_input['Kebun'] == estate_str)]

    # Extract unique blok list
    available_divisi_list = sorted(filtered_df['Divisi'].dropna().unique().tolist())
    print("Available divisi List updated:", available_divisi_list)

    # Update the combobox with the new blok list
    update_divisi_combobox()

# %%
def get_available_blok_list(df_mobile_input):
    global available_blok_list, \
    entry_tanggal_qa_terakhir, selected_estate, selected_divisi

    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate_str = selected_estate.get().strip()
    divisi_str = selected_divisi.get().strip()

    if divisi_str.isdigit():
        divisi_int = int(divisi_str)
    else:
        try:
            divisi_int = int(divisi_str)
        except ValueError:
            print("Nilai yang dimasukkan tidak bisa dikonversi menjadi integer.")
            divisi_int = None

    if tanggal_str == "" or estate_str == "None" or (divisi_int == None or divisi_str == "None"):
        available_blok_list = ["None"]
        print("Invalid input for date, estate or divisi")
        update_blok_combobox()
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except ValueError:
        available_blok_list = ["None"]
        print("Invalid date format")
        update_blok_combobox()
        return

    # Konversi kolom ke datetime.date (bukan datetime64)
    df_mobile_input['Tanggal'] = pd.to_datetime(df_mobile_input['Tanggal'], errors='coerce').dt.date

    # Filter dengan tipe yang sama
    filtered_df = df_mobile_input[(df_mobile_input['Tanggal'] == tanggal_dt) & (df_mobile_input['Kebun'] == estate_str) & (df_mobile_input['Divisi'] == divisi_int)]
    # Extract unique blok list
    available_blok_list = sorted(filtered_df['Blok'].dropna().unique().tolist())
    print("Available Blok List updated:", available_blok_list)

    # Update the combobox with the new blok list
    update_blok_combobox()

# %%
def validate_required_fields(fields):
    for label, value in fields.items():
        if not value or value == "None":
            messagebox.showerror("Error", f"{label} harus dipilih/diisi.")
            return False
    return True

# %%
def is_widget_alive(widget):
    try:
        return widget and widget.winfo_exists()
    except Exception:
        return False

# %%
def check_combobox(combobox_title, combobox, options, default_value):
    if combobox is None:
        return default_value
    
    value = combobox.get().strip()

    if not value:
        raise ValueError(f"Input {combobox_title} tidak boleh kosong.")
    
    if value not in options:
        raise ValueError(f"Input {combobox_title} tidak valid.")
    return value

# %%
def cek_entry_number(entry_title, entry, default_value=0.0):
    if entry is None:
        return default_value
    
    value = entry.get().strip()
    if not value:
        raise ValueError(f"Input {entry_title} tidak boleh kosong.")
    
    try:
        # Coba ubah value ke float
        value = float(value)
    except ValueError:
        raise ValueError(f"Input {entry_title} harus berupa angka yang valid.")
    
    return value

# %%
def extract_weights_by_year(weights_dict, year):
    extracted = {}

    for description, year_data in weights_dict.items():
        if year not in year_data:
            raise ValueError(f"Year {year} not found in data for '{description}'.")
        extracted[description] = year_data[year]

    return extracted

# %%
def is_zero_weight_year(reference_key, this_year_weights):
    for key, value in this_year_weights.items():
        if reference_key.lower() == key.lower():
            if value == "0%":
                return True
    return False

# %%
# Specifically used for fertilizer (pemupukan)
def restructure_data(data_dict):
    result = []
    for key, value in data_dict.items():
        parts = key.split('|')
        
        result.append({
            'Nama': parts[0],
            'Blok': parts[1],
            'Tanggal': parts[2],
            'Baris': int(value['baris'])
        })
    return result

# %%
def upload_photo_to_drive(file_path, note=""):
    try:
        # --- Auth using service account ---
        gauth = GoogleAuth()
        gauth.auth_method = 'service'
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, SCOPE)

        drive = GoogleDrive(gauth)

        # --- Generate filename with note ---
        filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{note}.jpg"

        # --- Upload to specified folder ---
        file_drive = drive.CreateFile({
            'title': filename,
            'parents': [{'id': PHOTO_FOLDER_ID}]
        })

        file_drive.SetContentFile(file_path)
        file_drive.Upload()

        print(f"Uploaded: {filename} to folder ID {PHOTO_FOLDER_ID}")

    except Exception as e:
        messagebox.showerror("Error", f"Gagal upload foto: {e}")
        print(f"Error uploading to Google Drive: {e}")

# %%
def upload_pdf_to_drive(file_path, note=""):
    try:
        # --- Auth using service account ---
        gauth = GoogleAuth()
        gauth.auth_method = 'service'
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, SCOPE)

        drive = GoogleDrive(gauth)

        # --- Generate filename with note ---
        filename = file_path

        # --- Upload to specified folder ---
        file_drive = drive.CreateFile({
            'title': filename,
            'parents': [{'id': PDF_PROCESSED_FOLDER_ID}]
        })

        file_drive.SetContentFile(file_path)
        file_drive.Upload()

        print(f"Uploaded: {filename} to folder ID {PDF_PROCESSED_FOLDER_ID}")

    except Exception as e:
        messagebox.showerror("Error", f"Gagal upload pdf: {e}")
        print(f"Error uploading to Google Drive: {e}")

# %%
def fetch_processed_pdfs(drive_folder_id):
    try:
        # --- Auth using service account ---
        gauth = GoogleAuth()
        gauth.auth_method = 'service'
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, SCOPE)

        drive = GoogleDrive(gauth)

        # --- List files in the specified folder ---
        file_list = drive.ListFile({'q': f"'{drive_folder_id}' in parents and trashed=false"}).GetList()

        pdf_files = []
        for file in file_list:
            print(f"file: {file}")
            if file['title'].lower().endswith('.pdf'):
                pdf_files.append({
                    'title': file['title'],
                    'id': file['id'],
                    'createdDate': file['createdDate'],
                    'alternateLink': file['alternateLink']
                })

        print(f"Fetched {len(pdf_files)} PDF files from folder ID {drive_folder_id}")
        return pdf_files

    except Exception as e:
        raise RuntimeError(f"Error fetching PDFs from Google Drive: {e}")

# %%
def save_to_sheet(worksheet, sheet_name, data_dict):
    try:
        header = worksheet.row_values(1)  # header from sheet

        # Convert all values to Python built-in types (int, float, str, etc.)
        def convert_value(val):
            # Handle numpy types
            if hasattr(val, 'item'):
                return val.item()
            # Handle pandas NaN
            if pd.isna(val):
                return ""
            return val

        values = [convert_value(data_dict.get(col, "")) for col in header]
        worksheet.append_row(values)
        print(f"Sukses menyimpan ke '{sheet_name}' (header matched)")
    except Exception as e:
        print(f"Gagal menyimpan ke '{sheet_name}': {e}")

# %%
def make_scrollable_frame(parent):
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event):
        canvas.itemconfig(scrollable_frame_id, width=event.width)

    scrollable_frame.bind("<Configure>", _on_frame_configure)
    canvas.bind("<Configure>", _on_canvas_configure)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")))
    scrollable_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    return scrollable_frame


# %%
def get_random_color():
    return "#{:06x}".format(random.randint(0x111111, 0xEEEEEE))  # Avoid too-dark or too-light

# %%
def remove_photo_row(frame):
    global photos_data, photo_upload_frame
    
    for item in photos_data:
        if item["frame"] == frame:
            photos_data.remove(item)
            break
    frame.destroy()
    
    if photo_upload_frame and not photos_data:
        photo_upload_frame.grid_remove()
    else:
        photo_upload_frame.grid()

# %%
def add_photo_row():
    global photos_data, photo_upload_frame
    
    photo_upload_frame.grid()
    
    row_frame = tk.Frame(photo_upload_frame)
    row_frame.pack(fill='x', pady=5)

    file_var = tk.StringVar()
    note_var = tk.StringVar()

    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if file_path:
            file_var.set(file_path)

    tk.Button(row_frame, text="Browse", command=browse_file).pack(side='left')
    tk.Entry(row_frame, textvariable=file_var, width=40).pack(side='left', padx=5)

    # --- Note Entry with placeholder ---
    note_entry = tk.Entry(row_frame, textvariable=note_var, width=30, fg="grey")
    note_entry.insert(0, "Masukkan catatan...") 
    note_entry.pack(side='left', padx=5)

    def on_focus_in(event):
        if note_var.get() == "Masukkan catatan...":
            note_entry.delete(0, tk.END)
            note_entry.config(fg="black")

    def on_focus_out(event):
        if note_var.get().strip() == "":
            note_entry.insert(0, "Masukkan catatan...")
            note_entry.config(fg="grey")

    note_entry.bind("<FocusIn>", on_focus_in)
    note_entry.bind("<FocusOut>", on_focus_out)

    remove_btn = tk.Button(row_frame, text="Remove", command=lambda: remove_photo_row(row_frame))
    remove_btn.pack(side='left')

    photos_data.append({
        "file_var": file_var,
        "note_var": note_var,
        "frame": row_frame
    })


# %%
def process_uploaded_photos():
    global photos_data
    
    for item in photos_data:
        file_path = item["file_var"].get()
        note_text = item["note_var"].get()

        if file_path:
            print(f"Uploading {file_path} with note: {note_text}")
            upload_photo_to_drive(file_path, note_text)
        else:
            print("Skipping empty file entry")

    if photos_data:
        messagebox.showinfo("Berhasil", "Foto berhasil diupload ke Google Drive.")

# %%
def proceed_to_upload_pdf():
    global pdf_data
    
    for item in pdf_data:

        if item:
            print(f"Uploading {item}")
            upload_pdf_to_drive(item)
        else:
            print("Skipping empty file entry")

    if pdf_data:
        messagebox.showinfo("Berhasil", "PDF berhasil diupload ke Google Drive.")

# %%
def open_pdf(pdf_url):
    # Fungsi untuk membuka PDF dari Google Drive menggunakan web browser
    webbrowser.open(pdf_url)

# %%
def display_pdf(event, pdf_files=None, group_title=""):
    """Display the selected PDF from the appropriate current list.
    This function uses the global processed/rejected/approved pdf lists so the handler
    will always operate on the freshest data. If the relevant list is empty it will
    attempt to re-fetch PDFs from Drive as a fallback.
    """
    global pdf_id, processed_pdf_files, rejected_pdf_files, approved_pdf_files

    # Choose the correct table and pdf list based on group_title
    if group_title == "Processed":
        table = processed_table
        current_list = processed_pdf_files
    elif group_title == "Rejected":
        table = rejected_table
        current_list = rejected_pdf_files
    elif group_title == "Approved":
        table = approved_table
        current_list = approved_pdf_files
    else:
        table = processed_table
        current_list = processed_pdf_files

    selected_item = table.selection()
    if not selected_item:
        return

    item_id = selected_item[0]
    pdf_title = table.item(item_id, "values")[0]

    # If the current in-memory list is empty, try re-fetching from Drive once
    if not current_list:
        try:
            processed_pdf_files, rejected_pdf_files, approved_pdf_files = fetch_pdfs()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil daftar PDF: {e}")
            return

        if group_title == "Processed":
            current_list = processed_pdf_files
        elif group_title == "Rejected":
            current_list = rejected_pdf_files
        else:
            current_list = approved_pdf_files

    # Find the selected PDF metadata
    try:
        selected_pdf = next(item for item in current_list if item.get("title") == pdf_title)
    except StopIteration:
        messagebox.showerror("Error", f"PDF '{pdf_title}' tidak ditemukan. Coba klik Refresh.")
        return

    pdf_url = selected_pdf.get("alternateLink")
    pdf_id = selected_pdf.get("id", "")

    pdf_display_area.config(text=f"Previewing: {group_title} - {pdf_title}")
    open_pdf(pdf_url)

# %%
def move_file_between_folders(file_id, source_folder_id, destination_folder_id):
    global pdf_id
    try:
        # Build service using service account credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, SCOPE)
        service = build('drive', 'v3', credentials=creds)

        # If source_folder_id is not provided, try to detect current parents and remove them
        if not source_folder_id:
            file_meta = service.files().get(fileId=file_id, fields='parents').execute()
            current_parents = file_meta.get('parents', [])
            remove_parents = ",".join(current_parents) if current_parents else None
        else:
            remove_parents = source_folder_id

        # Prepare parameters for update
        params = {'fileId': file_id, 'addParents': destination_folder_id, 'fields': 'id, parents'}
        if remove_parents:
            params['removeParents'] = remove_parents

        updated = service.files().update(**params).execute()

        print(f"Moved file {file_id} to folder {destination_folder_id}. New parents: {updated.get('parents')}")

        pdf_id = ""

        return updated

    except HttpError as e:
        raise RuntimeError(f"Google Drive API error moving file: {e}")
    except Exception as e:
        raise RuntimeError(f"Error moving file on Google Drive: {e}")

# %%
def add_approved_logo_to_drive_pdf(file_id, approved_logo_path=APPROVED_LOGO):
    """Download PDF from Drive, insert the approved logo inside the Manager signature box
    so it lines up with the DONE logos drawn by reportlab. Uses the same layout constants
    used when generating the PDF: margin=50, row_height=60, padding=6 and 4 equal columns.
    This computes coordinates in PDF (top-left origin used by PyMuPDF) by converting
    the reportlab bottom-based y coordinates.
    """
    try:
        if not approved_logo_path or not os.path.exists(approved_logo_path):
            print("Approved logo not found; skipping adding approved logo.")
            return

        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, SCOPE)
        service = build('drive', 'v3', credentials=creds)

        # --- Download the PDF into memory ---
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        pdf_bytes = fh.read()

        # --- Open PDF with PyMuPDF ---
        doc = fitz.open(stream=pdf_bytes, filetype='pdf')

        page_with_manager = None
        manager_rect = None

        # Search pages for the manager name; note the page where the manager name appears
        for page in doc:
            rects = page.search_for("Didik Wahyu Prasetyo")
            if rects:
                # Use first occurrence
                page_with_manager = page
                manager_rect = rects[0]
                break

        # Layout constants matching reportlab PDF generation
        margin = 50
        row_y_reportlab = 150  # y used in reportlab (distance from bottom)
        row_height = 60
        padding = 6

        # If we found the manager name page, use that page for placement; otherwise use last page
        target_page = page_with_manager if page_with_manager else doc[-1]
        page_rect = target_page.rect
        page_w = page_rect.width
        page_h = page_rect.height

        # Compute column width (4 equal columns as in reportlab)
        col_width = (page_w - 2 * margin) / 4.0
        img_w = col_width - padding * 2
        img_h = row_height - padding * 2

        # Manager box is the 4th column (index 3)
        box_x = margin + col_width * 3
        # reportlab box_y is measured from bottom; convert to top-based coordinate for fitz
        # In reportlab the image bottom-left is at (box_x + padding, box_y + padding)
        # For fitz, y0 (top) = page_h - (box_y + padding + img_h)
        x0 = box_x + padding
        y0 = page_h - (row_y_reportlab + padding + img_h)
        img_rect = fitz.Rect(x0, y0, x0 + img_w, y0 + img_h)

        try:
            target_page.insert_image(img_rect, filename=approved_logo_path, keep_proportion=True)
        except Exception as e:
            print(f"Failed to insert approved image at computed manager box: {e}")
            # Fallback: try a conservative placement near the right side at similar vertical pos
            try:
                fallback_x0 = page_w - 50 - img_w
                fallback_y0 = page_h - (row_y_reportlab + padding + img_h)
                fallback_rect = fitz.Rect(fallback_x0, fallback_y0, fallback_x0 + img_w, fallback_y0 + img_h)
                target_page.insert_image(fallback_rect, filename=approved_logo_path, keep_proportion=True)
            except Exception as e2:
                print(f"Fallback insertion also failed: {e2}")

        # --- Save modified PDF to memory ---
        out = io.BytesIO()
        doc.save(out)
        out.seek(0)

        # --- Update the file on Drive with new content ---
        media = MediaIoBaseUpload(out, mimetype='application/pdf', resumable=True)
        updated = service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Inserted approved logo into file {file_id}")

    except Exception as e:
        print(f"Failed to add approved logo to PDF: {e}")


# %%
def toggle_pdf_report_button_visibility(*args):
    if not pdf_id:
        # Case: Processed PDF is not selected
        print("Processed PDF is not selected.")
        for w in conditional_widgets:
            w.grid_remove()

    else:
        # Case: Processed PDF is selected
        print("Processed PDF is selected.")
        for w in conditional_widgets:
            w.grid()

# %%
def fetch_pdfs():
    global processed_pdf_files, rejected_pdf_files, approved_pdf_files
    processed_pdf_files = fetch_processed_pdfs(PDF_PROCESSED_FOLDER_ID)
    rejected_pdf_files = fetch_processed_pdfs(PDF_REJECTED_FOLDER_ID)
    approved_pdf_files = fetch_processed_pdfs(PDF_APPROVED_FOLDER_ID)

    return processed_pdf_files, rejected_pdf_files, approved_pdf_files

# %%
def refresh_table():
    global processed_table, rejected_table, approved_table, \
        processed_pdf_files, rejected_pdf_files, approved_pdf_files

    processed_pdf_files, rejected_pdf_files, approved_pdf_files = fetch_pdfs()

    for i in processed_table.get_children():
        processed_table.delete(i)
        
    for item in processed_pdf_files:
        pdf_title = item["title"]
        pdf_date = item["createdDate"]
        pdf_url = item["alternateLink"]
        processed_table.insert("", "end", values=(pdf_title, pdf_date))

    # Rejected Table
    for i in rejected_table.get_children():
        rejected_table.delete(i)
        
    for item in rejected_pdf_files:
        pdf_title = item["title"]
        pdf_date = item["createdDate"]
        pdf_url = item["alternateLink"]
        rejected_table.insert("", "end", values=(pdf_title, pdf_date))

    # Approved Table
    for i in approved_table.get_children():
        approved_table.delete(i)
        
    for item in approved_pdf_files:
        pdf_title = item["title"]
        pdf_date = item["createdDate"]
        pdf_url = item["alternateLink"]
        approved_table.insert("", "end", values=(pdf_title, pdf_date))



# %%
def approve_selected_pdf(pdf_id, PDF_PROCESSED_FOLDER_ID, PDF_APPROVED_FOLDER_ID):

    if not pdf_id:
        messagebox.showerror("Error", "No PDF selected to approve.")
        return

    try:
        # Add the "Approved" logo into the PDF on Drive (if possible) before moving it
        try:
            add_approved_logo_to_drive_pdf(pdf_id, APPROVED_LOGO)
        except Exception as e:
            # Non-fatal: log and continue to move the file
            print(f"Warning: could not add approved logo before moving: {e}")

        move_file_between_folders(pdf_id, PDF_PROCESSED_FOLDER_ID, PDF_APPROVED_FOLDER_ID)
        show_success_window()
        toggle_pdf_report_button_visibility()
        pdf_display_area.config(text=f"Select a PDF to preview")
        refresh_table()

    except Exception as e:
        messagebox.showerror("Error", f"Gagal memindahkan PDF ke folder Approved: {e}")


# %%
def decline_selected_pdf(pdf_id, PDF_PROCESSED_FOLDER_ID, PDF_REJECTED_FOLDER_ID):

    if not pdf_id:
        messagebox.showerror("Error", "No PDF selected to decline.")
        return

    try:
        move_file_between_folders(pdf_id, PDF_PROCESSED_FOLDER_ID, PDF_REJECTED_FOLDER_ID)
        show_success_window()
        toggle_pdf_report_button_visibility()
        pdf_display_area.config(text=f"Select a PDF to preview")
        refresh_table()

    except Exception as e:
        messagebox.showerror("Error", f"Gagal memindahkan PDF ke folder Rejected: {e}")

# %% [markdown]
#  ## 4. Global Variables (Application State)

# %%
# --- Core App State ---
root = None
previous_menu = None
root_exists = False
current_menu = None
df = pd.DataFrame() # In-memory data store
current_time_date = datetime.datetime.now(CURRENT_TIMEZONE) # Ensure it uses datetime.datetime
formatted_today = format_datetime(current_time_date)

# --- User State ---
username_var = None # Will be StringVar, created in main_process
username = ""     # Will store the string username

# --- Google Sheets Objects ---
mobile_input_production = None
input_production = None
input_nursery = None
input_chemist = None
input_fertilizer = None 
output_production = None
output_nursery = None
output_chemist = None
output_fertilizer = None
output_weight_production = None
output_weight_nursery = None
output_weight_chemist = None
output_weight_fertilizer = None

# --- GUI State ---
success_window = None
missing_dates_widgets = {}

# --- Widget References (Initialized to None in main_process) ---
# These are numerous, keeping them listed in main_process might be okay for now,
# but consider a class structure for larger apps.
# (List of widget variables like label_username, entry_username, etc.)


# %% [markdown]
#  ## 5. Google Sheets Interaction

# %%
def load_database(sheet_url, json_path):
    """Only connect to the spreadsheet. Do not load all sheets at once."""
    global client, sheet

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(sheet_url)

    except Exception as e:
        messagebox.showerror("Error", f"Gagal konek ke spreadsheet: {e}")
        print(traceback.format_exc())


# %%
def load_sheets_for_menu(qa_type):

    mobile_produksi_input_sheet_name = "Testing"
    mobile_perawatan_input_sheet_name = "Testing Perawatan"
    mobile_pemupukan_input_sheet_name = "Testing Pemupukan"
    mobile_chemist_input_sheet_name = "Testing Chemist"

    mapping_input = {
        "QA Produksi": "Input - Production",
        "QA Perawatan": "Input - Nursery",
        "QA Chemist": "Input - Chemist",
        "QA Pemupukan": "Input - Fertilizer"
    }
    mapping_output = {
        "QA Produksi": "Output - Production",
        "QA Perawatan": "Output - Nursery",
        "QA Chemist": "Output - Chemist",
        "QA Pemupukan": "Output - Fertilizer"
    }
    mapping_output_weight = {
        "QA Produksi": "Output (Weight) - Production",
        "QA Perawatan": "Output (Weight) - Nursery",
        "QA Chemist": "Output (Weight) - Chemist",
        "QA Pemupukan": "Output (Weight) - Fertilizer"
    }

    input_sheet_name = mapping_input.get(qa_type)
    output_sheet_name = mapping_output.get(qa_type)
    output_weight_sheet_name = mapping_output_weight.get(qa_type)

    if not input_sheet_name or not output_sheet_name or not output_weight_sheet_name:
        raise Exception("QA type tidak dikenali.")

    mobile_produksi_input_worksheet = sheet.worksheet(mobile_produksi_input_sheet_name)
    mobile_perawatan_input_worksheet = sheet.worksheet(mobile_perawatan_input_sheet_name)
    mobile_pemupukan_input_worksheet = sheet.worksheet(mobile_pemupukan_input_sheet_name)
    mobile_chemist_input_worksheet = sheet.worksheet(mobile_chemist_input_sheet_name)
    input_worksheet = sheet.worksheet(input_sheet_name)
    output_worksheet = sheet.worksheet(output_sheet_name)
    output_weight_worksheet = sheet.worksheet(output_weight_sheet_name)

    df_mobile_produksi_input = pd.DataFrame(mobile_produksi_input_worksheet.get_all_records())
    df_mobile_perawatan_input = pd.DataFrame(mobile_perawatan_input_worksheet.get_all_records())
    df_mobile_pemupukan_input = pd.DataFrame(mobile_pemupukan_input_worksheet.get_all_records())
    df_mobile_chemist_input = pd.DataFrame(mobile_chemist_input_worksheet.get_all_records())
    df_input = pd.DataFrame(input_worksheet.get_all_records())
    df_output = pd.DataFrame(output_worksheet.get_all_records())
    df_output_weight = pd.DataFrame(output_weight_worksheet.get_all_records())

    return df_mobile_produksi_input, df_mobile_perawatan_input, df_mobile_pemupukan_input, df_mobile_chemist_input, df_input, df_output, df_output_weight

# %% [markdown]
#  ## 6. Core Logic
#  

# %% [markdown]
#  ### 6.1 QA Production

# %%
def evaluate_budget_actual(budget, actual):
    difference_actual_budget = (actual / budget) * 100

    if difference_actual_budget > 100: # > 100%
        return 10
    elif 90 <= difference_actual_budget <= 100: # 90 - 100%
        return 8
    elif 80 <= difference_actual_budget < 90: # 80 - 90%
        return 6
    elif 70 <= difference_actual_budget < 80: # 70 - 80%
        return 4
    elif difference_actual_budget < 70: # < 70%
        return 2

# %%
def evaluate_buah_tinggal(buah_tinggal, pokok_sample):
    global perhitungan_buah_tinggal
    perhitungan_buah_tinggal = (buah_tinggal / pokok_sample) * 100

    if perhitungan_buah_tinggal == 0:  # 0%
        return 10
    elif 0 < perhitungan_buah_tinggal <= 0.2:  # > 0% - 0.2%
        return 8
    elif 0.2 < perhitungan_buah_tinggal <= 0.4:  # > 0.2% - 0.4%
        return 6
    elif 0.4 < perhitungan_buah_tinggal <= 0.6:  # > 0.4% - 0.6%
        return 4
    elif perhitungan_buah_tinggal > 0.6:  # > 0.6%
        return 2

# %%
# Immediately berondolan tertinggal
def evaluate_berondolan_tertinggal(berondolan_tertinggal, pokok_dipanen):
    global perhitungan_berondolan_tertinggal
    perhitungan_berondolan_tertinggal = (berondolan_tertinggal / pokok_dipanen)

    if perhitungan_berondolan_tertinggal < 0.5:  # < 0.5
        return 10
    elif 0.5 <= perhitungan_berondolan_tertinggal < 0.6:  # > 0.5 - 0.6
        return 8
    elif 0.6 <= perhitungan_berondolan_tertinggal <= 0.75:  # > 0.6 - 0.75
        return 6
    elif 0.75 <= perhitungan_berondolan_tertinggal <= 1:  # > 0.75 - 1
        return 4
    elif perhitungan_berondolan_tertinggal >= 1:  # > 1
        return 2

# %%
# Immediately buah tertinggal TPH
def evaluate_buah_tertinggal_tph(buah_tertinggal_tph, tph_counter):
    global perhitungan_buah_tertinggal_tph
    perhitungan_buah_tertinggal_tph = (buah_tertinggal_tph / tph_counter)

    if perhitungan_buah_tertinggal_tph == 0:  # 0
        return 10
    elif 0 < perhitungan_buah_tertinggal_tph <= 0.2:  # > 0 - 0.2
        return 8
    elif 0.2 < perhitungan_buah_tertinggal_tph <= 0.4:  # > 0.2 - 0.4
        return 6
    elif 0.4 < perhitungan_buah_tertinggal_tph <= 0.6:  # > 0.4 - 0.6
        return 4
    elif perhitungan_buah_tertinggal_tph > 0.6:  # > 0.6
        return 2

# %%
# Immediately berondolan tertinggal TPH
def evaluate_berondolan_tertinggal_tph(berondolan_tertinggal_tph, tph_counter):
    global perhitungan_berondolan_tertinggal_tph
    perhitungan_berondolan_tertinggal_tph = (berondolan_tertinggal_tph / tph_counter)

    if perhitungan_berondolan_tertinggal_tph < 1:  # < 1
        return 10
    elif 1 <= perhitungan_berondolan_tertinggal_tph < 2:  # > 1 - 2
        return 8
    elif 2 <= perhitungan_berondolan_tertinggal_tph < 3:  # > 2 - 3
        return 6
    elif 3 <= perhitungan_berondolan_tertinggal_tph < 4:  # > 3 - 4
        return 4
    elif perhitungan_berondolan_tertinggal_tph >= 4:  # > 4
        return 2

# %%
# Immediately rotasi panen bulanan
def evaluate_rotasi_panen_bulanan(rotasi_panen):
    perhitungan_rotasi_panen = DAY_IN_MONTH/rotasi_panen
    
    if perhitungan_rotasi_panen > 3: # > 3 round
        return 10
    elif 2.7 < perhitungan_rotasi_panen <= 3: # 2,7 - < 3 round
        return 8
    elif 2.4 < perhitungan_rotasi_panen <= 2.7: # 2,4 - < 2,7 round
        return 6
    elif 2.1 < perhitungan_rotasi_panen <= 2.4: # 2,1 - < 2,4 round
        return 4
    elif perhitungan_rotasi_panen < 2.1: # < 2,1 round
        return 2

# %%
# Immediately evaluate restan
def evaluate_restan(restan):
    if restan < 4: # < 4 %
        return 10
    elif 4 < restan <= 6: # > 4 - 6 %
        return 8
    elif 6 < restan <= 8: # > 6 - 8 %
        return 6
    elif 8 < restan <= 10: # > 8 - 10 %
        return 4
    elif restan > 10: # > 10 %
        return 2

# %%
# Immediately evaluate jaring
def evaluate_jaring(jaring):
    
    if jaring >= 100: # > 100%
        return 10
    elif 98 <= jaring < 100: # > 98% - 100%
        return 8
    elif 96 <= jaring < 98: # > 96% - 98%
        return 6
    elif 95 <= jaring < 96: # > 95% - 96%
        return 4
    elif jaring < 95: # < 95%
        return 2

# %%
def evaluate_tbs_busuk_tinggal(tbs_busuk_tertinggal, pokok_sample):
    global perhitungan_tbs_busuk_tinggal
    perhitungan_tbs_busuk_tinggal = (tbs_busuk_tertinggal / pokok_sample) * 100

    if perhitungan_tbs_busuk_tinggal == 0:  # 0%
        return 10
    elif 0 < perhitungan_tbs_busuk_tinggal <= 0.2:  # > 0% - 0.2%
        return 8
    elif 0.2 < perhitungan_tbs_busuk_tinggal <= 0.4:  # > 0.2% - 0.4%
        return 6
    elif 0.4 < perhitungan_tbs_busuk_tinggal <= 0.6:  # > 0.4% - 0.6%
        return 4
    elif perhitungan_tbs_busuk_tinggal > 0.6:  # > 0.6%
        return 2

# %%
# Immediately evaluate produktivitas pemanen
def evaluate_produktivitas_pemanen(produktivitas_pemanen):
    
    if produktivitas_pemanen > 750: # > 750 kg/HK
        return 10
    elif 700 < produktivitas_pemanen <= 750: # 700 - 750 kg/HK
        return 8
    elif 650 < produktivitas_pemanen <= 700: # 650 - 700 kg/HK
        return 6
    elif 600 < produktivitas_pemanen <= 650: # 600 - 650 kg/HK
        return 4
    elif produktivitas_pemanen < 600: # < 600 kg/HK
        return 2

# %%
# Immediately evaluate administrasi panen
def evaluate_administrasi_panen(administrasi_panen):
    
    if administrasi_panen == 0: # 0
        return 10
    elif 0 < administrasi_panen <= 1: # > 0 - 1
        return 8
    elif 1 < administrasi_panen <= 2: # > 1 - 2
        return 6
    elif 2 < administrasi_panen <= 3: # > 2 - 3
        return 4
    elif administrasi_panen > 3: # > 3
        return 2

# %%
# Immediately evaluate kualitas tbs
def evaluate_kualitas_tbs(kualitas_tbs):
    
    if kualitas_tbs > 98 : # > 98%
        return 10
    elif 97 < kualitas_tbs <= 98: # 97% - < 98%
        return 8
    elif 96 < kualitas_tbs <= 97: # 96% - < 97%
        return 6
    elif 95 < kualitas_tbs <= 96: # 95% - < 96%
        return 4
    elif kualitas_tbs < 95: # < 95%
        return 2

# %%
# Immediately evaluate muatan overload
def evaluate_muatan_overload(muatan_overload):
    
    if muatan_overload > 95 : # > 95%
        return 10
    elif 90 < muatan_overload <= 95: # 90 - < 95 %
        return 8
    elif 85 < muatan_overload <= 90: # 85 - < 90 %
        return 6
    elif 80 < muatan_overload <= 85: # 80 - < 85 %
        return 4
    elif muatan_overload < 80: # < 80 %
        return 2

# %%
def analyse_qa_production(
        identifier_data,
        pokok_sample,
        pokok_dipanen,
        actual,
        budget,
        buah_tertinggal,
        berondolan_tertinggal,
        buah_tertinggal_tph,
        berondolan_tertinggal_tph,
        tph_counter,
        panen_rotasi,
        restan,
        jaring,
        tbs_busuk_tertinggal,
        produktivitas_pemanen,
        administrasi_panen,
        kualitas_tbs,
        muatan_overload):
    
    global combobox_chosen_year, chosen_year_weight
    
    # Check chosen year if its empty
    chosen_year = combobox_chosen_year.get()
    if not chosen_year.strip():
        messagebox.showerror("Error", "Tolong masukkan pilihan tahun.")
        return

    # Get the rule data based on the chosen menu 
    try:
        chosen_year_weight = extract_weights_by_year(YEARLY_WEIGHT_PRODUCTION, chosen_year)
    except ValueError as e:
        messagebox.showerror("Error", f"Gagal memuat kriteria untuk tahun {chosen_year}: {e}")
        return
    
    # Evaluate each input
    score_actual_budget = evaluate_budget_actual(budget, actual)

    score_buah_tinggal = evaluate_buah_tinggal(buah_tertinggal, pokok_sample)

    score_berondolan_tertinggal = evaluate_berondolan_tertinggal(berondolan_tertinggal, pokok_dipanen)

    score_buah_tertinggal_tph = evaluate_buah_tertinggal_tph(buah_tertinggal_tph, tph_counter)

    score_berondolan_tertinggal_tph = evaluate_berondolan_tertinggal_tph(berondolan_tertinggal_tph, tph_counter)
    
    score_rotasi_perbulan = evaluate_rotasi_panen_bulanan(panen_rotasi)

    score_restan = evaluate_restan(restan)

    score_jaring = evaluate_jaring(jaring)

    score_tbs_busuk_tertinggal = evaluate_tbs_busuk_tinggal(tbs_busuk_tertinggal, pokok_sample)

    score_produktivitas_pemanen = evaluate_produktivitas_pemanen(produktivitas_pemanen)

    score_administrasi_panen = evaluate_administrasi_panen(administrasi_panen)

    score_kualitas_tbs = evaluate_kualitas_tbs(kualitas_tbs)

    score_muatan_overload = evaluate_muatan_overload(muatan_overload)

    # Store all the calculated scores in to dictionary 
    scores = {
        "Pencapaian Produksi": score_actual_budget,
        "Kualitas Panen - TBS Tertinggal": score_buah_tinggal,
        "Kualitas Panen - LF Tertinggal": score_berondolan_tertinggal,
        "Kualitas Transport - Jjg di TPH": score_buah_tertinggal_tph,
        "Kualitas Transport - LF di TPH": score_berondolan_tertinggal_tph,
        "Rotasi Panen": score_rotasi_perbulan,
        "Restan": score_restan,
        "Pemakaian Jaring/Terpal": score_jaring,
        "Kualitas Panen - TBS Busuk Tinggal": score_tbs_busuk_tertinggal,
        "Produktivitas Pemanen": score_produktivitas_pemanen,
        "Administrasi Panen": score_administrasi_panen,
        "Kualitas TBS": score_kualitas_tbs,
        "Muatan Overload": score_muatan_overload,
    }
    
    # Calculate the final score after yearly weight
    score_only_data = {}
    nilai_only_data = {}

    for description, score_value in scores.items():
        score_only_data[description] = score_value
        if description in chosen_year_weight:
            weight_percent = float(chosen_year_weight[description].replace("%", "")) / 100
            nilai_only_data[description] = score_value * weight_percent

    # Total
    total_score = sum(score_only_data.values())
    total_nilai = sum(nilai_only_data.values())

    # Merge final dict
    score_data = {**identifier_data, **score_only_data, "Total": total_score}
    nilai_data = {**identifier_data, **nilai_only_data, "Total": total_nilai}
    converted_input_data = {**identifier_data, **scores}

    return score_data, nilai_data, converted_input_data

# %% [markdown]
# ### 6.2 QA Nursery

# %%
def evaluate_kondisi_circle_path_tph(circle_baik, path_baik, tph_baik, pokok_sample):

    perhitungan_kondisi_circle_path_tph = ((circle_baik/pokok_sample) + (path_baik/pokok_sample) + (tph_baik/pokok_sample)) / 3

    if perhitungan_kondisi_circle_path_tph > 90:  # > 90 %
        return 10
    elif 85 < perhitungan_kondisi_circle_path_tph <= 90:  # > 85 - 90 %
        return 8
    elif 80 < perhitungan_kondisi_circle_path_tph <= 85:  # > 80 - 85 %
        return 6
    elif 75 < perhitungan_kondisi_circle_path_tph <= 80:  # > 75 - 80 %
        return 4
    elif perhitungan_kondisi_circle_path_tph <= 75:  # < 75 %
        return 2

# %%
def evaluate_kondisi_gawangan(lalang_tidak_ada, anak_kayu_tidak_ada, prupukan_tidak_ada, purun_tikus_tidak_ada, pakis_udang_tidak_ada, pokok_sample):

    perhitungan_kondisi_gawangan = (((lalang_tidak_ada/pokok_sample) + (anak_kayu_tidak_ada/pokok_sample) + (prupukan_tidak_ada/pokok_sample) + (purun_tikus_tidak_ada/pokok_sample) + (pakis_udang_tidak_ada/pokok_sample)) / 5) * 100

    if perhitungan_kondisi_gawangan > 90:  # > 90 %
        return 10
    elif 85 < perhitungan_kondisi_gawangan <= 90:  # > 85 - 90 %
        return 8
    elif 80 < perhitungan_kondisi_gawangan <= 85:  # > 80 - 85 %
        return 6
    elif 75 < perhitungan_kondisi_gawangan <= 80:  # > 75 - 80 %
        return 4
    elif perhitungan_kondisi_gawangan <= 75:  # < 75 %
        return 2

# %%
def evaluate_pruning_sanitasi(pruning_baik, pokok_sample):
    global perhitungan_pruning
    perhitungan_pruning = (pruning_baik / pokok_sample) * 100

    if perhitungan_pruning > 90:  # > 90 %
        return 10
    elif 85 < perhitungan_pruning <= 90:  # > 85 - 90 %
        return 8
    elif 80 < perhitungan_pruning <= 85:  # > 80 - 85 %
        return 6
    elif 75 < perhitungan_pruning <= 80:  # > 75 - 80 %
        return 4
    elif perhitungan_pruning <= 75:  # < 75 %
        return 2

# %%
def evaluate_susunan_pelepah(pelepah_rapi, pokok_sample):
    global perhitungan_susunan_pelepah
    
    perhitungan_susunan_pelepah = (pelepah_rapi / pokok_sample) * 100

    if perhitungan_susunan_pelepah > 90:  # > 90 %
        return 10
    elif 85 < perhitungan_susunan_pelepah <= 90:  # > 85 - 90 %
        return 8
    elif 80 < perhitungan_susunan_pelepah <= 85:  # > 80 - 85 %
        return 6
    elif 75 < perhitungan_susunan_pelepah <= 80:  # > 75 - 80 %
        return 4
    elif perhitungan_susunan_pelepah <= 75:  # < 75 %
        return 2

# %%
def evaluate_hama_penyakit(serangan_tikus_ada, serangan_rayap_ada, serangan_thirathaba_ada, serangan_updks_ada, pokok_sample):

    perhitungan_hama_penyakit = ((serangan_tikus_ada  + serangan_rayap_ada + serangan_thirathaba_ada + serangan_updks_ada) / pokok_sample) * 100

    if perhitungan_hama_penyakit < 1:  # < 1% damage
        return 10
    elif 1 < perhitungan_hama_penyakit <= 2:  # > 1% - 2% damage
        return 8
    elif 2 < perhitungan_hama_penyakit <= 3:  # > 2% - 3% damage
        return 6
    elif 3 < perhitungan_hama_penyakit <= 5:  # > 3% - 5% damage
        return 4
    elif perhitungan_hama_penyakit > 5:  # > 5% damage
        return 2

# %%
def evaluate_cover_crop(cover_crop, pokok_sample):

    perhitungan_cover_crop = (cover_crop / pokok_sample) * 100

    if perhitungan_cover_crop > 90:  # > 90 %
        return 10
    elif 80 < perhitungan_cover_crop <= 90:  # > 80 - 90 %
        return 8
    elif 70 < perhitungan_cover_crop <= 80:  # > 70 - 80 %
        return 6
    elif 60 < perhitungan_cover_crop <= 70:  # > 60 - 70 %
        return 4
    elif perhitungan_cover_crop <= 60:  # < 60 %
        return 2

# %%
def analyse_qa_nursery(
        identifier_data,
        pokok_sample,
        circle_baik, # tph
        path_baik,
        tph_baik,
        lalang_tidak_ada, # gawangan 
        anak_kayu_tidak_ada,
        perumpung_tidak_ada,
        purun_tikus_tidak_ada,
        pakis_udang_tidak_ada,
        score_titi_panen, # titi panen
        score_jalan_jembatan, # jalan jembatan
        pruning_baik, # pruning sanitasi
        pelepah_rapi, # susunan pelepah
        serangan_tikus_ada, # hama penyakit
        serangan_rayap_ada,
        serangan_thirathaba_ada,
        serangan_updks_ada,
        score_beneficial_plant, # beneficial plant
        score_peilscale, # peilscale
        cover_crop, # cover crop
        score_barn_owl # barn owl
        ):
    
    global combobox_chosen_year, chosen_year_weight
    
    # Check chosen year if its empty
    chosen_year = combobox_chosen_year.get()
    if not chosen_year.strip():
        messagebox.showerror("Error", "Tolong masukkan pilihan tahun.")
        return

    # Get the rule data based on the chosen menu 
    try:
        chosen_year_weight = extract_weights_by_year(YEARLY_WEIGHT_NURSERY, chosen_year)
        print(chosen_year_weight)
    except ValueError as e:
        messagebox.showerror("Error", f"Gagal memuat kriteria untuk tahun {chosen_year}: {e}")
        return
    
    # Evaluate each input
    score_kondisi_circle_path_tph = evaluate_kondisi_circle_path_tph(circle_baik, path_baik, tph_baik, pokok_sample)

    score_kondisi_gawangan = evaluate_kondisi_gawangan(lalang_tidak_ada, anak_kayu_tidak_ada, perumpung_tidak_ada, purun_tikus_tidak_ada, pakis_udang_tidak_ada, pokok_sample)

    score_pruning_sanitasi = evaluate_pruning_sanitasi(pruning_baik, pokok_sample)

    score_susunan_pelepah = evaluate_susunan_pelepah(pelepah_rapi, pokok_sample)

    score_hama_penyakit = evaluate_hama_penyakit(serangan_tikus_ada, serangan_rayap_ada, serangan_thirathaba_ada, serangan_updks_ada, pokok_sample)

    score_cover_crop = evaluate_cover_crop(cover_crop, pokok_sample)
    
    # Store all the calculated scores in to dictionary 
    scores = {
        "Kondisi Circle, Path dan TPH": score_kondisi_circle_path_tph,
        "Kondisi Gawangan": score_kondisi_gawangan,
        "Titi Panen": score_titi_panen,
        "Jalan & Jembatan": score_jalan_jembatan,
        "Pruning dan Sanitasi": score_pruning_sanitasi,
        "Susunan Pelepah": score_susunan_pelepah,
        "Hama Penyakit": score_hama_penyakit,
        "Beneficial Plant": score_beneficial_plant,
        "Peilscale": score_peilscale,
        "Cover Crop (Neprolepis sp.)": score_cover_crop,
        "Barn Owl": score_barn_owl,
    }
    
    # Calculate the final score after yearly weight
    score_only_data = {}
    nilai_only_data = {}

    for description, score_value in scores.items():
        score_only_data[description] = score_value
        if description in chosen_year_weight:
            weight_percent = float(chosen_year_weight[description].replace("%", "")) / 100
            nilai_only_data[description] = score_value * weight_percent

    # Total
    total_score = sum(score_only_data.values())
    total_nilai = sum(nilai_only_data.values())

    # Merge final dict
    score_data = {**identifier_data, **score_only_data, "Total": total_score}
    nilai_data = {**identifier_data, **nilai_only_data, "Total": total_nilai}
    converted_input_data = {**identifier_data, **scores}

    return score_data, nilai_data, converted_input_data

# %% [markdown]
# ### 6.3 QA Fertilizer

# %%
def evaluate_pokok_tidak_terpupuk(pokok_tidak_terpupuk):

    if pokok_tidak_terpupuk == 0:  # 0 pokok
        return 10
    elif 0 < pokok_tidak_terpupuk <= 5:  # 1 - 5 pokok
        return 8
    elif 6 <= pokok_tidak_terpupuk <= 10:  # > 6 - 10 pokok
        return 6
    elif 11 <= pokok_tidak_terpupuk <= 15:  # > 11 - 15 pokok
        return 4
    elif pokok_tidak_terpupuk > 15:  # > 15 pokok
        return 2

# %%
def evaluate_kondisi_piringan_gawangan(piringan_gawangan, pokok_sample):

    perhitungan_piringan_gawangan = ((pokok_sample - piringan_gawangan) / pokok_sample) * 100

    if perhitungan_piringan_gawangan > 95:  # > 95%
        return 10
    elif 85 < perhitungan_piringan_gawangan <= 95:  # 85% - < 95%
        return 8
    elif 75 < perhitungan_piringan_gawangan <= 85:  # 75% - < 85%
        return 6
    elif 65 < perhitungan_piringan_gawangan <= 75:  # 65% - < 75%
        return 4
    elif perhitungan_piringan_gawangan <= 65:  # < 65%
        return 2

# %%
def evaluate_cara_aplikasi(cara_aplikasi_sesuai, total_cara_aplikasi):

    perhitungan_cara_aplikasi = (cara_aplikasi_sesuai / total_cara_aplikasi) * 100

    if perhitungan_cara_aplikasi > 95:  # > 95%
        return 10
    elif 85 < perhitungan_cara_aplikasi <= 95:  # 85% - < 95%
        return 8
    elif 75 < perhitungan_cara_aplikasi <= 85:  # 75% - < 85%
        return 6
    elif 65 < perhitungan_cara_aplikasi <= 75:  # 65% - < 75%
        return 4
    elif perhitungan_cara_aplikasi <= 65:  # < 65%
        return 2

# %%
def evaluate_keseragaman_alat_tabur(keseragaman_alat_tabur, total_alat_tabur):
    perhitungan_keseragaman_alat_tabur = (keseragaman_alat_tabur / total_alat_tabur) * 100

    if perhitungan_keseragaman_alat_tabur == 100:  # 100%
        return 10
    elif 95 < perhitungan_keseragaman_alat_tabur < 100:  # 95% - < 100%
        return 8
    elif 90 < perhitungan_keseragaman_alat_tabur <= 95:  # 90% - < 95%
        return 6
    elif 85 < perhitungan_keseragaman_alat_tabur <= 90:  # 85% - < 90%
        return 4
    elif perhitungan_keseragaman_alat_tabur <= 85:  # < 85%
        return 2

# %%
def evaluate_dosis_alat_tabur(total_dosis_sesuai, total_dosis):
    perhitungan_dosis_alat_tabur = (total_dosis_sesuai / total_dosis) * 100

    if perhitungan_dosis_alat_tabur > 95:  # > 95%
        return 10
    elif 90 < perhitungan_dosis_alat_tabur <= 95:  # 90% - < 95%
        return 8
    elif 85 < perhitungan_dosis_alat_tabur <= 90:  # 85% - < 90%
        return 6
    elif 80 < perhitungan_dosis_alat_tabur <= 85:  # 80% - < 85%
        return 4
    elif perhitungan_dosis_alat_tabur <= 80:  # < 80%
        return 2

# %%
def analyse_qa_fertilizer(
        identifier_data,
        pokok_sample,
        pokok_tidak_terpupuk,
        kondisi_gawangan_semak,
        cara_aplikasi_standar,
        total_cara_aplikasi,
        total_alat_tabur_seragam,
        total_alat_tabur,
        total_dosis_sesuai,
        total_dosis,
        score_tenaga_pemupuk,
        score_supervisi,
        score_pemeriksaan_ancak,
        score_jadwal_pemupukan,
        score_apd_pekerja,
        score_fisik_pupuk,
        score_peletakan_pupuk,
        score_pupuk_tercecer,
        score_pengembalian_karung):
    
    global combobox_chosen_year, chosen_year_weight
    
    # Check chosen year if its empty
    chosen_year = combobox_chosen_year.get()
    if not chosen_year.strip():
        messagebox.showerror("Error", "Tolong masukkan pilihan tahun.")
        return

    # Get the rule data based on the chosen menu 
    try:
        chosen_year_weight = extract_weights_by_year(YEARLY_WEIGHT_FERTILIZER, chosen_year)
        print(chosen_year_weight)
    except ValueError as e:
        messagebox.showerror("Error", f"Gagal memuat kriteria untuk tahun {chosen_year}: {e}")
        return
    
    # Evaluate each input
    score_pokok_tidak_terpupuk = evaluate_pokok_tidak_terpupuk(pokok_tidak_terpupuk)

    score_kondisi_piringan_gawangan = evaluate_kondisi_piringan_gawangan(kondisi_gawangan_semak, pokok_sample)

    score_cara_aplikasi = evaluate_cara_aplikasi(cara_aplikasi_standar, total_cara_aplikasi)

    score_keseragaman_alat_tabur = evaluate_keseragaman_alat_tabur(total_alat_tabur_seragam, total_alat_tabur)

    score_kesesuaian_dosis_alat_tabur = evaluate_dosis_alat_tabur(total_dosis_sesuai, total_dosis)

    print(f"score_keseragaman_alat_tabur: {score_keseragaman_alat_tabur}")
    
    # Store all the calculated scores in to dictionary 
    scores = {
        "Pokok Tidak Terpupuk": score_pokok_tidak_terpupuk,
        "Kondisi Piringan / Gawangan": score_kondisi_piringan_gawangan,
        "Cara Aplikasi": score_cara_aplikasi,
        "Keseragaman Alat Tabur": score_keseragaman_alat_tabur,
        "Kesesuaian Dosis Alat Tabur": score_kesesuaian_dosis_alat_tabur,
        "Tenaga Pemupuk": score_tenaga_pemupuk,
        "Supervisi": score_supervisi,
        "Terdapat Pemeriksaan Ancak Pemupukan": score_pemeriksaan_ancak,
        "Jadwal Pemupukan": score_jadwal_pemupukan,
        "APD Pekerja": score_apd_pekerja,
        "Fisik Pupuk": score_fisik_pupuk,
        "Peletakan Pupuk": score_peletakan_pupuk,
        "Pupuk Tercecer": score_pupuk_tercecer,
        "Pengembalian Karung": score_pengembalian_karung,
    }
    
    # Calculate the final score after yearly weight
    score_only_data = {}
    nilai_only_data = {}

    for description, score_value in scores.items():
        print(f"Description: {description}, Score Value: {score_value}")
        score_only_data[description] = score_value
        if description in chosen_year_weight:
            weight_percent = float(chosen_year_weight[description].replace("%", "")) / 100
            nilai_only_data[description] = score_value * weight_percent

    # Total
    total_score = sum(score_only_data.values())
    total_nilai = sum(nilai_only_data.values())

    # Merge final dict
    score_data = {**identifier_data, **score_only_data, "Total": total_score}
    nilai_data = {**identifier_data, **nilai_only_data, "Total": total_nilai}
    converted_input_data = {**identifier_data, **scores}

    return score_data, nilai_data, converted_input_data

# %% [markdown]
# ### 6.4 QA Chemist

# %%
def evaluate_kematian_gulma(tipe_chemist, kematian_gulma_circle, kematian_gulma_path, kematian_gulma_tph, kematian_gulma_gawangan, pokok_gulma):

    perhitungan_kematian_gulma = 0
    if(tipe_chemist == "Chemist CPT"):
        perhitungan_kematian_gulma = (((kematian_gulma_circle/pokok_gulma) + (kematian_gulma_path/pokok_gulma) + (kematian_gulma_tph/pokok_gulma)) / 3) * 100

    elif(tipe_chemist == "Chemist Gawangan"):
        perhitungan_kematian_gulma = (kematian_gulma_gawangan/pokok_gulma) * 100

    elif(tipe_chemist == "Chemist CPT + Gawangan"):
        perhitungan_kematian_gulma = (((kematian_gulma_circle/pokok_gulma) + (kematian_gulma_path/pokok_gulma) + (kematian_gulma_tph/pokok_gulma) + (kematian_gulma_gawangan/pokok_gulma)) / 4) * 100

    if perhitungan_kematian_gulma > 95:  # > 95%
        return 10
    elif 85 < perhitungan_kematian_gulma <= 95:  # 85% - < 95%
        return 8
    elif 75 < perhitungan_kematian_gulma <= 85:  # 75% - < 85%
        return 6
    elif 65 < perhitungan_kematian_gulma <= 75:  # 65% - < 75%
        return 4
    elif perhitungan_kematian_gulma < 65:  # < 65%
        return 2

# %%
def evaluate_pokok_tersemprot(pokok_tersemprot, pokok_sample):
    perhitungan_pokok_tersemprot = (pokok_tersemprot / pokok_sample) * 100

    if perhitungan_pokok_tersemprot == 0:  # 0%
        return 10
    elif 0 < perhitungan_pokok_tersemprot <= 1:  # > 0% - 1%
        return 8
    elif 1 < perhitungan_pokok_tersemprot <= 2:  # > 1% - 2%
        return 6
    elif 2 < perhitungan_pokok_tersemprot <= 3:  # > 2% - 3%
        return 4
    elif perhitungan_pokok_tersemprot > 3:  # > 3%
        return 2

# %%
def evaluate_alat_semprot(total_alat_semprot_layak, total_tenaga_semprot):
    perhitungan_alat_semprot = (total_alat_semprot_layak / total_tenaga_semprot) * 100

    if perhitungan_alat_semprot == 100:  # 100%
        return 10
    elif 95 <= perhitungan_alat_semprot < 100:  # 95% - < 100%
        return 8
    elif 90 <= perhitungan_alat_semprot < 95:  # 90% - < 95%
        return 6
    elif 85 <= perhitungan_alat_semprot < 90:  # 85% - < 90%
        return 4
    elif perhitungan_alat_semprot < 85:  # < 85%
        return 2

# %%
def evaluate_keseragaman_nozel(total_nozel_seragam, total_tenaga_semprot):
    perhitungan_keseragaman_nozel = (total_nozel_seragam / total_tenaga_semprot) * 100

    if perhitungan_keseragaman_nozel == 100:  # 100%
        return 10
    elif 95 <= perhitungan_keseragaman_nozel < 100:  # 95% - < 100%
        return 8
    elif 90 <= perhitungan_keseragaman_nozel < 95:  # 90% - < 95%
        return 6
    elif 85 <= perhitungan_keseragaman_nozel < 90:  # 85% - < 90%
        return 4
    elif perhitungan_keseragaman_nozel < 85:  # < 85%
        return 2

# %%
def evaluate_dosis_knapsack(perhitungan_dosis_knapsack):

    if perhitungan_dosis_knapsack >= 100:  # > 100%
        return 10
    elif 97.5 <= perhitungan_dosis_knapsack < 100:  # 97.5% - < 100%
        return 8
    elif 95 <= perhitungan_dosis_knapsack < 97.5:  # 95% - < 97.5%
        return 6
    elif 92.5 <= perhitungan_dosis_knapsack < 95:  # 92.5% - < 95%
        return 4
    elif perhitungan_dosis_knapsack < 92.5:  # < 92.5%
        return 2

# %%
def evaluate_penggunaan_hk(tipe_chemist, score_kematian_gulma, total_tenaga_semprot, luas):
    standar = 0
    if(tipe_chemist == "Chemist CPT"):
        standar = 0.5
    elif(tipe_chemist == "Chemist Gawangan"):
        standar = 1.5
    elif(tipe_chemist == "Chemist CPT + Gawangan"):
        standar = 2

    perhitungan_hk = ((luas/total_tenaga_semprot) / standar) * 100

    if 95 < perhitungan_hk <= 100:  # 95% - 100%
        return 10
    elif 90 < perhitungan_hk <= 95:  # 90% - < 95%
        return 8
    elif 95 < perhitungan_hk <= 90:  # 85% - < 90%
        return 6
    elif 80 < perhitungan_hk <= 95:  # 80% - < 85%
        return 4
    elif perhitungan_hk < 80 or perhitungan_hk > 100:  # < 80% or > 100%
        if score_kematian_gulma == 10:
            return 10
        else:
            return 2

# %%
def analyse_qa_chemist(
        identifier_data,
        pokok_sample,
        total_tenaga_semprot,
        luas,
        tipe_chemist,
        pokok_gulma,
        kematian_gulma_circle,
        kematian_gulma_path,
        kematian_gulma_tph,
        kematian_gulma_gawangan,
        pokok_tersemprot,
        score_bahan_herbisida,
        total_alat_semprot_layak,
        total_nozel_seragam,
        kesesuaian_kalibrasi_dosis,
        score_pengendalian_gulma,
        score_p3k,
        score_apd_pekerja,
        score_kartu_pengambilan_pencampuran_bahan,
        score_kalibrasi_alat_nozel,
        score_alat_ukur_perkakas_perbaikan,
        score_peletakan_alat_semprot):
    
    global combobox_chosen_year, chosen_year_weight
    
    # Check chosen year if its empty
    chosen_year = combobox_chosen_year.get()
    if not chosen_year.strip():
        messagebox.showerror("Error", "Tolong masukkan pilihan tahun.")
        return

    # Get the rule data based on the chosen menu 
    try:
        chosen_year_weight = extract_weights_by_year(YEARLY_WEIGHT_CHEMIST, chosen_year)
    except ValueError as e:
        messagebox.showerror("Error", f"Gagal memuat kriteria untuk tahun {chosen_year}: {e}")
        return
    
    # Evaluate each input
    score_kematian_gulma = evaluate_kematian_gulma(tipe_chemist, kematian_gulma_circle, kematian_gulma_path, kematian_gulma_tph, kematian_gulma_gawangan, pokok_gulma)

    score_pokok_tersemprot = evaluate_pokok_tersemprot(pokok_tersemprot, pokok_sample)

    score_kondisi_alat_semprot = evaluate_alat_semprot(total_alat_semprot_layak, total_tenaga_semprot)

    score_kondisi_keseragaman_nozel = evaluate_keseragaman_nozel(total_nozel_seragam, total_tenaga_semprot)

    score_kondisi_standard_dosis_knapsack = evaluate_dosis_knapsack(kesesuaian_kalibrasi_dosis)

    score_kondisi_penggunaan_hk = evaluate_penggunaan_hk(tipe_chemist, score_kematian_gulma, total_tenaga_semprot, luas)
    
    # Store all the calculated scores in to dictionary 
    scores = {
        "Kematian Gulma": score_kematian_gulma,
        "Pokok Tersemprot": score_pokok_tersemprot,
        "Bahan Herbisida yang Dibawa ke Ancak": score_bahan_herbisida,
        "Kondisi Alat Semprot": score_kondisi_alat_semprot,
        "Keseragaman Nozel": score_kondisi_keseragaman_nozel,
        "Dosis per Knapsack Sesuai Standar Kalibrasi": score_kondisi_standard_dosis_knapsack,
        "Program Pengendalian Gulma": score_pengendalian_gulma,
        "Penggunaan HK Sesuai Norma Pekerjaan": score_kondisi_penggunaan_hk,
        "Kotak P3K Isi Lengkap dan Dibawa Oleh Mandor": score_p3k,
        "APD Pekerja": score_apd_pekerja,
        "Terdapat Kartu Pengambilan dan Pencampuran Bahan": score_kartu_pengambilan_pencampuran_bahan,
        "Terdapat Kalibrasi Alat dan Nozel": score_kalibrasi_alat_nozel,
        "Membawa Gelas Ukur & Perkakas Perbaikan Alat Semprot": score_alat_ukur_perkakas_perbaikan,
        "Peletakan Alat Semprot": score_peletakan_alat_semprot,
    }
    
    # Calculate the final score after yearly weight
    score_only_data = {}
    nilai_only_data = {}

    for description, score_value in scores.items():
        score_only_data[description] = score_value
        if description in chosen_year_weight:
            weight_percent = float(chosen_year_weight[description].replace("%", "")) / 100
            nilai_only_data[description] = score_value * weight_percent

    # Total
    total_score = sum(score_only_data.values())
    total_nilai = sum(nilai_only_data.values())

    # Merge final dict
    score_data = {**identifier_data, **score_only_data, "Total": total_score}
    nilai_data = {**identifier_data, **nilai_only_data, "Total": total_nilai}
    converted_input_data = {**identifier_data, **scores}

    return score_data, nilai_data, converted_input_data

# %% [markdown]
#  ## 8. GUI - Utility Functions

# %%
# (Place this function definition somewhere appropriate, e.g., Section 11)
def exit_fullscreen(event=None):
    """Exits fullscreen mode when the Escape key is pressed."""
    global root
    if root:
        print("Escape key pressed, exiting fullscreen.") # Feedback
        root.attributes('-fullscreen', False)
        # Optional: You might want to set a default size after exiting fullscreen
        # root.geometry("1200x800") # Example size
        # Or, just let it revert to its natural size based on content/previous state.

# %%
def configure_bg(color):
    """Sets the background color of the root window."""
    # Simplified: Only set root background. Widgets keep default or specific colors.
    if not root_exists:
        return
    root.configure(bg=color)

# %%
def get_date(entry_widget):
    """Creates a calendar popup and inserts the selected date (yyyy-mm-dd) into the entry widget."""
    if not root_exists: return

    def set_date():
        if not root_exists: return
        selected_date = cal.get_date() # This is "yyyy-mm-dd" from tkcalendar
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, selected_date)
        top.destroy()

    top = tk.Toplevel(root)
    today = datetime.datetime.now(CURRENT_TIMEZONE)
    cal = Calendar(top, font="Arial 10", selectmode='day',
                   year=today.year, month=today.month, day=today.day,
                   date_pattern="yyyy-mm-dd") # Keep this pattern for consistency
    cal.pack(pady=20)
    confirm_button = tk.Button(top, text="OK", command=set_date)
    confirm_button.pack(pady=10)
    top.transient(root)
    top.grab_set()
    top.wait_window(top)

# %%
def hide_all_widgets():
    """Hides ALL widgets gridded directly onto the root window."""
    if not root_exists: return
    # Be more specific: Hide only widgets placed with grid on root
    for widget in root.grid_slaves():
         widget.grid_forget()

# %% [markdown]
#  ## 9. GUI - Screen Creation Functions

# %%
def create_main_widgets():
    global label_username, entry_username, previous_menu, current_menu, back_button, exit_button, label_menu_qa, combobox_menu_qa, label_menu_data_overview, combobox_menu_data_overview, label_chosen_year, combobox_chosen_year, label_note_year, button_goto_chosen_qa_menu, button_goto_processed_pdf, button_goto_chosen_analytic_menu, button_analisa_pemupukan, username_var, label_saved_username, username, df # Add df

    if not root_exists: return
    root.geometry("500x400")
    current_menu = "main"
    configure_bg("#f0f0f0") # Default background

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---
    
    # --- Username Section ---
    row_offset = 0 
    if not username:
        label_username = make_label(parent=root, text="Masukkan Username:", row=row_offset, font=("Arial", 12, "bold"))
        row_offset += 1
        entry_username = make_entry(parent=root, row=row_offset, textvariable=username_var)
        row_offset += 1

        if not username_var.trace_info(): 
             username_var.trace_add("write", lambda *args: set_username())
    else:
        label_saved_username = make_label(parent=root, text=f"Masuk ke sistem sebagai: {username}", row=row_offset)
        row_offset += 2

    # --- QA Section ---
    label_qa_section_title = make_label(parent=root, text="Quality Assurance", row=row_offset, font=("Arial", 14, "bold"))
    row_offset += 1

    label_menu_qa = make_label(parent=root, text="Pilih Jenis QA:", row=row_offset, font=("Arial", 12))
    row_offset += 1

    combobox_menu_qa = ttk.Combobox(root, values=QA_TYPE, width=30, font=("Arial", 10))
    combobox_menu_qa.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    # --- Yearly Weight ---
    label_chosen_year = make_label(parent=root, text="Pilih Bobot Tahun:", row=row_offset, font=("Arial", 12))
    row_offset += 1

    combobox_chosen_year = ttk.Combobox(root, values=AVAILABLE_YEAR, width=30, font=("Arial", 10))
    combobox_chosen_year.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_note_year = make_label(parent=root, text="Catatan: Untuk tahun 2027 ke atas, gunakan bobot tahun 2027", row=row_offset, font=("Arial", 10, "italic"), fg="red")
    row_offset += 1

    # --- Buttons ---
    button_goto_chosen_qa_menu = make_button(root, text="Submit Menu", row=row_offset, command=goto_chosen_qa_menu, font=("Arial", 12))
    row_offset += 1

    # --- PDFs ---
    label_goto_processed_pdf_title = make_label(parent=root, text="Processed PDF", row=row_offset, font=("Arial", 14, "bold"))
    row_offset += 1

    button_goto_processed_pdf = make_button(root, text="PDF List", row=row_offset, command=goto_processed_pdf, font=("Arial", 12))
    row_offset += 1

    # --- Data Overview Section ---
    label_data_overview_section_title = make_label(parent=root, text="Data Overview", row=row_offset, font=("Arial", 14, "bold"))
    row_offset += 1

    label_menu_data_overview = make_label(parent=root, text="Pilih Jenis QA Untuk Analisis Data Overview:", row=row_offset, font=("Arial", 12))
    row_offset += 1

    combobox_menu_data_overview = ttk.Combobox(root, values=QA_TYPE, width=30, font=("Arial", 10))
    combobox_menu_data_overview.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    button_goto_chosen_data_overview_menu = make_button(root, text="Submit Menu", row=row_offset, command=goto_chosen_data_overview_menu, font=("Arial", 12))
    row_offset += 1

    exit_button = make_button(root, text="Exit", row=row_offset, command=on_closing, font=("Arial", 12), bg=EXIT_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row_offset += 1

    previous_menu = None
    back_button = None

# %%
def start_main_app():
    """Destroys splash screen elements, loads data, and starts the main app."""
    global splash_label, splash_button, root, df, sheet_data, sheet_output

    if not root_exists: return # Exit if window closed prematurely

    # Destroy splash screen widgets
    if splash_label:
        splash_label.destroy()
    if splash_button:
        splash_button.destroy()

    # Reset background color to light gray  after splash screen
    root.configure(bg="#f0f0f0")

    # --- Load Initial Data ---
    print("Loading initial data...")
    load_database(SHEET_URL, JSON_PATH)
    
    # --- Now create the main application widgets ---
    create_main_widgets()

# %%
def create_splash_screen():
    """Creates and displays the splash screen."""
    global splash_label, splash_button, root

    if not root_exists: return

    # Ensure root window is clean (optional, good practice)
    for widget in root.winfo_children():
        widget.destroy()

    try:
        # --- Load and Resize Image ---
        image_path = SPLASH_IMAGE # <-- REPLACE with your image filename
        if not os.path.exists(image_path):
             messagebox.showerror("Error", f"Splash image not found at:\n{image_path}")
             # Fallback or exit? Let's proceed without image for now
             img = None
             photo_image = None
        else:
            # Get screen size
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            # Open image with Pillow
            img_original = Image.open(image_path)

            # Resize to fit screen (using LANCZOS for good quality)
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS

            img_resized = img_original.resize((screen_width, screen_height), resample_filter)

            # Convert to Tkinter PhotoImage
            photo_image = ImageTk.PhotoImage(img_resized)

        # --- Create Label for Image ---
        splash_label = tk.Label(root, image=photo_image)
        # IMPORTANT: Keep a reference to the image to prevent garbage collection
        if photo_image:
            splash_label.image = photo_image
        splash_label.place(x=0, y=0, relwidth=1, relheight=1) # Cover entire window

        splash_button = tk.Button(root, text="Start", command=start_main_app, font=("Arial", 14, "bold"), bg="#3f4726", fg="white", relief=tk.RAISED, bd=3)
        
        splash_button.place(relx=0.27, rely=1.0, anchor='se', x=0, y=-20)

    except FileNotFoundError:
         messagebox.showerror("Error", f"Splash image file not found: {image_path}")
         root.after(100, start_main_app)
    except Exception as e:
        messagebox.showerror("Splash Screen Error", f"Could not load splash screen: {e}")
        traceback.print_exc()
        root.after(100, start_main_app)

# %% [markdown]
#  ## 10. GUI - Navigation & Action Functions

# %% [markdown]
# ### 10.1 QA Production

# %%
def convert_berondolan_tertinggal_to_score(berondolan_tertinggal):
    """Convert Berondolan Tertinggal to score."""
    if berondolan_tertinggal == "< 0,5 butir/pkk":
        return 10
    elif berondolan_tertinggal == "> 0,5 - 0,6 butir/pkk":
        return 8
    elif berondolan_tertinggal == "> 0,6 - 0,75 butir/pkk":
        return 6
    elif berondolan_tertinggal == "> 0,75 - 1 butir/pkk":
        return 4
    elif berondolan_tertinggal == "> 1 butir/pkk":
        return 2

# %%
def convert_buah_tertinggal_tph_to_score(buah_tertinggal_tph):
    """Convert Buah Tertinggal TPH to score."""
    if buah_tertinggal_tph == "0 jjg":
        return 10
    elif buah_tertinggal_tph == "> 0 - 0,2 jjg":
        return 8
    elif buah_tertinggal_tph == "> 0,2 - 0,4 jjg":
        return 6
    elif buah_tertinggal_tph == "> 0,4 - 0,6 jjg":
        return 4
    elif buah_tertinggal_tph == "> 0,6 jjg":
        return 2

# %%
def convert_berondolan_tertinggal_tph_to_score(berondolan_tertinggal_tph):
    """Convert Berondolan Tertinggal TPH to score."""
    if berondolan_tertinggal_tph == "< 5 butir":
        return 10
    elif berondolan_tertinggal_tph == "> 5 - 7 butir":
        return 8
    elif berondolan_tertinggal_tph == "> 7 - 10 butir":
        return 6
    elif berondolan_tertinggal_tph == "> 10 - 12 butir":
        return 4
    elif berondolan_tertinggal_tph == "> 12 butir":
        return 2

# %%
def submit_production_analysis():
    global df_mobile_produksi_input, entry_tanggal_qa_terakhir, selected_estate, selected_divisi, selected_blok, entry_mandor, available_blok_list, tph_counter, label_chosen_year, combobox_chosen_year, diperiksa, mandor, pokok_sample, sph, setara_ha, berondolan_tinggal_sph, buah_tinggal_sph,  buah_busuk_sph

    try:
        sph = cek_entry_number("sph", entry_sph, 0.0)
        actual = cek_entry_number("entry", entry_actual, 0.0)
        budget = cek_entry_number("budget", entry_budget, 0.0)
        restan = cek_entry_number("restan", entry_restant, 0.0)
        jaring = cek_entry_number("jaring", entry_jaring, 0.0)
        produktivitas_pemanen = cek_entry_number("produktivitas pemanen", entry_produktivitas_pemanen, 0.0)
        administrasi_panen = cek_entry_number("administrasi panen", entry_administrasi_panen, 0.0)
        kualitas_tbs = cek_entry_number("kualitas TBS", entry_kualitas_tbs, 0.0)
        muatan_overload = cek_entry_number("muatan overload", entry_muatan_overload, 0.0)
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate = selected_estate.get() if selected_estate else ""
    divisi = selected_divisi.get() if selected_divisi else ""
    blok = selected_blok.get() if selected_blok else ""
    mandor = entry_mandor.get().strip()

    if not validate_required_fields({
        "Tanggal": tanggal_str,
        "Estate": estate,
        "Divisi": divisi,
        "Blok": blok,
        "Mandor": mandor
    }):
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except Exception:
        messagebox.showerror("Error", "Format tanggal tidak valid.")
        return

    # 🔹 Ambil tahun QA dari combobox
    try:
        chosen_year = int(combobox_chosen_year.get())
    except ValueError:
        messagebox.showerror("Error", "Tahun QA belum dipilih atau tidak valid.")
        return

    try:
        divisi_val = int(divisi) if str(divisi).isdigit() else divisi
        filtered_df = df_mobile_produksi_input[
            (df_mobile_produksi_input['Tanggal'] == tanggal_dt) &
            (df_mobile_produksi_input['Kebun'] == estate) &
            (df_mobile_produksi_input['Divisi'] == divisi_val) &
            (df_mobile_produksi_input['Blok'] == blok)
        ]
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi error saat filter data: {e}")
        return

    if filtered_df.empty:
        messagebox.showerror("Error", "Data tidak ditemukan untuk kombinasi input tersebut.")
        return

    if blok in available_blok_list:
        available_blok_list.remove(blok)
        update_blok_combobox()

    diperiksa = filtered_df["Nama Petugas"].iloc[0]
    estate = filtered_df["Kebun"].iloc[0]
    divisi = filtered_df["Divisi"].iloc[0]
    pokok_sample = float(filtered_df["Jumlah Pokok"].sum())
    setara_ha = pokok_sample/sph
    pokok_dipanen = float(filtered_df["Pkk Dipanen"].sum())
    pokok_panen = float(filtered_df["Pkk Dipanen"].sum())
    buah_panen = float(filtered_df["Buah Dipanen"].sum())
    berondolan_tertinggal = float(filtered_df["LF Tinggal"].sum())
    buah_tertinggal = float(filtered_df["Buah Matang Tidak Dipanen"].sum() + filtered_df["Buah Tinggal (pr, pk, pp, lp)"].sum())
    tbs_busuk_tertinggal = float(filtered_df["Buah Busuk Tidak Dipanen"].sum())
    berondolan_tertinggal_tph = float(filtered_df["LF Tinggal (TPH)"].sum())
    buah_tertinggal_tph = float(filtered_df["Buah Tinggal (TPH)"].sum())
    tph_counter = float(filtered_df["TPH Counter"].sum())
    panen_rotasi = filtered_df["Rotasi"].iloc[0]

    # Hitung keterangan SPH
    berondolan_tinggal_sph = berondolan_tertinggal/setara_ha
    buah_tinggal_sph = buah_tertinggal/setara_ha
    buah_busuk_sph = tbs_busuk_tertinggal/setara_ha

    identifier_data = {
        "Blok": blok,
        "Panen Rotasi": panen_rotasi,
        "Tanggal Periksa": tanggal_str,
        "DivisiLabel": f"{estate}-{divisi}",
        "Divisi": divisi,
        "Estate": estate,
    }

    # 🔹 Data QA lengkap (versi 2025 ke atas)
    actual_data = {
        "Jumlah Pokok Sample": pokok_sample,
        "Jumlah Pokok Panen": pokok_panen,
        "Actual": actual,
        "Budget": budget,
        "Jumlah Buah Panen": buah_panen,
        "Jumlah Buah Tertinggal": buah_tertinggal,
        "Berondolan Tinggal/Tersangkut": berondolan_tertinggal,
        "Jumlah Buah Tinggal": buah_tertinggal_tph,
        "Jumlah Berondolan Tinggal": berondolan_tertinggal_tph,
        "Rotasi Panen": panen_rotasi,
        "Restan": restan,
        "Pemakaian Jaring/Terpal": jaring,
        "Kualitas Panen -TBS Busuk Tinggal": tbs_busuk_tertinggal,
        "Produktivitas Pemanen": produktivitas_pemanen,
        "Administrasi Panen": administrasi_panen,
        "Kualitas TBS": kualitas_tbs,
        "Muatan Overload": muatan_overload,
    }

    # 🔹 Filter otomatis berdasarkan tahun QA
    if chosen_year < 2025:
        keys_until_tbs_busuk = list(actual_data.keys())[:12]  # ambil sampai “Kualitas Panen -TBS Busuk Tinggal”
        actual_data = {k: actual_data[k] for k in keys_until_tbs_busuk}

    input_data = {**identifier_data, **actual_data}

    # 🔹 Proses analisis QA
    final_qa_score, final_qa_nilai, converted_input = analyse_qa_production(
        identifier_data,
        pokok_sample,
        pokok_dipanen,
        actual,
        budget,
        buah_tertinggal,
        berondolan_tertinggal,
        buah_tertinggal_tph,
        berondolan_tertinggal_tph,
        tph_counter,
        panen_rotasi,
        restan,
        jaring,
        tbs_busuk_tertinggal,
        produktivitas_pemanen,
        administrasi_panen,
        kualitas_tbs,
        muatan_overload)
    
    # Commented this for now as it is slowing the process
    # process_uploaded_photos()    
    
    # Save all the input and procesed datas into the spreadsheets
    save_to_sheet(input_production, "Input - Production", input_data)
    save_to_sheet(output_production, "Output - Production", final_qa_score)
    save_to_sheet(output_weight_production, "Output (Weight) - Production", final_qa_nilai)
    
    # Generate PDF hasil sesuai tahun QA
    generate_pdf_output(final_qa_score, final_qa_nilai, combobox_menu_qa.get(), input_data)

    # Upload PDF to Google Drive
    proceed_to_upload_pdf()

    # Clear cached photos data
    photos_data.clear()
    pdf_data.clear()

    # Display success window and go back to main menu
    show_success_window()

# %% [markdown]
# ### 10.2 QA Nursery

# %%
def convert_titi_panen_to_score(titi_panen):
    """Convert Titi Panen to score."""
    if titi_panen == "Rasio Standar, Permanen, Kondisi Baik":
        return 10
    elif titi_panen == "Rasio Standar, Semi Permanen, Kondisi Baik":
        return 8
    elif titi_panen == "Rasio Kurang Standar, Semi Permanen, Kondisi Baik":
        return 6
    elif titi_panen == "Rasio Kurang Standar, Semi Permanen, Kondisi Rusak":
        return 4
    elif titi_panen == "Tidak Ada Sama Sekali":
        return 2

# %%
def convert_jalan_jembatan_to_score(jalan_jembatan):
    """Convert Jalan/Jembatan to score."""
    if jalan_jembatan == "Jalan Rata (Tidak Lubang/Rel), Jembatan Permanen":
        return 10
    elif jalan_jembatan == "Jalan Kondisi Sedang, Jembatan Permanen":
        return 8
    elif jalan_jembatan == "Jalan Rusak Sebagian, Jembatan Rusak Sebagian":
        return 6
    elif jalan_jembatan == "Jalan Dominan Rusak, Jembatan Rusak":
        return 4
    elif jalan_jembatan == "Jalan Rusak Parah, Jembatan Rusak Parah":
        return 2

# %%
def convert_beneficial_plant_to_score(beneficial_plant):
    """Convert Beneficial Plan to score."""
    if beneficial_plant == "Semua ruas jalan terdapat tanaman rasio 10m2/ha":
        return 10
    elif beneficial_plant == "Salah satu MR atau CR saja, populasi sesuai rasio":
        return 8
    elif beneficial_plant == "Salah satu MR atau CR saja, populasi < rasio":
        return 6
    elif beneficial_plant == "Salah satu MR atau CR, jarang dan tidak terawat":
        return 4
    elif beneficial_plant == "Tidak dijumpai tanaman sama sekali":
        return 2

# %%
def convert_peilscale_to_score(peilscale):
    """Convert Peilscale to score."""
    if peilscale == "> -30cm, kondisi baik, update":
        return 10
    elif peilscale == "-30cm sampai -20cm , kondisi sedang, update":
        return 8
    elif peilscale == "-20cm sampai -10cm, kondisi sedang, update":
        return 6
    elif peilscale == "-10cm sampai 0cm, kondisi rusak, update":
        return 4
    elif peilscale == ">0cm, kondisi rusak, tidak update":
        return 2

# %%
def convert_barn_owl_to_score(barn_owl):
    """Convert Barn Owl to score."""
    if barn_owl == "Rasio gupon <40 ha, Ada burung hantu, gupon aktif, kondisi baik, sensus rutin":
        return 10
    elif barn_owl == "Ada burung hantu, gupon aktif, kondisi baik, sensus rutin":
        return 8
    elif barn_owl == "Ada atau tidak ada burung hantu, gupon aktif, kondisi baik atau rusak, sensus jarang":
        return 6
    elif barn_owl == "Tidak ada burung hantu, ada gupon, kondisi baik atau rusak, sensus jarang":
        return 4
    elif barn_owl == "Tidak ada burung hantu, tidak ada gupon, sensus tidak":
        return 2

# %%
def submit_nursery_analysis(): 
    global df_mobile_perawatan_input, entry_tanggal_qa_terakhir, selected_estate, selected_divisi, selected_blok, entry_mandor, available_blok_list, diperiksa, mandor, pokok_sample

    try:
        cover_crop = cek_entry_number("cover crop", entry_cover_crop, 0.0)
        barn_owl = check_combobox("barn owl", combobox_barn_owl, BARN_OWL_OPTIONS, BARN_OWL_OPTIONS[-1])
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    # Ambil nilai input
    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate = selected_estate.get() if selected_estate else ""
    divisi = selected_divisi.get() if selected_divisi else ""
    blok = selected_blok.get() if selected_blok else ""
    mandor = entry_mandor.get().strip()

    # Validasi input kosong/None
    if not validate_required_fields({
        "Tanggal": tanggal_str,
        "Estate": estate,
        "Divisi": divisi,
        "Blok": blok,
        "Mandor": mandor
    }):
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except Exception:
        messagebox.showerror("Error", "Format tanggal tidak valid.")
        return

    try:
        divisi_val = int(divisi) if str(divisi).isdigit() else divisi
        filtered_df = df_mobile_perawatan_input[
            (df_mobile_perawatan_input['Tanggal'] == tanggal_dt) &
            (df_mobile_perawatan_input['Kebun'] == estate) &
            (df_mobile_perawatan_input['Divisi'] == divisi_val) &
            (df_mobile_perawatan_input['Blok'] == blok)
        ]
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi error saat filter data: {e}")
        return

    if filtered_df.empty:
        messagebox.showerror("Error", "Data tidak ditemukan untuk kombinasi input tersebut.")
        return
    
    # Remove the processed blok
    if blok in available_blok_list:
        available_blok_list.remove(blok)
        update_blok_combobox()

    # Get the values from the filtered DataFrame
    diperiksa = filtered_df["Nama Petugas"].iloc[0]
    estate = filtered_df["Kebun"].iloc[0]
    divisi = filtered_df["Divisi"].iloc[0]
    pokok_sample = filtered_df["Jumlah Pokok"].sum()
    beneficial_plant = filtered_df["Beneficial Plant"].iloc[0]
    peilscale = filtered_df["Peilscale"].iloc[0]
    circle_baik = filtered_df["Kondisi Circle Baik"].sum()
    circle_tidak_baik = filtered_df["Kondisi Circle Semak"].sum() + filtered_df["Kondisi Circle Dominan Anak Sawit"].sum()+ filtered_df["Kondisi Circle Dominan Sampah (Berondolan Busuk)"].sum()
    path_baik = filtered_df["Kondisi Path Baik"].sum()
    path_tidak_baik = filtered_df["Kondisi Path Tidak Baik"].sum()
    tph_baik = (filtered_df["Kondisi TPH"] == "Baik").sum()
    tph_tidak_baik = (filtered_df["Kondisi TPH"] == "Tidak Baik").sum()
    lalang_ada = filtered_df["Lalang Ada"].sum()
    lalang_tidak_ada = filtered_df["Lalang Tidak Ada"].sum()
    anak_kayu_ada = filtered_df["Anak Kayu Ada"].sum()
    anak_kayu_tidak_ada = filtered_df["Anak Kayu Tidak Ada"].sum()
    perumpung_ada = filtered_df["Perumpung Ada"].sum()
    perumpung_tidak_ada = filtered_df["Perumpung Tidak Ada"].sum()
    purun_tikus_ada = filtered_df["Purun Tikus Ada"].sum()
    purun_tikus_tidak_ada = filtered_df["Purun Tikus Tidak Ada"].sum()
    pakis_udang_ada = filtered_df["Pakis Udang Ada"].sum()
    pakis_udang_tidak_ada = filtered_df["Pakis Udang Tidak Ada"].sum()
    titi_panen = filtered_df["Titi Panen"].iloc[0]
    jalan_jembatan = filtered_df["Jalan Jembatan"].iloc[0]
    pruning_baik = filtered_df["Pruning Baik"].sum()
    pruning_over = filtered_df["Pruning Over"].sum()
    pruning_sengkleh = filtered_df["Pruning Sengkleh"].sum()
    pruning_under = filtered_df["Pruning Under"].sum()
    pelepah_rapi = filtered_df["Susunan Pelepah Rapi"].sum()
    pelepah_tidak_rapi = filtered_df["Susunan Pelepah Tidak Rapi"].sum()
    serangan_tikus_ada = filtered_df["Serangan Tikus Ada"].sum()
    serangan_tikus_tidak_ada = filtered_df["Serang Tikus Tidak Ada"].sum()
    serangan_rayap_ada = filtered_df["Serangan Rayap Ada"].sum()
    serangan_rayap_tidak_ada = filtered_df["Serangan Rayap Tidak Ada"].sum()
    serangan_thirathaba_ada = filtered_df["Thirathaba Ada"].sum()
    serangan_thirathaba_tidak_ada = filtered_df["Thirathaba Tidak Ada"].sum()
    serangan_updks_ada = filtered_df["UPDPKS Ada"].sum()
    serangan_updks_tidak_ada = filtered_df["UPDPKS Tidak Ada"].sum()
        
    # Convert combobox option to float
    score_titi_panen = convert_titi_panen_to_score(titi_panen)

    score_jalan_jembatan = convert_jalan_jembatan_to_score(jalan_jembatan)

    score_beneficial_plant = convert_beneficial_plant_to_score(beneficial_plant)

    score_peilscale = convert_peilscale_to_score(peilscale)

    score_barn_owl = convert_barn_owl_to_score(barn_owl)
    
    # Compose a new dictionary for the input
    # Identifier info
    identifier_data = {
        "Blok": blok,
        "Tanggal Periksa": tanggal_str,
        "DivisiLabel": f"{estate}-{divisi}", 
        "Divisi": divisi,
        "Estate": estate,
    }

    actual_data = {
        "Jumlah Pokok Sample": pokok_sample,
        "Circle Baik": circle_baik,
        "Circle Tidak Baik": circle_tidak_baik,
        "Path Baik": path_baik,
        "Path Tidak Baik": path_tidak_baik,
        "TPH Baik": tph_baik,
        "TPH Tidak Baik": tph_tidak_baik,
        "Lalang Ada": lalang_ada,
        "Lalang Tidak Ada": lalang_tidak_ada,
        "Anak Kayu Ada": anak_kayu_ada,
        "Anak Kayu Tidak Ada": anak_kayu_tidak_ada,
        "Perumpung Ada": perumpung_ada,
        "Perumpung Tidak Ada": perumpung_tidak_ada,
        "Purun Tikus Ada": purun_tikus_ada,
        "Purun Tikus Tidak Ada": purun_tikus_tidak_ada,
        "Pakis Udang Ada": pakis_udang_ada,
        "Pakis Udang Tidak Ada": pakis_udang_tidak_ada,
        "Titi Panen": titi_panen,
        "Jalan Jembatan": jalan_jembatan,
        "Pruning Baik": pruning_baik,
        "Pruning Over": pruning_over,
        "Pruning Sengkleh": pruning_sengkleh,
        "Pruning Under": pruning_under,
        "Pelepah Rapi": pelepah_rapi,
        "Pelepah Tidak Rapi": pelepah_tidak_rapi,
        "Serangan Tikus Ada": serangan_tikus_ada,
        "Serangan Tikus Tidak Ada": serangan_rayap_tidak_ada,
        "Serangan Rayap Ada": serangan_rayap_ada,
        "Serangan Rayap Tidak Ada": serangan_rayap_tidak_ada,
        "Serangan Thirathaba Ada": serangan_thirathaba_ada,
        "Serangan Thirathaba Tidak Ada": serangan_thirathaba_tidak_ada,
        "Serangan UPDKS Ada": serangan_updks_ada,
        "Serangan UPDKS Tidak Ada": serangan_updks_tidak_ada,
        "Beneficial Plant": score_beneficial_plant,
        "Peilscale": score_peilscale,
        "Cover Crop": cover_crop,
        "Barn Owl": score_barn_owl,
    }

    input_data = {**identifier_data, **actual_data}
    
    # Analyze the input values 
    final_qa_score, final_qa_nilai, converted_input = analyse_qa_nursery(
        identifier_data,
        pokok_sample,
        circle_baik, # tph
        path_baik,
        tph_baik,
        lalang_tidak_ada, # gawangan 
        anak_kayu_tidak_ada,
        perumpung_tidak_ada,
        purun_tikus_tidak_ada,
        pakis_udang_tidak_ada,
        score_titi_panen, # titi panen
        score_jalan_jembatan, # jalan jembatan
        pruning_baik, # pruning sanitasi
        pelepah_rapi, # susunan pelepah
        serangan_tikus_ada, # hama penyakit
        serangan_rayap_ada,
        serangan_thirathaba_ada,
        serangan_updks_ada,
        score_beneficial_plant, # beneficial plant
        score_peilscale, # peilscale
        cover_crop, # cover crop
        score_barn_owl # barn owl
        )
    
    # Commented this for now as it is slowing the process
    # process_uploaded_photos()
        
    # Save all the input and procesed datas into the spreadsheets
    save_to_sheet(input_nursery, "Input - Nursery", input_data)
    save_to_sheet(output_nursery, "Output - Nursery", final_qa_score)
    save_to_sheet(output_weight_nursery, "Output (Weight) - Nursery", final_qa_nilai)

    # Compose PDF report
    generate_pdf_output(final_qa_score, final_qa_nilai, combobox_menu_qa.get(), converted_input)

    # Upload PDF to Google Drive
    proceed_to_upload_pdf()

    # Clear cached photos data
    photos_data.clear()
    pdf_data.clear()

    # Display success window and go back to main menu
    show_success_window()

# %% [markdown]
# ### 10.3 QA Fertilizer

# %%
def convert_tenaga_pemupuk_to_score(tenaga_pemupuk):
    """Convert Tenaga Pemupuk to score."""
    if tenaga_pemupuk == "Organisasi tetap, training rutin":
        return 10
    elif tenaga_pemupuk == "Organisasi tetap, tetapi training tidak rutin":
        return 8
    elif tenaga_pemupuk == "Organisasi tidak tetap, training rutin":
        return 6
    elif tenaga_pemupuk == "Organisasi tidak tetap, training tidak rutin":
        return 4
    elif tenaga_pemupuk == "Organisasi tidak tetap, tidak ada training":
        return 2

# %%
def convert_supervisi_to_score(supervisi):
    """Convert Supervisi to score."""
    if supervisi == "Lengkap":
        return 10
    elif supervisi == "Ada semua kecuali tidak ada Assistant / Mandor 1":
        return 8
    elif supervisi == "Ada semua kecuali tidak ada Assistant & Security":
        return 6
    elif supervisi == "Ada semua kecuali tidak ada Assistant & Mandor":
        return 4
    elif supervisi == "Tidak ada sama sekali supervisi":
        return 2

# %%
def convert_pemeriksaan_ancak_to_score(pemeriksaan_ancak):
    """Convert Pemeriksaan Ancak to score."""
    if pemeriksaan_ancak == "100%":
        return 10
    elif pemeriksaan_ancak == "95% - < 100%":
        return 8
    elif pemeriksaan_ancak == "90% - < 95%":
        return 6
    elif pemeriksaan_ancak == "85% - < 90%":
        return 4
    elif pemeriksaan_ancak == "< 85%":
        return 2

# %%
def convert_jadwal_pemupukan_to_score(jadwal_pemupukan):
    """Convert Jadwal Pemupukan to score."""
    if jadwal_pemupukan == "Sesuai bulan rekomendasi":
        return 10
    elif jadwal_pemupukan == "Terlambat / maju 1 bulan":
        return 8
    elif jadwal_pemupukan == "Terlambat / maju 2 bulan":
        return 6
    elif jadwal_pemupukan == "Terlambat / maju 3 bulan":
        return 4
    elif jadwal_pemupukan == "Terlambat / maju > 3 bulan":
        return 2

# %%
def convert_apd_pekerja_to_score(apd_pekerja):
    """Convert APD Pekerja to score."""
    if apd_pekerja == "Lengkap":
        return 10
    elif apd_pekerja == "Kurang dari 1 item":
        return 8
    elif apd_pekerja == "Kurang dari 2 item":
        return 6
    elif apd_pekerja == "Kurang dari 3 item":
        return 4
    elif apd_pekerja == "Tidak ada APD":
        return 2

# %%
def convert_fisik_pupuk_to_score(fisik_pupuk):
    """Convert Fisik Pupuk to score."""
    if fisik_pupuk == "Tekstur baik, kondisi kering":
        return 10
    elif fisik_pupuk == "Tekstur baik, sebagian menggumpal":
        return 8
    elif fisik_pupuk == "Tekstur kurang baik, sebagian menggumpal":
        return 6
    elif fisik_pupuk == "Tekstur tidak baik, sebagian menggumpal":
        return 4
    elif fisik_pupuk == "Tekstur tidak baik, semua menggumpal":
        return 2

# %%
def convert_peletakan_pupuk_to_score(peletakan_pupuk):
    """Convert Peletakan Pupuk to score."""
    if peletakan_pupuk == "Di TPP / dalam blok, dekat piringan":
        return 10
    elif peletakan_pupuk == "Dalam blok, jauh dari piringan":
        return 8
    elif peletakan_pupuk == "Di badan jalan sebagian":
        return 6
    elif peletakan_pupuk == "Semua diletak di badan jalan":
        return 4
    elif peletakan_pupuk == "Masuk ke parit jalan":
        return 2

# %%
def convert_pupuk_tercecer_to_score(pupuk_tercecer):
    """Convert Pupuk Tercecer to score."""
    if pupuk_tercecer == "0%":
        return 10
    elif pupuk_tercecer == "> 0% - 1%":
        return 8
    elif pupuk_tercecer == "> 1% - 2%":
        return 6
    elif pupuk_tercecer == "> 2% - 3%":
        return 4
    elif pupuk_tercecer == "> 3%":
        return 2

# %%
def convert_pengembalian_karung_to_score(pengembalian_karung):
    """Convert Pengembalian Karung to score."""
    if pengembalian_karung == "Rapi, gulungan 10 lembar, dikumpul pada hari H":
        return 10
    elif pengembalian_karung == "Rapi, gulungan kurang sesuai, dikumpul pada H+1":
        return 8
    elif pengembalian_karung == "Kurang rapi, gulungan kurang sesuai, dikumpul pada H+1":
        return 6
    elif pengembalian_karung == "Kurang rapi, gulungan kurang sesuai, dikumpul pada H+2":
        return 4
    elif pengembalian_karung == "Tidak rapi, gulungan tidak sesuai, dikumpul > H+2":
        return 2

# %%
def submit_fertilizer_analysis(): 
    global df_mobile_pemupukan_input, entry_tanggal_qa_terakhir, selected_estate, selected_divisi, selected_blok, entry_mandor, available_blok_list, diperiksa, mandor, pokok_sample

    try:
        pemeriksaan_ancak = check_combobox("pemeriksaan ancak pemupukan", combobox_pemeriksaan_ancak, PEMERIKSAAN_ANCAK_PEMUPUKAN_OPTIONS, PEMERIKSAAN_ANCAK_PEMUPUKAN_OPTIONS[-1])
        jadwal_pemupukan = check_combobox("jadwal pemupukan", combobox_jadwal_pemupukan, JADWAL_PEMUPUKAN_OPTIONS, JADWAL_PEMUPUKAN_OPTIONS[-1])
        peletakan_pupuk = check_combobox("peletakkan pupuk", combobox_peletakan_pupuk, PELETAKAN_PUPUK_OPTIONS, PELETAKAN_PUPUK_OPTIONS[-1])
        pupuk_tercecer = check_combobox("pupuk tercecer", combobox_pupuk_tercecer, PUPUK_TERCECER_OPTIONS, PUPUK_TERCECER_OPTIONS[-1])
        pengembalian_karung = check_combobox("pengembalian karung", combobox_pengembalian_karung, PENGEMBALIAN_KARUNG_OPTIONS, PENGEMBALIAN_KARUNG_OPTIONS[-1])
            
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    # Ambil nilai input
    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate = selected_estate.get() if selected_estate else ""
    divisi = selected_divisi.get() if selected_divisi else ""
    blok = selected_blok.get() if selected_blok else ""
    mandor = entry_mandor.get().strip()

    # Validasi input kosong/None
    if not validate_required_fields({
        "Tanggal": tanggal_str,
        "Estate": estate,
        "Divisi": divisi,
        "Blok": blok,
        "Mandor": mandor
    }):
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except Exception:
        messagebox.showerror("Error", "Format tanggal tidak valid.")
        return

    try:
        divisi_val = int(divisi) if str(divisi).isdigit() else divisi
        filtered_df = df_mobile_pemupukan_input[
            (df_mobile_pemupukan_input['Tanggal'] == tanggal_dt) &
            (df_mobile_pemupukan_input['Kebun'] == estate) &
            (df_mobile_pemupukan_input['Divisi'] == divisi_val) &
            (df_mobile_pemupukan_input['Blok'] == blok)
        ]
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi error saat filter data: {e}")
        return

    if filtered_df.empty:
        messagebox.showerror("Error", "Data tidak ditemukan untuk kombinasi input tersebut.")
        return
    
    # Remove the processed blok
    if blok in available_blok_list:
        available_blok_list.remove(blok)
        update_blok_combobox()

    # Get the values from the filtered DataFrame
    diperiksa = filtered_df["Nama Petugas"].iloc[0]
    jenis_pupuk = filtered_df["Jenis Pupuk"].iloc[0]
    dosis_pokok = filtered_df["Dosis"].iloc[0]
    tanggal_pemupukan = filtered_df["Tanggal Pemupukan"].iloc[0]
    pokok_sample = filtered_df["Jumlah Pokok"].sum()
    pokok_terpupuk = filtered_df["Pokok Terpupuk"].sum()
    pokok_tidak_terpupuk = filtered_df["Pokok Tidak Terpupuk"].sum()
    kondisi_gawangan_baik = filtered_df["Gawangan Baik"].sum()
    kondisi_gawangan_semak = filtered_df["Gawangan Semak"].sum()
    cara_aplikasi_standar = filtered_df["Cara Aplikasi Standar"].sum()
    cara_aplikasi_tidak_standar = filtered_df["Cara Aplikasi Tidak Standar"].sum()
    total_cara_aplikasi = cara_aplikasi_standar + cara_aplikasi_tidak_standar
    total_alat_tabur = filtered_df["Total Alat Tabur"].sum()
    total_alat_tabur_seragam = filtered_df["Alat Tabur Seragam"].sum()
    total_alat_tabur_tidak_seragam = filtered_df["Alat Tabur Tidak Seragam"].sum()
    total_dosis_sesuai = filtered_df["Total Dosis Sesuai"].sum()
    total_dosis_tidak_sesuai = filtered_df["Total Dosis Tidak Sesuai"].sum()
    total_dosis = total_dosis_sesuai + total_dosis_tidak_sesuai
    jenis_tenaga_pemupuk = filtered_df["Tenaga Pemupuk"].iloc[0]
    supervisi = filtered_df["Supervisi"].iloc[0]
    fisik_pupuk = filtered_df["Fisik Pupuk"].iloc[0]
    
    # Rank apd paling jelek
    apd_pekerja = filtered_df["Apd Pekerja"]

    worst_apd = ''
    worst_index = -1

    for apd in apd_pekerja:
        if apd is None:
            continue

        try:
            idx = APD_PEKERJA_RANK.index(apd)
        except ValueError:
            continue

        if idx > worst_index:
            worst_index = idx
            worst_apd = apd

    # Commented this since we're using the new flow to reduce the duplicate
    # Hitung daftar alat & total pekerja dari tenaga tabur
    # filtered_df['Daftar Tenaga Tabur Dict'] = filtered_df['Daftar Tenaga Tabur'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    # daftar_tenaga_tabur = [person for sublist in filtered_df['Daftar Tenaga Tabur Dict'] for person in sublist]
    # print(daftar_tenaga_tabur)

    # temp_df = pd.DataFrame(daftar_tenaga_tabur)
    # temp_df.drop_duplicates(subset='tenagaTabur', inplace=True)

    # temp_df['jumlah'] = pd.to_numeric(temp_df['jumlah'], errors='coerce')
    # temp_df['seragam'] = pd.to_numeric(temp_df['seragam'], errors='coerce')
    # temp_df['tidakSeragam'] = pd.to_numeric(temp_df['tidakSeragam'], errors='coerce')

    # total_tenaga_pemupuk = temp_df.shape[0]
    # total_alat_tabur = temp_df['jumlah'].sum()
    # total_alat_tabur_seragam = temp_df['seragam'].sum()
    # total_alat_tabur_tidak_seragam = temp_df['tidakSeragam'].sum()

    # Convert combobox option to float
    score_tenaga_pemupuk = convert_tenaga_pemupuk_to_score(jenis_tenaga_pemupuk)

    score_supervisi = convert_supervisi_to_score(supervisi)

    score_pemeriksaan_ancak = convert_pemeriksaan_ancak_to_score(pemeriksaan_ancak)

    score_jadwal_pemupukan = convert_jadwal_pemupukan_to_score(jadwal_pemupukan)

    score_apd_pekerja = convert_apd_pekerja_to_score(worst_apd)

    score_fisik_pupuk = convert_fisik_pupuk_to_score(fisik_pupuk)

    score_peletakan_pupuk = convert_peletakan_pupuk_to_score(peletakan_pupuk)

    score_pupuk_tercecer = convert_pupuk_tercecer_to_score(pupuk_tercecer)

    score_pengembalian_karung = convert_pengembalian_karung_to_score(pengembalian_karung)
    
    # Compose a new dictionary for the input
    # Identifier info
    identifier_data = {
        "Jenis Pupuk": jenis_pupuk,
        "Dosis / Pokok": dosis_pokok,
        "Tanggal Pemupukan": tanggal_pemupukan,
        "Blok": blok,
        "Tanggal Periksa": tanggal_str,
        "DivisiLabel": f"{estate}-{divisi}", 
        "Divisi": divisi,
        "Estate": estate,
    }
    
    actual_data = {
        "Jumlah Pokok Sample": pokok_sample,
        "Pokok Terpupuk": pokok_terpupuk,
        "Pokok Tidak Terpupuk": pokok_tidak_terpupuk,
        "Jumlah Ancak Semak Atau Gulma": kondisi_gawangan_semak,
        "Cara Aplikasi Standar": cara_aplikasi_standar,
        "Cara Aplikasi Tidak Standar": cara_aplikasi_tidak_standar,
        "Jumlah Alat Tabur Seragam": total_alat_tabur_seragam,
        "Alat Tabur Tidak Seragam": total_alat_tabur_tidak_seragam,
        "Total Alat Tabur": total_alat_tabur,
        "Total Dosis Sesuai": total_dosis_sesuai,
        "Total Dosis Tidak Sesuai": total_dosis_tidak_sesuai,
        "Total Dosis": total_dosis,
        "Tenaga Pemupuk": score_tenaga_pemupuk,
        "Supervisi": score_supervisi,
        "Terdapat Pemeriksaan Ancak Pemupukan": score_pemeriksaan_ancak,
        "Jadwal Pemupukan": score_jadwal_pemupukan,
        "Apd Pekerja": score_apd_pekerja,
        "Fisik Pupuk": score_fisik_pupuk,
        "Peletakan Pupuk": score_peletakan_pupuk,
        "Pupuk Tercecer": score_pupuk_tercecer,
        "Pengembalian Karung": score_pengembalian_karung,
    }

    input_data = {**identifier_data, **actual_data}
    
    # Analyze the input values 
    final_qa_score, final_qa_nilai, converted_input = analyse_qa_fertilizer(
        identifier_data,
        pokok_sample,
        pokok_tidak_terpupuk,
        kondisi_gawangan_semak,
        cara_aplikasi_standar,
        total_cara_aplikasi,
        total_alat_tabur_seragam,
        total_alat_tabur,
        total_dosis_sesuai,
        total_dosis,
        score_tenaga_pemupuk,
        score_supervisi,
        score_pemeriksaan_ancak,
        score_jadwal_pemupukan,
        score_apd_pekerja,
        score_fisik_pupuk,
        score_peletakan_pupuk,
        score_pupuk_tercecer,
        score_pengembalian_karung)
    
    # Commented this for now as it is slowing the process
    # process_uploaded_photos()
        
    # Save all the input and procesed datas into the spreadsheets
    save_to_sheet(input_fertilizer, "Input - Fertilizer", input_data)
    save_to_sheet(output_fertilizer, "Output - Fertilizer", final_qa_score)
    save_to_sheet(output_weight_fertilizer, "Output (Weight) - Fertilizer", final_qa_nilai)

    # Compose PDF report
    generate_pdf_output(final_qa_score, final_qa_nilai, combobox_menu_qa.get(), converted_input)

    # Upload PDF to Google Drive
    proceed_to_upload_pdf()

    # Clear cached photos data
    photos_data.clear()
    pdf_data.clear()

    # Display success window and go back to main menu
    show_success_window()

# %% [markdown]
# ### 10.4 QA Chemist

# %%
def convert_bahan_herbisida_to_score(bahan_herbisida):
    """Convert Bahan Herbisida to score."""
    if bahan_herbisida == "Sesuai sasaran, sesuai kebutuhan":
        return 10
    elif bahan_herbisida == "Kurang sesuai sasaran, Sesuai kebutuhan":
        return 8
    elif bahan_herbisida == "Sesuai gulma sasaran, tidak sesuai kebutuhan":
        return 6
    elif bahan_herbisida == "Kurang sesuai gulma sasaran, tidak sesuai kebutuhan":
        return 4
    elif bahan_herbisida == "Tidak Sesuai Gulma sasaran, Jumlah tidak sesuai":
        return 2

# %%
def convert_pengendalian_gulma_to_score(pengendalian_gulma):
    """Convert Pengendalian Gulma to score."""
    if pengendalian_gulma == "Terdapat RKB/RKH, Sesuai program Rotasi":
        return 10
    elif pengendalian_gulma == "Terdapat RKB/RKH,  kurang Sesuai program Rotasi":
        return 8
    elif pengendalian_gulma == "Terdapat RKB/RKH,  Tidak sesuai program Rotasi":
        return 6
    elif pengendalian_gulma == "Tidak terdapat RKB/RKH, Sesuai program Rotasi":
        return 4
    elif pengendalian_gulma == "Tidak terdapat RKB/RKH, Tidak Sesuai program Rotasi":
        return 2

# %%
def convert_apd_pekerja_chemist_to_score(apd_pekerja_chemist):
    """Convert APD Pekerja Chemist to score."""
    print(f"apd_pekerja_chemist: {apd_pekerja_chemist}")
    if apd_pekerja_chemist == "Lengkap":
        return 10
    elif apd_pekerja_chemist == "Kurang dari 1 item":
        return 8
    elif apd_pekerja_chemist == "Kurang dari 2 item":
        return 6
    elif apd_pekerja_chemist == "Kurang dari 3 item":
        return 4
    elif apd_pekerja_chemist == "Tidak ada APD":
        return 2

# %%
def convert_p3k_to_score(p3k):
    """Convert P3K to score."""
    if p3k == "Lengkap dan dibawa mandor":
        return 10
    elif p3k == "Kurang dari 1 item, dibawa mandor":
        return 8
    elif p3k == "Kurang dari 2 item, dibawa mandor":
        return 6
    elif p3k == "Kurang dari 3 item, tidak dibawa mandor":
        return 4
    elif p3k == "Tidak ada sama sekali":
        return 2

# %%
def convert_kartu_pengambilan_pencampuran_bahan_to_score(kartu_pengambilan_pencampuran_bahan):
    """Convert Kartu Pengambilan Pencampuran Bahan to score."""
    if kartu_pengambilan_pencampuran_bahan == "Kartu lengkap dan Update":
        return 10
    elif kartu_pengambilan_pencampuran_bahan == "Kartu lengkap, Terlambat 1 Hari":
        return 8
    elif kartu_pengambilan_pencampuran_bahan == "Kartu lengkap, Terlambat > 2 Hari":
        return 6
    elif kartu_pengambilan_pencampuran_bahan == "Kartu tidak lengkap, terlambat 1 hari":
        return 4
    elif kartu_pengambilan_pencampuran_bahan == "Kartu dan Monitoring tidak ada":
        return 2

# %%
def convert_kalibrasi_alat_nozel_to_score(kalibrasi_alat_nozel):
    """Convert Kalibrasi Alat Nozel to score."""
    if kalibrasi_alat_nozel == "Rutin dan Tercatat":
        return 10
    elif kalibrasi_alat_nozel == "Rutin dan tidak tercatat":
        return 8
    elif kalibrasi_alat_nozel == "Kurang rutin, tercatat":
        return 6
    elif kalibrasi_alat_nozel == "Tidak Rutin, tercatat":
        return 4
    elif kalibrasi_alat_nozel == "Tidak Pernah":
        return 2

# %%
def convert_alat_ukur_perkakas_perbaikan_to_score(alat_ukur_perkakas_perbaikan):
    """Convert Alat Ukur Perkakas Perbaikan to score."""
    if alat_ukur_perkakas_perbaikan == "Gelas ukur terkalibrasi, Toolkit lengkap":
        return 10
    elif alat_ukur_perkakas_perbaikan == "Gelas ukur terkalibrasi, Toolkit tidak lengkap":
        return 8
    elif alat_ukur_perkakas_perbaikan == "Gelas ukur tidak terkalibrasi, Toolkit  lengkap":
        return 6
    elif alat_ukur_perkakas_perbaikan == "Gelas ukur tidak terkalibrasi, Toolkit  tidak lengkap":
        return 4
    elif alat_ukur_perkakas_perbaikan == "Tidak membawa keduanya":
        return 2

# %%
def convert_peletakan_alat_semprot_to_score(peletakan_alat_semprot):
    """Convert Peletakan Alat Semprot to score."""
    if peletakan_alat_semprot == "Semua alat, tercatat":
        return 10
    elif peletakan_alat_semprot == "Semua alat, tidak tercatat":
        return 8
    elif peletakan_alat_semprot == "Sebagian alat saja dan tercatat":
        return 6
    elif peletakan_alat_semprot == "Sebagian alat saja, tidak tercatat":
        return 4
    elif peletakan_alat_semprot == "Tidak ada gudang dan pencatatan":
        return 2

# %%
def submit_chemist_analysis(): 
    global df_mobile_chemist_input, entry_tanggal_qa_terakhir, selected_estate, selected_divisi, selected_blok, entry_mandor, available_blok_list, diperiksa, mandor, pokok_sample

    try:
        kotak_p3k = check_combobox("kotak P3K", combobox_p3k, KOTAK_P3K_OPTIONS, KOTAK_P3K_OPTIONS[-1])
            
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    # Ambil nilai input
    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate = selected_estate.get() if selected_estate else ""
    divisi = selected_divisi.get() if selected_divisi else ""
    blok = selected_blok.get() if selected_blok else ""
    mandor = entry_mandor.get().strip()
    
    # Validasi input kosong/None
    if not validate_required_fields({
        "Tanggal": tanggal_str,
        "Estate": estate,
        "Divisi": divisi,
        "Blok": blok,
        "Mandor": mandor
    }):
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except Exception:
        messagebox.showerror("Error", "Format tanggal tidak valid.")
        return

    try:
        divisi_val = int(divisi) if str(divisi).isdigit() else divisi
        filtered_df = df_mobile_chemist_input[
            (df_mobile_chemist_input['Tanggal'] == tanggal_dt) &
            (df_mobile_chemist_input['Kebun'] == estate) &
            (df_mobile_chemist_input['Divisi'] == divisi_val) &
            (df_mobile_chemist_input['Blok'] == blok)
        ]
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi error saat filter data: {e}")
        return

    if filtered_df.empty:
        messagebox.showerror("Error", "Data tidak ditemukan untuk kombinasi input tersebut.")
        return
    
    # Remove the processed blok
    if blok in available_blok_list:
        available_blok_list.remove(blok)
        update_blok_combobox()

    # Get the values from the filtered DataFrame
    diperiksa = filtered_df["Nama Petugas"].iloc[0]
    tanggal_semprot = filtered_df["Tanggal Semprot"].iloc[0]
    dosis_knapsack = filtered_df["Dosis Knapsack"].iloc[0]
    luas = filtered_df["Luas"].sum()
    total_tenaga_semprot = filtered_df["Total Tenaga Kerja Semprot"].iloc[0]
    # pokok_sample = filtered_df["Jumlah Pokok"].sum()
    tipe_chemist = filtered_df["Chemist"].iloc[0]
    pokok_gulma = filtered_df["Jumlah Pokok Gulma"].sum()
    kematian_gulma_circle = filtered_df["Total Gulma Circle Mati"].sum()
    kematian_gulma_path = filtered_df["Total Gulma Path Mati"].sum()
    kematian_gulma_tph = filtered_df["Total Gulma Tph Mati"].sum()
    kematian_gulma_gawangan = filtered_df["Total Gulma Gawangan Mati"].sum()
    pokok_tersemprot = filtered_df["Total Pokok Tersemprot"].sum()
    pokok_tidak_tersemprot = filtered_df["Total Pokok Tidak Tersemprot"].sum()
    pokok_sample = pokok_tersemprot + pokok_tidak_tersemprot
    bahan_herbisida = filtered_df["Bahan Herbisida"].iloc[0]
    total_alat_semprot_layak = filtered_df[filtered_df["Kondisi Alat Semprot"] == "Baik dan Lancar"].shape[0]
    # total_alat_semprot_layak = filtered_df["Total Alat Semprot Baik"].sum()
    # total_alat_semprot_tidak_layak = filtered_df["Total Alat Semprot Tidak Layak"].sum()
    total_nozel_seragam = filtered_df[filtered_df["Keseragaman Nozel"] == "Seragam"].shape[0]
    # total_nozel_seragam = filtered_df["Total Nozel Seragam"].sum()
    # total_nozel_tidak_seragam = filtered_df["Total Nozel Tidak Seragam"].sum()
    # uji_petik_aktif = filtered_df["Total Uji Petik Aktif"].sum()
    # uji_petik_tidak_aktif = filtered_df["Total Uji Petik Nonaktif"].sum()
    # uji_petik_sesuai = filtered_df["Total Uji Petik Sesuai"].sum()
    # uji_petik_tidak_sesuai = filtered_df["Total Uji Petik Tidak Sesuai"].sum()
    program_pengendalian_gulma = filtered_df["Program Pengendalian Gulma"].iloc[0]
    kartu_pengambilan_campuran = filtered_df["Kartu Pengambilan Pencampuran"].iloc[0]
    kalibrasi_alat_nozel = filtered_df["Kalibrasi Alat Nozel"].iloc[0]
    gelas_ukur_perkakas = filtered_df["Gelas Ukur Perkakas"].iloc[0]
    peletakkan_alat_semprot = filtered_df["Peletakan Alat Semprot"].iloc[0]
    kesesuaian_kalibrasi_dosis = filtered_df["Kesesuaian Kalibrasi Dosis"].iloc[0]

    # Rank apd paling jelek
    apd_pekerja = filtered_df["Apd Pekerja"]

    worst_apd = ''
    worst_index = -1

    for apd in apd_pekerja:
        if apd is None:
            continue

        try:
            idx = APD_PEKERJA_RANK.index(apd)
        except ValueError:
            continue

        if idx > worst_index:
            worst_index = idx
            worst_apd = apd

    print(f"worst_apd: {worst_apd}")

    # Hitung kelayakan alat semprot, nozel & total pekerja dari tenaga semprot
    # filtered_df['Daftar Tenaga Semprot Dict'] = filtered_df['Daftar Tenaga Semprot'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    # daftar_tenaga_semprot = [person for sublist in filtered_df['Daftar Tenaga Semprot Dict'] for person in sublist]

    # temp_df = pd.DataFrame(daftar_tenaga_semprot)
    # temp_df.drop_duplicates(subset='tenagaSemprot', inplace=True)
    
    # total_tenaga_semprot = len(temp_df['tenagaSemprot'])
    # total_alat_semprot_layak = len(temp_df[temp_df['kondisiAlat'] == 'Baik dan Lancar'])
    # total_alat_semprot_tidak_layak = len(temp_df[temp_df['kondisiAlat'] == 'Tidak Baik'])
    # total_nozel_seragam = len(temp_df[temp_df['keseragamanNozel'] == 'Seragam'])
    # total_nozel_tidak_seragam = len(temp_df[temp_df['keseragamanNozel'] == 'Tidak Seragam'])
    
    # Convert combobox option to float
    score_bahan_herbisida = convert_bahan_herbisida_to_score(bahan_herbisida)

    score_pengendalian_gulma = convert_pengendalian_gulma_to_score(program_pengendalian_gulma)

    score_apd_pekerja = convert_apd_pekerja_chemist_to_score(worst_apd)

    score_p3k = convert_p3k_to_score(kotak_p3k)

    score_kartu_pengambilan_pencampuran_bahan = convert_kartu_pengambilan_pencampuran_bahan_to_score(kartu_pengambilan_campuran)

    score_kalibrasi_alat_nozel = convert_kalibrasi_alat_nozel_to_score(kalibrasi_alat_nozel)

    score_alat_ukur_perkakas_perbaikan = convert_alat_ukur_perkakas_perbaikan_to_score(gelas_ukur_perkakas)

    score_peletakan_alat_semprot = convert_peletakan_alat_semprot_to_score(peletakkan_alat_semprot)
    
    # Compose a new dictionary for the input
    # Identifier info
    identifier_data = {
        "Tanggal Semprot": tanggal_semprot,
        "Dosis / Knapsack": dosis_knapsack,
        "Jenis Chemist": tipe_chemist,
        "Tanggal Periksa": tanggal_str,
        "Blok": blok,
        "DivisiLabel": f"{estate}-{divisi}", 
        "Divisi": divisi,
        "Estate": estate,
    }

    actual_data = {
        "Jumlah Pokok Sample": pokok_sample,
        "Total Tenaga Kerja": total_tenaga_semprot,
        "Luas": luas,
        "Jumlah Pokok Gulma": pokok_gulma,
        "Total Gulma Circle Mati": kematian_gulma_circle,
        "Total Gulma Path Mati": kematian_gulma_path,
        "Total Gulma Tph Mati": kematian_gulma_tph,
        "Total Gulma Gawangan Mati": kematian_gulma_gawangan,
        "Pokok Tersemprot": pokok_tersemprot,
        "Bahan Herbisida yang Dibawa ke Ancak": score_bahan_herbisida,
        "Program Pengendalian Gulma": score_pengendalian_gulma,
        "Kotak P3K Isi Lengkap dan Dibawa Oleh Mandor": score_p3k,
        "APD Pekerja": score_apd_pekerja,
        "Terdapat Kartu Pengambilan dan Pencampuran Bahan": score_kartu_pengambilan_pencampuran_bahan,
        "Terdapat Kalibrasi Alat dan Nozel": score_kalibrasi_alat_nozel,
        "Membawa Gelas Ukur & Perkakas Perbaikan Alat Semprot": score_alat_ukur_perkakas_perbaikan,
        "Peletakan Alat Semprot": score_peletakan_alat_semprot,
    }

    input_data = {**identifier_data, **actual_data}
    
    # Analyze the input values 
    final_qa_score, final_qa_nilai, converted_input = analyse_qa_chemist(
        identifier_data,
        pokok_sample,
        total_tenaga_semprot,
        luas,
        tipe_chemist,
        pokok_gulma,
        kematian_gulma_circle,
        kematian_gulma_path,
        kematian_gulma_tph,
        kematian_gulma_gawangan,
        pokok_tersemprot,
        score_bahan_herbisida,
        total_alat_semprot_layak,
        total_nozel_seragam,
        kesesuaian_kalibrasi_dosis,
        score_pengendalian_gulma,
        score_p3k,
        score_apd_pekerja,
        score_kartu_pengambilan_pencampuran_bahan,
        score_kalibrasi_alat_nozel,
        score_alat_ukur_perkakas_perbaikan,
        score_peletakan_alat_semprot)
    
    # Commented this for now as it is slowing the process
    # process_uploaded_photos()
    
    # Save all the input and procesed datas into the spreadsheets
    save_to_sheet(input_chemist, "Input - Chemist", input_data)
    save_to_sheet(output_chemist, "Output - Chemist", final_qa_score)
    save_to_sheet(output_weight_chemist, "Output (Weight) - Chemist", final_qa_nilai)

    # Compose PDF report
    print(f"Final QA Score: {final_qa_score}")
    print(f"Final QA Nilai: {final_qa_nilai}")
    generate_pdf_output(final_qa_score, final_qa_nilai, combobox_menu_qa.get(), converted_input)

    # Upload PDF to Google Drive
    proceed_to_upload_pdf()

    # Clear cached photos data
    photos_data.clear()
    pdf_data.clear()

    # Display success window and go back to main menu
    show_success_window()

# %%
def close_success_and_go_back():
    """Closes the success window and returns to the main menu."""
    global success_window
    if not root_exists:
        return
    
    if success_window:
        success_window.destroy()  # Close the success window
        success_window = None  # Set to None after closing
    back_to_main()  # Go back to the main menu


# %%
def show_success_window():
    global success_window, root 
    if not root_exists:
        return
    
    # Create a new top-level window
    success_window = tk.Toplevel(root)
    success_window.title("Success")
    success_window.geometry("300x100")  # Adjust size as needed

    # Make the new window modal (prevent interaction with the main window)
    success_window.transient(root) 
    success_window.grab_set()   

    label_success = tk.Label(success_window, text="Sukses!", font=("Arial", 12))
    label_success.pack(pady=10)

    button_close_success_window = tk.Button(success_window, text="Tutup", command=success_window.destroy, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    button_close_success_window.pack(pady=5)

    success_window.columnconfigure(0, weight=1)


# %%
def go_back():
    """Handles navigation back; uses after_idle and hide_all_widgets."""
    global previous_menu
    if not root_exists:
        print("Root does not exist, cannot go back.")
        return
    
    print("Root does exist, go back.")
    print(f"previous_menu = {previous_menu}")

    if previous_menu == "missing_dates_input":
        hide_all_widgets()
        root.after_idle(show_ESTATE_OPTIONS_for_add_rainfall)
        previous_menu = "rainfall"
    elif previous_menu == "main":
        hide_all_widgets()
        root.after_idle(create_main_widgets)
    elif previous_menu == "rainfall":
        hide_all_widgets()
        root.after_idle(show_rainfall_options)
        previous_menu = "main"
    elif previous_menu == "estate":
        hide_all_widgets()
        root.after_idle(show_ESTATE_OPTIONS)
        previous_menu = "rainfall"
    elif previous_menu == "estate_analysis":
        hide_all_widgets()
        root.after_idle(create_main_widgets)
        previous_menu = "main"
    elif previous_menu == "estate_add_rainfall":
        hide_all_widgets()
        root.after_idle(show_rainfall_options)
        previous_menu = "rainfall"
    elif previous_menu == "analysis_results":
        hide_all_widgets()
        root.after_idle(show_estate_options_for_analysis)
        previous_menu = "estate_analysis"


# %%
def back_to_main():
    """Hides all widgets and recreates the main menu."""
    global previous_menu
    if not root_exists:
        return
    hide_all_widgets()
    create_main_widgets()
    previous_menu = "main"


# %%
def go_to_reanalyze():
    global previous_menu
    if not root_exists:
        return
    hide_all_widgets()
    show_estate_options_for_analysis()
    previous_menu = "estate_analysis" 


# %% [markdown]
# ### 10.6 Main Menu

# %%
def goto_chosen_qa_menu():
    global username, previous_menu, \
        df_mobile_produksi_input, df_mobile_perawatan_input, df_mobile_pemupukan_input, df_mobile_chemist_input, df_input, df_output, df_output_weight, \
        available_estate_list, available_divisi_list, available_blok_list

    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---

    # 1. Check username
    username = entry_username.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username.")
        return
    
    # 2. Check QA menu
    menu_qa = combobox_menu_qa.get()
    if not menu_qa.strip():
        messagebox.showerror("Error", "Tolong masukkan pilihan menu QA.")
        return
    
    # 3. Check chosen year
    chosen_year = combobox_chosen_year.get()
    if not chosen_year.strip():
        messagebox.showerror("Error", "Tolong masukkan pilihan tahun.")
        return
    
    # 4. Hide all widget and set previous menu flag to main menu
    previous_menu = "main"
    hide_all_widgets()

    print("combobox_menu_qa", menu_qa)

    # 5 Get the input and ouput data based on the chosen menu 
    try:
        df_mobile_produksi_input, df_mobile_perawatan_input, df_mobile_pemupukan_input, df_mobile_chemist_input, df_input, df_output, df_output_weight = load_sheets_for_menu(menu_qa)
        
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memuat data untuk {menu_qa}: {e}")
        print(f"Gagal memuat data untuk {menu_qa}: {e}")
        go_back()
        return
    
    available_estate_list = ["None"]
    available_divisi_list = ["None"]
    available_blok_list = ["None"]
    
    if menu_qa == "QA Produksi":
        qa_calculate_production()
    elif menu_qa == "QA Perawatan":
        qa_calculate_nursery()
    elif menu_qa == "QA Pemupukan":
        qa_calculate_fertilizer()
    elif menu_qa == "QA Chemist":
        qa_calculate_chemist()

# %%
def goto_processed_pdf():
    global username, previous_menu, \
        processed_pdf_files, rejected_pdf_files, approved_pdf_files 

    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---

    # 1. Check username
    username = entry_username.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username.")
        return
    
    # 2. Hide all widget and set previous menu flag to main menu
    previous_menu = "main"
    hide_all_widgets()

    # 3. Read all the processed PDF files from google drive
    try:
        processed_pdf_files, rejected_pdf_files, approved_pdf_files = fetch_pdfs()
        
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memuat data PDF: {e}")
        print(f"Gagal memuat data PDF: {e}")
        go_back()
        return
    
    # 4. Show the processed PDF files with table
    processed_pdfs(processed_pdf_files, rejected_pdf_files, approved_pdf_files)
    

# %%
def plot_bar_chart(data):
    fig_width = max(len(data) * 0.8, 4)  # at least 4 inches wide
    fig, ax = plt.subplots(figsize=(fig_width, 4))

    values = data["Total"]
    labels = data["DivisiLabel"]

    x = np.arange(len(labels))  # evenly spaced bar positions
    bar_width = 0.6 if len(labels) > 1 else 0.3  # thinner bar if only 1

    min_val = values.min()
    max_val = values.max()

    colors = []
    for val in values:
        if val == min_val:
            colors.append("red")
        elif val == max_val:
            colors.append("green")
        else:
            colors.append(get_random_color())

    bars = ax.bar(x, values, color=colors, width=bar_width)

    # Label on top
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f"{val:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')

    ax.set_xlabel("Divisi")
    ax.set_ylabel("Rata-rata Total")
    ax.set_ylim(0, 10)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20)  # tilt labels a bit for clarity

    # Add padding if only one bar
    if len(labels) == 1:
        ax.set_xlim(-0.5, 0.5)

    fig.tight_layout()
    return fig


# %%
def qa_data_overview(chosen_menu_qa, qa_score):
    global current_menu

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "qa_data_overview"

    df = pd.DataFrame(qa_score)
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
    df["Tanggal Periksa"] = pd.to_datetime(df["Tanggal Periksa"], errors="coerce")

    # === THIS MONTH CALCULATION ===
    this_month_df = df[
        (df["Tanggal Periksa"].dt.month == current_time_date.month) &
        (df["Tanggal Periksa"].dt.year == current_time_date.year)
    ]

    avg_this_month = this_month_df.groupby("DivisiLabel")["Total"].mean().reset_index()
    avg_this_month = avg_this_month.sort_values(by="DivisiLabel", ascending=True)

    # === TO DATE CALCULATION ===
    avg_to_date = df.groupby("DivisiLabel")["Total"].mean().reset_index()
    avg_to_date = avg_to_date.sort_values(by="DivisiLabel", ascending=True)

    # === SCROLLABLE CONTAINER ===
    outer_frame = tk.Frame(root)
    outer_frame.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)

    scrollable_frame = make_scrollable_frame(outer_frame)

    # Add this line to make entries stretch full width
    scrollable_frame.grid_columnconfigure(0, weight=1)

    # --- Data Overview Section ---
    row_offset = 0 # Start widgets at row 0

    label_chosen_menu_qa_title = make_label(parent=scrollable_frame, text=f"{chosen_menu_qa}", row=row_offset, font=("Arial", 16, "bold"))
    row_offset += 1

    # --- This Month Section ---
    label_this_month_title = make_label(parent=scrollable_frame, text="This Month Data Overview", row=row_offset, font=("Arial", 14, "bold"))
    row_offset += 1
    
    if this_month_df.empty:
        label_no_data = make_label(parent=scrollable_frame, text="No data available for this month.", row=row_offset, font=("Arial", 12))
        row_offset += 1
    else:
        fig_this_month = plot_bar_chart(avg_this_month)
        canvas_this_month = FigureCanvasTkAgg(fig_this_month, master=scrollable_frame)
        canvas_this_month.draw()
        canvas_this_month.get_tk_widget().grid(row=row_offset, column=0, padx=10, pady=10)
        row_offset += 1

    # --- To Date Section ---
    label_to_date_title = make_label(parent=scrollable_frame, text="To Date Data Overview", row=row_offset, font=("Arial", 14, "bold"))
    row_offset += 1

    fig_to_date = plot_bar_chart(avg_to_date)
    canvas_to_date = FigureCanvasTkAgg(fig_to_date, master=scrollable_frame)
    canvas_to_date.draw()
    canvas_to_date.get_tk_widget().grid(row=row_offset, column=0, padx=10, pady=10)
    row_offset += 1

    # --- This Month Parameter Rank Section ---
    label_this_month_parameter_rank_title = make_label(parent=scrollable_frame, text="This Month Parameter Rank Overview", row=row_offset, font=("Arial", 14, "bold"))
    row_offset += 1

    # --- This Month - All Divisi ---
    label_to_date_all_divsi_title = make_label(parent=scrollable_frame, text="This Month - All Divisi", row=row_offset, font=("Arial", 12, "bold"))
    row_offset += 1
    
    if this_month_df.empty:
        label_no_data = make_label(parent=scrollable_frame, text="No data available for this month.", row=row_offset, font=("Arial", 12))
        row_offset += 1
    else:
        all_this_month_avg_params = (
            this_month_df.drop(columns=DATABASE_IDENTIFIER, errors='ignore')
            .mean()
            .sort_values(ascending=False)
        )

        fig_this_month_all = plt.Figure(figsize=(14, 4), dpi=100)
        ax_this_month_all = fig_this_month_all.add_subplot(111)
        bars = ax_this_month_all.barh(all_this_month_avg_params.index, all_this_month_avg_params.values)
        for idx, bar in enumerate(bars):
            if idx == 0:
                bar.set_color("green")
            elif idx == len(bars) - 1:
                bar.set_color("red")
            else:
                bar.set_color(get_random_color())

        ax_this_month_all.bar_label(bars, fmt="%.2f", padding=5)

        ax_this_month_all.set_title("This Month Rank - All Divisi")
        ax_this_month_all.set_xlabel("Average Score")
        ax_this_month_all.set_ylabel("Parameter")
        fig_this_month_all.tight_layout()

        canvas_this_month_all = FigureCanvasTkAgg(fig_this_month_all, master=scrollable_frame)
        canvas_this_month_all.draw()
        canvas_this_month_all.get_tk_widget().grid(row=row_offset, column=0, padx=10, pady=10)
        row_offset += 1

    # --- This Month - By Divisi ---
    label_to_date_divsi_title = make_label(parent=scrollable_frame, text="This Month - By Divisi", row=row_offset, font=("Arial", 12, "bold"))
    row_offset += 1

    if this_month_df.empty:
        label_no_data = make_label(parent=scrollable_frame, text="No data available for this month.", row=row_offset, font=("Arial", 12))
        row_offset += 1
    else:
        this_month_divisi_list = sorted(this_month_df["DivisiLabel"].dropna().unique().tolist())
        this_month_selected_divisi = tk.StringVar(value=this_month_divisi_list[0])
        this_month_combobox, _ = make_combobox(scrollable_frame, values=this_month_divisi_list, row=row_offset, state="readonly")
        row_offset += 1

        fig_param_this_month = plt.Figure(figsize=(14, 4), dpi=100)
        ax_this_month = fig_param_this_month.add_subplot(111)
        canvas_param_this_month = FigureCanvasTkAgg(fig_param_this_month, master=scrollable_frame)
        canvas_param_this_month.get_tk_widget().grid(row=row_offset, column=0, padx=10, pady=10)
        row_offset += 1

        def update_this_month_chart(event=None):
            selected = this_month_selected_divisi.get()
            df_selected = this_month_df[this_month_df["DivisiLabel"] == selected]
            if not df_selected.empty:
                avg_params = (
                    df_selected.drop(columns=DATABASE_IDENTIFIER, errors='ignore')
                    .mean()
                    .sort_values(ascending=False)
                )
                # Clear and redraw
                ax_this_month.cla()
                bars = ax_this_month.barh(avg_params.index, avg_params.values)
                for idx, bar in enumerate(bars):
                    if idx == 0:
                        bar.set_color("green")
                    elif idx == len(bars) - 1:
                        bar.set_color("red")
                    else:
                        bar.set_color(get_random_color())
                        
                ax_this_month.bar_label(bars, fmt="%.2f", padding=5)

                ax_this_month.set_title(f"This Month Rank - {selected}")
                ax_this_month.set_xlabel("Average Score")
                ax_this_month.set_ylabel("Parameter")
                fig_param_this_month.tight_layout()
                canvas_param_this_month.draw()

        update_this_month_chart()
        this_month_combobox.bind("<<ComboboxSelected>>", update_this_month_chart)

    # --- To Date Parameter Rank Section ---
    label_to_date_parameter_rank_title = make_label(parent=scrollable_frame, text="To Date Parameter Rank Overview", row=row_offset, font=("Arial", 14, "bold"))
    row_offset += 1

    # --- To Date - All Divisi ---
    label_to_date_all_divsi_title = make_label(parent=scrollable_frame, text="To Date - All Divisi", row=row_offset, font=("Arial", 12, "bold"))
    row_offset += 1

    all_to_date_avg_params = (
        df.drop(columns=DATABASE_IDENTIFIER, errors='ignore')
        .mean()
        .sort_values(ascending=False)
    )

    fig_to_date_all = plt.Figure(figsize=(14, 4), dpi=100)
    ax_to_date_all = fig_to_date_all.add_subplot(111)
    bars = ax_to_date_all.barh(all_to_date_avg_params.index, all_to_date_avg_params.values)
    for idx, bar in enumerate(bars):
        if idx == 0:
            bar.set_color("green")
        elif idx == len(bars) - 1:
            bar.set_color("red")
        else:
            bar.set_color(get_random_color())
            
    ax_to_date_all.bar_label(bars, fmt="%.2f", padding=5)

    ax_to_date_all.set_title("To Date Rank - All Divisi")
    ax_to_date_all.set_xlabel("Average Score")
    ax_to_date_all.set_ylabel("Parameter")
    fig_to_date_all.tight_layout()

    canvas_to_date_all = FigureCanvasTkAgg(fig_to_date_all, master=scrollable_frame)
    canvas_to_date_all.draw()
    canvas_to_date_all.get_tk_widget().grid(row=row_offset, column=0, padx=10, pady=10)
    row_offset += 1

    # --- To Date - By Divisi ---
    label_to_date_divsi_title = make_label(parent=scrollable_frame, text="To Date - By Divisi", row=row_offset, font=("Arial", 12, "bold"))
    row_offset += 1

    to_date_divisi_list = sorted(df["DivisiLabel"].dropna().unique().tolist())
    to_date_selected_divisi = tk.StringVar(value=to_date_divisi_list[0])
    to_date_combobox, _ = make_combobox(scrollable_frame, values=to_date_divisi_list, row=row_offset, state="readonly")
    row_offset += 1

    fig_param_to_date = plt.Figure(figsize=(14, 4), dpi=100)
    ax_to_date = fig_param_to_date.add_subplot(111)
    canvas_param_to_date = FigureCanvasTkAgg(fig_param_to_date, master=scrollable_frame)
    canvas_param_to_date.get_tk_widget().grid(row=row_offset, column=0, padx=10, pady=10)
    row_offset += 1

    def update_to_date_chart(event=None):
        selected = to_date_selected_divisi.get()
        df_selected = df[df["DivisiLabel"] == selected]
        if not df_selected.empty:
            avg_params = (
                df_selected.drop(columns=DATABASE_IDENTIFIER, errors='ignore')
                .mean()
                .sort_values(ascending=False)
            )
            ax_to_date.cla()

            bars = ax_to_date.barh(avg_params.index, avg_params.values)
            for idx, bar in enumerate(bars):
                if idx == 0:
                    bar.set_color("green")
                elif idx == len(bars) - 1:
                    bar.set_color("red")
                else:
                    bar.set_color(get_random_color())
                    
            ax_to_date.bar_label(bars, fmt="%.2f", padding=5)
                
            ax_to_date.set_title(f"To Date Rank - {selected}")
            ax_to_date.set_xlabel("Average Score")
            ax_to_date.set_ylabel("Parameter")
            fig_param_to_date.tight_layout()
            canvas_param_to_date.draw()

    update_to_date_chart()
    to_date_combobox.bind("<<ComboboxSelected>>", update_to_date_chart)

    back_button = make_button(scrollable_frame, text="Back", row=row_offset, command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)

# %%
def goto_chosen_data_overview_menu():
    global previous_menu, \
    df_mobile_produksi_input, df_mobile_perawatan_input, df_mobile_pemupukan_input, df_mobile_chemist_input, df_input, df_output, df_output_weight

    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---

    # 1. Check username
    username = entry_username.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username.")
        return
    
    # 2. Check QA menu
    menu_qa = combobox_menu_data_overview.get()
    if not menu_qa.strip():
        messagebox.showerror("Error", "Tolong masukkan pilihan menu QA.")
        return
    
    # 3. Hide all widget and set previous menu flag to main menu
    previous_menu = "main"
    hide_all_widgets()

    print("combobox_menu_qa", menu_qa)

    # 4. Get the input and ouput data based on the chosen menu 
    try:
        df_mobile_produksi_input, df_mobile_perawatan_input, df_mobile_pemupukan_input, df_mobile_chemist_input, df_input, df_output, df_output_weight = load_sheets_for_menu(menu_qa)

        # Check for empty DataFrames
        if df_input.empty or df_output.empty or df_output_weight.empty:
            raise ValueError("Salah satu atau lebih sheet kosong.")
        
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memuat data untuk {menu_qa}: {e}")
        print(f"Gagal memuat data untuk {menu_qa}: {e}")
        go_back()
        return
    
    qa_data_overview(menu_qa, df_output_weight)

# %%
def generate_pdf_output(final_qa_scores, final_qa_nilai, combobox_menu_qa, input_data):
    global uploaded_photo_path, pdf_path, \
        keterangan_cpt, keterangan_gawangan, keterangan_titi_panen, \
        keterangan_jalan_jembatan, keterangan_hama_penyakit, keterangan_beneficial_plan, \
        keterangan_peilscale, keterangan_cover_crop, keterangan_barn_owl, \
        keterangan_tidak_terpupuk, keterangan_piringan_gawangan, keterangan_cara_aplikasi, \
        keterangan_alat_tabur_seragam, keterangan_dosis_alat_tabur, keterangan_tenaga_pemupuk, \
        keterangan_supervisi, keterangan_pemeriksaan_ancak, keterangan_jadwal_pemupukan, \
        keterangan_apd_pekerja, keterangan_fisik_pupuk, keterangan_peletakan_pupuk, \
        keterangan_pupuk_tercecer, keterangan_pengembalian_karung, \
        entry_keterangan_kematian_gulma, entry_keterangan_pokok_tersemprot, entry_keterangan_bahan_herbisida, \
        entry_keterangan_kondisi_alat_semprot, entry_keterangan_keseragaman_nozel, entry_keterangan_standard_dosis_knapsack, \
        entry_keterangan_pengendalian_gulma, entry_keterangan_penggunaan_hk, entry_keterangan_apd_pekerja, \
        entry_keterangan_p3k, entry_keterangan_kartu_pengambilan_pencampuran_bahan, \
        entry_keterangan_kalibrasi_alat_nozel, entry_keterangan_alat_ukur_perkakas_perbaikan, entry_keterangan_peletakan_alat_semprot, \
        photos_data, sph, setara_ha, berondolan_tinggal_sph, buah_tinggal_sph,  buah_busuk_sph
    
    menu_qa = combobox_menu_qa.replace(" ", "_")
    pdf_path = f"hasil_analisa_{menu_qa}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    margin = 50

    # --- Company Logos ---
    logo_width = 120
    logo_height = 48
    logo_y = height - logo_height - 20

    # Left logo (PANCARAN)
    if os.path.exists(PANCARAN_LOGO):
        try:
            c.drawImage(PANCARAN_LOGO, margin, logo_y,
                        width=logo_width, height=logo_height, preserveAspectRatio=False, mask='auto')
        except Exception as e:
            print(f"PANCARAN logo error: {e}")

    # Right logo (COMPANY)
    if os.path.exists(COMPANY_LOGO):
        try:
            c.drawImage(COMPANY_LOGO, width - margin - logo_width, logo_y,
                        width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"COMPANY logo error: {e}")

    # --- Title ---
    title_y = logo_y - 30  # Add extra space below the logos
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, title_y, f"Hasil Analisa {combobox_menu_qa}")

    # --- Metadata Section ---
    c.setFont("Helvetica", 11)
    meta_y = title_y - 25
    left_x = margin
    right_x = margin + 250

    c.drawString(left_x, meta_y, f"Estate  : {final_qa_scores.get('Estate', '')}")
    c.drawString(right_x, meta_y, f"Divisi  : {final_qa_scores.get('Divisi', '')}")
    meta_y -= 15
    c.drawString(right_x, meta_y, f"Blok  : {final_qa_scores.get('Blok', '')}")
    c.drawString(left_x, meta_y, f"Tanggal Periksa  : {final_qa_scores.get('Tanggal Periksa', '')}")

    if "Produksi" in combobox_menu_qa:
        meta_y -= 15
        c.drawString(left_x, meta_y, f"Panen Rotasi  : {final_qa_scores.get('Panen Rotasi', '')}")
        c.drawString(right_x, meta_y, f"SPH  : {sph}")
        meta_y -= 15
        c.drawString(left_x, meta_y, f"Pokok Sample  : {pokok_sample}")
    elif "Perawatan" in combobox_menu_qa:
        meta_y -= 15
        c.drawString(left_x, meta_y, f"Pokok Sample  : {pokok_sample}")
    elif "Pemupukan" in combobox_menu_qa:
        meta_y -= 15
        c.drawString(left_x, meta_y, f"Jenis Pupuk  : {final_qa_scores.get('Jenis Pupuk', '')}")
        c.drawString(right_x, meta_y, f"Dosis / Pokok  : {final_qa_scores.get('Dosis / Pokok', '')}")
        meta_y -= 15
        c.drawString(left_x, meta_y, f"Tanggal Pemupukan  : {final_qa_scores.get('Tanggal Pemupukan', '')}")
    elif "Chemist" in combobox_menu_qa:
        meta_y -= 15
        c.drawString(left_x, meta_y, f"Jenis Chemist  : {final_qa_scores.get('Jenis Chemist', '')}")
        c.drawString(right_x, meta_y, f"Dosis / Knapsack  : {final_qa_scores.get('Dosis / Knapsack', '')}")
        meta_y -= 15
        c.drawString(left_x, meta_y, f"Tanggal Semprot  : {final_qa_scores.get('Tanggal Semprot', '')}")

    # --- Table Header ---
    meta_y -= 30
    y = meta_y
    col1_x = margin                    # Deskripsi Penilaian

    # Score
    if "Produksi" in combobox_menu_qa:
        col2_x = col1_x + 200
    elif "Perawatan" in combobox_menu_qa:
        col2_x = col1_x + 150
    elif "Pemupukan" in combobox_menu_qa:
        col2_x = col1_x + 200
    else:
        col2_x = col1_x + 280
    
    col3_x = col2_x + 55               # Nilai
    col4_x = col3_x + 55               # Keterangan

    c.setFont("Helvetica-Bold", 12)
    c.drawString(col1_x, y, "Deskripsi Penilaian")
    c.drawString(col2_x, y, "Score")
    c.drawString(col3_x, y, "Nilai")
    c.drawString(col4_x, y, "Keterangan")
    c.line(col1_x, y - 2, col4_x + 90, y - 2)

    # --- Table Content ---
    y -= 20
    c.setFont("Helvetica", 10)

    for key in final_qa_scores:
        if key in DATABASE_IDENTIFIER:
            continue

        score = final_qa_scores.get(key, "")
        nilai = final_qa_nilai.get(key, "")

        if(nilai == "" or nilai == 0):
            continue

        # --- Draw Description (black) ---
        c.setFillColor(colors.black)
        c.drawString(col1_x, y, str(key))

        # --- Determine score color ---
        try:
            # Try converting the score to a float
            score_val = float(score)
            print(f"Converted Score value: {score_val}")
        except ValueError as e:
            print(f"ValueError: Could not convert {score} to a float.")
            score_val = None
        except TypeError as e:
            print(f"TypeError: Invalid type {type(score)} for conversion to float.")
            score_val = None
        except Exception as e:
            print(f"Unexpected error: {e}")
            score_val = None

        score_bg_color = colors.white
        if score_val == 10:
            score_bg_color = colors.green
        elif score_val == 8:
            score_bg_color = colors.blue
        elif score_val == 6:
            score_bg_color = colors.orange
        elif score_val == 4:
            score_bg_color = colors.yellow
        elif score_val <= 2:
            score_bg_color = colors.red

        # --- Draw colored rectangle for score ---
        rect_x = col2_x - 2
        rect_y = y - 2
        rect_width = 40
        rect_height = 12
        c.setFillColor(score_bg_color)
        c.rect(rect_x, rect_y, rect_width, rect_height, fill=1, stroke=0)

        # --- Draw score text over it (white or black depending on bg) ---
        if score_bg_color in [colors.green, colors.blue, colors.red]:
            text_color = colors.white
        else:
            text_color = colors.black

        c.setFillColor(text_color)
        c.drawCentredString(col2_x + 17, y, str(score))  # 20 = half of score cell width (40)

        # --- Draw nilai normally (black) ---
        c.setFillColor(colors.black)
        c.drawCentredString(col3_x + 17, y, str(round(nilai, 2)) if isinstance(nilai, (float, int)) else str(nilai))

        # --- Generate and Draw Keterangan ---
        raw_value = input_data.get(key, "")
        keterangan = ""

        if "Produksi" in combobox_menu_qa:
            if key == "Pencapaian Produksi":
                keterangan = f"{(input_data["Actual"] / input_data["Budget"]) * 100:.2f}% trhdp Bgd"
            elif key == "Kualitas Panen - TBS Tertinggal":
                keterangan = f"{perhitungan_buah_tinggal:.2f}% buah tinggal, {buah_tinggal_sph:.2f} jjg/Ha"
            elif key ==  "Kualitas Panen - LF Tertinggal":
                keterangan = f"{perhitungan_berondolan_tertinggal:.2f} butir/pokok, {berondolan_tinggal_sph:.2f} butir/Ha"
            elif key == "Kualitas Transport - Jjg di TPH":
                keterangan = f"{perhitungan_buah_tertinggal_tph:.2f} Jjg/TPH (Sample {tph_counter} TPH)"
            elif key == "Kualitas Transport - LF di TPH":
                keterangan = f"{perhitungan_berondolan_tertinggal_tph:.2f} Btr/TPH (Sample {tph_counter} TPH)"
            elif key == "Rotasi Panen":
                keterangan = f"{(DAY_IN_MONTH/input_data["Rotasi Panen"]):.2f} (Pusingan {input_data["Rotasi Panen"]} hari)"
            elif key == "Kualitas Panen - TBS Busuk Tinggal":
                keterangan = f"{perhitungan_tbs_busuk_tinggal:.2f}% buah busuk tinggal, {buah_busuk_sph:.2f} jjg/Ha"
            else:
                keterangan = ""

        elif "Perawatan" in combobox_menu_qa:
            if key == "Kondisi Circle, Path dan TPH":
                keterangan = f"{keterangan_cpt:.2f} Kondisi CPT Baik"
            elif key == "Kondisi Gawangan":
                keterangan = f"{keterangan_gawangan:.2f} Kondisi Gawangan Baik"
            elif key ==  "Titi Panen":
                keterangan = f"{keterangan_titi_panen}"
            elif key == "Jalan & Jembatan":
                keterangan = f"{keterangan_jalan_jembatan}"
            elif key == "Pruning dan Sanitasi":
                keterangan = f"{perhitungan_pruning:.2f}% Pruning Baik"
            elif key == "Susunan Pelepah":
                keterangan = f"{perhitungan_susunan_pelepah:.2f}% Susunan Pelepah Baik"
            elif key == "Hama Penyakit":
                keterangan = f"{keterangan_hama_penyakit:.2f} Serangan Hama"
            elif key == "Beneficial Plant":
                keterangan = f"{keterangan_beneficial_plan}"
            elif key == "Peilscale":
                keterangan = f"{keterangan_peilscale}"
            elif key == "Cover Crop (Neprolepis sp.)":
                keterangan = f"{keterangan_cover_crop}"
            elif key == "Barn Owl":
                keterangan = f"{keterangan_barn_owl}"
            else:
                keterangan = ""

        elif "Pemupukan" in combobox_menu_qa:
            if key == "Pokok Tidak Terpupuk":
                keterangan = f"{keterangan_tidak_terpupuk:.2f} Pkk Tidak Terpupuk"
            elif key == "Kondisi Piringan / Gawangan":
                keterangan = f"{keterangan_piringan_gawangan:.2f} Kondisi Piringan Baik"
            elif key ==  "Cara Aplikasi":
                keterangan = f"{keterangan_cara_aplikasi:.2f} Aplikasi Standar"
            elif key == "Keseragaman Alat Tabur":
                keterangan = f"{keterangan_alat_tabur_seragam:.2f} Alat Tabur Seragam"
            elif key == "Kesesuaian Dosis Alat Tabur":
                keterangan = f"{keterangan_dosis_alat_tabur}"
            elif key == "Tenaga Pemupuk":
                keterangan = f"{keterangan_tenaga_pemupuk}"
            elif key == "Supervisi":
                keterangan = f"{keterangan_supervisi}"
            elif key == "Terdapat Pemeriksaan Ancak Pemupukan":
                keterangan = f"{keterangan_pemeriksaan_ancak}"
            elif key == "Jadwal Pemupukan":
                keterangan = f"{keterangan_jadwal_pemupukan}"
            elif key == "APD Pekerja":
                keterangan = f"{keterangan_apd_pekerja}"
            elif key == "Fisik Pupuk":
                keterangan = f"{keterangan_fisik_pupuk}"
            elif key == "Peletakan Pupuk":
                keterangan = f"{keterangan_peletakan_pupuk}"
            elif key == "Pupuk Tercecer":
                keterangan = f"{keterangan_pupuk_tercecer}"
            elif key == "Pengembalian Karung":
                keterangan = f"{keterangan_pengembalian_karung}"
            else:
                keterangan = ""
        
        elif "Chemist" in combobox_menu_qa:
            if key == "Kematian Gulma":
                keterangan = f"{entry_keterangan_kematian_gulma.get()}"
            elif key == "Pokok Tersemprot":
                keterangan = f"{entry_keterangan_pokok_tersemprot.get()}"
            elif key == "Bahan Herbisida yang Dibawa ke Ancak":
                keterangan = f"{entry_keterangan_bahan_herbisida.get()}"
            elif key == "Kondisi Alat Semprot":
                keterangan = f"{entry_keterangan_kondisi_alat_semprot.get()}"
            elif key == "Keseragaman Nozel":
                keterangan = f"{entry_keterangan_keseragaman_nozel.get()}"
            elif key == "Dosis per Knapsack Sesuai Standar Kalibrasi":
                keterangan = f"{entry_keterangan_standard_dosis_knapsack.get()}"
            elif key == "Program Pengendalian Gulma":
                keterangan = f"{entry_keterangan_pengendalian_gulma.get()}"
            elif key == "Penggunaan HK Sesuai Norma Pekerjaan":
                keterangan = f"{entry_keterangan_penggunaan_hk.get()}"
            elif key == "APD Pekerja":
                keterangan = f"{entry_keterangan_apd_pekerja.get()}"
            elif key == "Kotak P3K Isi Lengkap dan Dibawa Oleh Mandor":
                keterangan = f"{entry_keterangan_p3k.get()}"
            elif key == "Terdapat Kartu Pengambilan dan Pencampuran Bahan":
                keterangan = f"{entry_keterangan_kartu_pengambilan_pencampuran_bahan.get()}"
            elif key == "Terdapat Kalibrasi Alat dan Nozel":
                keterangan = f"{entry_keterangan_kalibrasi_alat_nozel.get()}"
            elif key == "Membawa Gelas Ukur & Perkakas Perbaikan Alat Semprot":
                keterangan = f"{entry_keterangan_alat_ukur_perkakas_perbaikan.get()}"
            elif key == "Peletakan Alat Semprot":
                keterangan = f"{entry_keterangan_peletakan_alat_semprot.get()}"
            else:
                keterangan = ""

        else:
            keterangan = ""

        c.drawString(col4_x, y, keterangan)

        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50

    # --- Total Row ---
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col1_x, y, "Total")
    c.drawString(col2_x, y, str(""))
    c.drawCentredString(col3_x + 17, y, str(round(final_qa_nilai.get("Total", 0), 2)))

    y -= 20

    # --- Signature Section ---
    y = 150  # Adjust this based on previous content positioning
    x_start = margin
    col_width = (width - 2 * margin) / 4
    row_height = 60

    # Titles
    c.setFont("Helvetica-Bold", 10)
    titles = ["Diperiksa", "Disaksikan", "Diverifikasi", "Diketahui"]
    for i, title in enumerate(titles):
        c.drawCentredString(x_start + col_width * (i + 0.5), y + row_height + 10, title)

    # Empty signature boxes (with optional logos)
    # For the first three roles (Petugas QA, Mdr 1 / Mdr Panen, Asisten) draw DONE_LOGO if available.
    # For the Manager slot draw APPROVED_LOGO only when the current entry username == "Didik Wahyu Prasetyo".
    for i in range(4):
        box_x = x_start + col_width * i
        box_y = y
        c.rect(box_x, box_y, col_width, row_height)

        # Choose logo for this slot
        logo_path = None
        try:
            if i in (0, 1, 2):
                # first three roles get DONE_LOGO if the file exists
                if 'DONE_LOGO' in globals() and DONE_LOGO and os.path.exists(DONE_LOGO):
                    logo_path = DONE_LOGO
            # else:
            #     # Manager slot: only show APPROVED_LOGO when username matches
            #     if 'username' in locals() and username == "Didik Wahyu Prasetyo":
            #         if 'APPROVED_LOGO' in globals() and APPROVED_LOGO and os.path.exists(APPROVED_LOGO):
            #             logo_path = APPROVED_LOGO
        except Exception as e:
            print(f"Logo existence check error: {e}")

        if logo_path:
            try:
                img = ImageReader(logo_path)
                padding = 6
                img_w = col_width - padding * 2
                img_h = row_height - padding * 2
                # Draw image inside the box with preserved aspect ratio
                c.drawImage(img, box_x + padding, box_y + padding, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Failed to draw signature image in box {i}: {e}")

    # Roles (titles under boxes)
    c.setFont("Helvetica", 10)
    titles = ["Petugas QA", "Mdr 1 / Mdr Panen", "Asisten QA", "Head of Agromony Services"]
    for i, title in enumerate(titles):
        c.drawCentredString(x_start + col_width * (i + 0.5), y - 15, title)

    # Persons (names under the role labels)
    c.setFont("Helvetica", 10)
    persons = [diperiksa, mandor, username, "Didik Wahyu Prasetyo"]
    for i, person in enumerate(persons):
        c.drawCentredString(x_start + col_width * (i + 0.5), y - 25, person)

    # --- Optional Image ---
    if uploaded_photo_path and os.path.exists(uploaded_photo_path):
        try:
            img = ImageReader(uploaded_photo_path)
            c.drawImage(img, margin, y - 200, width=200, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            c.drawString(margin, y - 20, f"Gagal memuat foto: {e}")

    # --- Finalize the Report Page ---
    c.showPage()
    
    # --- Add Photo Page (New Page) ---
    if photos_data:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, height - 50, "Foto Dokumentasi")

        y = height - 100
        image_width = 240
        image_height = 150
        spacing_x = 20  # space between two images horizontally
        spacing_y = 40  # space between rows
        x_positions = [margin, margin + image_width + spacing_x]

        for i in range(0, len(photos_data), 2):
            # Calculate required space before drawing the next row
            required_space = image_height + spacing_y + 15
            if y - required_space < 100:
                c.showPage()
                c.setFont("Helvetica-Bold", 14)
                c.drawString(margin, height - 50, "Foto Dokumentasi (Lanjutan)")
                y = height - 100

            # Draw up to 2 images in this row
            for j in range(2):
                if i + j >= len(photos_data):
                    break

                photo = photos_data[i + j]
                file_path = photo.get("file_var").get()
                note = "-" if photo.get("note_var").get() == "Masukkan catatan..." else photo.get("note_var").get()

                if os.path.exists(file_path):
                    try:
                        x = x_positions[j]
                        img_y = y - image_height

                        c.drawImage(file_path, x, img_y, width=image_width, height=image_height, preserveAspectRatio=True)
                        c.setFont("Helvetica", 10)
                        c.drawString(x, img_y - 15, f"Catatan: {note}")

                    except Exception as e:
                        print(f"Gagal menambahkan foto: {file_path}, error: {e}")
                else:
                    print(f"File tidak ditemukan: {file_path}")

            # After drawing both photos, move y down for the next row
            y -= (image_height + spacing_y + 15)

    # --- Finalize ---
    c.save()
    messagebox.showinfo("Berhasil", f"PDF berhasil dibuat:\n{pdf_path}")
    os.startfile(pdf_path)

    pdf_data.append(pdf_path)

# %%
def toggle_qa_visibility(*args):
    value = entry_tanggal_qa_terakhir.get().strip()
    if not value:
        # Case: Empty input
        print("Input is empty.")
        label_tanggal_kosong.grid()
        label_tanggal_salah.grid_remove()
        for w in qa_conditional_widgets:
            w.grid_remove()

    elif is_valid_date(value):
        # Case: Valid date
        print("Valid date.")
        label_tanggal_kosong.grid_remove()
        label_tanggal_salah.grid_remove()
        for w in qa_conditional_widgets:
            w.grid()

    else:
        # Case: Invalid format
        print("Invalid date format.")
        label_tanggal_kosong.grid_remove()
        label_tanggal_salah.grid()
        for w in qa_conditional_widgets:
            w.grid_remove()

# %%
def process_production_calculation(df_mobile_input):
    global tree, tph_counter, diperiksa, pokok_sample
    if not is_widget_alive(tree):
        messagebox.showerror("Error", "Tabel hasil tidak tersedia.")
        return
    
    try:
        sph = cek_entry_number("sph", entry_sph, 0.0)
        actual = cek_entry_number("entry", entry_actual, 0.0)
        budget = cek_entry_number("budget", entry_budget, 0.0)
        restan = cek_entry_number("restan", entry_restant, 0.0)
        jaring = cek_entry_number("jaring", entry_jaring, 0.0)
        produktivitas_pemanen = cek_entry_number("produktivitas pemanen", entry_produktivitas_pemanen, 0.0)
        administrasi_panen = cek_entry_number("administrasi panen", entry_administrasi_panen, 0.0)
        kualitas_tbs = cek_entry_number("kualitas TBS", entry_kualitas_tbs, 0.0)
        muatan_overload = cek_entry_number("muatan overload", entry_muatan_overload, 0.0)
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return
    
    # Ambil nilai input
    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate = selected_estate.get() if selected_estate else ""
    divisi = selected_divisi.get() if selected_divisi else ""
    blok = selected_blok.get() if selected_blok else ""

    # Validasi input kosong/None
    if not validate_required_fields({
        "Tanggal": tanggal_str,
        "Estate": estate,
        "Divisi": divisi,
        "Blok": blok
    }):
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except Exception:
        messagebox.showerror("Error", "Format tanggal tidak valid.")
        return

    try:
        divisi_val = int(divisi) if str(divisi).isdigit() else divisi
        filtered_df = df_mobile_produksi_input[
            (df_mobile_produksi_input['Tanggal'] == tanggal_dt) &
            (df_mobile_produksi_input['Kebun'] == estate) &
            (df_mobile_produksi_input['Divisi'] == divisi_val) &
            (df_mobile_produksi_input['Blok'] == blok)
        ]
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi error saat filter data: {e}")
        return

    if filtered_df.empty:
        messagebox.showerror("Error", "Data tidak ditemukan untuk kombinasi input tersebut.")
        return
        
    diperiksa = filtered_df["Nama Petugas"].iloc[0]
    pokok_sample = filtered_df["Jumlah Pokok"].sum()
    setara_ha = pokok_sample/sph
    pokok_dipanen = filtered_df["Pkk Dipanen"].sum()
    berondolan_tertinggal = filtered_df["LF Tinggal"].sum()
    buah_tertinggal = filtered_df["Buah Matang Tidak Dipanen"].sum() + filtered_df["Buah Tinggal (pr, pk, pp, lp)"].sum()
    berondolan_tertinggal_tph = float(filtered_df["LF Tinggal (TPH)"].sum())
    buah_tertinggal_tph = float(filtered_df["Buah Tinggal (TPH)"].sum())
    tph_counter = float(filtered_df["TPH Counter"].sum())
    panen_rotasi = filtered_df["Rotasi"].iloc[0]
    tbs_busuk_tertinggal = filtered_df["Buah Busuk Tidak Dipanen"].sum()

    # Hitung skor menggunakan fungsi yang sudah ada
    table = []
    score_dict = {
        "Pencapaian Produksi": evaluate_budget_actual(budget, actual),
        "Kualitas Panen - TBS Tertinggal": evaluate_buah_tinggal(buah_tertinggal, pokok_sample),
        "Kualitas Panen - LF Tertinggal": evaluate_berondolan_tertinggal(berondolan_tertinggal, pokok_dipanen),
        "Kualitas Transport - Jjg di TPH": evaluate_buah_tertinggal_tph(buah_tertinggal_tph, tph_counter),
        "Kualitas Transport - LF di TPH": evaluate_berondolan_tertinggal_tph(berondolan_tertinggal_tph, tph_counter),
        "Rotasi Panen": evaluate_rotasi_panen_bulanan(panen_rotasi),
        "Restan": evaluate_restan(restan),
        "Pemakaian Jaring/Terpal": evaluate_jaring(jaring),
        "Kualitas Panen - TBS Busuk Tinggal": evaluate_tbs_busuk_tinggal(tbs_busuk_tertinggal, pokok_sample),
        "Produktivitas Pemanen": evaluate_produktivitas_pemanen(produktivitas_pemanen),
        "Administrasi Panen": evaluate_administrasi_panen(administrasi_panen),
        "Kualitas TBS": evaluate_kualitas_tbs(kualitas_tbs),
        "Muatan Overload": evaluate_muatan_overload(muatan_overload),
    }

    # Dapatkan bobot tahun
    year = combobox_chosen_year.get()
    weights = extract_weights_by_year(YEARLY_WEIGHT_PRODUCTION, year)

    # Hitung Keterangan SPH
    berondolan_tinggal_sph = berondolan_tertinggal/setara_ha
    buah_tinggal_sph = buah_tertinggal/setara_ha
    buah_busuk_sph = tbs_busuk_tertinggal/setara_ha

    for key, score in score_dict.items():
        weight = float(weights.get(key, "0%").replace("%", "")) / 100
        nilai = score * weight
        
        if key == "Pencapaian Produksi":
            ket = f"{(actual/budget)*100:.2f}% trhdp Bgd"
        elif key == "Kualitas Panen - TBS Tertinggal":
            ket = f"{perhitungan_buah_tinggal:.2f}% buah tinggal, {buah_tinggal_sph:.2f} jjg/Ha"
        elif key ==  "Kualitas Panen - LF Tertinggal":
            ket = f"{perhitungan_berondolan_tertinggal:.2f} butir/pokok, {berondolan_tinggal_sph:.2f} butir/Ha"
        elif key == "Kualitas Transport - Jjg di TPH":
            ket = f"{perhitungan_buah_tertinggal_tph:.2f} Jjg/TPH (Sample {tph_counter} TPH)"
        elif key == "Kualitas Transport - LF di TPH":
            ket = f"{perhitungan_berondolan_tertinggal_tph:.2f} Btr/TPH (Sample {tph_counter} TPH)"
        elif key == "Rotasi Panen":
            ket = f"{(DAY_IN_MONTH/panen_rotasi):.2f} (Pusingan {panen_rotasi} hari)"
        elif key == "Kualitas Panen - TBS Busuk Tinggal":
            ket = f"{perhitungan_tbs_busuk_tinggal:.2f}% buah busuk tinggal, {buah_busuk_sph:.2f} jjg/Ha"
        else:
            ket = ""

        table.append({"Parameter": key, "Score": score, "Nilai": round(nilai,2), "Keterangan": ket})

    # Tampilkan ke tabel (treeview)
    for i in tree.get_children():
        tree.delete(i)
    total_nilai = 0
    for item in table:
        if item["Nilai"] != 0:
            tree.insert("", "end", values=(item["Parameter"], item["Score"], item["Nilai"], item["Keterangan"]))
            total_nilai += item["Nilai"]
    tree.insert("", "end", values=("TOTAL", "", round(total_nilai, 2), ""), tags=("total",))
    tree.tag_configure("total", background="#e0e0e0", font=("Arial", 10, "bold"))

# %%
def process_nursery_calculation(df_mobile_input):
    global tree, diperiksa, pokok_sample, \
        keterangan_cpt, keterangan_gawangan, keterangan_titi_panen, \
        keterangan_jalan_jembatan, keterangan_hama_penyakit, keterangan_beneficial_plan, \
        keterangan_peilscale, keterangan_cover_crop, keterangan_barn_owl
        
    if not is_widget_alive(tree):
        messagebox.showerror("Error", "Tabel hasil tidak tersedia.")
        return
    
    try:
        cover_crop = cek_entry_number("cover crop", entry_cover_crop, 0.0)
        barn_owl = check_combobox("barn owl", combobox_barn_owl, BARN_OWL_OPTIONS, BARN_OWL_OPTIONS[-1])
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    # Validasi input kosong/None
    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate = selected_estate.get() if selected_estate else ""
    divisi = selected_divisi.get() if selected_divisi else ""
    blok = selected_blok.get() if selected_blok else ""

    if not validate_required_fields({
        "Tanggal": tanggal_str,
        "Estate": estate,
        "Divisi": divisi,
        "Blok": blok
    }):
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except Exception:
        messagebox.showerror("Error", "Format tanggal tidak valid.")
        return

    try:
        divisi_val = int(divisi) if str(divisi).isdigit() else divisi
        filtered_df = df_mobile_perawatan_input[
            (df_mobile_perawatan_input['Tanggal'] == tanggal_dt) &
            (df_mobile_perawatan_input['Kebun'] == estate) &
            (df_mobile_perawatan_input['Divisi'] == divisi_val) &
            (df_mobile_perawatan_input['Blok'] == blok)
        ]
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi error saat filter data: {e}")
        return

    if filtered_df.empty:
        messagebox.showerror("Error", "Data tidak ditemukan untuk kombinasi input tersebut.")
        return    
    
    diperiksa = filtered_df["Nama Petugas"].iloc[0]
    pokok_sample = filtered_df["Jumlah Pokok"].sum()
    beneficial_plant = filtered_df["Beneficial Plant"].iloc[0]
    peilscale = filtered_df["Peilscale"].iloc[0]
    circle_baik = filtered_df["Kondisi Circle Baik"].sum()
    circle_tidak_baik = filtered_df["Kondisi Circle Semak"].sum() + filtered_df["Kondisi Circle Dominan Anak Sawit"].sum()+ filtered_df["Kondisi Circle Dominan Sampah (Berondolan Busuk)"].sum()
    path_baik = filtered_df["Kondisi Path Baik"].sum()
    path_tidak_baik = filtered_df["Kondisi Path Tidak Baik"].sum()
    tph_baik = (filtered_df["Kondisi TPH"] == "Baik").sum()
    tph_tidak_baik = (filtered_df["Kondisi TPH"] == "Tidak Baik").sum()
    lalang_ada = filtered_df["Lalang Ada"].sum()
    lalang_tidak_ada = filtered_df["Lalang Tidak Ada"].sum()
    anak_kayu_ada = filtered_df["Anak Kayu Ada"].sum()
    anak_kayu_tidak_ada = filtered_df["Anak Kayu Tidak Ada"].sum()
    perumpung_ada = filtered_df["Perumpung Ada"].sum()
    perumpung_tidak_ada = filtered_df["Perumpung Tidak Ada"].sum()
    purun_tikus_ada = filtered_df["Purun Tikus Ada"].sum()
    purun_tikus_tidak_ada = filtered_df["Purun Tikus Tidak Ada"].sum()
    pakis_udang_ada = filtered_df["Pakis Udang Ada"].sum()
    pakis_udang_tidak_ada = filtered_df["Pakis Udang Tidak Ada"].sum()
    titi_panen = filtered_df["Titi Panen"].iloc[0]
    jalan_jembatan = filtered_df["Jalan Jembatan"].iloc[0]
    pruning_baik = filtered_df["Pruning Baik"].sum()
    pruning_over = filtered_df["Pruning Over"].sum()
    pruning_sengkleh = filtered_df["Pruning Sengkleh"].sum()
    pruning_under = filtered_df["Pruning Under"].sum()
    pelepah_rapi = filtered_df["Susunan Pelepah Rapi"].sum()
    pelepah_tidak_rapi = filtered_df["Susunan Pelepah Tidak Rapi"].sum()
    serangan_tikus_ada = filtered_df["Serangan Tikus Ada"].sum()
    serangan_tikus_tidak_ada = filtered_df["Serang Tikus Tidak Ada"].sum()
    serangan_rayap_ada = filtered_df["Serangan Rayap Ada"].sum()
    serangan_rayap_tidak_ada = filtered_df["Serangan Rayap Tidak Ada"].sum()
    serangan_thirathaba_ada = filtered_df["Thirathaba Ada"].sum()
    serangan_thirathaba_tidak_ada = filtered_df["Thirathaba Tidak Ada"].sum()
    serangan_updks_ada = filtered_df["UPDPKS Ada"].sum()
    serangan_updks_tidak_ada = filtered_df["UPDPKS Tidak Ada"].sum()

    # Hitung skor menggunakan fungsi yang sudah ada
    table = []
    score_dict = {
        "Kondisi Circle, Path dan TPH": evaluate_kondisi_circle_path_tph(circle_baik, path_baik, tph_baik, pokok_sample),
        "Kondisi Gawangan": evaluate_kondisi_gawangan(lalang_tidak_ada, anak_kayu_tidak_ada, perumpung_tidak_ada, purun_tikus_tidak_ada, pakis_udang_tidak_ada, pokok_sample),
        "Titi Panen": convert_titi_panen_to_score(titi_panen),
        "Jalan & Jembatan": convert_jalan_jembatan_to_score(jalan_jembatan),
        "Pruning dan Sanitasi": evaluate_pruning_sanitasi(pruning_baik, pokok_sample),
        "Susunan Pelepah": evaluate_susunan_pelepah(pelepah_rapi, pokok_sample),
        "Hama Penyakit": evaluate_hama_penyakit(serangan_tikus_ada, serangan_rayap_ada, serangan_thirathaba_ada, serangan_updks_ada, pokok_sample),
        "Beneficial Plant": convert_beneficial_plant_to_score(beneficial_plant),
        "Peilscale": convert_peilscale_to_score(peilscale),
        "Cover Crop (Neprolepis sp.)": evaluate_cover_crop(cover_crop, pokok_sample),
        "Barn Owl": convert_barn_owl_to_score(barn_owl),
    }

    keterangan_cpt = (((circle_baik/pokok_sample)+(path_baik/pokok_sample))/filtered_df.shape[0])*100
    keterangan_gawangan = (((lalang_tidak_ada/pokok_sample)+(anak_kayu_tidak_ada/pokok_sample)+(perumpung_tidak_ada/pokok_sample)+(purun_tikus_tidak_ada/pokok_sample)+(pakis_udang_tidak_ada/pokok_sample))/filtered_df.shape[0])*100
    keterangan_titi_panen = titi_panen
    keterangan_jalan_jembatan = jalan_jembatan
    keterangan_hama_penyakit = (((serangan_tikus_ada/pokok_sample)+(serangan_rayap_ada/pokok_sample)+(serangan_thirathaba_ada/pokok_sample)+(serangan_updks_ada/pokok_sample))/filtered_df.shape[0])*100
    keterangan_beneficial_plan = beneficial_plant
    keterangan_peilscale = peilscale
    keterangan_cover_crop = entry_keterangan_cover_crop.get().strip() if entry_keterangan_cover_crop else ""
    keterangan_barn_owl = entry_keterangan_barn_owl.get().strip() if entry_keterangan_barn_owl else ""

    # Dapatkan bobot tahun
    year = combobox_chosen_year.get()
    weights = extract_weights_by_year(YEARLY_WEIGHT_NURSERY, year)

    for key, score in score_dict.items():
        weight = float(weights.get(key, "0%").replace("%", "")) / 100
        nilai = score * weight
        
        if key == "Kondisi Circle, Path dan TPH":
            ket = f"{keterangan_cpt:.2f}% Kondisi CPT Baik"
        elif key == "Kondisi Gawangan":
            ket = f"{keterangan_gawangan:.2f}% Kondisi Gawangan Baik"
        elif key ==  "Titi Panen":
            ket = f"{keterangan_titi_panen}"
        elif key == "Jalan & Jembatan":
            ket = f"{keterangan_jalan_jembatan}"
        elif key == "Pruning dan Sanitasi":
            ket = f"{perhitungan_pruning:.2f}% Pruning Baik"
        elif key == "Susunan Pelepah":
            ket = f"{perhitungan_susunan_pelepah:.2f}% Susunan Pelepah Baik"
        elif key == "Hama Penyakit":
            ket = f"{keterangan_hama_penyakit:.2f}% Serangan Hama"
        elif key == "Beneficial Plant":
            ket = f"{keterangan_beneficial_plan}"
        elif key == "Peilscale":
            ket = f"{keterangan_peilscale}"
        elif key == "Cover Crop (Neprolepis sp.)":
            ket = f"{keterangan_cover_crop}"
        elif key == "Barn Owl":
            ket = f"{keterangan_barn_owl}"
        else:
            ket = ""

        table.append({"Parameter": key, "Score": score, "Nilai": round(nilai,2), "Keterangan": ket})

    # Tampilkan ke tabel (treeview)
    for i in tree.get_children():
        tree.delete(i)
    total_nilai = 0
    for item in table:
        if item["Nilai"] != 0:
            tree.insert("", "end", values=(item["Parameter"], item["Score"], item["Nilai"], item["Keterangan"]))
            total_nilai += item["Nilai"]
    tree.insert("", "end", values=("TOTAL", "", round(total_nilai, 2), ""), tags=("total",))
    tree.tag_configure("total", background="#e0e0e0", font=("Arial", 10, "bold"))

# %%
def process_fertilizer_calculation(df_mobile_input):
    global tree, diperiksa, pokok_sample, \
        keterangan_tidak_terpupuk, keterangan_piringan_gawangan, keterangan_cara_aplikasi, \
        keterangan_alat_tabur_seragam, keterangan_dosis_alat_tabur, keterangan_tenaga_pemupuk, \
        keterangan_supervisi, keterangan_pemeriksaan_ancak, keterangan_jadwal_pemupukan, \
        keterangan_apd_pekerja, keterangan_fisik_pupuk, keterangan_peletakan_pupuk, \
        keterangan_pupuk_tercecer, keterangan_pengembalian_karung
    
    if not is_widget_alive(tree):
        messagebox.showerror("Error", "Tabel hasil tidak tersedia.")
        return
    
    try:
        pemeriksaan_ancak = check_combobox("pemeriksaan ancak pemupukan", combobox_pemeriksaan_ancak, PEMERIKSAAN_ANCAK_PEMUPUKAN_OPTIONS, PEMERIKSAAN_ANCAK_PEMUPUKAN_OPTIONS[-1])
        jadwal_pemupukan = check_combobox("jadwal pemupukan", combobox_jadwal_pemupukan, JADWAL_PEMUPUKAN_OPTIONS, JADWAL_PEMUPUKAN_OPTIONS[-1])
        peletakan_pupuk = check_combobox("peletakkan pupuk", combobox_peletakan_pupuk, PELETAKAN_PUPUK_OPTIONS, PELETAKAN_PUPUK_OPTIONS[-1])
        pupuk_tercecer = check_combobox("pupuk tercecer", combobox_pupuk_tercecer, PUPUK_TERCECER_OPTIONS, PUPUK_TERCECER_OPTIONS[-1])
        pengembalian_karung = check_combobox("pengembalian karung", combobox_pengembalian_karung, PENGEMBALIAN_KARUNG_OPTIONS, PENGEMBALIAN_KARUNG_OPTIONS[-1])
            
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    # Validasi input kosong/None
    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate = selected_estate.get() if selected_estate else ""
    divisi = selected_divisi.get() if selected_divisi else ""
    blok = selected_blok.get() if selected_blok else ""
    
    if not validate_required_fields({
        "Tanggal": tanggal_str,
        "Estate": estate,
        "Divisi": divisi,
        "Blok": blok
    }):
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except Exception:
        messagebox.showerror("Error", "Format tanggal tidak valid.")
        return

    try:
        divisi_val = int(divisi) if str(divisi).isdigit() else divisi
        filtered_df = df_mobile_pemupukan_input[
            (df_mobile_pemupukan_input['Tanggal'] == tanggal_dt) &
            (df_mobile_pemupukan_input['Kebun'] == estate) &
            (df_mobile_pemupukan_input['Divisi'] == divisi_val) &
            (df_mobile_pemupukan_input['Blok'] == blok)
        ]
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi error saat filter data: {e}")
        return

    if filtered_df.empty:
        messagebox.showerror("Error", "Data tidak ditemukan untuk kombinasi input tersebut.")
        return    
    
    diperiksa = filtered_df["Nama Petugas"].iloc[0]
    pokok_sample = filtered_df["Jumlah Pokok"].sum()
    pokok_tidak_terpupuk = filtered_df["Pokok Tidak Terpupuk"].sum()
    kondisi_gawangan_baik = filtered_df["Gawangan Baik"].sum()
    kondisi_gawangan_semak = filtered_df["Gawangan Semak"].sum()
    cara_aplikasi_standar = filtered_df["Cara Aplikasi Standar"].sum()
    cara_aplikasi_tidak_standar = filtered_df["Cara Aplikasi Tidak Standar"].sum()
    total_cara_aplikasi = cara_aplikasi_standar + cara_aplikasi_tidak_standar
    total_alat_tabur = filtered_df["Total Alat Tabur"].sum()
    total_alat_tabur_seragam = filtered_df["Alat Tabur Seragam"].sum()
    total_alat_tabur_tidak_seragam = filtered_df["Alat Tabur Tidak Seragam"].sum()
    total_uji_petik_aktif = filtered_df["Total Uji Petik Aktif"].sum()
    total_uji_petik_non_aktif = filtered_df["Total Uji Petik Nonaktif"].sum()
    total_dosis_sesuai = filtered_df["Total Dosis Sesuai"].sum()
    total_dosis_tidak_sesuai = filtered_df["Total Dosis Tidak Sesuai"].sum()
    total_dosis = total_dosis_sesuai + total_dosis_tidak_sesuai
    jenis_tenaga_pemupuk = filtered_df["Tenaga Pemupuk"].iloc[0]
    supervisi = filtered_df["Supervisi"].iloc[0]
    fisik_pupuk = filtered_df["Fisik Pupuk"].iloc[0]

    # Rank apd paling jelek
    apd_pekerja = filtered_df["Apd Pekerja"]

    worst_apd = ''
    worst_index = -1

    for apd in apd_pekerja:
        if apd is None:
            continue

        try:
            idx = APD_PEKERJA_RANK.index(apd)
        except ValueError:
            continue

        if idx > worst_index:
            worst_index = idx
            worst_apd = apd
    
    # Hitung daftar alat & total pekerja dari tenaga tabur
    filtered_df['Daftar Tenaga Tabur Dict'] = filtered_df['Daftar Tenaga Tabur'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    filtered_df['Rapi Daftar Tenaga Tabur'] = filtered_df['Daftar Tenaga Tabur Dict'].apply(restructure_data)
    total_tenaga_pemupuk = len(set(filtered_df['Rapi Daftar Tenaga Tabur'].explode().apply(lambda x: x['Nama'])))

    # Hitung skor menggunakan fungsi yang sudah ada
    table = []
    score_dict = {
        "Pokok Tidak Terpupuk": evaluate_pokok_tidak_terpupuk(pokok_tidak_terpupuk),
        "Kondisi Piringan / Gawangan": evaluate_kondisi_piringan_gawangan(kondisi_gawangan_semak, pokok_sample),
        "Cara Aplikasi": evaluate_cara_aplikasi(cara_aplikasi_standar, total_cara_aplikasi),
        "Keseragaman Alat Tabur": evaluate_keseragaman_alat_tabur(total_alat_tabur_seragam, total_alat_tabur),
        "Kesesuaian Dosis Alat Tabur": evaluate_dosis_alat_tabur(total_dosis_sesuai, total_dosis),
        "Tenaga Pemupuk": convert_tenaga_pemupuk_to_score(jenis_tenaga_pemupuk),
        "Supervisi": convert_supervisi_to_score(supervisi),
        "Terdapat Pemeriksaan Ancak Pemupukan": convert_pemeriksaan_ancak_to_score(pemeriksaan_ancak),
        "Jadwal Pemupukan": convert_jadwal_pemupukan_to_score(jadwal_pemupukan),
        "APD Pekerja": convert_apd_pekerja_to_score(worst_apd),
        "Fisik Pupuk": convert_fisik_pupuk_to_score(fisik_pupuk),
        "Peletakan Pupuk": convert_peletakan_pupuk_to_score(peletakan_pupuk),
        "Pupuk Tercecer": convert_pupuk_tercecer_to_score(pupuk_tercecer),
        "Pengembalian Karung": convert_pengembalian_karung_to_score(pengembalian_karung),
    }

    keterangan_tidak_terpupuk = pokok_tidak_terpupuk
    keterangan_piringan_gawangan = (kondisi_gawangan_baik/pokok_sample)*100
    keterangan_cara_aplikasi = (cara_aplikasi_standar/pokok_sample)*100
    keterangan_alat_tabur_seragam = (total_alat_tabur_seragam/total_alat_tabur)*100
    keterangan_dosis_alat_tabur = f"Jumlah Uji Petik (Aktif): {total_uji_petik_aktif:.2f}, {((total_dosis_sesuai/total_uji_petik_aktif)*100):.2f}% Sesuai"
    keterangan_tenaga_pemupuk = jenis_tenaga_pemupuk
    keterangan_supervisi = entry_keterangan_supervisi.get().strip() if entry_keterangan_supervisi else ""
    keterangan_pemeriksaan_ancak = pemeriksaan_ancak
    keterangan_jadwal_pemupukan = entry_keterangan_jadwal_pemupukan.get().strip() if entry_keterangan_jadwal_pemupukan else ""
    keterangan_apd_pekerja = worst_apd
    keterangan_fisik_pupuk = fisik_pupuk
    keterangan_peletakan_pupuk = peletakan_pupuk
    keterangan_pupuk_tercecer = pupuk_tercecer
    keterangan_pengembalian_karung = pengembalian_karung

    # Dapatkan bobot tahun
    year = combobox_chosen_year.get()
    weights = extract_weights_by_year(YEARLY_WEIGHT_FERTILIZER, year)

    print(f"score_dict: {score_dict}")
    for key, score in score_dict.items():
        weight = float(weights.get(key, "0%").replace("%", "")) / 100
        nilai = score * weight
        
        if key == "Pokok Tidak Terpupuk":
            ket = f"{keterangan_tidak_terpupuk:.2f} Pkk Tidak Terpupuk"
        elif key == "Kondisi Piringan / Gawangan":
            ket = f"{keterangan_piringan_gawangan:.2f}% Kondisi Piringan Baik"
        elif key ==  "Cara Aplikasi":
            ket = f"{keterangan_cara_aplikasi:.2f}% Aplikasi Standar"
        elif key == "Keseragaman Alat Tabur":
            ket = f"{keterangan_alat_tabur_seragam:.2f}% Alat Tabur Seragam"
        elif key == "Kesesuaian Dosis Alat Tabur":
            ket = f"{keterangan_dosis_alat_tabur}"
        elif key == "Tenaga Pemupuk":
            ket = f"{keterangan_tenaga_pemupuk}"
        elif key == "Supervisi":
            ket = f"{keterangan_supervisi}"
        elif key == "Terdapat Pemeriksaan Ancak Pemupukan":
            ket = f"{keterangan_pemeriksaan_ancak}"
        elif key == "Jadwal Pemupukan":
            ket = f"{keterangan_jadwal_pemupukan}"
        elif key == "APD Pekerja":
            ket = f"{keterangan_apd_pekerja}"
        elif key == "Fisik Pupuk":
            ket = f"{keterangan_fisik_pupuk}"
        elif key == "Peletakan Pupuk":
            ket = f"{keterangan_peletakan_pupuk}"
        elif key == "Pupuk Tercecer":
            ket = f"{keterangan_pupuk_tercecer}"
        elif key == "Pengembalian Karung":
            ket = f"{keterangan_pengembalian_karung}"
        else:
            ket = ""

        table.append({"Parameter": key, "Score": score, "Nilai": round(nilai,2), "Keterangan": ket})

    # Tampilkan ke tabel (treeview)
    for i in tree.get_children():
        tree.delete(i)
    total_nilai = 0
    for item in table:
        if item["Nilai"] != 0:
            tree.insert("", "end", values=(item["Parameter"], item["Score"], item["Nilai"], item["Keterangan"]))
            total_nilai += item["Nilai"]
    tree.insert("", "end", values=("TOTAL", "", round(total_nilai, 2), ""), tags=("total",))
    tree.tag_configure("total", background="#e0e0e0", font=("Arial", 10, "bold"))

# %%
def process_chemist_calculation(df_mobile_input):
    global tree, diperiksa, pokok_sample
    if not is_widget_alive(tree):
        messagebox.showerror("Error", "Tabel hasil tidak tersedia.")
        return
    
    try:
        kotak_p3k = check_combobox("kotak P3K", combobox_p3k, KOTAK_P3K_OPTIONS, KOTAK_P3K_OPTIONS[-1])
            
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return
    
    # Ambil nilai input
    tanggal_str = entry_tanggal_qa_terakhir.get().strip()
    estate = selected_estate.get() if selected_estate else ""
    divisi = selected_divisi.get() if selected_divisi else ""
    blok = selected_blok.get() if selected_blok else ""
    keterangan_kematian_gulma = entry_keterangan_kematian_gulma.get().strip() if entry_keterangan_kematian_gulma else ""
    keterangan_pokok_tersemprot = entry_keterangan_pokok_tersemprot.get().strip() if entry_keterangan_pokok_tersemprot else ""
    keterangan_bahan_herbisida = entry_keterangan_bahan_herbisida.get().strip() if entry_keterangan_bahan_herbisida else ""
    keterangan_kondisi_alat_semprot = entry_keterangan_kondisi_alat_semprot.get().strip() if entry_keterangan_kondisi_alat_semprot else ""
    keterangan_keseragaman_nozel = entry_keterangan_keseragaman_nozel.get().strip() if entry_keterangan_keseragaman_nozel else ""
    keterangan_standard_dosis_knapsack = entry_keterangan_standard_dosis_knapsack.get().strip() if entry_keterangan_standard_dosis_knapsack else ""
    keterangan_pengendalian_gulma = entry_keterangan_pengendalian_gulma.get().strip() if entry_keterangan_pengendalian_gulma else ""
    keterangan_penggunaan_hk = entry_keterangan_penggunaan_hk.get().strip() if entry_keterangan_penggunaan_hk else ""
    keterangan_apd_pekerja = entry_keterangan_apd_pekerja.get().strip() if entry_keterangan_apd_pekerja else ""
    keterangan_p3k = entry_keterangan_p3k.get().strip() if entry_keterangan_p3k else ""
    keterangan_kartu_pengambilan_pencampuran_bahan = entry_keterangan_kartu_pengambilan_pencampuran_bahan.get().strip() if entry_keterangan_kartu_pengambilan_pencampuran_bahan else ""
    keterangan_kalibrasi_alat_nozel = entry_keterangan_kalibrasi_alat_nozel.get().strip() if entry_keterangan_kalibrasi_alat_nozel else ""
    keterangan_alat_ukur_perkakas_perbaikan = entry_keterangan_alat_ukur_perkakas_perbaikan.get().strip() if entry_keterangan_alat_ukur_perkakas_perbaikan else ""
    keterangan_peletakan_alat_semprot = entry_keterangan_peletakan_alat_semprot.get().strip() if entry_keterangan_peletakan_alat_semprot else ""

    # Validasi input kosong/None
    if not validate_required_fields({
        "Tanggal": tanggal_str,
        "Estate": estate,
        "Divisi": divisi,
        "Blok": blok
    }):
        return

    try:
        tanggal_dt = datetime.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
    except Exception:
        messagebox.showerror("Error", "Format tanggal tidak valid.")
        return

    try:
        divisi_val = int(divisi) if str(divisi).isdigit() else divisi
        filtered_df = df_mobile_chemist_input[
            (df_mobile_chemist_input['Tanggal'] == tanggal_dt) &
            (df_mobile_chemist_input['Kebun'] == estate) &
            (df_mobile_chemist_input['Divisi'] == divisi_val) &
            (df_mobile_chemist_input['Blok'] == blok)
        ]
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi error saat filter data: {e}")
        return

    if filtered_df.empty:
        messagebox.showerror("Error", "Data tidak ditemukan untuk kombinasi input tersebut.")
        return    
    
    diperiksa = filtered_df["Nama Petugas"].iloc[0]
    luas = filtered_df["Luas"].sum()
    total_tenaga_semprot = filtered_df["Total Tenaga Kerja Semprot"].iloc[0]
    # pokok_sample = filtered_df["Jumlah Pokok"].sum()
    tipe_chemist = filtered_df["Chemist"].iloc[0]
    pokok_gulma = filtered_df["Jumlah Pokok Gulma"].sum()
    kematian_gulma_circle = filtered_df["Total Gulma Circle Mati"].sum()
    kematian_gulma_path = filtered_df["Total Gulma Path Mati"].sum()
    kematian_gulma_tph = filtered_df["Total Gulma Tph Mati"].sum()
    kematian_gulma_gawangan = filtered_df["Total Gulma Gawangan Mati"].sum()
    pokok_tersemprot = filtered_df["Total Pokok Tersemprot"].sum()
    pokok_tidak_tersemprot = filtered_df["Total Pokok Tidak Tersemprot"].sum()
    pokok_sample = pokok_tersemprot + pokok_tidak_tersemprot
    bahan_herbisida = filtered_df["Bahan Herbisida"].iloc[0]
    total_alat_semprot_layak = filtered_df[filtered_df["Kondisi Alat Semprot"] == "Baik dan Lancar"].shape[0]
    # total_alat_semprot_layak = filtered_df["Total Alat Semprot Baik"].sum()
    # total_alat_semprot_tidak_layak = filtered_df["Total Alat Semprot Tidak Layak"].sum()
    total_nozel_seragam = filtered_df[filtered_df["Keseragaman Nozel"] == "Seragam"].shape[0]
    # total_nozel_seragam = filtered_df["Total Nozel Seragam"].sum()
    # total_nozel_tidak_seragam = filtered_df["Total Nozel Tidak Seragam"].sum()
    # uji_petik_aktif = filtered_df["Total Uji Petik Aktif"].sum()
    # uji_petik_tidak_aktif = filtered_df["Total Uji Petik Nonaktif"].sum()
    # uji_petik_sesuai = filtered_df["Total Uji Petik Sesuai"].sum()
    # uji_petik_tidak_sesuai = filtered_df["Total Uji Petik Tidak Sesuai"].sum()
    program_pengendalian_gulma = filtered_df["Program Pengendalian Gulma"].iloc[0]
    kartu_pengambilan_campuran = filtered_df["Kartu Pengambilan Pencampuran"].iloc[0]
    kalibrasi_alat_nozel = filtered_df["Kalibrasi Alat Nozel"].iloc[0]
    gelas_ukur_perkakas = filtered_df["Gelas Ukur Perkakas"].iloc[0]
    peletakkan_alat_semprot = filtered_df["Peletakan Alat Semprot"].iloc[0]
    kesesuaian_kalibrasi_dosis = filtered_df["Kesesuaian Kalibrasi Dosis"].iloc[0]

    # Rank apd paling jelek
    apd_pekerja = filtered_df["Apd Pekerja"]

    worst_apd = ''
    worst_index = -1

    for apd in apd_pekerja:
        if apd is None:
            continue

        try:
            idx = APD_PEKERJA_RANK.index(apd)
        except ValueError:
            continue

        if idx > worst_index:
            worst_index = idx
            worst_apd = apd

    print(f"worst_apd: {worst_apd}")

    # Hitung kelayakan alat semprot, nozel & total pekerja dari tenaga semprot
    # filtered_df['Daftar Tenaga Semprot Dict'] = filtered_df['Daftar Tenaga Semprot'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    # daftar_tenaga_semprot = [person for sublist in filtered_df['Daftar Tenaga Semprot Dict'] for person in sublist]

    # temp_df = pd.DataFrame(daftar_tenaga_semprot)
    # temp_df.drop_duplicates(subset='tenagaSemprot', inplace=True)
    
    # total_tenaga_semprot = len(temp_df['tenagaSemprot'])
    # total_alat_semprot_layak = len(temp_df[temp_df['kondisiAlat'] == 'Baik dan Lancar'])
    # total_alat_semprot_tidak_layak = len(temp_df[temp_df['kondisiAlat'] == 'Tidak Baik'])
    # total_nozel_seragam = len(temp_df[temp_df['keseragamanNozel'] == 'Seragam'])
    # total_nozel_tidak_seragam = len(temp_df[temp_df['keseragamanNozel'] == 'Tidak Seragam'])
    
    # Hitung skor menggunakan fungsi yang sudah ada
    score_kematian_gulma = evaluate_kematian_gulma(tipe_chemist, kematian_gulma_circle, kematian_gulma_path, kematian_gulma_tph, kematian_gulma_gawangan, pokok_gulma)

    table = []
    score_dict = {
        "Kematian Gulma": score_kematian_gulma,
        "Pokok Tersemprot": evaluate_pokok_tersemprot(pokok_tersemprot, pokok_sample),
        "Bahan Herbisida yang Dibawa ke Ancak": convert_bahan_herbisida_to_score(bahan_herbisida),
        "Kondisi Alat Semprot": evaluate_alat_semprot(total_alat_semprot_layak, total_tenaga_semprot),
        "Keseragaman Nozel": evaluate_keseragaman_nozel(total_nozel_seragam, total_tenaga_semprot),
        "Dosis per Knapsack Sesuai Standar Kalibrasi": evaluate_dosis_knapsack(kesesuaian_kalibrasi_dosis),
        "Program Pengendalian Gulma": convert_pengendalian_gulma_to_score(program_pengendalian_gulma),
        "Penggunaan HK Sesuai Norma Pekerjaan": evaluate_penggunaan_hk(tipe_chemist, score_kematian_gulma, total_tenaga_semprot, luas),
        "Kotak P3K Isi Lengkap dan Dibawa Oleh Mandor": convert_p3k_to_score(kotak_p3k),
        "APD Pekerja": convert_apd_pekerja_chemist_to_score(worst_apd),
        "Terdapat Kartu Pengambilan dan Pencampuran Bahan": convert_kartu_pengambilan_pencampuran_bahan_to_score(kartu_pengambilan_campuran),
        "Terdapat Kalibrasi Alat dan Nozel": convert_kalibrasi_alat_nozel_to_score(kalibrasi_alat_nozel),
        "Membawa Gelas Ukur & Perkakas Perbaikan Alat Semprot": convert_alat_ukur_perkakas_perbaikan_to_score(gelas_ukur_perkakas),
        "Peletakan Alat Semprot": convert_peletakan_alat_semprot_to_score(peletakkan_alat_semprot),
    }

    # Dapatkan bobot tahun
    year = combobox_chosen_year.get()
    weights = extract_weights_by_year(YEARLY_WEIGHT_CHEMIST, year)

    print(f"score_dict: {score_dict}")
    for key, score in score_dict.items():
        weight = float(weights.get(key, "0%").replace("%", "")) / 100
        nilai = score * weight
        
        if key == "Kematian Gulma":
            ket = f"{keterangan_kematian_gulma}"
        elif key == "Pokok Tersemprot":
            ket = f"{keterangan_pokok_tersemprot}"
        elif key == "Bahan Herbisida yang Dibawa ke Ancak":
            ket = f"{keterangan_bahan_herbisida}"
        elif key == "Kondisi Alat Semprot":
            ket = f"{keterangan_kondisi_alat_semprot}"
        elif key == "Keseragaman Nozel":
            ket = f"{keterangan_keseragaman_nozel}"
        elif key == "Dosis per Knapsack Sesuai Standar Kalibrasi":
            ket = f"{keterangan_standard_dosis_knapsack}"
        elif key == "Program Pengendalian Gulma":
            ket = f"{keterangan_pengendalian_gulma}"
        elif key == "Penggunaan HK Sesuai Norma Pekerjaan":
            ket = f"{keterangan_penggunaan_hk}"
        elif key == "APD Pekerja":
            ket = f"{keterangan_apd_pekerja}"
        elif key == "Kotak P3K Isi Lengkap dan Dibawa Oleh Mandor":
            ket = f"{keterangan_p3k}"
        elif key == "Terdapat Kartu Pengambilan dan Pencampuran Bahan":
            ket = f"{keterangan_kartu_pengambilan_pencampuran_bahan}"
        elif key == "Terdapat Kalibrasi Alat dan Nozel":
            ket = f"{keterangan_kalibrasi_alat_nozel}"
        elif key == "Membawa Gelas Ukur & Perkakas Perbaikan Alat Semprot":
            ket = f"{keterangan_alat_ukur_perkakas_perbaikan}"
        elif key == "Peletakan Alat Semprot":
            ket = f"{keterangan_peletakan_alat_semprot}"
        else:
            ket = ""

        table.append({"Parameter": key, "Score": score, "Nilai": round(nilai,2), "Keterangan": ket})

    # Tampilkan ke tabel (treeview)
    for i in tree.get_children():
        tree.delete(i)
    total_nilai = 0
    for item in table:
        if item["Nilai"] != 0:
            tree.insert("", "end", values=(item["Parameter"], item["Score"], item["Nilai"], item["Keterangan"]))
            total_nilai += item["Nilai"]
    tree.insert("", "end", values=("TOTAL", "", round(total_nilai, 2), ""), tags=("total",))
    tree.tag_configure("total", background="#e0e0e0", font=("Arial", 10, "bold"))

# %%
def update_estate_combobox():
    global combobox_estate, available_estate_list, selected_estate
    if combobox_estate:
        combobox_estate['values'] = available_estate_list
        if available_estate_list:
            selected_estate.set(available_estate_list[0])
        else:
            selected_estate.set("None")

# %%
def update_divisi_combobox():
    global combobox_divisi, available_divisi_list, selected_divisi
    if combobox_divisi:
        combobox_divisi['values'] = available_divisi_list
        if available_divisi_list:
            selected_divisi.set(available_divisi_list[0])
        else:
            selected_divisi.set("None")

# %%
def update_blok_combobox():
    global combobox_blok, available_blok_list, selected_blok
    if combobox_blok:
        combobox_blok['values'] = available_blok_list
        if available_blok_list:
            selected_blok.set(available_blok_list[0])
        else:
            selected_blok.set("None")

# %%
def processed_pdfs(processed_pdf_files, rejected_pdf_files, approved_pdf_files):
    global pdf_id, \
    processed_table, \
    rejected_table, \
    approved_table, \
    button_approve, \
    button_decline, \
    back_button, \
    current_menu, \
    pdf_display_area
        
    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "processed_pdfs"
    pdf_id = ""

    # === SCROLLABLE CONTAINER ===
    outer_frame = tk.Frame(root)
    outer_frame.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)

    scrollable_frame = make_scrollable_frame(outer_frame)
    scrollable_frame.grid_columnconfigure(0, weight=1)

    row = 0

    # Processed pdfs
    label_processed_pdfs = make_label(parent=scrollable_frame, text="Processed PDF", row=row, font=("Arial", 16, "bold"))
    row += 1

    processed_table = ttk.Treeview(scrollable_frame, columns=PDF_TABLE_COLUMNS, show="headings", height=12)
    for col in PDF_TABLE_COLUMNS:
        processed_table.heading(col, text=col)
        processed_table.column(col, anchor="center", width=180)
    processed_table.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1
    
    # Rejected pdfs
    label_rejected_pdfs = make_label(parent=scrollable_frame, text="Rejected PDF", row=row, font=("Arial", 16, "bold"))
    row += 1

    rejected_table = ttk.Treeview(scrollable_frame, columns=PDF_TABLE_COLUMNS, show="headings", height=12)
    for col in PDF_TABLE_COLUMNS:
        rejected_table.heading(col, text=col)
        rejected_table.column(col, anchor="center", width=180)
    rejected_table.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1
    
    # Mengikat event <<TreeviewSelect>> untuk menangkap pilihan baris
    # Pass None for pdf_files so display_pdf will use the up-to-date global lists
    rejected_table.bind("<<TreeviewSelect>>", lambda event: display_pdf(event, None, "Rejected"))

    # Approved pdfs
    label_approved_pdfs = make_label(parent=scrollable_frame, text="Approved PDF", row=row, font=("Arial", 16, "bold"))
    row += 1

    approved_table = ttk.Treeview(scrollable_frame, columns=PDF_TABLE_COLUMNS, show="headings", height=12)
    for col in PDF_TABLE_COLUMNS:
        approved_table.heading(col, text=col)
        approved_table.column(col, anchor="center", width=180)
    approved_table.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1
    
    # Mengikat event <<TreeviewSelect>> untuk menangkap pilihan baris
    # Pass None for pdf_files so display_pdf will use the up-to-date global lists
    approved_table.bind("<<TreeviewSelect>>", lambda event: display_pdf(event, None, "Approved"))

    # Untuk menampilkan PDF yang sedang direview
    pdf_display_area = tk.Label(scrollable_frame, text="Select a PDF to preview", font=("Arial", 12))
    pdf_display_area.grid(row=row, column=0, padx=10, pady=10, sticky="w")
    row += 1

    button_approve = make_button(scrollable_frame, text="Approve", row=row, command=lambda: [approve_selected_pdf(pdf_id, PDF_PROCESSED_FOLDER_ID, PDF_APPROVED_FOLDER_ID)], font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1
    
    button_decline = make_button(scrollable_frame, text="Decline", row=row, command=lambda: [decline_selected_pdf(pdf_id, PDF_PROCESSED_FOLDER_ID, PDF_REJECTED_FOLDER_ID)], font=("Arial", 10), bg=EXIT_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    back_button = make_button(scrollable_frame, text="Refresh Tables", row=row+1, command=refresh_table, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    back_button = make_button(scrollable_frame, text="Back", row=row+1, command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    global conditional_widgets
    conditional_widgets = [
        button_approve,
        button_decline
    ]

    # Mengikat event <<TreeviewSelect>> untuk menangkap pilihan baris di processed table & menampilkan button approve/decline
    # Don't pass a snapshot of processed_pdf_files (it may become stale after refresh).
    processed_table.bind("<<TreeviewSelect>>", lambda event: (display_pdf(event, None, "Processed"), toggle_pdf_report_button_visibility()))
    toggle_pdf_report_button_visibility()
    refresh_table()

# %%
def qa_calculate_production():
    global label_tanggal_qa_terakhir, entry_tanggal_qa_terakhir, button_tanggal_qa_terakhir, \
        label_tanggal_kosong, label_tanggal_salah, \
        label_identifikasi_qa, \
        label_estate, selected_estate, combobox_estate, \
        label_divisi, selected_divisi, combobox_divisi, \
        label_blok, selected_blok, combobox_blok, \
        label_mandor, entry_mandor, \
        label_sph, entry_sph, \
        label_actual, entry_actual, \
        label_budget, entry_budget, \
        label_restant, entry_restant, \
        label_jaring, entry_jaring, \
        label_produktivitas_pemanen, entry_produktivitas_pemanen, \
        label_administrasi_panen, entry_administrasi_panen, \
        label_kualitas_tbs, entry_kualitas_tbs, \
        label_muatan_overload, entry_muatan_overload, \
        process_calculation_production_button, \
        tree, \
        photo_upload_frame, button_upload_photo, \
        submit_calculation_production_button, back_button, \
        current_menu, \
        available_estate_list, available_divisi_list, available_blok_list

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "qa_calculate_production"
    year = combobox_chosen_year.get()
    weights = extract_weights_by_year(YEARLY_WEIGHT_PRODUCTION, year)
    print(f"Bobot untuk tahun {year}: {weights}")

    # === SCROLLABLE CONTAINER ===
    outer_frame = tk.Frame(root)
    outer_frame.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)

    scrollable_frame = make_scrollable_frame(outer_frame)
    scrollable_frame.grid_columnconfigure(0, weight=1)

    row = 0

    label_qa_production = make_label(parent=scrollable_frame, text="QA Produksi", row=row, font=("Arial", 16, "bold"))
    row += 1

    label_tanggal_qa_terakhir = make_label(parent=scrollable_frame, text="Masukkan tanggal QA:", row=row, font=("Arial", 12))
    row += 1

    entry_tanggal_qa_terakhir = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    button_tanggal_qa_terakhir = make_button(scrollable_frame, text="Select Date", row=row, command=lambda: [get_date(entry_tanggal_qa_terakhir), toggle_qa_visibility(), get_available_estate_list(df_mobile_produksi_input)], font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    label_tanggal_kosong = make_label(parent=scrollable_frame, text="Tanggal Belum Dipilih", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_tanggal_salah = make_label(parent=scrollable_frame, text="Format Tanggal Salah", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_identifikasi_qa = make_label(parent=scrollable_frame, text="Detail QA Produksi", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_estate = make_label(parent=scrollable_frame, text="Masukkan Nama Estate:", row=row, font=("Arial", 12))
    row += 1
    
    selected_estate = tk.StringVar(value=available_estate_list[0])
    combobox_estate, _ = make_combobox(scrollable_frame, values=available_estate_list, row=row, state="readonly", textvariable=selected_estate)
    row += 1
    combobox_estate.bind("<<ComboboxSelected>>", lambda event: get_available_divisi_list(df_mobile_produksi_input))

    label_divisi = make_label(parent=scrollable_frame, text="Masukkan Nama Divisi:", row=row, font=("Arial", 12))
    row += 1
    
    selected_divisi = tk.StringVar(value=available_divisi_list[0])
    combobox_divisi, _ = make_combobox(scrollable_frame, values=available_divisi_list, row=row, state="readonly", textvariable=selected_divisi)
    row += 1
    combobox_divisi.bind("<<ComboboxSelected>>", lambda event: get_available_blok_list(df_mobile_produksi_input))

    label_blok = make_label(parent=scrollable_frame, text="Masukkan Nama Blok:", row=row, font=("Arial", 12))
    row += 1
    
    selected_blok = tk.StringVar(value=available_blok_list[0])
    combobox_blok, _ = make_combobox(scrollable_frame, values=available_blok_list, row=row, state="readonly", textvariable=selected_blok)
    row += 1

    label_mandor = make_label(parent=scrollable_frame, text="Mandor Panen", row=row, font=("Arial", 12))
    row+=1

    entry_mandor = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row+=1

    label_sph = make_label(parent=scrollable_frame, text="SPH", row=row, font=("Arial", 12))
    row+=1

    entry_sph = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row+=1

    label_actual = make_label(parent=scrollable_frame, text="Actual", row=row, font=("Arial", 12))
    row += 1

    entry_actual = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    label_budget = make_label(parent=scrollable_frame, text="Budget", row=row, font=("Arial", 12))
    row += 1

    entry_budget = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    label_restant = make_label(parent=scrollable_frame, text="Nilai restan dalam persen (%)", row=row, font=("Arial", 12))
    row += 1

    entry_restant = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    label_jaring = make_label(parent=scrollable_frame, text="Total jaring", row=row, font=("Arial", 12))
    row += 1

    entry_jaring = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    if not is_zero_weight_year("produktivitas pemanen", weights):
        label_produktivitas_pemanen = make_label(parent=scrollable_frame, text="Masukkan produktivitas pemanen (Kg/HK)", row=row, font=("Arial", 12))
        row += 1

        entry_produktivitas_pemanen = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
        row += 1

    if not is_zero_weight_year("administrasi panen", weights):
        label_administrasi_panen = make_label(parent=scrollable_frame, text="Masukkan administrasi panen", row=row, font=("Arial", 12))
        row += 1

        entry_administrasi_panen = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
        row += 1

    if not is_zero_weight_year("kualitas TBS", weights):
        label_kualitas_tbs = make_label(parent=scrollable_frame, text="Masukkan kualitas TBS (Kg/Jjg)", row=row, font=("Arial", 12))
        row += 1

        entry_kualitas_tbs = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
        row += 1
    
    if not is_zero_weight_year("muatan overload", weights):
        label_muatan_overload = make_label(parent=scrollable_frame, text="Masukkan muatan overload", row=row, font=("Arial", 12))
        row += 1

        entry_muatan_overload = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
        row += 1

    process_calculation_production_button = make_button(scrollable_frame, text="Process", row=row, command = lambda: process_production_calculation(df_mobile_produksi_input), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    tree = ttk.Treeview(scrollable_frame, columns=TABLE_COLUMNS, show="headings", height=12)
    for col in TABLE_COLUMNS:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=180)
    tree.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1
    
    # === UPLOAD PHOTO SECTION ===
    photo_upload_frame = tk.Frame(scrollable_frame)
    photo_upload_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    button_upload_photo = make_button(scrollable_frame, text="Tambahkan Foto", row=row, command=add_photo_row, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    submit_calculation_production_button = make_button(scrollable_frame, text="Submit", row=row, command=submit_production_analysis, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    back_button = make_button(scrollable_frame, text="Back", row=row, command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    global qa_conditional_widgets
    qa_conditional_widgets = [
        label_identifikasi_qa, 
        label_estate, combobox_estate,
        label_divisi, combobox_divisi,
        label_blok, combobox_blok,
        label_mandor, entry_mandor,
        label_sph, entry_sph,
        label_actual, entry_actual,
        label_budget, entry_budget,
        label_restant, entry_restant,
        label_jaring, entry_jaring,
        process_calculation_production_button,
        tree,
        photo_upload_frame,
        button_upload_photo,
        submit_calculation_production_button
    ]

    if label_produktivitas_pemanen is not None and entry_produktivitas_pemanen is not None:
        qa_conditional_widgets.append(label_produktivitas_pemanen)
        qa_conditional_widgets.append(entry_produktivitas_pemanen)

    if label_administrasi_panen is not None and entry_administrasi_panen is not None:
        qa_conditional_widgets.append(label_administrasi_panen)
        qa_conditional_widgets.append(entry_administrasi_panen)

    if label_kualitas_tbs is not None and entry_kualitas_tbs is not None:
        qa_conditional_widgets.append(label_kualitas_tbs)
        qa_conditional_widgets.append(entry_kualitas_tbs)

    if label_muatan_overload is not None and entry_muatan_overload is not None:
        qa_conditional_widgets.append(label_muatan_overload)
        qa_conditional_widgets.append(entry_muatan_overload)

    entry_tanggal_qa_terakhir.bind("<KeyRelease>", toggle_qa_visibility)
    toggle_qa_visibility()


# %%
def qa_calculate_nursery():
    global label_tanggal_qa_terakhir, entry_tanggal_qa_terakhir, button_tanggal_qa_terakhir, \
        label_tanggal_kosong, label_tanggal_salah, \
        label_identifikasi_qa, \
        label_estate, selected_estate, combobox_estate, \
        label_divisi, selected_divisi, combobox_divisi, \
        label_blok, selected_blok, combobox_blok, \
        label_mandor, entry_mandor, \
        label_cover_crop_title, label_cover_crop, entry_cover_crop, label_keterangan_cover_crop, entry_keterangan_cover_crop, \
        label_barn_owl_title, label_barn_owl, combobox_barn_owl, label_keterangan_barn_owl, entry_keterangan_barn_owl, \
        tree, \
        photo_upload_frame, button_upload_photo, \
        submit_calculation_nursery_button, back_button, \
        current_menu, \
        available_estate_list, available_divisi_list, available_blok_list

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "qa_calculate_nursery"
    year = combobox_chosen_year.get()
    weights = extract_weights_by_year(YEARLY_WEIGHT_NURSERY, year)
    print(f"Bobot untuk tahun {year}: {weights}")

    # === SCROLLABLE CONTAINER ===
    outer_frame = tk.Frame(root)
    outer_frame.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)

    scrollable_frame = make_scrollable_frame(outer_frame)

    # Add this line to make entries stretch full width
    scrollable_frame.grid_columnconfigure(0, weight=1)

    row = 0

    label_qa_nursery = make_label(parent=scrollable_frame, text="QA Perawatan", row=row, font=("Arial", 16, "bold"))
    row += 1

    label_tanggal_qa_terakhir = make_label(parent=scrollable_frame, text="Masukkan tanggal QA:", row=row, font=("Arial", 12))
    row += 1

    entry_tanggal_qa_terakhir = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    button_tanggal_qa_terakhir = make_button(scrollable_frame, text="Select Date", row=row, command=lambda: [get_date(entry_tanggal_qa_terakhir), toggle_qa_visibility(), get_available_estate_list(df_mobile_perawatan_input)], font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    label_tanggal_kosong = make_label(parent=scrollable_frame, text="Tanggal Belum Dipilih", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_tanggal_salah = make_label(parent=scrollable_frame, text="Format Tanggal Salah", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_identifikasi_qa = make_label(parent=scrollable_frame, text="Detail QA Perawatan", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_estate = make_label(parent=scrollable_frame, text="Masukkan Nama Estate:", row=row, font=("Arial", 12))
    row += 1
    
    selected_estate = tk.StringVar(value=available_estate_list[0])
    combobox_estate, _ = make_combobox(scrollable_frame, values=available_estate_list, row=row, state="readonly", textvariable=selected_estate)
    row += 1
    combobox_estate.bind("<<ComboboxSelected>>", lambda event: get_available_divisi_list(df_mobile_perawatan_input))

    label_divisi = make_label(parent=scrollable_frame, text="Masukkan Nama Divisi:", row=row, font=("Arial", 12))
    row += 1
    
    selected_divisi = tk.StringVar(value=available_divisi_list[0])
    combobox_divisi, _ = make_combobox(scrollable_frame, values=available_divisi_list, row=row, state="readonly", textvariable=selected_divisi)
    row += 1
    combobox_divisi.bind("<<ComboboxSelected>>", lambda event: get_available_blok_list(df_mobile_perawatan_input))

    label_blok = make_label(parent=scrollable_frame, text="Masukkan Nama Blok:", row=row, font=("Arial", 12))
    row += 1
    
    selected_blok = tk.StringVar(value=available_blok_list[0])
    combobox_blok, _ = make_combobox(scrollable_frame, values=available_blok_list, row=row, state="readonly", textvariable=selected_blok)
    row += 1

    label_mandor = make_label(parent=scrollable_frame, text="Mandor Perawatan", row=row, font=("Arial", 12))
    row+=1

    entry_mandor = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row+=1
    
    # Cover Crop
    label_cover_crop_title = make_label(parent=scrollable_frame, text="Cover Crop", row=row, font=("Arial", 14, "bold"))
    row += 1

    if not is_zero_weight_year("Cover Crop (Neprolepis sp.)", weights):
        label_cover_crop = make_label(parent=scrollable_frame, text="Masukkan Jumlah Cover Crop (Neprolepis sp.):", row=row, font=("Arial", 12))
        row += 1

        entry_cover_crop = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
        row += 1

    label_keterangan_cover_crop = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan Cover Crop:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_cover_crop = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    # Barn Owl
    label_barn_owl_title = make_label(parent=scrollable_frame, text="Barn Owl", row=row, font=("Arial", 14, "bold"))
    row += 1

    if not is_zero_weight_year("Barn Owl", weights):
        label_barn_owl = make_label(parent=scrollable_frame, text="Masukkan Score Barn Owl:", row=row, font=("Arial", 12))
        row += 1

        combobox_barn_owl, _ = make_combobox(scrollable_frame, values=BARN_OWL_OPTIONS, row=row)
        row += 1

    label_keterangan_barn_owl = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan Barn Owl:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_barn_owl = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    process_calculation_nursery_button = make_button(scrollable_frame, text="Process", row=row, command= lambda: process_nursery_calculation(df_mobile_perawatan_input), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    tree = ttk.Treeview(scrollable_frame, columns=TABLE_COLUMNS, show="headings", height=12)
    for col in TABLE_COLUMNS:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=180)
    tree.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    # === UPLOAD PHOTO SECTION ===
    photo_upload_frame = tk.Frame(scrollable_frame)
    photo_upload_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1
    
    button_upload_photo = make_button(scrollable_frame, text="Tambahkan Foto", row=row, command=add_photo_row, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    submit_calculation_nursery_button = make_button(scrollable_frame, text="Submit", row=row, command=submit_nursery_analysis, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    back_button = make_button(scrollable_frame, text="Back", row=row, command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    global qa_conditional_widgets
    qa_conditional_widgets = [
        label_identifikasi_qa, 
        label_estate, combobox_estate,
        label_divisi, combobox_divisi,
        label_blok, combobox_blok,
        label_mandor, entry_mandor,
        label_cover_crop_title, label_keterangan_cover_crop, entry_keterangan_cover_crop,
        label_barn_owl_title, label_keterangan_barn_owl, entry_keterangan_barn_owl,
        process_calculation_nursery_button,
        tree,
        photo_upload_frame,
        button_upload_photo,
        submit_calculation_nursery_button
    ]

    if label_cover_crop is not None and entry_cover_crop is not None:
        qa_conditional_widgets.append(label_cover_crop)
        qa_conditional_widgets.append(entry_cover_crop)

    if label_barn_owl is not None and combobox_barn_owl is not None:
        qa_conditional_widgets.append(label_barn_owl)
        qa_conditional_widgets.append(combobox_barn_owl)

    entry_tanggal_qa_terakhir.bind("<KeyRelease>", toggle_qa_visibility)
    toggle_qa_visibility()

# %%
def qa_calculate_fertilizer():
    global label_tanggal_qa_terakhir, entry_tanggal_qa_terakhir, button_tanggal_qa_terakhir, \
            label_tanggal_kosong, label_tanggal_salah, \
            label_identifikasi_qa, \
            label_estate, selected_estate, combobox_estate, \
            label_divisi, selected_divisi, combobox_divisi, \
            label_blok, selected_blok, combobox_blok, \
            label_mandor, entry_mandor, \
            label_organisasi_title, \
            label_keterangan_supervisi, entry_keterangan_supervisi, \
            label_pemeriksaan_ancak, combobox_pemeriksaan_ancak, \
            label_jadwal_pemupukan, combobox_jadwal_pemupukan, label_keterangan_jadwal_pemupukan, entry_keterangan_jadwal_pemupukan, \
            label_penanganan_pupuk_title, \
            label_peletakan_pupuk, combobox_peletakan_pupuk, \
            label_pupuk_tercecer, combobox_pupuk_tercecer, \
            label_pengembalian_karung, combobox_pengembalian_karung, \
            tree, \
            photo_upload_frame, button_upload_photo, \
            submit_calculation_fertilizer_button, back_button, \
            current_menu, \
            available_estate_list, available_divisi_list, available_blok_list

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "qa_calculate_fertilizer"
    year = combobox_chosen_year.get()
    weights = extract_weights_by_year(YEARLY_WEIGHT_FERTILIZER, year)
    print(f"Bobot untuk tahun {year}: {weights}")

    # === SCROLLABLE CONTAINER ===
    outer_frame = tk.Frame(root)
    outer_frame.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)

    scrollable_frame = make_scrollable_frame(outer_frame)
    scrollable_frame.grid_columnconfigure(0, weight=1)

    row = 0

    label_qa_fertilizer = make_label(parent=scrollable_frame, text="QA Fertilizer", row=row, font=("Arial", 16, "bold"))
    row += 1

    label_tanggal_qa_terakhir = make_label(parent=scrollable_frame, text="Masukkan tanggal QA:", row=row, font=("Arial", 12))
    row += 1

    entry_tanggal_qa_terakhir = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    button_tanggal_qa_terakhir = make_button(scrollable_frame, text="Select Date", row=row, command=lambda: [get_date(entry_tanggal_qa_terakhir), toggle_qa_visibility(), get_available_estate_list(df_mobile_pemupukan_input)], font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    label_tanggal_kosong = make_label(parent=scrollable_frame, text="Tanggal Belum Dipilih", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_tanggal_salah = make_label(parent=scrollable_frame, text="Format Tanggal Salah", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_identifikasi_qa = make_label(parent=scrollable_frame, text="Detail QA Fertilizer", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_estate = make_label(parent=scrollable_frame, text="Masukkan Nama Estate:", row=row, font=("Arial", 12))
    row += 1
    
    selected_estate = tk.StringVar(value=available_estate_list[0])
    combobox_estate, _ = make_combobox(scrollable_frame, values=available_estate_list, row=row, state="readonly", textvariable=selected_estate)
    row += 1
    combobox_estate.bind("<<ComboboxSelected>>", lambda event: get_available_divisi_list(df_mobile_pemupukan_input))

    label_divisi = make_label(parent=scrollable_frame, text="Masukkan Nama Divisi:", row=row, font=("Arial", 12))
    row += 1
    
    selected_divisi = tk.StringVar(value=available_divisi_list[0])
    combobox_divisi, _ = make_combobox(scrollable_frame, values=available_divisi_list, row=row, state="readonly", textvariable=selected_divisi)
    row += 1
    combobox_divisi.bind("<<ComboboxSelected>>", lambda event: get_available_blok_list(df_mobile_pemupukan_input))

    label_blok = make_label(parent=scrollable_frame, text="Masukkan Nama Blok:", row=row, font=("Arial", 12))
    row += 1
    
    selected_blok = tk.StringVar(value=available_blok_list[0])
    combobox_blok, _ = make_combobox(scrollable_frame, values=available_blok_list, row=row, state="readonly", textvariable=selected_blok)
    row += 1

    label_mandor = make_label(parent=scrollable_frame, text="Mandor Pupuk", row=row, font=("Arial", 12))
    row+=1

    entry_mandor = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row+=1
    
    # Organisasi
    label_organisasi_title = make_label(parent=scrollable_frame, text="Organisasi", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_keterangan_supervisi = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan supervisi:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_supervisi = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1
    
    label_pemeriksaan_ancak = make_label(parent=scrollable_frame, text="Masukkan Score Terdapatnya Pemeriksaan Ancak Pemupukan:", row=row, font=("Arial", 12))
    row += 1

    combobox_pemeriksaan_ancak, _ = make_combobox(scrollable_frame, values=PEMERIKSAAN_ANCAK_PEMUPUKAN_OPTIONS, row=row)
    row += 1

    label_jadwal_pemupukan = make_label(parent=scrollable_frame, text="Masukkan Score Jadwal Pemupukan:", row=row, font=("Arial", 12))
    row += 1

    combobox_jadwal_pemupukan, _ = make_combobox(scrollable_frame, values=JADWAL_PEMUPUKAN_OPTIONS, row=row)
    row += 1

    label_keterangan_jadwal_pemupukan = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan jadwal pemupukan:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_jadwal_pemupukan = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1
    
    # Penanganan Pupuk
    label_penanganan_pupuk_title = make_label(parent=scrollable_frame, text="Penanganan Pupuk", row=row, font=("Arial", 14, "bold"))
    row += 1
    
    if not is_zero_weight_year("Peletakan Pupuk", weights):
        label_peletakan_pupuk = make_label(parent=scrollable_frame, text="Masukkan Score Peletakan Pupuk:", row=row, font=("Arial", 12))
        row += 1

        combobox_peletakan_pupuk, _ = make_combobox(scrollable_frame, values=PELETAKAN_PUPUK_OPTIONS, row=row)
        row += 1
        
    if not is_zero_weight_year("Pupuk Tercecer", weights):
        label_pupuk_tercecer = make_label(parent=scrollable_frame, text="Masukkan Score Pupuk Tercecer:", row=row, font=("Arial", 12))
        row += 1

        combobox_pupuk_tercecer, _ = make_combobox(scrollable_frame, values=PUPUK_TERCECER_OPTIONS, row=row)
        row += 1
        
    if not is_zero_weight_year("Pengembalian Karung", weights):
        label_pengembalian_karung = make_label(parent=scrollable_frame, text="Masukkan Score Pengembalian Karung:", row=row, font=("Arial", 12))
        row += 1

        combobox_pengembalian_karung, _ = make_combobox(scrollable_frame, values=PENGEMBALIAN_KARUNG_OPTIONS, row=row)
        row += 1
        
    process_calculation_fertilizer_button = make_button(scrollable_frame, text="Process", row=row, command= lambda: process_fertilizer_calculation(df_mobile_pemupukan_input), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    tree = ttk.Treeview(scrollable_frame, columns=TABLE_COLUMNS, show="headings", height=12)
    for col in TABLE_COLUMNS:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=180)
    tree.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    # === UPLOAD PHOTO SECTION ===
    photo_upload_frame = tk.Frame(scrollable_frame)
    photo_upload_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1
    
    button_upload_photo = make_button(scrollable_frame, text="Tambahkan Foto", row=row, command=add_photo_row, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    submit_calculation_fertilizer_button = make_button(scrollable_frame, text="Submit", row=row, command=submit_fertilizer_analysis, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    back_button = make_button(scrollable_frame, text="Back", row=row, command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    global qa_conditional_widgets
    qa_conditional_widgets = [
        label_identifikasi_qa, 
        label_estate, combobox_estate,
        label_divisi, combobox_divisi,
        label_blok, combobox_blok,
        label_mandor, entry_mandor,
        process_calculation_fertilizer_button,
        label_organisasi_title,
        label_keterangan_supervisi, entry_keterangan_supervisi,
        label_pemeriksaan_ancak, combobox_pemeriksaan_ancak,
        label_jadwal_pemupukan, combobox_jadwal_pemupukan,
        label_keterangan_jadwal_pemupukan, entry_keterangan_jadwal_pemupukan,
        label_penanganan_pupuk_title,
        tree,
        photo_upload_frame,
        button_upload_photo,
        submit_calculation_fertilizer_button
    ]
    
    if label_peletakan_pupuk is not None and combobox_peletakan_pupuk is not None:
        qa_conditional_widgets.append(label_peletakan_pupuk)
        qa_conditional_widgets.append(combobox_peletakan_pupuk)

    if label_pupuk_tercecer is not None and combobox_pupuk_tercecer is not None:
        qa_conditional_widgets.append(label_pupuk_tercecer)
        qa_conditional_widgets.append(combobox_pupuk_tercecer)

    if label_pengembalian_karung is not None and combobox_pengembalian_karung is not None:
        qa_conditional_widgets.append(label_pengembalian_karung)
        qa_conditional_widgets.append(combobox_pengembalian_karung)

    entry_tanggal_qa_terakhir.bind("<KeyRelease>", toggle_qa_visibility)
    toggle_qa_visibility()


# %%
def qa_calculate_chemist():
    global label_tanggal_qa_terakhir, entry_tanggal_qa_terakhir, button_tanggal_qa_terakhir, \
            label_tanggal_kosong, label_tanggal_salah, \
            label_identifikasi_qa, \
            label_estate, selected_estate, combobox_estate, \
            label_divisi, selected_divisi, combobox_divisi, \
            label_blok, selected_blok, combobox_blok, \
            label_mandor, entry_mandor, \
            label_kualitas_aplikasi_title, \
            label_keterangan_kematian_gulma, entry_keterangan_kematian_gulma, \
            label_keterangan_pokok_tersemprot, entry_keterangan_pokok_tersemprot, \
            label_bahan_alat_title, \
            label_keterangan_bahan_herbisida, entry_keterangan_bahan_herbisida, \
            label_keterangan_kondisi_alat_semprot, entry_keterangan_kondisi_alat_semprot, \
            label_keterangan_keseragaman_nozel, entry_keterangan_keseragaman_nozel, \
            label_keterangan_standard_dosis_knapsack, entry_keterangan_standard_dosis_knapsack, \
            label_organisasi_apd_title, \
            label_keterangan_pengendalian_gulma, entry_keterangan_pengendalian_gulma, \
            label_keterangan_penggunaan_hk, entry_keterangan_penggunaan_hk, \
            label_keterangan_apd_pekerja, entry_keterangan_apd_pekerja, \
            label_p3k, combobox_p3k, label_keterangan_p3k, entry_keterangan_p3k, \
            label_administrasi_penanganan_title, \
            label_keterangan_kartu_pengambilan_pencampuran_bahan, entry_keterangan_kartu_pengambilan_pencampuran_bahan, \
            label_keterangan_kalibrasi_alat_nozel, entry_keterangan_kalibrasi_alat_nozel, \
            label_keterangan_alat_ukur_perkakas_perbaikan, entry_keterangan_alat_ukur_perkakas_perbaikan, \
            label_keterangan_peletakan_alat_semprot, entry_keterangan_peletakan_alat_semprot, \
            tree, \
            photo_upload_frame, button_upload_photo, \
            submit_calculation_chemist_button, back_button, \
            current_menu, \
            available_estate_list, available_divisi_list, available_blok_list

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "qa_calculate_chemist"
    year = combobox_chosen_year.get()
    weights = extract_weights_by_year(YEARLY_WEIGHT_CHEMIST, year)
    print(f"Bobot untuk tahun {year}: {weights}")

    # === SCROLLABLE CONTAINER ===
    outer_frame = tk.Frame(root)
    outer_frame.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)

    scrollable_frame = make_scrollable_frame(outer_frame)
    scrollable_frame.grid_columnconfigure(0, weight=1)

    row = 0

    label_qa_chemist = make_label(parent=scrollable_frame, text="QA Chemist", row=row, font=("Arial", 16, "bold"))
    row += 1

    label_tanggal_qa_terakhir = make_label(parent=scrollable_frame, text="Masukkan tanggal QA:", row=row, font=("Arial", 12))
    row += 1

    entry_tanggal_qa_terakhir = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    button_tanggal_qa_terakhir = make_button(scrollable_frame, text="Select Date", row=row, command=lambda: [get_date(entry_tanggal_qa_terakhir), toggle_qa_visibility(), get_available_estate_list(df_mobile_chemist_input)], font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    label_tanggal_kosong = make_label(parent=scrollable_frame, text="Tanggal Belum Dipilih", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_tanggal_salah = make_label(parent=scrollable_frame, text="Format Tanggal Salah", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_identifikasi_qa = make_label(parent=scrollable_frame, text="Detail QA Chemist", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_estate = make_label(parent=scrollable_frame, text="Masukkan Nama Estate:", row=row, font=("Arial", 12))
    row += 1
    
    selected_estate = tk.StringVar(value=available_estate_list[0])
    combobox_estate, _ = make_combobox(scrollable_frame, values=available_estate_list, row=row, state="readonly", textvariable=selected_estate)
    row += 1
    combobox_estate.bind("<<ComboboxSelected>>", lambda event: get_available_divisi_list(df_mobile_chemist_input))

    label_divisi = make_label(parent=scrollable_frame, text="Masukkan Nama Divisi:", row=row, font=("Arial", 12))
    row += 1
    
    selected_divisi = tk.StringVar(value=available_divisi_list[0])
    combobox_divisi, _ = make_combobox(scrollable_frame, values=available_divisi_list, row=row, state="readonly", textvariable=selected_divisi)
    row += 1
    combobox_divisi.bind("<<ComboboxSelected>>", lambda event: get_available_blok_list(df_mobile_chemist_input))

    label_blok = make_label(parent=scrollable_frame, text="Masukkan Nama Blok:", row=row, font=("Arial", 12))
    row += 1
    
    selected_blok = tk.StringVar(value=available_blok_list[0])
    combobox_blok, _ = make_combobox(scrollable_frame, values=available_blok_list, row=row, state="readonly", textvariable=selected_blok)
    row += 1

    label_mandor = make_label(parent=scrollable_frame, text="Mandor Chemist", row=row, font=("Arial", 12))
    row+=1

    entry_mandor = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row+=1

    # Kualitas Aplikasi
    label_kualitas_aplikasi_title = make_label(parent=scrollable_frame, text="Kualitas Aplikasi", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_keterangan_kematian_gulma = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan kematian gulma:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_kematian_gulma = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    label_keterangan_pokok_tersemprot = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan pokok tersemprot:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_pokok_tersemprot = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    # Kualitas Bahan dan Alat
    label_bahan_alat_title = make_label(parent=scrollable_frame, text="Kualitas Bahan dan Alat", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_keterangan_bahan_herbisida = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan bahan herbisida yang dibawa ke ancak:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_bahan_herbisida = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    label_keterangan_kondisi_alat_semprot = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan kondisi alat semprot:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_kondisi_alat_semprot = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    label_keterangan_keseragaman_nozel = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan keseragaman nozel:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_keseragaman_nozel = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    label_keterangan_standard_dosis_knapsack = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan dosis per knapsack:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_standard_dosis_knapsack = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    # Organisasi & APD
    label_organisasi_apd_title = make_label(parent=scrollable_frame, text="Organisasi & APD", row=row, font=("Arial", 14, "bold"))
    row += 1

    label_keterangan_pengendalian_gulma = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan pengendalian gulma:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_pengendalian_gulma = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1
    
    label_keterangan_penggunaan_hk = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan penggunaan HK:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_penggunaan_hk = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    if not is_zero_weight_year("Kotak P3K Isi Lengkap dan Dibawa Oleh Mandor", weights):
        label_p3k = make_label(parent=scrollable_frame, text="Kotak P3K Isi Lengkap dan Dibawa Mandor:", row=row, font=("Arial", 12))
        row += 1

        combobox_p3k, _ = make_combobox(scrollable_frame, values=KOTAK_P3K_OPTIONS, row=row)
        row += 1

    label_keterangan_p3k = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan Kotak P3K yang Dibawa Mandor:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_p3k = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1
    
    label_keterangan_apd_pekerja = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan APD Pekerja:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_apd_pekerja = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    # Administrasi dan Penanganan
    label_administrasi_penanganan_title = make_label(parent=scrollable_frame, text="Administrasi dan Penanganan", row=row, font=("Arial", 14, "bold"))
    row += 1
    
    label_keterangan_kartu_pengambilan_pencampuran_bahan = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan Kartu Pengambilan dan Pencampuran Bahan:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_kartu_pengambilan_pencampuran_bahan = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1
    
    label_keterangan_kalibrasi_alat_nozel = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan Kalibrasi Alat dan Nozel:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_kalibrasi_alat_nozel = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1
    
    label_keterangan_alat_ukur_perkakas_perbaikan = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan untuk membawa gelas ukur dan perkakas:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_alat_ukur_perkakas_perbaikan = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1
    
    label_keterangan_peletakan_alat_semprot = make_label(parent=scrollable_frame, text="Opsional, masukkan keterangan untuk peletakan alat semprot:", row=row, font=("Arial", 12))
    row += 1

    entry_keterangan_peletakan_alat_semprot = make_entry(parent=scrollable_frame, row=row, font=("Arial", 10))
    row += 1

    process_calculation_chemist_button = make_button(scrollable_frame, text="Process", row=row, command = lambda: process_chemist_calculation(df_mobile_chemist_input), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    tree = ttk.Treeview(scrollable_frame, columns=TABLE_COLUMNS, show="headings", height=12)
    for col in TABLE_COLUMNS:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=180)
    tree.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    # === UPLOAD PHOTO SECTION ===
    photo_upload_frame = tk.Frame(scrollable_frame)
    photo_upload_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1
    
    button_upload_photo = make_button(scrollable_frame, text="Tambahkan Foto", row=row, command=add_photo_row, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    submit_calculation_chemist_button = make_button(scrollable_frame, text="Submit", row=row, command=submit_chemist_analysis, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    back_button = make_button(scrollable_frame, text="Back", row=row, command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    row += 1

    global qa_conditional_widgets
    qa_conditional_widgets = [
        label_identifikasi_qa,
        label_estate, combobox_estate,
        label_divisi, combobox_divisi,
        label_blok, combobox_blok,
        label_mandor, entry_mandor,
        process_calculation_chemist_button,
        label_kualitas_aplikasi_title,
        label_keterangan_kematian_gulma, entry_keterangan_kematian_gulma,
        label_keterangan_pokok_tersemprot, entry_keterangan_pokok_tersemprot,
        label_bahan_alat_title,
        label_keterangan_bahan_herbisida, entry_keterangan_bahan_herbisida,
        label_keterangan_kondisi_alat_semprot, entry_keterangan_kondisi_alat_semprot,
        label_keterangan_keseragaman_nozel, entry_keterangan_keseragaman_nozel,
        label_keterangan_standard_dosis_knapsack, entry_keterangan_standard_dosis_knapsack,
        label_organisasi_apd_title,
        label_keterangan_pengendalian_gulma, entry_keterangan_pengendalian_gulma,
        label_keterangan_penggunaan_hk, entry_keterangan_penggunaan_hk,
        label_keterangan_p3k, entry_keterangan_p3k,
        label_keterangan_apd_pekerja, entry_keterangan_apd_pekerja,
        label_administrasi_penanganan_title,
        label_keterangan_kartu_pengambilan_pencampuran_bahan, entry_keterangan_kartu_pengambilan_pencampuran_bahan,
        label_keterangan_kalibrasi_alat_nozel, entry_keterangan_kalibrasi_alat_nozel,
        label_keterangan_alat_ukur_perkakas_perbaikan, entry_keterangan_alat_ukur_perkakas_perbaikan,
        label_keterangan_peletakan_alat_semprot, entry_keterangan_peletakan_alat_semprot,
        tree,
        photo_upload_frame,
        button_upload_photo,
        submit_calculation_chemist_button
    ]
    
    if label_p3k is not None and combobox_p3k is not None:
        qa_conditional_widgets.append(label_p3k)
        qa_conditional_widgets.append(combobox_p3k)
        
    entry_tanggal_qa_terakhir.bind("<KeyRelease>", toggle_qa_visibility)
    toggle_qa_visibility()

# %% [markdown]
#  ## 11. GUI - Window Management

# %%
def on_closing():
    global root_exists
    root_exists = False
    if root:
       root.destroy()

# %% [markdown]
#  ## 12. Main Application (`main_process`)

# %%
def main_process():
    # Define all globals used within this function and others it calls
    global root, previous_menu, root_exists, current_menu, \
           df, input_sheets, output_sheets, df_input_sheets, df_output_sheets, \
           df_mobile_input, df_input, df_output, df_output_weight, \
           chosen_year_weight, \
           photo_image, \
           username_var, username, \
           mobile_input_production, input_production, input_nursery, input_chemist, input_fertilizer, \
           output_production, output_nursery , output_chemist, output_fertilizer, \
           output_weight_production, output_weight_nursery , output_weight_chemist, output_weight_fertilizer, \
           label_username, entry_username, exit_button, label_rainfall_option, \
           button_update_rainfall, button_add_rainfall, back_button, \
           label_menu_qa, combobox_menu_qa, label_menu_data_overview, combobox_menu_data_overview, label_chosen_year, combobox_chosen_year, label_note_year, \
           label_estate_option, combobox_estate, submit_estate_button, \
           main_menu_button, submit_estate_check_button, \
           label_missing_dates_title, missing_dates_widgets, submit_missing_dates_button, \
           canvas, scrollbar, inner_frame, \
           label_daily_rainfall, entry_daily_rainfall, submit_add_rainfall_button, \
           label_update_rainfall, entry_update_rainfall, submit_update_rainfall_button, \
           entry_tanggal_qa_terakhir, entry_blok, entry_divisi, entry_mandor, entry_tanggal_rencana_pupuk, entry_pokok_sample, entry_pokok_panen, entry_sph, entry_actual, entry_budget, \
           entry_buah_panen, entry_buah_tertinggal, entry_berondolan_tertinggal, entry_buah_tertinggal_tph, \
           entry_berondolan_tertinggal_tph, entry_rotasi_panen, entry_restan, entry_jaring, entry_produktivitas_pemanen, \
           entry_administrasi_panen, entry_kualitas_tbs, entry_muatan_overload, \
           entry_kondisi_circle, entry_kondisi_path, entry_kondisi_tph, \
           entry_keterangan_cpt, entry_keterangan_gawangan, entry_keterangan_titi_panen, \
           entry_keterangan_jalan_jembatan, entry_keterangan_hama_penyakit, entry_keterangan_beneficial_plan, \
           entry_keterangan_peilscale, entry_keterangan_cover_crop, entry_keterangan_barn_owl, \
           entry_keterangan_pokok_tidak_terpupuk, entry_keterangan_piringan_gawangan, entry_keterangan_cara_aplikasi, \
           entry_keterangan_alat_tabur_seragam, entry_keterangan_dosis_alat_tabur, entry_keterangan_tenaga_pemupuk, \
           entry_keterangan_supervisi, entry_keterangan_pemeriksaan_ancak, entry_keterangan_jadwal_pemupukan, \
           entry_keterangan_apd_pekerja, entry_keterangan_fisik_pupuk, entry_keterangan_peletakan_pupuk, \
           entry_keterangan_pupuk_tercecer, entry_keterangan_pengembalian_karung, \
           entry_keterangan_kematian_gulma, entry_keterangan_pokok_tersemprot, entry_keterangan_bahan_herbisida, \
           entry_keterangan_kondisi_alat_semprot, entry_keterangan_keseragaman_nozel, entry_keterangan_standard_dosis_knapsack, \
           entry_keterangan_pengendalian_gulma, entry_keterangan_penggunaan_hk, entry_keterangan_apd_pekerja, \
           entry_keterangan_p3k, entry_keterangan_kartu_pengambilan_pencampuran_bahan, \
           entry_keterangan_kalibrasi_alat_nozel, entry_keterangan_alat_ukur_perkakas_perbaikan, entry_keterangan_peletakan_alat_semprot, \
           entry_lalang, entry_anak_kayu, entry_prupukan, entry_purun_tikus, \
           entry_pakis_udang, entry_pruning_baik, entry_pruning_over, \
           entry_sengkleh, entry_under_pruning, entry_pelepah_rapi, entry_serangan_tikus, \
           entry_serangan_rayap, entry_serangan_thirathaba, entry_serangan_updks, \
           entry_dosis_per_pokok, entry_tanggal_pemupukan, \
           entry_jenis_chemist, entry_dosis_knapsack, entry_tanggal_semprot, \
           entry_kematian_gulma, entry_pokok_tersemprot, \
           combobox_jenis_pupuk, entry_pokok_tidak_terpupuk, entry_ancak_gulma, entry_alat_tabur_seragam, entry_total_alat_tabur, \
           combobox_titi_panen, combobox_jalan_jembatan, combobox_beneficial_plan, \
           combobox_peilscale, entry_cover_crop, combobox_barn_owl, \
           combobox_cara_aplikasi, combobox_kesesuaian_dosis_alat_tabur, combobox_tenaga_pemupuk, combobox_supervisi, \
           combobox_pemeriksaan_ancak, combobox_jadwal_pemupukan, combobox_apd_pekerja, combobox_fisik_pupuk, \
           combobox_peletakan_pupuk, combobox_pupuk_tercecer, combobox_pengembalian_karung, \
           combobox_bahan_herbisida, combobox_kondisi_alat_semprot, combobox_kondisi_keseragaman_nozel, \
           combobox_kondisi_standard_dosis_knapsack, combobox_kondisi_penggunaan_hk, \
           combobox_pengendalian_gulma, combobox_apd_pekerja, combobox_p3k, \
           combobox_kartu_pengambilan_pencampuran_bahan, combobox_kalibrasi_alat_nozel, \
           combobox_alat_ukur_perkakas_perbaikan, combobox_peletakan_alat_semprot, \
           label_tanggal_qa_terakhir, \
           label_blok, label_divisi, label_mandor, label_tanggal_rencana_pupuk, label_pokok_sample, label_pokok_panen, label_sph, label_actual, label_budget, \
           label_buah_panen, label_buah_tertinggal, label_berondolan_tertinggal, label_buah_tertinggal_tph, \
           label_berondolan_tertinggal_tph, label_rotasi_panen, label_restan, label_jaring, label_produktivitas_pemanen, \
           label_administrasi_panen, label_kualitas_tbs, label_muatan_overload, \
           label_kondisi_circle, label_kondisi_path, label_kondisi_tph, \
           label_keterangan_cpt, label_keterangan_gawangan, label_keterangan_titi_panen, \
           label_keterangan_jalan_jembatan, label_keterangan_hama_penyakit, label_keterangan_beneficial_plan, \
           label_keterangan_peilscale, label_keterangan_cover_crop, label_keterangan_barn_owl, \
           label_keterangan_pokok_tidak_terpupuk, label_keterangan_piringan_gawangan, label_keterangan_cara_aplikasi, \
           label_keterangan_alat_tabur_seragam, label_keterangan_dosis_alat_tabur, label_keterangan_tenaga_pemupuk, \
           label_keterangan_supervisi, label_keterangan_pemeriksaan_ancak, label_keterangan_jadwal_pemupukan, \
           label_keterangan_apd_pekerja, label_keterangan_fisik_pupuk, label_keterangan_peletakan_pupuk, \
           label_keterangan_pupuk_tercecer, label_keterangan_pengembalian_karung, \
           label_keterangan_kematian_gulma, label_kematian_gulma, label_keterangan_pokok_tersemprot, label_keterangan_bahan_herbisida, \
           label_kondisi_alat_semprot, label_kondisi_keseragaman_nozel, label_kondisi_standard_dosis_knapsack, label_kondisi_penggunaan_hk, \
           label_keterangan_kondisi_alat_semprot, label_keterangan_keseragaman_nozel, label_keterangan_standard_dosis_knapsack, \
           label_keterangan_pengendalian_gulma, label_keterangan_penggunaan_hk, entry_keterangan_apd_pekerja, \
           label_keterangan_p3k, label_keterangan_kartu_pengambilan_pencampuran_bahan, label_keterangan_kalibrasi_alat_nozel, \
           label_keterangan_alat_ukur_perkakas_perbaikan, label_keterangan_peletakan_alat_semprot, \
           label_lalang, label_anak_kayu, label_prupukan, label_purun_tikus, \
           label_pakis_udang, label_titi_panen, label_jalan_jembatan, label_pruning_baik, label_pruning_over, \
           label_sengkleh, label_under_pruning, label_pelepah_rapi, label_serangan_tikus, \
           label_serangan_rayap, label_serangan_thirathaba, label_serangan_updks, \
           label_beneficial_plan, label_peilscale, label_cover_crop, label_barn_owl, \
           label_dosis_per_pokok, label_tanggal_pemupukan, \
           label_jenis_pupuk, label_pokok_tidak_terpupuk, label_ancak_gulma, label_cara_aplikasi, label_alat_tabur_seragam, \
           label_total_alat_tabur, label_kesesuaian_dosis_alat_tabur, label_tenaga_pemupuk, label_supervisi, \
           label_pemeriksaan_ancak, label_jadwal_pemupukan, label_apd_pekerja, label_fisik_pupuk, \
           label_peletakan_pupuk, label_pupuk_tercecer, label_pengembalian_karung, \
           label_jenis_chemist, label_dosis_knapsack, label_tanggal_semprot, \
           label_pokok_tersemprot, \
           label_bahan_herbisida, label_pengendalian_gulma, label_apd_pekerja, label_p3k, \
           label_kartu_pengambilan_pencampuran_bahan, label_kalibrasi_alat_nozel, \
           label_alat_ukur_perkakas_perbaikan, label_peletakan_alat_semprot, \
           uploaded_photo_path, \
           button_tanggal_qa_terakhir, button_upload_photo, \
           button_tanggal_semprot, \
           submit_calculation_production_button, submit_calculation_nursery_button, \
           submit_calculation_fertilizer_button, submit_calculation_chemist_button, \
           label_rencana_jenis_value, back_to_main_button, reanalyze_button, \
           label_saved_username, label_no_data, splash_label, splash_button, \
           label_tanggal_kosong, label_tanggal_salah, label_identifikasi_qa, \
           available_estate_list, available_divisi_list, available_blok_list


    # --- Initialize App ---
    root = tk.Tk()
    root.title("QA Agronomy Services Dept - Pancaran Agro (TDK)")
    root.attributes('-fullscreen', True)

    # --- Initialize State Variables ---
    username_var = StringVar()
    username = ""
    previous_menu = None
    root_exists = True
    current_menu = None
    df = pd.DataFrame()
    missing_dates_widgets = {}
    photo_image = None
    input_sheets = None
    output_sheets = None
    df_input_sheets = None
    df_output_sheets = None
    df_mobile_input = None
    df_input = None 
    df_output = None
    df_output_weight = None
    chosen_year_weight = None

    # --- Initialize Widget References (Good Practice) ---
    # (Keep the list of widget=None assignments here)
    label_username = None
    entry_username = None
    exit_button = None
    label_rainfall_option = None
    back_button = None
    label_menu_qa = None
    combobox_menu_qa = None
    label_menu_data_overview = None
    combobox_menu_data_overview = None
    label_chosen_year = None
    combobox_chosen_year = None
    label_note_year = None
    label_estate_option = None
    combobox_estate = None
    submit_estate_button = None
    label_blok = None
    entry_blok = None
    label_mandor = None
    entry_mandor = None
    label_divisi = None
    entry_divisi = None
    label_tanggal_rencana_pupuk = None
    entry_tanggal_rencana_pupuk = None
    button_tanggal_qa_terakhir = None

    # Production
    label_pokok_sample = None
    entry_pokok_sample = None
    label_pokok_panen = None
    entry_pokok_panen = None
    label_sph = None
    entry_sph = None
    label_actual = None
    entry_actual = None
    label_budget = None
    entry_budget = None
    label_buah_panen = None
    entry_buah_panen = None
    label_buah_tertinggal = None
    entry_buah_tertinggal = None
    label_berondolan_tertinggal = None
    entry_berondolan_tertinggal = None
    label_buah_tertinggal_tph = None
    entry_buah_tertinggal_tph = None
    label_berondolan_tertinggal_tph = None
    entry_berondolan_tertinggal_tph = None
    label_rotasi_panen = None
    entry_rotasi_panen = None
    label_restan = None
    entry_restan = None
    label_jaring = None
    entry_jaring = None
    label_produktivitas_pemanen = None
    entry_produktivitas_pemanen = None
    label_administrasi_panen = None
    entry_administrasi_panen = None
    label_kualitas_tbs = None
    entry_kualitas_tbs = None
    label_muatan_overload = None
    entry_muatan_overload = None
    label_tanggal_qa_terakhir = None
    entry_tanggal_qa_terakhir = None
    uploaded_photo_path = None
    button_upload_photo = None
    submit_calculation_production_button = None

    # Nursery
    label_kondisi_circle = None
    entry_kondisi_circle = None
    label_kondisi_path = None
    entry_kondisi_path = None
    label_kondisi_tph = None
    entry_kondisi_tph = None
    label_lalang = None
    entry_lalang = None
    label_anak_kayu = None
    entry_anak_kayu = None
    label_prupukan = None
    entry_prupukan = None
    label_purun_tikus = None
    entry_purun_tikus = None
    label_pakis_udang = None
    entry_pakis_udang = None
    label_titi_panen = None
    combobox_titi_panen = None
    label_jalan_jembatan = None
    combobox_jalan_jembatan = None
    label_pruning_baik = None
    entry_pruning_baik = None
    label_pruning_over = None
    entry_pruning_over = None
    label_sengkleh = None
    entry_sengkleh = None
    label_under_pruning = None
    entry_under_pruning = None
    label_pelepah_rapi = None
    entry_pelepah_rapi = None
    label_serangan_tikus = None
    entry_serangan_tikus = None
    label_serangan_rayap = None
    entry_serangan_rayap = None
    label_serangan_thirathaba = None
    entry_serangan_thirathaba = None
    label_serangan_updks = None
    entry_serangan_updks = None
    label_beneficial_plan = None
    combobox_beneficial_plan = None
    label_peilscale = None
    combobox_peilscale = None
    label_cover_crop = None
    entry_cover_crop = None
    label_barn_owl = None
    combobox_barn_owl = None
    submit_calculation_nursery_button = None

    label_keterangan_cpt = None
    entry_keterangan_cpt = None
    label_keterangan_gawangan = None
    entry_keterangan_gawangan = None
    label_keterangan_titi_panen = None
    entry_keterangan_titi_panen = None
    label_keterangan_jalan_jembatan = None
    entry_keterangan_jalan_jembatan = None
    label_keterangan_hama_penyakit = None
    entry_keterangan_hama_penyakit = None
    label_keterangan_beneficial_plan = None
    entry_keterangan_beneficial_plan = None
    label_keterangan_peilscale = None
    entry_keterangan_peilscale = None
    label_keterangan_cover_crop = None
    entry_keterangan_cover_crop = None
    label_keterangan_barn_owl = None
    entry_keterangan_barn_owl = None

    #Fertilizer
    label_dosis_per_pokok = None
    entry_dosis_per_pokok = None
    label_tanggal_pemupukan = None
    entry_tanggal_pemupukan = None
    label_jenis_pupuk = None
    combobox_jenis_pupuk = None
    label_pokok_tidak_terpupuk = None
    entry_pokok_tidak_terpupuk = None
    label_ancak_gulma = None
    entry_ancak_gulma = None
    label_cara_aplikasi = None
    combobox_cara_aplikasi = None
    label_alat_tabur_seragam = None
    entry_alat_tabur_seragam = None
    label_total_alat_tabur = None
    entry_total_alat_tabur = None
    label_kesesuaian_dosis_alat_tabur = None
    combobox_kesesuaian_dosis_alat_tabur = None
    label_tenaga_pemupuk = None
    combobox_tenaga_pemupuk = None
    label_supervisi = None
    combobox_supervisi = None
    label_pemeriksaan_ancak = None
    combobox_pemeriksaan_ancak = None
    label_jadwal_pemupukan = None
    combobox_jadwal_pemupukan = None
    label_apd_pekerja = None
    combobox_apd_pekerja = None
    label_fisik_pupuk = None
    combobox_fisik_pupuk = None
    label_peletakan_pupuk = None
    combobox_peletakan_pupuk = None
    label_pupuk_tercecer = None
    combobox_pupuk_tercecer = None
    label_pengembalian_karung = None
    combobox_pengembalian_karung = None
    submit_calculation_fertilizer_button = None
    
    label_keterangan_pokok_tidak_terpupuk = None
    entry_keterangan_pokok_tidak_terpupuk = None
    label_keterangan_piringan_gawangan = None
    entry_keterangan_piringan_gawangan = None
    label_keterangan_cara_aplikasi = None
    entry_keterangan_cara_aplikasi = None
    label_keterangan_alat_tabur_seragam = None
    entry_keterangan_alat_tabur_seragam = None
    label_keterangan_dosis_alat_tabur = None
    entry_keterangan_dosis_alat_tabur = None
    label_keterangan_tenaga_pemupuk = None
    entry_keterangan_tenaga_pemupuk = None
    label_keterangan_supervisi = None
    entry_keterangan_supervisi = None
    label_keterangan_pemeriksaan_ancak = None
    entry_keterangan_pemeriksaan_ancak = None
    label_keterangan_jadwal_pemupukan = None
    entry_keterangan_jadwal_pemupukan = None
    label_keterangan_apd_pekerja = None
    entry_keterangan_apd_pekerja = None
    label_keterangan_fisik_pupuk = None
    entry_keterangan_fisik_pupuk = None
    label_keterangan_peletakan_pupuk = None
    entry_keterangan_peletakan_pupuk = None
    label_keterangan_pupuk_tercecer = None
    entry_keterangan_pupuk_tercecer = None
    label_keterangan_pengembalian_karung = None
    entry_keterangan_pengembalian_karung = None

    # Chemist
    label_jenis_chemist = None
    entry_jenis_chemist = None
    label_dosis_knapsack = None
    entry_dosis_knapsack = None
    label_tanggal_semprot = None
    entry_tanggal_semprot = None
    button_tanggal_semprot = None
    label_pokok_tersemprot = None
    entry_pokok_tersemprot = None
    label_kematian_gulma = None
    entry_kematian_gulma = None
    label_bahan_herbisida = None
    combobox_bahan_herbisida = None
    label_kondisi_alat_semprot = None
    combobox_kondisi_alat_semprot = None
    label_kondisi_keseragaman_nozel = None
    combobox_kondisi_keseragaman_nozel = None
    label_kondisi_standard_dosis_knapsack = None
    combobox_kondisi_standard_dosis_knapsack = None
    label_pengendalian_gulma = None
    combobox_pengendalian_gulma = None
    label_kondisi_penggunaan_hk = None
    combobox_kondisi_penggunaan_hk = None
    label_apd_pekerja = None
    combobox_apd_pekerja = None
    label_p3k = None
    combobox_p3k = None
    label_kartu_pengambilan_pencampuran_bahan = None
    combobox_kartu_pengambilan_pencampuran_bahan = None
    label_kalibrasi_alat_nozel = None
    combobox_kalibrasi_alat_nozel = None
    label_alat_ukur_perkakas_perbaikan = None
    combobox_alat_ukur_perkakas_perbaikan = None
    label_peletakan_alat_semprot = None
    combobox_peletakan_alat_semprot = None
    submit_calculation_chemist_button = None

    label_keterangan_kematian_gulma = None
    entry_keterangan_kematian_gulma = None
    label_keterangan_pokok_tersemprot = None
    entry_keterangan_pokok_tersemprot = None
    label_keterangan_bahan_herbisida = None
    entry_keterangan_bahan_herbisida = None
    label_keterangan_kondisi_alat_semprot = None
    entry_keterangan_kondisi_alat_semprot = None
    label_keterangan_keseragaman_nozel = None
    entry_keterangan_keseragaman_nozel = None
    label_keterangan_standard_dosis_knapsack = None
    entry_keterangan_standard_dosis_knapsack = None
    label_keterangan_pengendalian_gulma = None
    entry_keterangan_pengendalian_gulma = None
    label_keterangan_penggunaan_hk = None
    entry_keterangan_penggunaan_hk = None
    label_keterangan_apd_pekerja = None
    entry_keterangan_apd_pekerja = None
    label_keterangan_p3k = None
    entry_keterangan_p3k = None
    label_keterangan_kartu_pengambilan_pencampuran_bahan = None
    entry_keterangan_kartu_pengambilan_pencampuran_bahan = None
    label_keterangan_kalibrasi_alat_nozel = None
    entry_keterangan_kalibrasi_alat_nozel = None
    label_keterangan_alat_ukur_perkakas_perbaikan = None
    entry_keterangan_alat_ukur_perkakas_perbaikan = None
    label_keterangan_peletakan_alat_semprot = None
    entry_keterangan_peletakan_alat_semprot = None

    back_to_main_button = None
    reanalyze_button = None
    main_menu_button = None
    label_saved_username = None
    missing_dates_widgets = {}
    label_missing_dates_title = None
    submit_missing_dates_button = None
    splash_label = None
    splash_button = None
    photo_upload_frame = None
    photos_data = []
    pdf_data = []
    label_tanggal_kosong = None
    label_tanggal_salah = None
    label_identifikasi_qa = None
    available_estate_list = ["None"]
    available_divisi_list = ["None"]
    available_blok_list = ["None"]

    # --- Connect to Google Sheets ---
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, SCOPE)
        client = gspread.authorize(creds)

        # Sheets for mobile input
        mobile_input_production = client.open_by_url(SHEET_URL).worksheet("Testing")

        # Sheets for input
        input_production = client.open_by_url(SHEET_URL).worksheet("Input - Production")
        input_nursery = client.open_by_url(SHEET_URL).worksheet("Input - Nursery")
        input_chemist = client.open_by_url(SHEET_URL).worksheet("Input - Chemist")
        input_fertilizer = client.open_by_url(SHEET_URL).worksheet("Input - Fertilizer")

        # Sheets for output
        output_production = client.open_by_url(SHEET_URL).worksheet("Output - Production")
        output_nursery = client.open_by_url(SHEET_URL).worksheet("Output - Nursery")
        output_chemist = client.open_by_url(SHEET_URL).worksheet("Output - Chemist")
        output_fertilizer = client.open_by_url(SHEET_URL).worksheet("Output - Fertilizer")

        # Sheets for output
        output_weight_production = client.open_by_url(SHEET_URL).worksheet("Output (Weight) - Production")
        output_weight_nursery = client.open_by_url(SHEET_URL).worksheet("Output (Weight) - Nursery")
        output_weight_chemist = client.open_by_url(SHEET_URL).worksheet("Output (Weight) - Chemist")
        output_weight_fertilizer = client.open_by_url(SHEET_URL).worksheet("Output (Weight) - Fertilizer")

        print("Successfully connected to Google Sheets.")
    except Exception as e:
        messagebox.showerror("Startup Error", f"Gagal terhubung ke Google Sheets: {e}")
        root.destroy()
        return

    # --- Load Initial Data ---
    print("Loading initial data...")
    load_database(SHEET_URL, JSON_PATH)
    
    # --- Setup Window Closing Protocol ---
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.columnconfigure(0, weight=1) # Configure root column initially

    root.bind('<Escape>', lambda event: on_closing())

    # --- Start GUI ---
    create_splash_screen()
    root.iconbitmap(COMPANY_LOGO)  # Make sure the path is correct
    root.mainloop()

# %% [markdown]
#  ## 13. Main

# %%
if __name__ == "__main__":
    if not os.path.exists(JSON_PATH):
         print(f"ERROR: Credential file not found at {JSON_PATH}")
         sys.exit("Credential file missing.")

    main_process()


