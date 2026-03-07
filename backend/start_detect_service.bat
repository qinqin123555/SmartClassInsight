@echo off
echo Starting YOLOv11 Detection Service...
cd /d "%~dp0.."
py -3 python\detect_service.py
