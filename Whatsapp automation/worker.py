# worker.py
import sys
import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Robust Selectors with Fallbacks
SELECTORS = {
    "search_box": ['//div[@contenteditable="true"][@data-tab="3"]', '//label/div/div[2]'],
    "attach_btn": ['//div[@title="Attach"]', '//span[@data-icon="plus"]'],
    "file_input": ['//input[@type="file"]'],
    "send_btn": ['//span[@data-icon="send"]', '//button[@aria-label="Send"]']
}

def send_whatsapp_task(phone, message, file_path=None):
    options = uc.ChromeOptions()
    options.add_argument("--user-data-dir=C:/WhatsAppAutomation/Profile") # Persistent login
    
    driver = uc.Chrome(options=options, headless=False) # Fake-headless: keep window logic but minimize
    try:
        driver.get(f"https://web.whatsapp.com/send?phone={phone}&text={message}")
        wait = WebDriverWait(driver, 30)
        
        # 1. Wait for Send Button (Text only) or Attachment Button
        send_btn = None
        for xpath in SELECTORS["send_btn"]:
            try:
                send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                break
            except: continue
            
        if file_path:
            # 2. Handle File Attachment
            for xpath in SELECTORS["attach_btn"]:
                try:
                    driver.find_element(By.XPATH, xpath).click()
                    file_input = driver.find_element(By.XPATH, SELECTORS["file_input"][0])
                    file_input.send_keys(file_path)
                    time.sleep(2) # Wait for upload
                    # Click the final send button for media
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))).click()
                    break
                except: continue
        else:
            send_btn.click()
            
        time.sleep(5) # Cooldown to ensure delivery
        logging.info(f"Success: Message sent to {phone}")
    except Exception as e:
        logging.error(f"Failed to send to {phone}: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Task Scheduler passes arguments: python worker.py [phone] [msg] [file]
    send_whatsapp_task(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv)>3 else None)
