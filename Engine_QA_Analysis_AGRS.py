# %% [markdown]
#  # **ENGINE WAKTU APLIKASI PUPUK 2025**
# 
# 
# 
#  ## Refactored Code Structure

# %% [markdown]
#  ## 1. Imports and Setup

# %%
# Standard Libraries
import sys
import os
import datetime
from datetime import timedelta
import subprocess
import traceback

# Third-Party Libraries
import pandas as pd
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tkinter import filedialog
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# GUI Libraries
import tkinter as tk
from tkinter import ttk, messagebox, StringVar
# from reportlab import Calendar
from PIL import Image, ImageTk

# %% [markdown]
#  ## 2. Configuration and Constants

# %%
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Authentication ---
JSON_PATH = resource_path('enginewaktuaplikasipemupukan-03e33861bae9.json')
SHEET_URL = "https://docs.google.com/spreadsheets/d/1yCrPTPT6xVMEAYs7d31Vya0GhxQ_AySbfg-CXD7UaMw/edit?usp=sharing"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SPLASH_IMAGE = resource_path('bgqa.png')
FOLDER_ID = "1_OgkeR2Iooh9dyoIC6gskIYnJnt8qyJ6"

# --- Sheets ---
SHEET_NAMES_INPUT = ["Input - Production", "Input - Nursery", "Input - Chemist", "Input - Fertilizer"]
SHEET_NAMES_OUTPUT = ["Output - Production", "Output - Nursery", "Output - Chemist", "Output - Fertilizer"]
SHEET_NAMES_OUTPUT_WEIGHT = ["Output (Weight) - Production", "Output (Weight) - Nursery", "Output (Weight) - Chemist", "Output (Weight) - Fertilizer"]

MAPPING_SCORE_TO_DESC = {
    "score_actual_budget": "Pencapaian Produksi",
    "score_buah_tinggal": "Kualitas Panen - TBS Tertinggal",
    "score_berondolan_tinggal": "Kualitas Panen - LF Tertinggal",
    "score_buah_tinggal_tph": "Kualitas Transport - Jjg di TPH",
    "score_berondolan_tinggal_tph": "Kualitas Transport - LF di TPH",
    "score_rotasi_perbulan": "Rotasi Panen",
    "score_restan": "Restan",
    "score_jaring": "Pemakaian Jaring/Terpal",
    "score_produktivitas_pemanen": "Produktivitas Pemenen",
    "score_administrasi_panen": "Administrasi Panen",
    "score_kualitas_tbs": "Kualitas TBS",
    "score_muatan_overload": "Muatan Overload"
}

ESTATE_OPTIONS = ["Inti", "Plasma"] # Use constant for options

YEARLY_WEIGHT_PRODUCTION = {
    "Pencapaian Produksi": {"2025": "20%", "2026": "18%", "2027": "15%"},
    "Kualitas Panen - TBS Tertinggal": {"2025": "15%", "2026": "13%", "2027": "12%"},
    "Kualitas Panen - LF Tertinggal": {"2025": "15%", "2026": "13%", "2027": "12%"},
    "Kualitas Transport - Jjg di TPH": {"2025": "10%", "2026": "8%", "2027": "4%"},
    "Kualitas Transport - LF di TPH": {"2025": "10%", "2026": "8%", "2027": "4%"},
    "Rotasi Panen": {"2025": "15%", "2026": "13%", "2027": "12%"},
    "Restan": {"2025": "10%", "2026": "10%", "2027": "10%"},
    "Pemakaian Jaring/Terpal": {"2025": "5%", "2026": "5%", "2027": "5%"},
    "Produktivitas Pemenen": {"2025": "0%", "2026": "7%", "2027": "4%"},
    "Administrasi Panen": {"2025": "0%", "2026": "5%", "2027": "5%"},
    "Kualitas TBS": {"2025": "0%", "2026": "0%", "2027": "12%"},
    "Muatan Overload": {"2025": "0%", "2026": "0%", "2027": "5%"},
}


QA_TYPE = ["QA Produksi", "QA Perawatan", "QA Pemupukan", "QA Chemist"]

AVAILABLE_YEAR = ["2025", "2026", "2027"]

# --- Styling and Misc ---
BORDER_LINE = "=" * 80
PRIMARY_BUTTON_COLOR = "#4CAF50"  # Green
SECONDARY_BUTTON_COLOR = "#2196F3"  # Blue
MAIN_MENU_BUTTON_COLOR = "#f44336"  # Red
EXIT_BUTTON_COLOR = "#f44336" # Red
TEXT_COLOR = "#000000" # Black
BUTTON_TEXT_COLOR = "#ffffff"  # White

# --- Timezone ---
CURRENT_TIMEZONE = pytz.timezone('Asia/Jakarta') # Or your preferred timezone


# %% [markdown]
#  ## 3. Utility Functions

# %%
def format_datetime(dt):
    # Use datetime.datetime and datetime.date
    if isinstance(dt, (datetime.datetime, datetime.date)):
         # ADD CHECK: Ensure dt is not None before calling strftime
         if dt:
             return dt.strftime('%d/%m/%Y')
    return '' # Return empty string if not a valid date/datetime or if None

def format_datetimehour(dt):
    # Use datetime.datetime
    if isinstance(dt, datetime.datetime):
         # ADD CHECK: Ensure dt is not None
         if dt:
             return dt.strftime('%d/%m/%Y %H:%M:%S')
    return ''

def _on_mousewheel(event, canvas):
    """Handles mouse wheel scrolling on the canvas."""
    # Determine scroll direction and amount based on platform
    if event.num == 4:  # Linux scroll up
        canvas.yview_scroll(-1, "units")
    elif event.num == 5:  # Linux scroll down
        canvas.yview_scroll(1, "units")
    else:  # Windows/macOS scroll
        # Adjust scrolling speed if necessary
        scroll_factor = 1 if sys.platform == 'darwin' else 120 # macOS needs smaller delta factor
        canvas.yview_scroll(int(-1*(event.delta/scroll_factor)), "units")

def set_username():
    """Updates the global username string from the StringVar."""
    global username, username_var
    if username_var: # Check if StringVar exists
        username = username_var.get()

def get_fertilizer_group(fertilizer):
    """Finds the group a given fertilizer belongs to."""
    for group, types in FERTILIZER_GROUPS.items():
        if fertilizer in types:
            return group
    return None # Return None if not found


# %%
def get_missing_dates(df, estate_name, current_time_date): # current_time_date is tz-aware datetime.datetime
    """Calculates the missing dates for a given estate."""
    global CURRENT_TIMEZONE

    # Filter and sort data
    estate_data = df[(df['Estate'] == estate_name)].sort_values(by='Date')

    if estate_data.empty:
        print(f"No previous data found for {estate_name}. Cannot determine missing dates.")
        return pd.DatetimeIndex([]), None, 0

    # --- Ensure 'Date' column is datetime ---
    # ... (Keep the robust datetime conversion block from the previous step) ...
    if not pd.api.types.is_datetime64_any_dtype(estate_data['Date']):
        try:
            estate_data = estate_data.assign(Date=pd.to_datetime(estate_data['Date'], errors='coerce'))
            estate_data = estate_data.dropna(subset=['Date'])
        except Exception as e:
            print(f"Error converting 'Date' column to datetime for {estate_name}: {e}")
            return pd.DatetimeIndex([]), None, 0
        if estate_data.empty:
            print(f"No valid dates found for {estate_name} after conversion.")
            return pd.DatetimeIndex([]), None, 0
    # --- End datetime check ---

    last_reported_timestamp_naive = estate_data['Date'].iloc[-1]

    # --- Make last_reported_timestamp timezone-aware ---
    try:
        if last_reported_timestamp_naive.tzinfo is None:
            last_reported_time_aware = last_reported_timestamp_naive.tz_localize(CURRENT_TIMEZONE)
        elif last_reported_timestamp_naive.tzinfo == CURRENT_TIMEZONE:
            last_reported_time_aware = last_reported_timestamp_naive
        else:
            last_reported_time_aware = last_reported_timestamp_naive.tz_convert(CURRENT_TIMEZONE)
            print(f"Warning: Converted last reported time from {last_reported_timestamp_naive.tzinfo} to {CURRENT_TIMEZONE}")
    except Exception as e:
        print(f"Error handling timezone for last reported date ({last_reported_timestamp_naive}): {e}")
        return pd.DatetimeIndex([]), None, 0
    # --- End timezone handling ---


    # Prepare start and end dates for the range
    # last_reported_time_aware should be a pandas Timestamp, so .normalize() is OK
    start_date = last_reported_time_aware.normalize() + pd.Timedelta(days=1) # Keep pd.Timedelta from pandas

    # --- FIX HERE ---
    # current_time_date is standard datetime, use .replace() to set time to midnight
    midnight_today = current_time_date.replace(hour=0, minute=0, second=0, microsecond=0) # current_time_date is already datetime.datetime
    end_date = midnight_today - pd.Timedelta(days=1) # Keep pd.Timedelta from pandas
    # --- END FIX ---

    print(f"Debug: Calculated start_date: {start_date}")
    print(f"Debug: Calculated end_date: {end_date}")

    # Check if start_date is actually after end_date
    if start_date > end_date:
         print(f"No missing dates found (Start {start_date.date()} > End {end_date.date()}).")
         return pd.DatetimeIndex([]), last_reported_time_aware, 0

    # Generate the date range
    try:
        missing_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    except Exception as e:
        print(f"Error calling pd.date_range with start={start_date}, end={end_date}: {e}")
        return pd.DatetimeIndex([]), last_reported_time_aware, 0

    total_missing_dates = len(missing_dates)
    print(f"Debug: Found {total_missing_dates} missing dates.")

    return missing_dates, last_reported_time_aware, total_missing_dates

# %%
def extract_weights_by_year(weights_dict, year):
    extracted = {}

    for description, year_data in weights_dict.items():
        if year not in year_data:
            raise ValueError(f"Year {year} not found in data for '{description}'.")
        extracted[description] = year_data[year]

    return extracted

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
input_production = None
input_nursery = None
input_chemist = None
input_fertilizer = None 
output_production = None
output_nursery = None
output_chemist = None
output_fertilizer = None

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
    """Load input and output sheet on demand based on the selected QA type."""
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
    output_weight_sheet_name = mapping_output.get(qa_type)

    if not input_sheet_name or not output_sheet_name or not output_weight_sheet_name:
        raise Exception("QA type tidak dikenali.")

    input_worksheet = sheet.worksheet(input_sheet_name)
    output_worksheet = sheet.worksheet(output_sheet_name)
    output_weight_worksheet = sheet.worksheet(output_sheet_name)

    df_input = pd.DataFrame(input_worksheet.get_all_records())
    df_output = pd.DataFrame(output_worksheet.get_all_records())
    df_output_weight = pd.DataFrame(output_weight_worksheet.get_all_records())

    return df_input, df_output, df_output_weight

