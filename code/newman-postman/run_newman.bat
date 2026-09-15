@echo off
chcp 65001 >nul
title Newman 定时执行
echo ============================================
echo  Newman 批量执行 + 日志落盘
echo ============================================

:: 1. 切换到脚本所在目录（把本脚本与 collection 放同一目录即可）
cd /d "%~dp0"
echo [1] 当前目录: %cd%

:: 2. 列出将执行的 collection
echo [2] 发现 collection:
dir /b "*.postman_collection.json"

:: 3. 逐个执行并追加日志（文件名带日期，便于每天区分）
set LOG=newman_run_%date:~0,4%%date:~5,2%%date:~8,2%.log
echo ====================== %date% %time% ====================== >> "%LOG%"
for %%f in (*.postman_collection.json) do (
    echo [3] 执行: %%f
    newman run "%%f" >> "%LOG%" 2>&1
    echo [3] %%f 退出码: %errorlevel%
)

:: 4. 停留片刻便于查看（计划任务场景可删除）
echo.
echo 完成，日志见 %LOG%
timeout /t 5 /nobreak >nul
