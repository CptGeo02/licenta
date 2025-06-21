# Standard library
import json
import logging
import math
import os
import platform
import subprocess
import tempfile
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import (
    Canvas, Frame, Button, Label, Tk, StringVar, OptionMenu, Checkbutton,
    BooleanVar, filedialog, messagebox, simpledialog, ttk
)
from xmlrpc.client import boolean

# External libraries
import cv2  # OpenCV
import customtkinter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil
import pygame
import serial
import torch  # PyTorch
from idlelib.tooltip import Hovertip
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
from openpyxl.utils import get_column_letter
from PIL import Image, ImageTk
from tkcalendar import Calendar
from ultralytics import YOLO
from flask import Flask, render_template, Response
from serial.tools import list_ports

# Local project imports
from src.utils.detection_utils import *
from src.utils.excel_utils import *
from src.utils.frame_utils import *
from src.utils.gui_utils import *
from src.utils.time_utils import *

# Logging configuration
logging.basicConfig(level=logging.ERROR)

# Set device for PyTorch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