# %%
def analyze_fertilizer(date_input, username, estate_name, blok_name, df, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date):

  # Filter the DataFrame for the selected estate
  estate_df = df[df['Estate'] == estate_name]

  # Get the current daily rainfall (last entry for the estate)
  current_daily_rainfall = estate_df['Daily Rainfall (mm)'].iloc[-1]

  #check if today's rainfall is greater than or equal to 60
  reason = ""
  if current_daily_rainfall >= 60:
    reason = "Curah hujan lebih dari 60 mm, pemupukan dihentikan"
    print(reason)
    status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, 0, "", last_fertilizer_date, "", next_fertilizer_date, reason, "")
    recommendation = ""
    return current_daily_rainfall, status, reason, recommendation

  #check the accumulated rainfall data
  validate_water, rain_factor, peilscale_factor, season_factor, dry_with_rain = validate_water_track(df, current_daily_rainfall, peilscale, next_fertilizer)
  if(not validate_water):
    if(not rain_factor):
      reason = "Tidak bisa melakukan pemupukan, karena curah hujan"
      status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, "", last_fertilizer_date, "", next_fertilizer_date, reason, "")
      recommendation = ""
      return current_daily_rainfall, status, reason, recommendation
    elif(not peilscale_factor):
      reason = "Tidak bisa melakukan pemupukan, karena peilscale di atas -51"
      status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, "", last_fertilizer_date, "", next_fertilizer_date, reason, "")
      recommendation = ""
      return current_daily_rainfall, status, reason, recommendation
    elif(not season_factor):
      reason = f"Tidak bisa melakukan pemupukan, karena musim {season_factor}"
      if season_factor == "Wet":
          status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, "", last_fertilizer_date, "", next_fertilizer_date, reason, "")
          recommendation = ""
          return current_daily_rainfall, status, reason, recommendation
      elif season_factor == "Dry":
          print(reason)

  #get the last fertilizer's group
  last_group = get_fertilizer_group(last_fertilizer)
  #get the next fertilizer's group
  next_group = get_fertilizer_group(next_fertilizer)

  #check the interval between the last & the next fertilizer
  validate_interval_result = validate_interval_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date)

  #check the alternative
  Alternatives = []
  if (not validate_interval_result):
    if last_group == next_group:
      reason = "Karena jarak interval pemupukan di bawah 60 hari"
    elif last_group != next_group:
      reason = "Karena jarak interval pemupukan di bawah 30 hari"
    Alternatives = get_alternative_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS)
  else:
    Alternatives = get_all_recommendation(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS)

  #check the specific fertilizer trait
  #Dolomite
  Alternatives = validate_dolomite(df, last_fertilizer, last_fertilizer_date, next_fertilizer_date, Alternatives)
  #Discard because dry week
  is_dry_week = validate_dry_week(next_fertilizer, df)
  if next_fertilizer == "Urea" and is_dry_week >= 3:
      reason = "3 hari kebelakang tidak terdapat hujan sama sekali"
  elif next_fertilizer in ["Urea", "MOP", "HGFB"] and is_dry_week >= 7:
      reason = "7 hari kebelakang tidak terdapat hujan sama sekali"

  #Join the alternative option
  alternative = ', '.join(Alternatives)
  recommendation = ""
  plan_fertilizer_date = (last_fertilizer_date + datetime.timedelta(days=14)).date()
  if (len(Alternatives) != 0):
    recommendation = f"Pupuk alternatif yang disarankan: {alternative}"

  # Append to spreadsheet
  status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, recommendation)

  return current_daily_rainfall, status, reason, recommendation

# %% [markdown]
#  ## 6. Core Logic
#  

# %% [markdown]
#  ### 6.1 QA Production

# %%
def evaluate_budget_actual(budget, actual):

    difference_actual_budget = ((actual - budget) / budget) * 100

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
        perhitungan_buah_tinggal = (buah_tinggal / pokok_sample) * 100  # percentage

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
def evaluate_berondolan_tinggal(berondolan_tinggal, pokok_sample):
    perhitungan_berondolan_tinggal = berondolan_tinggal/pokok_sample

    if perhitungan_berondolan_tinggal <= 0.005: # < 0,5 butir/pkk
        return 10
    elif 0.005 < perhitungan_berondolan_tinggal <= 0.006: # > 0,5 - 0,6 butir/pkk
        return 8
    elif 0.006 < perhitungan_berondolan_tinggal <= 0.0075: # > 0,6 - 0,75 butir/pkk
        return 6
    elif 0.0075 < perhitungan_berondolan_tinggal <= 0.01: # > 0,75 - 1 butir/pkk
        return 4
    elif perhitungan_berondolan_tinggal > 0.01: # > 1 butir/pkk
        return 2

# %%
def evaluate_buah_tinggal_tph(buah_tinggal_tph, pokok_sample):
    perhitungan_buah_tinggal_tph = buah_tinggal_tph/pokok_sample

    if perhitungan_buah_tinggal_tph == 0: # 0 jjg
        return 10
    elif 0 < perhitungan_buah_tinggal_tph <= 0.002: # > 0 - 0,2 jjg
        return 8
    elif 0.002 < perhitungan_buah_tinggal_tph <= 0.004: # > 0,2 - 0,4 jjg
        return 6
    elif 0.004 < perhitungan_buah_tinggal_tph <= 0.006: # > 0,4 - 0,6 jjg
        return 4
    elif perhitungan_buah_tinggal_tph > 0.006: # > 0,6 jjg
        return 2

# %%
def evaluate_berondolan_tinggal_tph(berondolan_tinggal_tph, pokok_sample):

    perhitungan_berondolan_tinggal_tph = berondolan_tinggal_tph/pokok_sample

    if perhitungan_berondolan_tinggal_tph < 5: # < 5 butir
        return 10
    elif 5 < perhitungan_berondolan_tinggal_tph <= 7: # > 5 - 7 butir
        return 8
    elif 7 < perhitungan_berondolan_tinggal_tph <= 10: # > 7 - 10 butir
        return 6
    elif 10 < perhitungan_berondolan_tinggal_tph <= 12: # > 10 - 12 butir
        return 4
    elif perhitungan_berondolan_tinggal_tph > 12: # > 12 butir
        return 2

# %%
def evaluate_rotasi_panen_bulanan(rotasi_panen):
    perhitungan_rotasi_panen = 30/rotasi_panen
    
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
    
    if jaring > 100: # > 100%
        return 10
    elif 98 < jaring <= 100: # > 98% - 100%
        return 8
    elif 96 < jaring <= 98: # > 96% - 98%
        return 6
    elif 95 < jaring <= 96: # > 95% - 96%
        return 4
    elif jaring > 95: # < 95%
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
def analyse_qa_production(combobox_estate, 
                          entry_divisi,
                          entry_blok,
                          pokok_sample_float,
                          pokok_panen_float,
                          actual_float,
                          budget_float,
                          buah_panen_float,
                          buah_tertinggal_float,
                          berondolan_tertinggal_float,
                          buah_tertinggal_tph_float,
                          berondolan_tertinggal_tph_float,
                          rotasi_panen_float,
                          restan_float,
                          jaring_float,
                          produktivitas_pemanen_float,
                          administrasi_panen_float,
                          kualitas_tbs_float,
                          muatan_overload_float):
    
    global combobox_chosen_year, chosen_year_weight

    # Check chosen year if its empty
    chosen_year = combobox_chosen_year.get()
    if not chosen_year.strip():
        messagebox.showerror("Error", "Tolong masukkan pilihan tahun.")
        return

    # Get the rule data based on the chosen menu 
    try:
        chosen_year_weight = extract_weights_by_year(YEARLY_WEIGHT_PRODUCTION, chosen_year)
        print(chosen_year_weight)
    except ValueError as e:
        messagebox.showerror("Error", f"Gagal memuat kriteria untuk tahun {chosen_year}: {e}")
        return
    
    # Evaluate each input for production
    score_actual_budget = evaluate_budget_actual(budget_float, actual_float)

    score_buah_tinggal = evaluate_buah_tinggal(buah_tertinggal_float, pokok_sample_float)

    score_berondolan_tinggal = evaluate_berondolan_tinggal(berondolan_tertinggal_float, pokok_sample_float)

    score_buah_tinggal_tph = evaluate_buah_tinggal_tph(buah_tertinggal_tph_float, pokok_sample_float)

    score_berondolan_tinggal_tph = evaluate_berondolan_tinggal_tph(berondolan_tertinggal_tph_float, pokok_sample_float)

    score_rotasi_perbulan = evaluate_rotasi_panen_bulanan(rotasi_panen_float)

    score_restan = evaluate_restan(restan_float)

    score_jaring = evaluate_jaring(jaring_float)

    score_produktivitas_pemanen = evaluate_produktivitas_pemanen(produktivitas_pemanen_float)

    score_administrasi_panen = evaluate_administrasi_panen(administrasi_panen_float)

    score_kualitas_tbs = evaluate_kualitas_tbs(kualitas_tbs_float)

    score_muatan_overload = evaluate_muatan_overload(muatan_overload_float)

    # Store all the calculated scores in to dictionary 
    scores = {
        "Pencapaian Produksi": score_actual_budget,
        "Kualitas Panen - TBS Tertinggal": score_buah_tinggal,
        "Kualitas Panen - LF Tertinggal": score_berondolan_tinggal,
        "Kualitas Transport - Jjg di TPH": score_buah_tinggal_tph,
        "Kualitas Transport - LF di TPH": score_berondolan_tinggal_tph,
        "Rotasi Panen": score_rotasi_perbulan,
        "Restan": score_restan,
        "Pemakaian Jaring/Terpal": score_jaring,
        "Produktivitas Pemenen": score_produktivitas_pemanen,
        "Administrasi Panen": score_administrasi_panen,
        "Kualitas TBS": score_kualitas_tbs,
        "Muatan Overload": score_muatan_overload,
    }
    
    # Calculate the final score after yearly weight
    final_scores = {}

    for description, score_value in scores.items():
        weight_percent = float(chosen_year_weight[description].replace("%", "")) / 100
        weighted_score = score_value * weight_percent
        final_scores[description] = {
            "score": score_value,
            "nilai": weighted_score
        }

    return final_scores

# %% [markdown]
#  ## 7. Core Logic - Fertilizer Rules & Validation

# %%
# (Keep functions: check_groundwater, check_peilscale, check_season,
#  check_rain_in_dry_seasion, validate_water_track, get_minimal_interval,
#  get_alternative_fertilizer, get_all_recommendation, validate_interval_fertilizer,
#  get_fertilizer_group, validate_dry_week, validate_dolomite, analyze_fertilizer)
# Ensure analyze_fertilizer uses the updated arguments if necessary and that
# date objects (not strings) are passed where expected.

# Example: Minor correction in analyze_fertilizer if needed
# Make sure last_fertilizer_date and next_fertilizer_date are datetime objects
# when calling validate_interval_fertilizer, get_alternative_fertilizer, etc.


