from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def scrape_contacts(target_url):
    # Configure Chrome in headless mode with user-agent
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(target_url)
        time.sleep(3)  # Let JS load
        soup = BeautifulSoup(driver.page_source, 'lxml')
        text = soup.get_text()
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        phones = re.findall(r'\+?\d[\d\s\-\(\)]{9,15}', text)
        emails = list(set(emails))
        phones = list(set(phones))
        return {"emails": emails, "phones": phones}
    finally:
        driver.quit()

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided."}), 400
    try:
        result = scrape_contacts(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 