:: Ejecutar los scripts de creación de tablas y el api de notificacion por whastapp.
start 1.bat

:: Se espera 10sg e inicia el Microservicio BRMS simplificado
timeout /t 10 /nobreak >nul
start 2.bat

:: Se espera 10sg e inicia el Microservicio de Churn Risk Prediction
timeout /t 10 /nobreak >nul
start 3.bat

:: Se espera 20sg e inicia el simulador de precciones de churn 
timeout /t 20 /nobreak >nul
cd simulador
py simulador_churn-v2.py