# %%
def analyze_fertilizer(date_input, username, estate_name, blok_name, df, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date):

  # Filter the DataFrame for the selected estate
  estate_df = df[df['Estate'] == estate_name]

  # Get the current daily rainfall (last entry for the estate)
  current_daily_rainfall = estate_df['Daily Rainfall (mm)'].iloc[-1]

  #check if today's rainfall is greater than or equal to 60
  reason = ""
  if current_daily_rainfall >= 60:
    reason = "Curah hujan lebih dari 60 mm, pemupukan dihentikan"
    print(reason)
    status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, 0, "", last_fertilizer_date, "", next_fertilizer_date, reason, "")
    recommendation = ""
    return current_daily_rainfall, status, reason, recommendation

  #check the accumulated rainfall data
  validate_water, rain_factor, peilscale_factor, season_factor, dry_with_rain = validate_water_track(df, current_daily_rainfall, peilscale, next_fertilizer)
  if(not validate_water):
    if(not rain_factor):
      reason = "Tidak bisa melakukan pemupukan, karena curah hujan"
      status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, "", last_fertilizer_date, "", next_fertilizer_date, reason, "")
      recommendation = ""
      return current_daily_rainfall, status, reason, recommendation
    elif(not peilscale_factor):
      reason = "Tidak bisa melakukan pemupukan, karena peilscale di atas -51"
      status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, "", last_fertilizer_date, "", next_fertilizer_date, reason, "")
      recommendation = ""
      return current_daily_rainfall, status, reason, recommendation
    elif(not season_factor):
      reason = f"Tidak bisa melakukan pemupukan, karena musim {season_factor}"
      if season_factor == "Wet":
          status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, "", last_fertilizer_date, "", next_fertilizer_date, reason, "")
          recommendation = ""
          return current_daily_rainfall, status, reason, recommendation
      elif season_factor == "Dry":
          print(reason)

  #get the last fertilizer's group
  last_group = get_fertilizer_group(last_fertilizer)
  #get the next fertilizer's group
  next_group = get_fertilizer_group(next_fertilizer)

  #check the interval between the last & the next fertilizer
  validate_interval_result = validate_interval_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date)

  #check the alternative
  Alternatives = []
  if (not validate_interval_result):
    if last_group == next_group:
      reason = "Karena jarak interval pemupukan di bawah 60 hari"
    elif last_group != next_group:
      reason = "Karena jarak interval pemupukan di bawah 30 hari"
    Alternatives = get_alternative_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS)
  else:
    Alternatives = get_all_recommendation(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS)

  #check the specific fertilizer trait
  #Dolomite
  Alternatives = validate_dolomite(df, last_fertilizer, last_fertilizer_date, next_fertilizer_date, Alternatives)
  #Discard because dry week
  is_dry_week = validate_dry_week(next_fertilizer, df)
  if next_fertilizer == "Urea" and is_dry_week >= 3:
      reason = "3 hari kebelakang tidak terdapat hujan sama sekali"
  elif next_fertilizer in ["Urea", "MOP", "HGFB"] and is_dry_week >= 7:
      reason = "7 hari kebelakang tidak terdapat hujan sama sekali"

  #Join the alternative option
  alternative = ', '.join(Alternatives)
  recommendation = ""
  plan_fertilizer_date = (last_fertilizer_date + datetime.timedelta(days=14)).date()
  if (len(Alternatives) != 0):
    recommendation = f"Pupuk alternatif yang disarankan: {alternative}"

  # Append to spreadsheet
  status = append_to_spreadsheet(date_input, username, estate_name, blok_name, current_daily_rainfall, peilscale, last_fertilizer, last_fertilizer_date, next_fertilizer, next_fertilizer_date, reason, recommendation)

  return current_daily_rainfall, status, reason, recommendation

# %%
def validate_dolomite(df, last_fertilizer, last_fertilizer_date, next_fertilizer_date, Alternatives):
  dolomite_fertilizer = "Dolomite"

  # Check if the alternatives already has Dolomite inside it
  if dolomite_fertilizer in Alternatives:
    return Alternatives  # Dolomite not allowed

  # 1. Check if the last Daily Rainfall (mm) is < 60
  last_daily_rainfall = df['Daily Rainfall (mm)'].iloc[-1]
  if last_daily_rainfall >= 60:
    return Alternatives  # Dolomite not allowed

  # 2. Check if Accumulation Rainfall is < 300
  accumulation_rainfall = df['Accumulation Rainfall -29 days'].iloc[-1]
  if accumulation_rainfall >= 300:
    return Alternatives  # Dolomite not allowed

  # 3. Check if the interval is met (same as other fertilizers)
  last_group = get_fertilizer_group(last_fertilizer)
  next_group = get_fertilizer_group(dolomite_fertilizer)  # Assuming Dolomite is the next_fertilizer
  min_interval = get_minimal_interval(last_group, next_group)
  
  selisih_hari = (next_fertilizer_date - last_fertilizer_date).days
  if selisih_hari < min_interval:
    return Alternatives  # Dolomite not allowed

  # If all checks pass, add Dolomite to Alternatives
  Alternatives.append(dolomite_fertilizer)
  return Alternatives

# %%
def validate_dry_week(fertilizer, df):
  last_days = df['Daily Rainfall (mm)'].iloc[-7:]

  no_rain = 0
  for i in last_days:
    if i == 0:
      no_rain += 1

  return no_rain

# %%
def get_fertilizer_group(fertilizer):
    for group, types in FERTILIZER_GROUPS.items():
        if fertilizer in types:
            return group
    return None

# %%
def check_groundwater(accumulation_rainfall, water_surplus):
  if (accumulation_rainfall >= 300) and (water_surplus == 0):
    return True
  elif (accumulation_rainfall >= 60) and (accumulation_rainfall <= 300) and (water_surplus >= 0):
    return True
  else:
    return False

# %%
def check_peilscale(peilscale):
  if peilscale <= -51:
    return True
  else:
    return False

# %%
def check_season(accumulation_rainfall):
  if accumulation_rainfall < 60 :
    return "Dry"
  elif accumulation_rainfall > 300:
    return "Wet"

# %%
def check_rain_in_dry_seasion(daily_rainfall_last_7):
  raining_once = (daily_rainfall_last_7 >= 60).sum() >= 1
  raining_twice = (daily_rainfall_last_7 >= 30).sum() >= 2

  if raining_once or raining_twice:
    return True
  else:
    return False

# %%
def validate_water_track(df, current_daily_rainfall, peilscale, next_fertilizer):

  last_row = df.iloc[-1]
  accumulation_rainfall = last_row['Accumulation Rainfall -29 days']
  water_surplus = last_row['Water Surplus']
  daily_rainfall_last_7 = df['Daily Rainfall (mm)'].iloc[-7:]

  # Syarat 1
  validation1 = check_groundwater(accumulation_rainfall, water_surplus)

  # Syarat 2
  print("peilscale", peilscale)
  validation2 = check_peilscale(peilscale)
  print("validation2", validation2)

  # Syarat 3
  season = check_season(accumulation_rainfall)
  validation3 = season not in ["Wet", "Dry"] # if validation3 has value that means it's either 'Wet' or 'Dry', None means it's Optimal

  # Check if season is 'Dry' with rains around 7 days back
  dry_with_rain = False
  if (season == "Dry"):
    dry_with_rain = check_rain_in_dry_seasion(daily_rainfall_last_7)

  return (validation1 and validation2 and validation3), validation1, validation2, season, dry_with_rain

# %%
def get_minimal_interval(last_group, next_group):
    return INTERVAL_TABLE.get(last_group, {}).get(next_group, 30)  # Default to 30 if not found

# %%
def validate_interval_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date):
  min_interval = get_minimal_interval(last_group, next_group)
  if min_interval == None:  # Handle cases with no defined interval
      return False  # Or return True, depending on how you want to handle these cases
  
  selisih_hari = (next_fertilizer_date - last_fertilizer_date).days
  return selisih_hari >= min_interval

# %%
def get_alternative_fertilizer(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS):
    recommendation = []
    selisih_hari = (next_fertilizer_date - last_fertilizer_date).days

    for group, fertilizers in FERTILIZER_GROUPS.items():
        if group != next_group:  # Exclude the desired fertilizer because it hits the interval
            interval = INTERVAL_TABLE.get(last_group, {}).get(group, None)
            if interval is not None and selisih_hari >= interval:
                recommendation.extend(fertilizers)

    return recommendation

# %%
def get_all_recommendation(last_group, next_group, last_fertilizer_date, next_fertilizer_date, INTERVAL_TABLE, FERTILIZER_GROUPS):
  recommendation = []
  selisih_hari = (next_fertilizer_date - last_fertilizer_date).days

  # Always include the next_group
  if next_group in FERTILIZER_GROUPS:
      recommendation.extend(FERTILIZER_GROUPS[next_group])

  # Add other fertilizers that meet the interval
  for group, fertilizers in FERTILIZER_GROUPS.items():
      if group != next_group:  # Exclude the desired fertilizer
          interval = INTERVAL_TABLE.get(last_group, {}).get(group, None)
          if interval is not None and selisih_hari >= interval:
              recommendation.extend(fertilizers)

  return recommendation

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

def hide_all_widgets():
    """Hides ALL widgets gridded directly onto the root window."""
    if not root_exists: return
    # Be more specific: Hide only widgets placed with grid on root
    for widget in root.grid_slaves():
         widget.grid_forget()
    # Also forget frames that might contain other widgets if needed
    # Example: if outer_frame exists and is a direct child
    # try:
    #     if 'outer_frame' in globals() and outer_frame:
    #         outer_frame.grid_forget()
    # except NameError: pass # If outer_frame was never created

def hide_rainfall_data_entry_widgets(): # Make sure this is defined
    """Hides the widgets specifically for the rainfall data entry/update screen."""
    global label_update_rainfall, entry_update_rainfall, submit_update_rainfall_button, back_button, main_menu_button, label_no_data

    if not root_exists: return

    widgets_to_hide = [
        label_update_rainfall, entry_update_rainfall, submit_update_rainfall_button,
        back_button, main_menu_button, label_no_data # Include label_no_data
    ]
    for widget in widgets_to_hide:
        try:
            if widget: widget.grid_forget()
        except (AttributeError, NameError, tk.TclError): # Catch potential errors if widget doesn't exist or is destroyed
            pass

# Removed hide_estate_widgets as it seems redundant with hide_all_widgets strategy


# %%
def validate_rainfall_data_exists(selected_estate):
    """
    Checks if rainfall data exists for the selected estate,
    if there are no missing dates before today, and if today's data exists.
    Returns True if all checks pass, False otherwise. Displays error messages.
    """
    global df, current_time_date # Need access to these globals

    # 1. Basic Estate Check (Redundant if called after submit_analysis checks, but safe)
    if not selected_estate:
        # This case might not be reachable if submit_analysis checks first
        messagebox.showerror("Error", "Estate belum dipilih.")
        return False
    # Use the constant if defined, otherwise the list
    valid_estates = ["Inti", "Plasma"] # Or use ESTATE_OPTIONS constant
    if selected_estate not in valid_estates:
         messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'.")
         return False

    # --- Check current_time_date type ---
    # Use the fully qualified class name datetime.datetime
    if not isinstance(current_time_date, datetime.datetime):
         messagebox.showerror("Internal Error", "Format tanggal tidak valid.")
         print(f"DEBUG: Invalid current_time_date type: {type(current_time_date)}") # Debug print
         return False
    # --- End Check ---


    # 2. Check for Missing Dates Before Today
    missing_dates, last_reported_time, total_missing_dates = get_missing_dates(df, selected_estate, current_time_date)

    if total_missing_dates > 0:
        # Format last_reported_time safely - it's already timezone-aware from get_missing_dates
        last_reported_str = format_datetime(last_reported_time.date()) if last_reported_time else "awal data"
        messagebox.showerror("Data Tidak Lengkap",
                             f"Terdapat {total_missing_dates} hari data hujan yang belum diinput untuk estate {selected_estate} "
                             f"sejak {last_reported_str}.\n\n"
                             "Harap lengkapi data melalui menu 'Masukkan Data Hujan' → 'Masukkan Data Hujan Baru'")
        return False

    # 3. Check for Today's Data (only if no missing dates before today)
    today_date = current_time_date.date() # Get today's date part

    # Ensure Date column is datetime before comparison
    # This check might be redundant if load_database guarantees it, but safe to keep
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
         try:
             df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
             df.dropna(subset=['Date'], inplace=True) # Recalculate df if necessary
         except Exception as e:
             messagebox.showerror("Error", f"Gagal memproses kolom Tanggal: {e}")
             return False


    estate_data_today = df[(df['Estate'] == selected_estate) & (df['Date'].dt.date == today_date)]

    if estate_data_today.empty:
        messagebox.showerror("Data Tidak Lengkap",
                             f"Data curah hujan untuk hari ini ({format_datetime(today_date)}) "
                             f"bagi estate {selected_estate} belum dimasukkan.\n\n"
                             "Harap masukkan data hari ini melalui menu 'Masukkan Data Hujan'.")
        return False

    # If all checks pass
    print(f"Rainfall data validation passed for {selected_estate}") # Debug print
    return True

