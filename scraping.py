import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure Chrome in headless mode with user-agent
options = Options()
options.headless = True
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")

# Launch browser with WebDriver Manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Replace this with the website you want to scrape
target_url = "https://www.contactspace.com/contact-us/"  # Example page with contact info

print(f"Scraping: {target_url}")

try:
    driver.get(target_url)
    time.sleep(3)  # Let JS load

    # Parse the HTML
    soup = BeautifulSoup(driver.page_source, 'lxml')
    text = soup.get_text()

    # REGEX to extract emails and phone numbers
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phones = re.findall(r'\+?\d[\d\s\-\(\)]{9,15}', text)

    # Deduplicate
    emails = list(set(emails))
    phones = list(set(phones))

    # Output
    print("\nEmails Found:")
    for email in emails:
        print(" -", email)

    print("\nPhone Numbers Found:")
    for phone in phones:
        print(" -", phone)

    # Save to file
    with open("contacts.txt", "w") as f:
        f.write("Emails:\n" + "\n".join(emails) + "\n\n")
        f.write("Phone Numbers:\n" + "\n".join(phones))

    print("\n✅ Results saved to contacts.txt")

except Exception as e:
    print("❌ Error during scraping:", e)

finally:
    driver.quit()
