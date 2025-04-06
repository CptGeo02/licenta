# Centralized import of external libraries
import threading
import torch # PyTorch, used for YOLOv8 model inference
import cv2  # OpenCV, used for video/image processing
import tkinter as tk # Tkinter for GUI
import os # To manage file and directory operations
import numpy as np # NumPy for numerical operations
from tkinter import filedialog
from ultralytics import YOLO  # Import YOLO to load the model properly
from PIL import Image, ImageTk
from tkinter import Canvas, Frame, Button, Label, Tk, StringVar, OptionMenu
import time
import pandas as pd
from datetime import timedelta, datetime
from tkinter import Checkbutton, BooleanVar  # Adăugare import pentru switch
import psutil
import platform
import subprocess
import json
from tkinter import messagebox
from tkinter import ttk
import customtkinter
from openpyxl.drawing.image import Image as ExcelImage
from tkcalendar import Calendar
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
from openpyxl.utils import get_column_letter
import tempfile
import logging
from idlelib.tooltip import Hovertip  # Pentru tooltips informative

from src.utils.detection_utils import *
from src.utils.excel_utils import *
from src.utils.frame_utils import *
from src.utils.gui_utils import *
from src.utils.time_utils import *

logging.basicConfig(level=logging.ERROR)

# Check if CUDA is available and set the device to GPU if so
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")