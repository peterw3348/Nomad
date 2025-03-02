from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

from src.api import paths

def scrape_champion_cells(url):
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())  # Auto-downloads and sets up ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    
    try:
        # Wait until the table is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "champion-cell"))
        )
        
        champion_cells = driver.find_elements(By.CLASS_NAME, "champion-cell")
        filtered_champions = []
        
        for cell in champion_cells:
            img_tag = cell.find_element(By.TAG_NAME, "img") if cell.find_elements(By.TAG_NAME, "img") else None
            img_url = process_url_to_key(img_tag.get_attribute("src") if img_tag else "")
            champion_name = cell.text.strip()
            
            # Find next td elements (win rate & pick rate)
            parent_row = cell.find_element(By.XPATH, "./parent::tr")
            td_elements = parent_row.find_elements(By.TAG_NAME, "td")
            
            winrate = td_elements[1].text.strip() if len(td_elements) > 1 else ""
            pickrate = td_elements[2].text.strip() if len(td_elements) > 2 else ""
            
            filtered_champions.append((champion_name, img_url, winrate, pickrate))
        
        df = pd.DataFrame(filtered_champions, columns=["Champion Name", "Key", "Win Rate", "Pick Rate"])
        return df
    
    finally:
        driver.quit()

def process_url_to_key(url):
    #https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/1.png
    return url.split("/")[-1].replace(".png", "")

if __name__ == "__main__":
    url = "https://www.friendsofdirtydoughnuthighmmraramwinrate.com/"
    champion_data = scrape_champion_cells(url)
    path = paths.DATA_DIR / "static" / "dd_wr.csv"
    if champion_data is not None:
        print(champion_data.head())  # Show first few rows
        champion_data.to_csv(path, index=False)
        print(f"Data saved to {path}")
