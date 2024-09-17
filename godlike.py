import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import logging
from time import sleep

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to scrape Yellow Pages
def scrape_yellowpages(city, search_term):
    driver = webdriver.Firefox()
    driver.get("https://www.yellowpages.com/")

    try:
        # Enter search term and location
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "query"))
        )
        search_box.send_keys(search_term)

        location_box = driver.find_element(By.ID, "location")
        location_box.clear()
        location_box.send_keys(city)

        # Submit the search
        search_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        search_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.result'))
        )

        # Extract data from the results
        businesses = driver.find_elements(By.CSS_SELECTOR, '.result')
        results = []
        for business in businesses:
            try:
                name = business.find_element(By.CSS_SELECTOR, '.business-name').text
                address = business.find_element(By.CSS_SELECTOR, '.street-address').text
                phone = business.find_element(By.CSS_SELECTOR, '.phones').text
                website = business.find_element(By.CSS_SELECTOR, '.links a').get_attribute('href') if business.find_elements(By.CSS_SELECTOR, '.links a') else 'N/A'
                
                results.append({
                    'Name': name,
                    'Address': address,
                    'Phone': phone,
                    'Website': website
                })
            except Exception as e:
                logging.error(f"Error extracting business details: {e}")

        return results

    except Exception as e:
        return str(e)
    finally:
        driver.quit()

# Function to scrape IndianMart
def scrape_indianmart(city, search_term):
    driver = webdriver.Firefox()
    driver.get("https://www.indiamart.com/")

    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search_string"))
        )
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.lst-clmn-rt'))
        )

        products = driver.find_elements(By.CSS_SELECTOR, '.lst-clmn-rt')
        results = []
        for product in products:
            try:
                title = product.find_element(By.CSS_SELECTOR, '.prod-name').text
                price = product.find_element(By.CSS_SELECTOR, '.price').text if product.find_elements(By.CSS_SELECTOR, '.price') else "N/A"
                
                results.append({
                    'Title': title,
                    'Price': price
                })
            except Exception as e:
                logging.error(f"Error extracting product details: {e}")

        return results

    except Exception as e:
        return str(e)
    finally:
        driver.quit()


# Streamlit UI
st.title('Multi-Site Scraper')

# Input for search term and city/location
city = st.text_input("Enter Location/City", "Delhi")
search_term = st.text_input("Enter Search Term", "Laptops")

# Dropdown to select the website to scrape
website = st.selectbox("Select Website to Scrape", ("IndianMart", "Yellow Pages"))

# Scrape button
if st.button('Scrape'):

    st.info(f"Scraping data from {website} for '{search_term}' in '{city}'...")
    
    # Show progress while scraping
    with st.spinner('Scraping in progress...'):
        if website == "IndianMart":
            data = scrape_indianmart(city, search_term)
        elif website == "Yellow Pages":
            data = scrape_yellowpages(city, search_term)

    if data:
        # Display results as a DataFrame
        df = pd.DataFrame(data)
        st.write(df)

        # Download button to save data as CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{website}_scrape_results.csv',
            mime='text/csv',
        )
    else:
        st.warning("No results found or an error occurred.")
