@echo off
cls
echo ====================================================================
echo                      EDI 944 CONVERTER APPLICATION                  
echo                             Version 2.1                            
echo ====================================================================
echo.
echo This application converts tabular EDI 944 data to EDI 944 code format.
echo Enhanced with client-specific format requirements and improved templates.
echo.
echo Please choose an option:
echo.
echo 1) Run the main application (Standard and Synapse EDI 944 conversion)
echo 2) Run the API test tool (to verify your OpenAI API key)
echo.
set /p choice=Enter your choice (1 or 2): 

echo.
if "%choice%"=="1" (
    echo Starting the main EDI 944 Converter application...
    echo This may take a moment. The application will open in your browser.
    echo.
    streamlit run app.py
) else if "%choice%"=="2" (
    echo Starting the API test tool...
    echo This may take a moment. The tool will open in your browser.
    echo.
    streamlit run test_api.py
) else (
    echo Invalid choice. Running the main application by default...
    echo.
    streamlit run app.py
)

echo.
echo If the application doesn't open automatically, please visit:
echo http://localhost:8501
echo.
pause 