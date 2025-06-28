# AI Restaurant Monitoring System 🍽️🤖

Sistem inteligent de monitorizare a activității din restaurante, bazat pe detecție computerizată și analiză automată a comportamentului meselor.

---

## 🧠 Tehnologii utilizate
- **Python 3.12**
- **YOLOv10 / YOLOv8** (detecție obiecte)
- **Tkinter + CustomTkinter** (interfață grafică)
- **OpenCV** (procesare video)
- **Matplotlib** (vizualizare statistici)
- **NumPy & Pandas** (analiză de date)
- **Openpyxl** (rapoarte Excel)
- **Intel RealSense D435i** (cameră RGB + adâncime)
- **ESP32-S3-MINI** (control cameră motorizată)

---

## 📂 Structură generală


```
AI_restaurant
├─ classes_Licenta.svg
├─ data
│  ├─ alarms
│  │  ├─ alarm.mp3
│  │  ├─ alarm.wav
│  │  └─ mixkit-digital-quick-tone-2866.wav
│  ├─ config
│  ├─ images
│  └─ videos
│     └─ vid1.mp4
├─ Dockerfile
├─ docs
│  ├─ 12Vto5V.jpg
│  ├─ 5Vto3.3Vjpg.jpg
│  ├─ Documentatie licenta etapa preliminara.pdf
│  ├─ Documentatie licenta.docx
│  ├─ Intel RealSense.jpg
│  ├─ structure-of-yolo.webp
│  ├─ WhatsApp Image 2025-05-11 at 15.37.20.jpeg
│  ├─ WhatsApp Image 2025-06-09 at 11.27.31.jpeg
│  ├─ WhatsApp Image 2025-06-09 at 11.27.32 (1).jpeg
│  ├─ WhatsApp Image 2025-06-09 at 11.27.32 (2).jpeg
│  ├─ WhatsApp Image 2025-06-09 at 11.27.32 (3).jpeg
│  ├─ WhatsApp Image 2025-06-09 at 11.27.32 (4).jpeg
│  ├─ WhatsApp Image 2025-06-09 at 11.27.32 (5).jpeg
│  └─ WhatsApp Image 2025-06-09 at 11.27.32.jpeg
├─ main.py
├─ main.spec
├─ Makefile
├─ MANIFEST.in
├─ out
│  └─ uml
├─ packages_Licenta.svg
├─ prezentare ppt
│  └─ 739e4fee-25b4-4b2d-93f0-0770b0c7bdb1.jpg
├─ pyproject.toml
├─ README.md
├─ requirements.txt
├─ scripts
│  ├─ extract_yt_video.py
│  ├─ images_to_video.py
│  ├─ test_dir.py
│  ├─ test_servos.py
│  └─ __init__.py
├─ setup.cfg
├─ src
│  ├─ detectors
│  │  ├─ yolo_detector.py
│  │  └─ __init__.py
│  ├─ gui
│  │  ├─ admin_gui.py
│  │  ├─ frames
│  │  │  ├─ calendar_selector_frame.py
│  │  │  ├─ display_frame.py
│  │  │  ├─ move_camera_frame.py
│  │  │  ├─ schedule_frame.py
│  │  │  └─ __init__.py
│  │  ├─ main_gui.py
│  │  ├─ modes
│  │  │  ├─ run_camera.py
│  │  │  ├─ run_video.py
│  │  │  └─ __init__.py
│  │  ├─ user_gui.py
│  │  └─ __init__.py
│  ├─ libs.py
│  ├─ managers
│  │  ├─ alarm_manager.py
│  │  ├─ people_manager.py
│  │  ├─ table_manager.py
│  │  ├─ table_status.py
│  │  └─ __init__.py
│  ├─ reports
│  │  ├─ automatic_report_generator.py
│  │  ├─ manual_report_generator.py
│  │  └─ __init__.py
│  ├─ utils
│  │  ├─ detection_utils.py
│  │  ├─ excel_utils.py
│  │  ├─ frame_utils.py
│  │  ├─ gui_utils.py
│  │  ├─ time_utils.py
│  │  └─ __init__.py
│  ├─ web
│  │  ├─ main_web.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ static
│  ├─ css
│  │  └─ style.css
│  └─ js
│     └─ script.js
├─ templates
│  └─ index.html
└─ __init__.py

```