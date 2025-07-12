from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import os

app = Flask(__name__)

# Configure CORS to allow all origins and methods
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def scrape_contacts(target_url):
    try:
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Do NOT set options.binary_location - let undetected-chromedriver handle it
        driver = uc.Chrome(options=options)
        
        driver.get(target_url)
        time.sleep(3)  # Let JS load
        soup = BeautifulSoup(driver.page_source, 'lxml')
        text = soup.get_text()
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        phones = re.findall(r'\+?\d[\d\s\-\(\)]{9,15}', text)
        emails = list(set(emails))
        phones = list(set(phones))
        return {"emails": emails, "phones": phones}
    except Exception as e:
        print(f"Error in scrape_contacts: {e}")
        raise e
    finally:
        if 'driver' in locals():
            driver.quit()

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/scrape', methods=['POST', 'OPTIONS'])
def scrape():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        data = request.get_json()
        print("Received data:", data)
        url = data.get('url')
        if not url:
            print("No URL provided")
            return jsonify({"error": "No URL provided."}), 400
        try:
            result = scrape_contacts(url)
            print("Scraping result:", result)
            return jsonify(result)
        except Exception as e:
            print("Scraping error:", e)
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        print("General error in /scrape:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 