# %% [markdown]
#  ## 9. GUI - Screen Creation Functions

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
            # Pillow versions >= 9.1.0 use Image.Resampling.LANCZOS
            # Older versions use Image.LANCZOS
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS # Fallback for older Pillow

            img_resized = img_original.resize((screen_width, screen_height), resample_filter)

            # Convert to Tkinter PhotoImage
            photo_image = ImageTk.PhotoImage(img_resized)

        # --- Create Label for Image ---
        splash_label = tk.Label(root, image=photo_image)
        # IMPORTANT: Keep a reference to the image to prevent garbage collection
        if photo_image:
            splash_label.image = photo_image
        splash_label.place(x=0, y=0, relwidth=1, relheight=1) # Cover entire window

        # --- Create Start Button ---
        # Place it slightly offset from the left-right corner
        splash_button = tk.Button(root, text="Start", command=start_main_app,
                                  font=("Arial", 14, "bold"), # Make it stand out
                                  bg="#3f4726", # Green background
                                  fg="white",   # White text
                                  relief=tk.RAISED, bd=3)
        
        splash_button.place(relx=0.27, rely=1.0, anchor='se', x=0, y=-20)

    except FileNotFoundError:
         messagebox.showerror("Error", f"Splash image file not found: {image_path}")
         root.after(100, start_main_app)
    except Exception as e:
        messagebox.showerror("Splash Screen Error", f"Could not load splash screen: {e}")
        traceback.print_exc()
        root.after(100, start_main_app)

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
def create_main_widgets():
    global label_username, entry_username, previous_menu, current_menu, back_button, exit_button, label_menu_qa, combobox_menu_qa, label_chosen_year, combobox_chosen_year, label_note_year, button_input_hujan, button_analisa_pemupukan, username_var, label_saved_username, username, df # Add df

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
    row_offset = 0 # Start widgets at row 0
    if not username:
        label_username = tk.Label(root, text="Masukkan Username:", font=("Arial", 12))
        label_username.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
        row_offset += 1
        entry_username = tk.Entry(root, font=("Arial", 10), textvariable=username_var)
        entry_username.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
        row_offset += 1
        # Setup trace *only if* entry is created
        if not username_var.trace_info(): # Check if trace exists
             username_var.trace_add("write", lambda *args: set_username())
    else:
        label_saved_username = tk.Label(root, text=f"Masuk ke sistem sebagai: {username}", font=("Arial", 12))
        label_saved_username.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
        row_offset += 2 # Skip the row where entry would have been

    # --- QA Section ---
    label_menu_qa = tk.Label(root, text="Pilih Jenis QA:", font=("Arial", 12))
    label_menu_qa.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
    row_offset += 1

    combobox_menu_qa = ttk.Combobox(root, values=QA_TYPE, width=30, font=("Arial", 10))
    combobox_menu_qa.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    # --- Yearly Weight ---
    label_chosen_year = tk.Label(root, text="Pilih Bobot Tahun:", font=("Arial", 12))
    label_chosen_year.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
    row_offset += 1

    combobox_chosen_year = ttk.Combobox(root, values=AVAILABLE_YEAR, width=30, font=("Arial", 10))
    combobox_chosen_year.grid(row=row_offset, column=0, padx=10, pady=5, sticky="ew")
    row_offset += 1

    label_note_year = tk.Label(root, text="Catatan: Untuk tahun 2027 ke atas, gunakan bobot tahun", font=("Arial", 10, "italic"), fg="red")
    label_note_year.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
    row_offset += 1

    # --- Buttons ---
    button_input_hujan = tk.Button(root, text="Submit Menu", command=goto_chosen_menu, font=("Arial", 12), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    button_input_hujan.grid(row=row_offset, column=0, padx=10, pady=10, sticky="ew")
    row_offset += 1
    
    # Add some space before exit button
    root.rowconfigure(row_offset, weight=1) # Add flexible space before exit
    row_offset += 1

    exit_button = tk.Button(root, text="Exit", command=on_closing, font=("Arial", 10), bg=EXIT_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    exit_button.grid(row=row_offset, column=0, padx=10, pady=10)

    previous_menu = None
    back_button = None

# (Add the ROW/COLUMN reset block to the start of ALL other show_ functions)
# Example for show_rainfall_options:
def show_rainfall_options():
    global label_rainfall_option, back_button, current_menu, button_update_rainfall, button_add_rainfall, previous_menu

    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---

    hide_all_widgets()
    current_menu = "rainfall"
    previous_menu = "main"
    configure_bg("#f0f0f0") # Use default bg

    label_rainfall_option = tk.Label(root, text="Pilih Opsi Untuk Data Hujan:", font=("Arial", 12))
    label_rainfall_option.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    # ... rest of widgets with colors ...
    button_update_rainfall = tk.Button(root, text="Update Data Hujan Terakhir", command=goto_update_rainfall, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    button_update_rainfall.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    button_add_rainfall = tk.Button(root, text="Masukkan Data Hujan Baru", command=goto_add_rainfall, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    button_add_rainfall.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    back_button.grid(row=3, column=0, padx=10, pady=10)

# Apply reset to show_ESTATE_OPTIONS, show_ESTATE_OPTIONS_for_add_rainfall,
# show_add_rainfall_entry, show_rainfall_data_entry, show_estate_options_for_analysis,
# display_analysis_results, show_missing_dates_input (it already does it)

def display_analysis_results(selected_estate, nama_blok, tanggal_rencana, peilscale, tanggal_terakhir,
                              jenis_terakhir, rencana_jenis, username, curah_hujan, status, reason, recommendation):
    
    global current_menu, label_tanggal_analisa, label_nama_user, label_curah_hujan, \
           label_status, label_reason, label_recommendation, label_selected_estate, \
           label_nama_blok, label_tanggal_rencana, label_peilscale_value, \
           label_tanggal_terakhir_value, label_jenis_terakhir_value, \
           label_rencana_jenis_value, back_to_main_button, reanalyze_button  # Add reanalyze_button

    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END CONFIGURATION ---

    hide_all_widgets()
    current_menu = "analysis_results"

    # --- Display Analysis Results ---
    current_time_input = datetime.datetime.now(CURRENT_TIMEZONE)
    label_tanggal_analisa = tk.Label(root, text=f"Tanggal Analisa: {current_time_input.strftime('%Y-%m-%d %H:%M:%S')}", font=("Arial", 12))
    label_tanggal_analisa.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

    label_nama_user = tk.Label(root, text=f"Nama User: {username}", font=("Arial", 12))
    label_nama_user.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    label_selected_estate = tk.Label(root, text=f"Nama Estate: {selected_estate}", font=("Arial", 12))
    label_selected_estate.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    label_nama_blok = tk.Label(root, text=f"Nama Blok: {nama_blok}", font=("Arial", 12))
    label_nama_blok.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

    label_curah_hujan = tk.Label(root, text=f"Curah Hujan: {curah_hujan}", font=("Arial", 12))
    label_curah_hujan.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

    label_peilscale_value = tk.Label(root, text=f"Nilai Peilscale: {peilscale}", font=("Arial", 12))
    label_peilscale_value.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

    label_jenis_terakhir_value = tk.Label(root, text=f"Jenis Pupuk Terakhir: {jenis_terakhir}", font=("Arial", 12, "bold"))
    label_jenis_terakhir_value.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

    label_tanggal_terakhir_value = tk.Label(root, text=f"Tanggal Pupuk Terakhir: {tanggal_terakhir}", font=("Arial", 12, "bold"))
    label_tanggal_terakhir_value.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

    label_rencana_jenis_value = tk.Label(root, text=f"Rencana Jenis Pupuk: {rencana_jenis}", font=("Arial", 12, "bold"))
    label_rencana_jenis_value.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

    label_tanggal_rencana = tk.Label(root, text=f"Tanggal Rencana Pupuk: {tanggal_rencana}", font=("Arial", 12, "bold"))
    label_tanggal_rencana.grid(row=9, column=0, padx=10, pady=5, sticky="ew")

    label_status = tk.Label(root, text=f"Status: {status}", font=("Arial", 12, "bold"))
    label_status.grid(row=10, column=0, padx=10, pady=5, sticky="ew")

    label_reason = tk.Label(root, text=f"Alasan: {reason}", font=("Arial", 12))
    label_reason.grid(row=11, column=0, padx=10, pady=5, sticky="ew")

    label_recommendation = tk.Label(root, text=f"Rekomendasi: {recommendation}", font=("Arial", 12))
    label_recommendation.grid(row=12, column=0, padx=10, pady=5, sticky="ew")

    # --- Re-analyze Button --- (Row 13)
    reanalyze_button = tk.Button(root, text="Reanalyze", command=show_estate_options_for_analysis, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
    reanalyze_button.grid(row=13, column=0, padx=10, pady=10)

    # --- Back to Main Menu Button --- (Row 14)
    back_to_main_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
    back_to_main_button.grid(row=14, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)


# Modify show_missing_dates_input slightly for clarity
def show_missing_dates_input(selected_estate, missing_dates_list):
    global missing_dates_widgets, label_missing_dates_title, submit_missing_dates_button, \
           back_button, main_menu_button, previous_menu, current_menu, \
           canvas, scrollbar, inner_frame

    if not root_exists: return

    hide_all_widgets()
    current_menu = "missing_dates_input"
    previous_menu = "estate_add_rainfall"
    configure_bg("#f0f0f0") # Use default bg

    # --- ROW & COLUMN RESET for ROOT ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END ROOT RESET ---

    # --- Title (On Root) ---
    label_missing_dates_title = tk.Label(root, text=f"Masukkan data hujan untuk tanggal yang belum diinput ({selected_estate}):", font=("Arial", 12, "bold"))
    label_missing_dates_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

    # --- Create Scrollable Area (On Root) ---
    outer_frame = tk.Frame(root)
    outer_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
    outer_frame.grid_rowconfigure(0, weight=1)
    outer_frame.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(outer_frame)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    inner_frame = tk.Frame(canvas) # Frame INSIDE canvas
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # --- Bind Mouse Wheel ---
    # ... (keep mouse wheel bindings) ...

    # --- Populate Inner Frame ---
    missing_dates_widgets = {}
    row_num = 0
    for date in missing_dates_list:
        # ... (create label and entry INSIDE inner_frame) ...
        label = tk.Label(inner_frame, text=f"Tanggal {format_datetime(date.date())} (mm):", font=("Arial", 10))
        label.grid(row=row_num, column=0, padx=5, pady=2, sticky="w")
        entry = tk.Entry(inner_frame, font=("Arial", 10))
        entry.grid(row=row_num, column=1, padx=5, pady=2, sticky="ew")
        missing_dates_widgets[date.date()] = {"label": label, "entry": entry}
        row_num += 1
    inner_frame.columnconfigure(1, weight=1)

    # --- Buttons (On Root) ---
    button_row = 2
    submit_missing_dates_button = tk.Button(root, text="Submit Data", command=lambda: submit_missing_dates(selected_estate, missing_dates_list), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    submit_missing_dates_button.grid(row=button_row, column=0, padx=10, pady=10)
    button_row += 1
    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    back_button.grid(row=button_row, column=0, padx=10, pady=5)
    button_row += 1
    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    main_menu_button.grid(row=button_row, column=0, padx=10, pady=5)

    # --- Configure Root Window Rows for Resizing ---
    root.grid_rowconfigure(0, weight=0)  # Title row
    root.grid_rowconfigure(1, weight=1)  # Scrollable area row
    root.grid_rowconfigure(button_row, weight=0) # Last button row

# --- (Ensure the reset block is added to show_ESTATE_OPTIONS, show_add_rainfall_entry, etc.) ---


# %%
def show_ESTATE_OPTIONS():
    global label_estate_option, combobox_estate, submit_estate_button, back_button, current_menu, main_menu_button, df
    if not root_exists:
        return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---

    hide_all_widgets()

    current_menu = "estate"
    label_estate_option = tk.Label(root, text="Pilih estate (Inti/Plasma):", font=("Arial", 12))
    label_estate_option.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    ESTATE_OPTIONS = ["Inti", "Plasma"]
    combobox_estate = ttk.Combobox(root, values=ESTATE_OPTIONS, width=30, font=("Arial", 10))
    combobox_estate.grid(row=1, column=0, padx=10, pady=10)
    submit_estate_button = tk.Button(root, text="Submit Estate", command=lambda: submit_estate(combobox_estate.get()), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    submit_estate_button.grid(row=2, column=0, padx=10, pady=10)
    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    back_button.grid(row=3, column=0, padx=10, pady=10)
    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    main_menu_button.grid(row=4, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)


# %%
def show_estate_options_for_analysis():
    global label_estate_option, combobox_estate, submit_estate_button, back_button, current_menu, \
           entry_blok, entry_tanggal_rencana_pupuk, entry_peilscale, entry_tanggal_pupuk_terakhir, \
           combobox_jenis_pupuk_terakhir, combobox_rencana_jenis_pupuk, label_blok, label_tanggal_rencana_pupuk, \
           label_peilscale, label_tanggal_pupuk_terakhir, label_jenis_pupuk_terakhir, label_rencana_jenis_pupuk, \
           button_tanggal_rencana_pupuk, button_tanggal_pupuk_terakhir

    if not root_exists:
        return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---

    hide_all_widgets()
    current_menu = "estate_analysis"

    # --- Use sticky="ew" on ALL widgets ---
    label_estate_option = tk.Label(root, text="Pilih estate (Inti/Plasma):", font=("Arial", 12))
    label_estate_option.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

    ESTATE_OPTIONS = ["Inti", "Plasma"]
    combobox_estate = ttk.Combobox(root, values=ESTATE_OPTIONS, width=30, font=("Arial", 10))
    combobox_estate.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    label_blok = tk.Label(root, text="Masukkan Nama Blok:", font=("Arial", 12))
    label_blok.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    entry_blok = tk.Entry(root, font=("Arial", 10))
    entry_blok.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

    label_tanggal_rencana_pupuk = tk.Label(root, text="Masukkan tanggal rencana pupuk:", font=("Arial", 12))
    label_tanggal_rencana_pupuk.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

    entry_tanggal_rencana_pupuk = tk.Entry(root, font=("Arial", 10))
    entry_tanggal_rencana_pupuk.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

    button_tanggal_rencana_pupuk = tk.Button(root, text="Select Date", command=lambda: get_date(entry_tanggal_rencana_pupuk), font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) #Added button and color
    button_tanggal_rencana_pupuk.grid(row=5, column=1, padx=5, pady=5) # Place button next to entry

    label_tanggal_pupuk_terakhir = tk.Label(root, text="Masukkan tanggal pupuk terakhir:", font=("Arial", 12))
    label_tanggal_pupuk_terakhir.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

    entry_tanggal_pupuk_terakhir = tk.Entry(root, font=("Arial", 10))
    entry_tanggal_pupuk_terakhir.grid(row=9, column=0, padx=10, pady=5, sticky="ew")

    button_tanggal_pupuk_terakhir = tk.Button(root, text="Select Date", command=lambda: get_date(entry_tanggal_pupuk_terakhir), font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) #Added button and color
    button_tanggal_pupuk_terakhir.grid(row=9, column=1, padx=5, pady=5) # Place button next to entry

    label_peilscale = tk.Label(root, text="Masukkan nilai Peilscale:", font=("Arial", 12))
    label_peilscale.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

    entry_peilscale = tk.Entry(root, font=("Arial", 10))
    entry_peilscale.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

    label_jenis_pupuk_terakhir = tk.Label(root, text="Masukkan jenis pupuk terakhir:", font=("Arial", 12))
    label_jenis_pupuk_terakhir.grid(row=10, column=0, padx=10, pady=5, sticky="ew")

    combobox_jenis_pupuk_terakhir = ttk.Combobox(root, values=FERTILIZER_TYPE, width=30, font=("Arial", 10))
    combobox_jenis_pupuk_terakhir.grid(row=11, column=0, padx=10, pady=5, sticky="ew")

    label_rencana_jenis_pupuk = tk.Label(root, text="Masukkan rencana jenis pupuk:", font=("Arial", 12))
    label_rencana_jenis_pupuk.grid(row=12, column=0, padx=10, pady=5, sticky="ew")

    combobox_rencana_jenis_pupuk = ttk.Combobox(root, values=FERTILIZER_TYPE, width=30, font=("Arial", 10))
    combobox_rencana_jenis_pupuk.grid(row=13, column=0, padx=10, pady=5, sticky="ew")

    submit_estate_button = tk.Button(root, text="Submit", command=lambda: submit_analysis(
        combobox_estate.get(),
        entry_blok.get(),
        entry_peilscale.get(),
        combobox_jenis_pupuk_terakhir.get(),
        entry_tanggal_pupuk_terakhir.get(),
        combobox_rencana_jenis_pupuk.get(),
        entry_tanggal_rencana_pupuk.get()
    ), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    submit_estate_button.grid(row=14, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    back_button.grid(row=15, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)


# %%
def show_ESTATE_OPTIONS_for_add_rainfall():
    global label_estate_option, combobox_estate, submit_estate_check_button, back_button, current_menu, previous_menu

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "estate_add_rainfall"
    previous_menu = "rainfall"

    # --- ROW & COLUMN RESET for ROOT ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END ROOT RESET ---

    label_estate_option = tk.Label(root, text="Pilih estate (Inti/Plasma):", font=("Arial", 12))
    label_estate_option.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    ESTATE_OPTIONS = ["Inti", "Plasma"]
    combobox_estate = ttk.Combobox(root, values=ESTATE_OPTIONS, width=30, font=("Arial", 10))
    combobox_estate.grid(row=1, column=0, padx=10, pady=10)

    submit_estate_check_button = tk.Button(root, text="Check Estate", command=lambda: check_existing_rainfall(combobox_estate.get(), current_time_date), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    submit_estate_check_button.grid(row=2, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    back_button.grid(row=3, column=0, padx=10, pady=10)

    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # Set color
    main_menu_button.grid(row=4, column=0, padx=10, pady=10)

    root.columnconfigure(0, weight=1)


# %%
def show_rainfall_data_entry(selected_estate):
    """Displays the rainfall data entry fields, pre-populated with the last entry."""
    global previous_menu, entry_update_rainfall, label_update_rainfall, back_button, main_menu_button, submit_update_rainfall_button, df

    if not root_exists:
        return

    hide_all_widgets()

    previous_menu = "estate"

    estate_data = df[df['Estate'] == selected_estate]

    if not estate_data.empty: 
        last_date = estate_data['Date'].iloc[-1] 
        last_rainfall = estate_data['Daily Rainfall (mm)'].iloc[-1]

        label_update_rainfall = tk.Label(root, text=f"Update Data Hujan Untuk {selected_estate} Pada Tanggal {format_datetime(last_date)} (mm):", font=("Arial", 12))
        label_update_rainfall.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        entry_update_rainfall = tk.Entry(root, font=("Arial", 10))
        entry_update_rainfall.insert(0, str(last_rainfall))  
        entry_update_rainfall.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        submit_update_rainfall_button = tk.Button(root, text="Submit Rainfall", command=lambda: submit_update_rainfall(selected_estate, last_date, entry_update_rainfall.get()), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        submit_update_rainfall_button.grid(row=4, column=0, padx=10, pady=10)

        back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        back_button.grid(row=5, column=0, padx=10, pady=10)

        main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        main_menu_button.grid(row=6, column=0, padx=10, pady=10)

        root.columnconfigure(0, weight=1)

    else:
        # Handle the case where there's no data for the selected estate.
        label_no_data = tk.Label(root, text=f"No rainfall data found for {selected_estate}.", font=("Arial", 12))
        label_no_data.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        back_button.grid(row=3, column=0, padx=10, pady=10)

        main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
        main_menu_button.grid(row=4, column=0, padx=10, pady=10)
        root.columnconfigure(0, weight=1)


# %%
def show_add_rainfall_entry(selected_estate, date):
    """Displays the screen to add new rainfall data."""
    global entry_daily_rainfall, label_daily_rainfall, submit_add_rainfall_button, previous_menu # Added previous_menu

    if not root_exists: return # Added check

    # --- ROW & COLUMN RESET for ROOT ---
    for i in range(20): root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    # --- END ROOT RESET ---

    hide_all_widgets()
    # Make sure previous_menu is set correctly before calling this function
    # If coming from submit_missing_dates, previous_menu should ideally be set
    # to 'missing_dates_input' or similar before calling this.
    # Let's set it here for now if it wasn't set properly before.
    previous_menu = "missing_dates_input" # Or adjust based on actual flow

    # --- COLUMN CONFIGURATION (Add Reset for Column 1) ---
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0) # <<< ADD THIS LINE
    # --- END COLUMN CONFIGURATION ---

    # --- FIX THE LABEL TEXT ---
    label_daily_rainfall = tk.Label(root, text=f"Masukkan Data Hujan (mm) untuk {selected_estate} pada tanggal {format_datetime(date)}:", font=("Arial", 12))
    label_daily_rainfall.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    entry_daily_rainfall = tk.Entry(root, font=("Arial", 10))
    entry_daily_rainfall.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    # Pass the correct 'date' (which is datetime.date) to the submit function
    submit_add_rainfall_button = tk.Button(root, text="Submit Rainfall", command=lambda: submit_estate_for_add_rainfall(selected_estate, date, entry_daily_rainfall.get()), font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    submit_add_rainfall_button.grid(row=2, column=0, padx=10, pady=10)

    back_button = tk.Button(root, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    back_button.grid(row=3, column=0, padx=10, pady=10)

    main_menu_button = tk.Button(root, text="Back to Main Menu", command=back_to_main, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    main_menu_button.grid(row=4, column=0, padx=10, pady=10)
    root.columnconfigure(0, weight=1)


# %% [markdown]
#  ## 10. GUI - Navigation & Action Functions

# %%
def submit_production_analysis(): 
    global username_var, combobox_estate, entry_divisi, entry_blok, entry_pokok_sample, entry_pokok_panen, entry_actual, entry_budget, \
           entry_buah_panen, entry_buah_tertinggal, entry_berondolan_tertinggal, entry_buah_tertinggal_tph, \
           entry_berondolan_tertinggal_tph, entry_rotasi_panen, entry_restan, entry_jaring, entry_produktivitas_pemanen, \
           entry_administrasi_panen, entry_kualitas_tbs, entry_muatan_overload, entry_upload_note

    if not root_exists: return

    # --- Basic Input Validation ---
    if not combobox_estate.get(): messagebox.showerror("Error", "Tolong masukkan nama estate."); return
    if combobox_estate.get() not in ESTATE_OPTIONS: messagebox.showerror("Error", f"Nama estate invalid: '{combobox_estate.get()}'."); return
    if not entry_divisi.get(): messagebox.showerror("Error", "Tolong masukkan nama divisi."); return
    if not entry_blok.get(): messagebox.showerror("Error", "Tolong masukkan nama blok."); return
    if not entry_pokok_sample.get(): messagebox.showerror("Error", "Tolong masukkan pokok sample."); return
    if not entry_pokok_panen.get(): messagebox.showerror("Error", "Tolong masukkan pokok panen."); return
    if not entry_actual.get(): messagebox.showerror("Error", "Tolong masukkan produksi actual."); return
    if not entry_budget.get(): messagebox.showerror("Error", "Tolong masukkan budget produksi."); return
    if not entry_buah_panen.get(): messagebox.showerror("Error", "Tolong masukkan jumlah buah terpanen."); return
    if not entry_buah_tertinggal.get(): messagebox.showerror("Error", "Tolong masukkan jumlah buah tertinggal."); return
    if not entry_berondolan_tertinggal.get(): messagebox.showerror("Error", "Tolong masukkan jumlah berondolan tertinggal."); return
    if not entry_buah_tertinggal_tph.get(): messagebox.showerror("Error", "Tolong masukkan jumlah buah tertinggal di mobil."); return
    if not entry_berondolan_tertinggal_tph.get(): messagebox.showerror("Error", "Tolong masukkan jumlah berondolan tertinggal di mobil."); return
    if not entry_rotasi_panen.get(): messagebox.showerror("Error", "Tolong masukkan rotasi panen."); return
    if not entry_restan.get(): messagebox.showerror("Error", "Tolong masukkan nilai restan."); return
    if not entry_jaring.get(): messagebox.showerror("Error", "Tolong masukkan jumlah jaring."); return
    if not entry_produktivitas_pemanen.get(): messagebox.showerror("Error", "Tolong masukkan nilai produktivitas pemanen."); return
    if not entry_administrasi_panen.get(): messagebox.showerror("Error", "Tolong masukkan nilai administrasi panen."); return
    if not entry_kualitas_tbs.get(): messagebox.showerror("Error", "Tolong masukkan nilai kualitas TBS."); return
    if not entry_muatan_overload.get(): messagebox.showerror("Error", "Tolong masukkan jumlah muatan overload."); return
    if not entry_upload_note.get(): messagebox.showerror("Error", "Tolong masukkan rencana jenis pupuk."); return

    username = username_var.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username di dalam main menu.")
        return
    
    try:
        pokok_sample_float = float(entry_pokok_sample)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        pokok_panen_float = float(entry_pokok_panen)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok panen harus berupa angka.")
        return
    
    try:
        actual_float = float(entry_actual)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        budget_float = float(entry_budget)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        buah_panen_float = float(entry_buah_panen)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        buah_tertinggal_float = float(entry_buah_tertinggal)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        berondolan_tertinggal_float = float(entry_berondolan_tertinggal)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        buah_tertinggal_tph_float = float(entry_buah_tertinggal_tph)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        berondolan_tertinggal_tph_float = float(entry_berondolan_tertinggal_tph)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        rotasi_panen_float = float(entry_rotasi_panen)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        restan_float = float(entry_restan)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        jaring_float = float(entry_jaring)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        produktivitas_pemanen_float = float(entry_produktivitas_pemanen)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        administrasi_panen_float = float(entry_administrasi_panen)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        kualitas_tbs_float = float(entry_kualitas_tbs)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        muatan_overload_float = float(entry_muatan_overload)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    try:
        upload_note_float = float(entry_upload_note)
    except ValueError:
        messagebox.showerror("Error", "Nilai pokok sample harus berupa angka.")
        return
    
    final_qa_scores = analyse_qa_production(combobox_estate.get(), 
                          entry_divisi.get(),
                          entry_blok.get(),
                          pokok_sample_float,
                          pokok_panen_float,
                          actual_float,
                          budget_float,
                          buah_panen_float,
                          buah_tertinggal_float,
                          berondolan_tertinggal_float,
                          buah_tertinggal_tph_float,
                          berondolan_tertinggal_tph_float,
                          rotasi_panen_float,
                          restan_float,
                          jaring_float,
                          produktivitas_pemanen_float,
                          administrasi_panen_float,
                          kualitas_tbs_float,
                          muatan_overload_float)
    
    # Display the results - Pass strings for display as they were entered/selected
    display_analysis_results(
        selected_estate, blok, tanggal_rencana_pupuk_str, peilscale, # Pass original peilscale string
        tanggal_pupuk_terakhir_str, jenis_pupuk_terakhir, rencana_jenis_pupuk,
        username, current_daily_rainfall, status, reason, recommendation
    )

# %%
def submit_missing_dates(selected_estate, missing_dates_list):
    """Processes the input for missing rainfall dates."""
    global df, missing_dates_widgets # Remove current_time_date from global if not needed elsewhere in this func

    if not root_exists:
        return

    rainfall_inputs = {}
    try:
        # --- Validation Phase ---
        for date_item in missing_dates_list: # Use different variable name to avoid confusion
            print(f"Validating date: {date_item}, Type: {type(date_item)}") # Debug print

            # --- Gracefully handle date object ---
            if isinstance(date_item, datetime.datetime) or hasattr(date_item, 'date'): # Check if it's datetime or has .date() (like Timestamp)
                 date_obj = date_item.date()
            elif isinstance(date_item, datetime.date):
                 date_obj = date_item # It's already a date object
            else:
                 # Handle unexpected type if necessary
                 messagebox.showerror("Error", f"Tipe data tanggal tidak dikenal: {type(date_item)}")
                 return
            # --- End of handling ---

            # Now use date_obj (which is guaranteed to be a datetime.date) as the key
            if date_obj not in missing_dates_widgets:
                 messagebox.showerror("Error", f"Widget input tidak ditemukan untuk tanggal {format_datetime(date_obj)}")
                 print(f"Key error: {date_obj} not in {missing_dates_widgets.keys()}") # Debug print
                 return

            entry_widget = missing_dates_widgets[date_obj]["entry"]
            rainfall_str = entry_widget.get()
            if not rainfall_str:
                messagebox.showerror("Error", f"Nilai curah hujan untuk tanggal {format_datetime(date_obj)} tidak boleh kosong.")
                return

            rainfall_val = float(rainfall_str)
            if rainfall_val < 0:
                messagebox.showerror("Error", f"Nilai curah hujan untuk tanggal {format_datetime(date_obj)} tidak boleh negatif.")
                return
            rainfall_inputs[date_obj] = rainfall_val # Store validated value, keyed by date_obj

        # --- Processing Phase ---
        # Sort dates to ensure correct calculation order
        sorted_dates = sorted(rainfall_inputs.keys())

        for date_obj in sorted_dates:
            rainfall_val = rainfall_inputs[date_obj]
            print(f"Processing missing date: {format_datetime(date_obj)}, Rainfall: {rainfall_val}") # Debug print
            df = calculate_rainfall(df, date_obj, rainfall_val, selected_estate)
            root.update_idletasks() # Update UI briefly


        messagebox.showinfo("Sukses", f"Data hujan untuk tanggal yang belum diinput ({len(sorted_dates)} hari) telah berhasil ditambahkan.")

        # --- Proceed to Today's Input ---
        today_now = datetime.datetime.now(CURRENT_TIMEZONE) # Get FRESH datetime HERE
        today_date_obj = today_now.date()          # Extract date part correctly

        # Ensure 'Date' column is datetime before comparison
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
             df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True) # Drop rows where conversion failed

        estate_data_today = df[(df['Estate'] == selected_estate) & (df['Date'].dt.date == today_date_obj)]

        if estate_data_today.empty:
            print("Proceeding to input today's rainfall...")
            # Pass today_date_obj (which is datetime.date)
            show_add_rainfall_entry(selected_estate, today_date_obj)
        else:
            print("Today's rainfall already exists after filling gaps.")
            messagebox.showinfo("Info", f"Data hujan untuk hari ini ({format_datetime(today_date_obj)}) sudah ada.")
            back_to_main()

    except ValueError:
        messagebox.showerror("Error", "Input curah hujan tidak valid. Harap masukkan angka.")
        return
    except Exception as e:
        # Print detailed traceback
        import traceback
        print("--- Traceback ---")
        traceback.print_exc()
        print("--- End Traceback ---")
        messagebox.showerror("Error", f"Terjadi kesalahan saat memproses data: {e}")
        print(f"Error during submit_missing_dates: {e}") # Log the error
        return


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
    """Displays a success window with a button to return to the main menu."""
    global success_window, root  # Declare success_window as global
    if not root_exists:
        return
    
    # Create a new top-level window
    success_window = tk.Toplevel(root)
    success_window.title("Success")
    success_window.geometry("300x100")  # Adjust size as needed

    # Make the new window modal (prevent interaction with the main window)
    success_window.transient(root) 
    success_window.grab_set()   

    label_success = tk.Label(success_window, text="Update data hujan sukses!", font=("Arial", 12))
    label_success.pack(pady=10)
    
    button_back_to_main = tk.Button(success_window, text="Back to Main Menu", command=close_success_and_go_back, font=("Arial", 10), bg=MAIN_MENU_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR) # set color
    button_back_to_main.pack(pady=5)
    
    success_window.columnconfigure(0, weight=1)


# %%
def submit_update_rainfall(selected_estate, date, new_rainfall):
    """Submits the updated rainfall data to the spreadsheet."""
    global previous_menu, df, entry_update_rainfall
    if not root_exists:
        return
    
    try:
        new_rainfall = float(new_rainfall)
        if new_rainfall < 0:
            raise ValueError("Rainfall cannot be negative.")
    except ValueError:
        tk.messagebox.showerror("Error", "Nilai curah hujan invalid. Tolong masukkan bilangan positif.")
        return
    
    # Remove the old data
    df = remove_old_data(df, date, selected_estate)

    # Recalculate dependent columns using calculate_rainfall
    df = calculate_rainfall(df, date, new_rainfall, selected_estate)

    show_success_window()


# %%
def submit_estate_for_add_rainfall(selected_estate, date, new_rainfall):
    global previous_menu, df

    if not root_exists:
        return
    
    ESTATE_OPTIONS = ["Inti", "Plasma"]
    if selected_estate not in ESTATE_OPTIONS:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(ESTATE_OPTIONS)}")
        return
    
    try:
        new_rainfall = float(new_rainfall)
        if new_rainfall < 0:
            raise ValueError("Rainfall cannot be negative.")
    except ValueError:
        tk.messagebox.showerror("Error", "Nilai curah hujan invalid. Tolong masukkan bilangan positif.")
        return
    
    df = calculate_rainfall(df, date, new_rainfall, selected_estate)
    
    show_success_window()


# %%
def check_existing_rainfall(selected_estate, current_time_date):
    global df, previous_menu

    if not root_exists:
        return

    # --- Input Validation ---
    ESTATE_OPTIONS = ["Inti", "Plasma"]
    if not selected_estate:
        messagebox.showerror("Error", "Silakan pilih estate terlebih dahulu.")
        return
    if selected_estate not in ESTATE_OPTIONS:
        messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(ESTATE_OPTIONS)}")
        return

    # --- Check for Missing Dates FIRST ---
    missing_dates, last_reported_time, total_missing_dates = get_missing_dates(df, selected_estate, current_time_date)

    print(f"Checking estate: {selected_estate}") # Debug
    print(f"Last reported: {last_reported_time}, Missing: {total_missing_dates}") # Debug
    # print(f"Missing dates list: {missing_dates}") # Debug (can be long)

    if total_missing_dates > 0:
        # --- Show Missing Dates Input Screen ---
        print(f"Found {total_missing_dates} missing dates. Showing input screen.") # Debug
        # It's generally better *not* to show a blocking error here, but proceed to the input screen
        # messagebox.showinfo("Info", f"Terdapat {total_missing_dates} hari data hujan yang hilang untuk estate {selected_estate} sejak {format_datetime(last_reported_time + timedelta(days=1))}.\n\nAnda akan diminta untuk mengisi data tersebut terlebih dahulu.")
        show_missing_dates_input(selected_estate, missing_dates)
        # previous_menu is set inside show_missing_dates_input

    else:
        # --- No Missing Dates, Check Today's Data ---
        print("No missing dates found. Checking today's data.") # Debug
        today_date = current_time_date.date() # Use date object for comparison
        # Ensure 'Date' column in df is datetime type before comparison
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
             df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        estate_data_today = df[(df['Estate'] == selected_estate) & (df['Date'].dt.date == today_date)]

        if estate_data_today.empty:
            # --- Today's Data Missing: Show Input Screen for Today ---
            print("Today's data not found. Showing add rainfall entry.") # Debug
            # hide_estate_widgets() # hide_all_widgets is called in show_add_rainfall_entry
            show_add_rainfall_entry(selected_estate, today_date)
            previous_menu = "estate_add_rainfall" # Came from estate selection
        else:
            # --- Today's Data Exists ---
            print("Today's data already exists.") # Debug
            estate_rainfall_today = df['Daily Rainfall (mm)'].iloc[-1]
            # hide_estate_widgets() # hide_all_widgets is called later if needed
            messagebox.showinfo("Info", f"Data hujan untuk estate {selected_estate} pada hari ini ({format_datetime(today_date)}) sudah dimasukkan sebesar {estate_rainfall_today}."
                                "\nSilahkan update data melalui menu 'Masukkan Data Hujan' → 'Update Data Hujan Terakhir' ")
            # Decide where to go now - maybe back to main menu or rainfall options?
            back_to_main() # Or show_rainfall_options()
            # Alternatively, you could offer to go to the 'Update' screen:
            # print("Going to update screen as today's data exists.")
            # show_rainfall_data_entry(selected_estate)
            # previous_menu = "estate_add_rainfall" # Or adjust as needed


# %%
def go_back():
    """Handles navigation back; uses after_idle and hide_all_widgets."""
    global previous_menu
    if not root_exists:
        return
    
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


# %%
def submit_estate_for_analysis(selected_estate, nama_blok, peilscale, jenis_terakhir, tanggal_terakhir, rencana_jenis, tanggal_rencana):
    global previous_menu, username_var, df
    if not root_exists:
        return
    
    ESTATE_OPTIONS = ["Inti", "Plasma"]
    if selected_estate not in ESTATE_OPTIONS:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(ESTATE_OPTIONS)}")
        return
    
    # Get current time
    date_input = datetime.now(CURRENT_TIMEZONE)

    # Get the username
    username = username_var.get()

    # Convert string to integer
    peilscale = int(peilscale)

    current_daily_rainfall, status, reason, recommendation = analyze_fertilizer(date_input, username, selected_estate, nama_blok, df, peilscale, jenis_terakhir, tanggal_terakhir, rencana_jenis, tanggal_rencana)

    # Display the results
    display_analysis_results(
        selected_estate, nama_blok, tanggal_rencana, peilscale, tanggal_terakhir,
        jenis_terakhir, rencana_jenis, username, current_daily_rainfall, status, reason, recommendation
    )
    # previous_menu = "main"  # No longer going back to main immediately
    # cancel_to_main()


# %%
def submit_estate(selected_estate):
    global previous_menu
    if not root_exists:
        return
    
    ESTATE_OPTIONS = ["Inti", "Plasma"]
    if selected_estate not in ESTATE_OPTIONS:
        tk.messagebox.showerror("Error", f"Nama estate invalid: '{selected_estate}'. Tolong pilih antara: {', '.join(ESTATE_OPTIONS)}")
        return

    print(f"Selected Estate: {selected_estate}")
    show_rainfall_data_entry(selected_estate)


# %%
def goto_chosen_menu():
    global previous_menu, entry_username, combobox_menu_qa, combobox_chosen_year, df_input, df_output, df_output_weight, chosen_year_weight

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
        df_input, df_output, df_output_weight = load_sheets_for_menu(menu_qa)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memuat data untuk {menu_qa}: {e}")
        return
    
    if menu_qa == "QA Produksi":
        qa_calculate_production()
    elif menu_qa == "QA Perawatan":
        qa_calculate_production()
    elif menu_qa == "QA Pemupukan":
        qa_calculate_production()
    elif menu_qa == "QA Chemist":
        qa_calculate_production()

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
            'parents': [{'id': FOLDER_ID}]
        })

        file_drive.SetContentFile(file_path)
        file_drive.Upload()

        messagebox.showinfo("Berhasil", "Foto berhasil diupload ke Google Drive.")
        print(f"Uploaded: {filename} to folder ID {FOLDER_ID}")

    except Exception as e:
        messagebox.showerror("Error", f"Gagal upload foto: {e}")
        print(f"Error uploading to Google Drive: {e}")

# %%
def choose_and_upload_file():
    global uploaded_photo_path
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return

    note_text = entry_upload_note.get()
    uploaded_photo_path = file_path
    upload_photo_to_drive(file_path, note_text)

# %%
def generate_pdf_output():
    global uploaded_photo_path

    pdf_path = f"hasil_analisa_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # --- Sample Text Data (You can replace these with actual values) ---
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 50, "Hasil Analisa QA Produksi")
    c.drawString(50, height - 80, f"Tanggal: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}")
    c.drawString(50, height - 110, f"Catatan: {entry_upload_note.get()}")

    # --- Insert the image if available ---
    if uploaded_photo_path and os.path.exists(uploaded_photo_path):
        try:
            img = ImageReader(uploaded_photo_path)
            c.drawImage(img, 50, height - 400, width=200, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error loading image in PDF: {e}")
            c.drawString(50, height - 140, "Gagal memuat foto untuk PDF.")

    # --- Finalize PDF ---
    c.showPage()
    c.save()

    messagebox.showinfo("Berhasil", f"PDF berhasil dibuat:\n{pdf_path}")
    os.startfile(pdf_path)  # Optional: Open PDF automatically (Windows only)

# %%
def qa_calculate_production():
    global label_estate_option, label_divisi, label_blok, label_pokok_sample, label_pokok_panen, label_actual, label_budget, \
           label_buah_panen, label_buah_tertinggal, label_berondolan_tertinggal, label_buah_tertinggal_tph, \
           label_berondolan_tertinggal_tph, label_rotasi_panen, label_restan, label_jaring, label_produktivitas_pemanen, \
           label_administrasi_panen, label_kualitas_tbs, label_muatan_overload, label_upload_note, \
           combobox_estate, entry_divisi, entry_blok, entry_pokok_sample, entry_pokok_panen, entry_actual, entry_budget, \
           entry_buah_panen, entry_buah_tertinggal, entry_berondolan_tertinggal, entry_buah_tertinggal_tph, \
           entry_berondolan_tertinggal_tph, entry_rotasi_panen, entry_restan, entry_jaring, entry_produktivitas_pemanen, \
           entry_administrasi_panen, entry_kualitas_tbs, entry_muatan_overload, entry_upload_note, \
           button_upload_photo, submit_calculation_production_button, back_button, current_menu

    if not root_exists:
        return

    hide_all_widgets()
    current_menu = "qa_calculate_production"

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

    # === ALL YOUR WIDGETS GO INTO scrollable_frame ===
    row = 0
    label_estate_option = tk.Label(scrollable_frame, text="Pilih estate (Inti/Plasma):", font=("Arial", 12))
    label_estate_option.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    combobox_estate = ttk.Combobox(scrollable_frame, values=["Inti", "Plasma"], width=30, font=("Arial", 10))
    combobox_estate.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_divisi = tk.Label(scrollable_frame, text="Masukkan Nama Divisi:", font=("Arial", 12))
    label_divisi.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_divisi = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_divisi.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_blok = tk.Label(scrollable_frame, text="Masukkan Nama Blok:", font=("Arial", 12))
    label_blok.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_blok = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_blok.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_pokok_sample = tk.Label(scrollable_frame, text="Masukkan jumlah pokok sample:", font=("Arial", 12))
    label_pokok_sample.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_pokok_sample = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_pokok_sample.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_pokok_panen = tk.Label(scrollable_frame, text="Masukkan jumlah pokok panen:", font=("Arial", 12))
    label_pokok_panen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_pokok_panen = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_pokok_panen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_actual = tk.Label(scrollable_frame, text="Masukkan jumlah produksi aktual:", font=("Arial", 12))
    label_actual.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_actual = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_actual.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_budget = tk.Label(scrollable_frame, text="Masukkan jumlah budget produksi:", font=("Arial", 12))
    label_budget.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_budget = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_budget.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_buah_panen = tk.Label(scrollable_frame, text="Masukkan jumlah buah panen:", font=("Arial", 12))
    label_buah_panen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_buah_panen = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_buah_panen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_buah_tertinggal = tk.Label(scrollable_frame, text="Masukkan jumlah buah tertinggal (di pokok/piringan/path/gawangan (masak, overripe, busuk)):", font=("Arial", 12))
    label_buah_tertinggal.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_buah_tertinggal = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_buah_tertinggal.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_berondolan_tertinggal = tk.Label(scrollable_frame, text="Masukkan jumlah berondolan tertinggal/tersangkut (di pelepah, piringan, path, gawangan):", font=("Arial", 12))
    label_berondolan_tertinggal.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_berondolan_tertinggal = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_berondolan_tertinggal.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_buah_tertinggal_tph = tk.Label(scrollable_frame, text="Masukkan jumlah buah tertinggal di TPH atau tercecer di CR & MR:", font=("Arial", 12))
    label_buah_tertinggal_tph.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_buah_tertinggal_tph = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_buah_tertinggal_tph.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_berondolan_tertinggal_tph = tk.Label(scrollable_frame, text="Masukkan jumlah berondolan tertinggal di TPH atau tercecer di CR & MR:", font=("Arial", 12))
    label_berondolan_tertinggal_tph.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_berondolan_tertinggal_tph = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_berondolan_tertinggal_tph.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_rotasi_panen = tk.Label(scrollable_frame, text="Masukkan jumlah rotasi panen perbulan:", font=("Arial", 12))
    label_rotasi_panen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_rotasi_panen = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_rotasi_panen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_restan = tk.Label(scrollable_frame, text="Masukkan nilai restan:", font=("Arial", 12))
    label_restan.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_restan = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_restan.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_jaring = tk.Label(scrollable_frame, text="Masukkan jumlah pemakaian jaring:", font=("Arial", 12))
    label_jaring.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_jaring = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_jaring.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_produktivitas_pemanen = tk.Label(scrollable_frame, text="Masukkan nilai produktivitas pemanen:", font=("Arial", 12))
    label_produktivitas_pemanen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_produktivitas_pemanen = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_produktivitas_pemanen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_administrasi_panen = tk.Label(scrollable_frame, text="Masukkan administrasi pemanen:", font=("Arial", 12))
    label_administrasi_panen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_administrasi_panen = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_administrasi_panen.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_kualitas_tbs = tk.Label(scrollable_frame, text="Masukkan nilai kualitas TBS:", font=("Arial", 12))
    label_kualitas_tbs.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_kualitas_tbs = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_kualitas_tbs.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_muatan_overload = tk.Label(scrollable_frame, text="Masukkan nilai muatan overload:", font=("Arial", 12))
    label_muatan_overload.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_muatan_overload = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_muatan_overload.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    label_upload_note = tk.Label(scrollable_frame, text="Catatan Foto (opsional):", font=("Arial", 12))
    label_upload_note.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    entry_upload_note = tk.Entry(scrollable_frame, font=("Arial", 10))
    entry_upload_note.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
    row += 1

    button_upload_photo = tk.Button(scrollable_frame, text="Upload Foto", command=choose_and_upload_file, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    button_upload_photo.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
    row += 1

    submit_pdf_button = tk.Button(scrollable_frame, text="Buat PDF", command=generate_pdf_output, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    submit_pdf_button.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
    row += 1

    submit_calculation_production_button = tk.Button(scrollable_frame, text="Submit", command=submit_production_analysis, font=("Arial", 10), bg=PRIMARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    submit_calculation_production_button.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
    row += 1

    back_button = tk.Button(scrollable_frame, text="Back", command=go_back, font=("Arial", 10), bg=SECONDARY_BUTTON_COLOR, fg=BUTTON_TEXT_COLOR)
    back_button.grid(row=row, column=0, padx=10, pady=10, sticky="ew")


# %%
def goto_input_hujan():
    global previous_menu, entry_username
    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---

    # Check username for the first time
    username = entry_username.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username.")
        return

    previous_menu = "main"
    hide_all_widgets()
    show_rainfall_options()


# %%
def goto_analisa_pemupukan():
    global previous_menu, entry_username
    if not root_exists: return

    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---

    # Check username for the first time
    username = entry_username.get()
    if not username.strip():
        messagebox.showerror("Error", "Tolong masukkan username.")
        return
    
    previous_menu = "main"
    hide_all_widgets()
    show_estate_options_for_analysis()


# %%
def goto_update_rainfall():
    global previous_menu
    if not root_exists:
        return
    
    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---
    
    print(f"Selected Rainfall Option: Update Data Hujan Terakhir")
    previous_menu = "rainfall"
    show_ESTATE_OPTIONS()


# %%
def goto_add_rainfall():
    global previous_menu
    if not root_exists:
        return
    
    # --- ROW & COLUMN CONFIGURATION RESET ---
    for i in range(20): # Reset rows
        root.rowconfigure(i, weight=0)
    root.columnconfigure(0, weight=1) # Configure columns needed by THIS screen
    root.columnconfigure(1, weight=0) # Reset unused columns
    # --- END CONFIGURATION ---
    
    print(f"Selected Rainfall Option: Masukkan Data Hujan Baru")
    show_ESTATE_OPTIONS_for_add_rainfall()


# %% [markdown]
#  ## 11. GUI - Window Management

# %%
def on_closing():
    global root_exists
    root_exists = False
    disable_buttons()
    if root: # Check if root exists before destroying
       root.destroy()

def disable_buttons():
    """Disables all interactive buttons to prevent further events."""
    # Keep this function as is, it's robust.
    # ... (Your existing disable_buttons code) ...


# %% [markdown]
#  ## 12. Main Application (`main_process`)

# %%
def main_process():
    # Define all globals used within this function and others it calls
    global root, previous_menu, root_exists, current_menu, \
           df, input_sheets, output_sheets, df_input_sheets, df_output_sheets, \
           df_input, df_output, df_output_weight, \
           chosen_year_weight, \
           photo_image, \
           username_var, username, \
           input_production, input_nursery, input_chemist, input_fertilizer, \
           output_production, output_nursery , output_chemist, output_fertilizer, \
           label_username, entry_username, exit_button, label_rainfall_option, \
           button_update_rainfall, button_add_rainfall, back_button, \
           label_menu_qa, combobox_menu_qa, label_chosen_year, combobox_chosen_year, label_note_year, \
           label_estate_option, combobox_estate, submit_estate_button, \
           main_menu_button, submit_estate_check_button, \
           label_missing_dates_title, missing_dates_widgets, submit_missing_dates_button, \
           canvas, scrollbar, inner_frame, \
           label_daily_rainfall, entry_daily_rainfall, submit_add_rainfall_button, \
           label_update_rainfall, entry_update_rainfall, submit_update_rainfall_button, \
           entry_blok, entry_divisi, entry_tanggal_rencana_pupuk, entry_pokok_sample, entry_pokok_panen, entry_actual, entry_budget, \
           entry_buah_panen, entry_buah_tertinggal, entry_berondolan_tertinggal, entry_buah_tertinggal_tph, \
           entry_berondolan_tertinggal_tph, entry_rotasi_panen, entry_restan, entry_jaring, entry_produktivitas_pemanen, \
           entry_administrasi_panen, entry_kualitas_tbs, entry_muatan_overload, label_upload_note, \
           label_blok, label_divisi,  label_tanggal_rencana_pupuk, label_pokok_sample, label_pokok_panen, label_actual, label_budget, \
           label_buah_panen, label_buah_tertinggal, label_berondolan_tertinggal, label_buah_tertinggal_tph, \
           label_berondolan_tertinggal_tph, label_rotasi_panen, label_restan, label_jaring, label_produktivitas_pemanen, \
           label_administrasi_panen, label_kualitas_tbs, label_muatan_overload, entry_upload_note, \
           uploaded_photo_path, \
           button_upload_photo, submit_calculation_production_button, \
           button_tanggal_rencana_pupuk, button_tanggal_pupuk_terakhir, \
           label_tanggal_analisa, label_nama_user, label_curah_hujan, \
           label_status, label_reason, label_recommendation, label_selected_estate, \
           label_nama_blok, label_tanggal_rencana, label_peilscale_value, \
           label_tanggal_terakhir_value, label_jenis_terakhir_value, \
           label_rencana_jenis_value, back_to_main_button, reanalyze_button, \
           label_saved_username, label_no_data, splash_label, splash_button


    # --- Initialize App ---
    root = tk.Tk()
    root.title("QA Agronomy Services Dept - Pancaran Agro")
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
    combobox_rainfall = None
    submit_rainfall_button = None
    back_button = None
    label_menu_qa = None
    combobox_menu_qa = None
    label_chosen_year = None
    combobox_chosen_year = None
    label_note_year = None
    label_estate_option = None
    combobox_estate = None
    submit_estate_button = None
    entry_blok = None
    entry_divisi = None
    label_tanggal_rencana_pupuk = None
    entry_tanggal_rencana_pupuk = None
    label_pokok_sample = None
    entry_pokok_sample = None
    label_pokok_panen = None
    entry_pokok_panen = None
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
    label_upload_note = None
    entry_upload_note = None
    uploaded_photo_path = None
    button_upload_photo = None
    submit_calculation_production_button = None
    label_tanggal_pupuk_terakhir = None
    entry_tanggal_pupuk_terakhir = None
    label_jenis_pupuk_terakhir = None
    combobox_jenis_pupuk_terakhir = None
    label_rencana_jenis_pupuk = None
    combobox_rencana_jenis_pupuk = None
    submit_estate_add_rainfall_button = None
    entry_daily_rainfall = None
    label_daily_rainfall = None
    label_blok = None
    label_divisi = None
    button_input_hujan = None
    button_analisa_pemupukan = None
    button_update_rainfall = None
    button_add_rainfall = None
    label_tanggal_analisa = None
    label_nama_user = None
    label_curah_hujan = None
    label_status = None
    label_reason = None
    label_recommendation = None
    label_selected_estate = None
    label_nama_blok = None
    label_tanggal_rencana = None
    label_peilscale_value = None
    label_tanggal_terakhir_value = None
    label_jenis_terakhir_value = None
    label_rencana_jenis_value = None
    back_to_main_button = None
    reanalyze_button = None
    main_menu_button = None
    label_update_rainfall = None
    entry_update_rainfall = None
    submit_update_rainfall_button = None
    label_saved_username = None
    missing_dates_widgets = {}
    label_missing_dates_title = None
    submit_missing_dates_button = None
    splash_label = None
    splash_button = None

    # --- Connect to Google Sheets ---
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, SCOPE)
        client = gspread.authorize(creds)

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
    root.iconbitmap(resource_path("Logo_Pancaran_Agro-removebg-preview.ico"))  # Make sure the path is correct
    root.mainloop()


# %% [markdown]
#  ## 13. Execution Block

# %%
if __name__ == "__main__":
    # Any setup required before starting the process
    # (like checking for credential file existence maybe)
    if not os.path.exists(JSON_PATH):
         print(f"ERROR: Credential file not found at {JSON_PATH}")
         # Optionally show a Tkinter error box even before root is created
         # temp_root = tk.Tk(); temp_root.withdraw() # Hide temp root
         # messagebox.showerror("Startup Error", f"Credential file missing:\n{JSON_PATH}")
         # temp_root.destroy()
         sys.exit("Credential file missing.") # Exit if critical file missing

    main_process()


