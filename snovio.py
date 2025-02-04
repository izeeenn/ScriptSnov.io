import os
import requests
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

CLIENT_ID = os.getenv("SNOVIO_CLIENT_ID", "#PON LA ID DE USUARIO DE LA API")
CLIENT_SECRET = os.getenv("SNOVIO_CLIENT_SECRET", "#PON EL SECRET DE LA API")
TOKEN_URL = "https://api.snov.io/v1/oauth/access_token"

# Obtener el access token de Snov.io
def get_access_token():
    params = {"grant_type": "client_credentials", "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    res = requests.post(TOKEN_URL, data=params)
    if res.status_code != 200:
        print(f"❌ Error: No se pudo obtener el token de acceso. Código {res.status_code}")
        return None
    return res.json().get("access_token")

# Obtener correos electrónicos asociados al dominio
def get_emails(domain, token):
    url = "https://api.snov.io/v2/domain-emails-with-info"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"domain": domain, "type": "all", "limit": 100}  # ESCOGE EL LIMITE DE EMAILS QUE QUIERES LISTAR POR CADA PAGINA
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"⚠️ Error al obtener emails para {domain}: {response.status_code}")
        return []
    return [email.get("email", "") for email in response.json().get("emails", [])]

# Función para contar los emails encontrados
def count_emails(emails):
    return len(emails)

# Leer listado de empresas desde un archivo
def read_companies_from_file(filename):
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print("❌ Error: Archivo no encontrado.")
        return []

# Extraer empresas desde Labelexpo Europe
def extract_companies_from_labelexpo():
    driver = webdriver.Chrome()
    driver.get("https://www.labelexpo-europe.com/es/lista-de-expositores?language=es")
    companies = []
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "exhibitor-list")))
        while True:
            exhibitors = driver.find_elements(By.CLASS_NAME, "exhibitor-name")
            companies.extend([exhibitor.text.strip() for exhibitor in exhibitors])
            try:
                next_button = driver.find_element(By.CLASS_NAME, "next-page")
                if "disabled" in next_button.get_attribute("class"):
                    break
                next_button.click()
                time.sleep(random.uniform(1, 3))
            except:
                break
    finally:
        driver.quit()
    return companies

# Guardar resultados en CSV
def save_results_to_csv(results, filename):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Empresa", "Dominio", "Número de Correos Electrónicos", "Correos Electrónicos"])
        writer.writerows(results)

# Guardar empresas y dominios no encontrados en TXT
def save_not_found_to_txt(not_found, filename):
    with open(filename, "w", encoding="utf-8") as file:
        for company, domain in not_found:
            file.write(f"{company} -> {domain}\n")

# Guardar los correos electrónicos encontrados en empresas.txt
def save_emails_to_txt(results, filename):
    with open(filename, "a", encoding="utf-8") as file:  # Usamos "a" para agregar al final del archivo sin sobrescribir
        for company, domain, email_count, emails in results:
            file.write(f"{company} -> {domain} -> Correos encontrados: {email_count} -> Emails: {emails}\n")

# Proceso principal
def main():
    token = get_access_token()
    if not token:
        return
    
    companies = read_companies_from_file("empresas.txt")  # PUEDES CAMBIAR EL NOMBRE DEL ARCHIVO DONDE TENAS LISTADAS TODAS LAS EMPRESAS QUE QUIERES BUSCAR
    # Lista de extensiones de dominio a buscar, incluyendo más de Europa y populares de EE.UU.
    extensions = [
        ".com", ".net", ".org", ".co", ".io", ".biz", 
        ".es", ".it", ".fr", ".de", ".nl", ".uk", ".pl", ".be", ".ch", ".at", ".se", 
        ".us", ".gov", ".edu", ".ca", ".au", ".mx", ".jp", ".in", ".br", ".ru"
    ]
    results = []
    not_found = []  # Para empresas no encontradas
    
    for company in companies:
        found = False
        for ext in extensions:
            domain = company.lower().replace(" ", "") + ext
            emails = get_emails(domain, token)
            print(f"🏢 Empresa: {company} -> 🌐 {domain}")
            email_count = count_emails(emails)
            if email_count > 0:
                print(f"📧 Emails encontrados: {email_count}")
                results.append([company, domain, email_count, ', '.join(emails)])
                found = True
                break  # Si encontramos emails, no seguimos buscando otras extensiones
            else:
                print("📧 Emails: No encontrados")
        if not found:
            not_found.append((company, domain))  # Guardamos empresa y dominio no encontrado

        time.sleep(random.uniform(1, 3))

    save_results_to_csv(results, "empresas_info.csv")
    save_not_found_to_txt(not_found, "no_encontrados.txt")
    save_emails_to_txt(results, "empresas.txt")  # Guardamos los correos encontrados en empresas.txt
    print("✅ Datos guardados en empresas_info.csv")
    print("❌ Empresas y dominios no encontrados guardados en no_encontrados.txt")
    print("📧 Correos encontrados guardados en empresas.txt")

if __name__ == "__main__":
    main()
