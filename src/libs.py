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
from PIL import Image, ImageTk
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

# Check if CUDA is available and set the device to GPU if so
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")