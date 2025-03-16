from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import requests

# Configuration du serveur
SERVER_URL = "http://localhost:6080"


chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

service = Service("/usr/bin/chromedriver")  
driver = webdriver.Chrome(service=service, options=chrome_options)

def login():
    driver.get(SERVER_URL)

    driver.find_element(By.XPATH, '//button[contains(text(), "Se connecter")]').click()

    
    time.sleep(1)

   
    driver.find_element(By.NAME, "username").send_keys("admin")  # Remplir le champ "username"
    driver.find_element(By.NAME, "password").send_keys("SuperSecretPass123")  # Remplir le champ "password"
    
    
    driver.find_element(By.XPATH, '//button[text()="Se connecter"]').click()

    time.sleep(3)


    cookies = driver.get_cookies()
    jwt_cookie = next((cookie["value"] for cookie in cookies if cookie["name"] == "authToken"), None)
    
    if jwt_cookie:
        print(f"[+] JWT récupéré depuis les cookies : {jwt_cookie}")
        return jwt_cookie
    else:
        print("[-] Aucun JWT trouvé dans les cookies.")
        return None

def visit_random_pages(jwt_token):
    """Simule la navigation avec le JWT."""
    PAGES_TO_VISIT = ["/", "profile?user_id=0"]
    headers = {"Authorization": f"Bearer {jwt_token}"}

    while True:
        page = random.choice(PAGES_TO_VISIT)
        response = requests.get(SERVER_URL + page, headers=headers)

        print(f"[+] Visite {page} -> Statut {response.status_code}")
        
        # Pause aléatoire pour simuler un comportement humain
        time.sleep(random.randint(5, 15))

if __name__ == "__main__":
    jwt_token = login()
    if jwt_token:
        visit_random_pages(jwt_token)
