import os
import requests
import csv
import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
    params = {"domain": domain, "type": "all", "limit": 100}            #ESCOGE EL LIMITE DE EMAILS QUE QUIERES LISTAR POR CADA PAGINA
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"⚠️ Error al obtener emails para {domain}: {response.status_code}")
        return []
    return [email.get("email", "") for email in response.json().get("emails", [])]

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
        writer.writerow(["Empresa", "Dominio", "Correos Electrónicos"])
        writer.writerows(results)

# Proceso principal
def main():
    token = get_access_token()
    if not token:
        return
    
    companies = read_companies_from_file("empresas.txt") #PUEDES CAMBIAR EL NOMBRE DEL ARCHIVO DONDE TENAS LISTADAS TODAS LAS EMPRESAS QUE QUIERES BUSCAR
    results = []
    
    for company in companies:
        domain = company.lower().replace(" ", "") + ".com"
        emails = get_emails(domain, token)
        print(f"🏢 Empresa: {company} -> 🌐 {domain}")
        print(f"📧 Emails: {', '.join(emails) if emails else 'No encontrados'}")
        results.append([company, domain, ', '.join(emails)])
        time.sleep(random.uniform(1, 3))

    save_results_to_csv(results, "empresas_info.csv")
    print("✅ Datos guardados en empresas_info.csv")

if __name__ == "__main__":
    main()
