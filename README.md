Scraper de Empresas y Correos Electrónicos

Este script permite extraer nombres de empresas desde la web de Labelexpo Europe o desde un archivo local, obtener sus dominios y buscar correos electrónicos asociados usando la API de Snov.io.

Requisitos de Instalación

Antes de ejecutar el script, instala los siguientes paquetes de Python. Puedes hacerlo manualmente o usando el archivo requirements.txt:

pip install -r requirements.txt

Contenido de requirements.txt:

os
requests
csv
time
json
random
selenium
dotenv

Configuración de Snov.io

Para utilizar la API de Snov.io, debes configurar tus credenciales:

Obtén tu CLIENT_ID y CLIENT_SECRET desde tu cuenta de Snov.io.

Configura las variables de entorno o edita el script para incluirlas manualmente.

Opcionalmente, puedes definirlas en un archivo .env en el mismo directorio que el script:

SNOVIO_CLIENT_ID=tu_client_id
SNOVIO_CLIENT_SECRET=tu_client_secret

Uso del Script

Ejecutar con un archivo de empresas:

Crea un archivo empresas.txt con una empresa por línea.

Ejecuta el script:

python3 snovio_scraper.py

Extraer empresas de Labelexpo Europe:

Modifica el script para usar extract_companies_from_labelexpo() en lugar de read_companies_from_file().

Ejecuta el script normalmente.

Salida

El script genera un archivo empresas_info.csv con los siguientes campos:

Nombre de la empresa

Dominio web estimado

Correos electrónicos encontrados

Notas Adicionales

Asegúrate de tener instalado el driver de Selenium para tu navegador (ChromeDriver, GeckoDriver, etc.).

Si usas Selenium, es posible que necesites modificar la configuración según tu sistema operativo y navegador.
