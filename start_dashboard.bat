@echo off
title GitHub Trending Analyzer Dashboard
echo ========================================================
echo   GitHub Trending Analyzer - Web Dashboard
echo ========================================================
echo   Khoi dong server tai: http://127.0.0.1:8766/
echo   Nhan Ctrl+C de dong server khi khong dung.
echo ========================================================
python gh_trending.py --serve --port 8766
pause
