import time
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from parse_weather_text import parse_weather_text as extract_weather_json
from variables import (baseUrl, search_container_class, css_selector, 
                       extract_temperature_description, extract_city_name, 
                       extract_current_temperature, extract_more_details, 
                       extract_temperature_value, current_mobile_padding, 
                       input_tag, first_list_element, main_list_element, date_and_time)

load_dotenv()

app = FastAPI()

def setup_driver():
    """Setup and return a headless Chrome WebDriver instance."""
    options = Options()
    options.headless = True  # Enables headless mode
    options.add_argument("--headless=new")  # Ensures headless mode for newer versions
    options.add_argument("--disable-gpu")  # Required for headless mode in some environments
    options.add_argument("--disable-extensions")  # Disables extensions
    options.add_argument("--disable-dev-shm-usage")  # Overcomes limited resources in containerized environments
    options.add_argument("--no-sandbox")  # Required for some environments (e.g., Docker)
    driver = webdriver.Chrome(options=options)
    return driver

async def extract_temperature_with_city(city):
    """Extracts basic temperature info by searching with city name using Selenium."""
    data = {}
    if city:
        driver = setup_driver()
        try:
            driver.get(baseUrl)
            driver.maximize_window()

            search_container = driver.find_element(
                By.CLASS_NAME, search_container_class)

            search_input = search_container.find_element(By.TAG_NAME, input_tag)
            search_input.send_keys(city)

            search_input.send_keys(Keys.RETURN)

            time.sleep(3)

            search_list = search_container.find_element(
                By.TAG_NAME, main_list_element)

            first_list_item = search_list.find_element(
                By.XPATH, first_list_element)  # Xpath for the first <li>

            # Click on the first <li> element
            first_list_item.click()

            time.sleep(2)

            get_data = driver.find_elements(By.CSS_SELECTOR, css_selector)

            if get_data:
                get_data = get_data[0].find_element(
                    By.CLASS_NAME, current_mobile_padding)
            
            date_time = get_data.find_element(By.CLASS_NAME,date_and_time).text

            city = get_data.find_element(By.TAG_NAME, extract_city_name).text

            temperature = get_data.find_element(
                By.CLASS_NAME, extract_current_temperature)
            temperature = temperature.find_element(
                By.CLASS_NAME, extract_temperature_value).text

            temp_description = get_data.find_element(
                By.CLASS_NAME, extract_temperature_description).text

            more_details = get_data.find_element(
                By.TAG_NAME, extract_more_details).text

            raw_weather_text = date_time+"\n"+city + "\n" + temperature + "\n" + temp_description + "\n" + more_details
            data = extract_weather_json(weather_text=raw_weather_text)
        finally:
            driver.quit()

    return data

class Temperature(BaseModel):
    """Schema Model for Temperature API"""
    city: str = None

@app.post("/api/temperature")
async def extract_temperature(temperature: Temperature):
    """Extracts Temperature"""
    try:
        city = temperature.city
        if not city:
            raise HTTPException(detail="Provide city to get temperature data", status_code=400)
        
        # Use asyncio.to_thread to run the synchronous scraping code in a separate thread
        data = await asyncio.to_thread(extract_temperature_with_city, city)
        
        return JSONResponse(content=data, status_code=200)
    
    except HTTPException as e:
        return JSONResponse(content={"data": {}, "error": str(e)}, status_code=400)

@app.get("/api/health")
async def get_health():
    """Get Health Status"""
    return {"status": "Ok"}

@app.get("/")
async def home():
    """Default API"""
    return {"message": "Welcome to weattemp"}