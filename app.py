import streamlit as st
import os
from db import DataBase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep

# Constants and Environment Variables
DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "./chromedriver.exe")
BRAVE_PATH = os.getenv(
    "BRAVE_BROWSER_PATH",
    "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
)
IMDB_BASE_URL = "https://www.imdb.com/"

# Streamlit home page
st.set_page_config(page_title="Capybar'App", page_icon="🦫", layout="wide")
st.title("Capybar'App")


# Functions
def init_browser():
    options = Options()
    options.binary_location = BRAVE_PATH
    options.add_argument("--incognito")
    # options.add_argument("--headless")
    service = Service(executable_path=DRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)


# DB functions
def store_series_in_db(series, genre):
    database = DataBase()
    try:
        database.create_table('series', 'title', 'year', 'rating', 'description', 'img_url', 'genre')
    except Exception as e:
        st.error("Database error: " + str(e))
        return

    for serie in series:
        database.add_row('series', **serie, genre=genre)


# Streamlit UI
def show_series():
    st.title("Trouver votre série préférée !")
    search_genre = st.text_input("Spécifiez un genre", placeholder="Action, Comedy, Drama, ...")
    num_pages = st.slider("Combien de page à prendre en compte ?", 1, 10, 1)
    search_button = st.button("Lancer la recherche")

    if search_button:
        st.write(f"Recherche des séries du genre {search_genre} sur {num_pages} pages...")
        url = IMDB_BASE_URL + f"search/title/?genres={search_genre}&title_type=tv_series&explore=genres"
        st.write(f"URL: {url}")

        browser = init_browser()
        try:
            browser.get(url)
        except Exception as e:
            st.error("Error loading page: " + str(e))
            return

        series = []

        # Navigate through pages
        for page in range(1, num_pages):
            try:
                browser.implicitly_wait(1)
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(1)
                button = browser.find_element(By.CLASS_NAME, "ipc-see-more__button")
                button.click()
                sleep(3)
            except Exception as e:
                st.error("Error navigating pages: " + str(e))
                continue

        # Scrape series from all loaded pages
        try:
            series_list = browser.find_elements(By.CLASS_NAME, "ipc-metadata-list-summary-item__tc")
            for serie in series_list:
                try:
                    # Get info about the serie
                    title = serie.find_element(By.CLASS_NAME, "ipc-title__text").text
                    year = serie.find_element(By.CLASS_NAME, "dli-title-metadata-item").text
                    rating = serie.find_element(By.CLASS_NAME, "ipc-rating-star").text
                    description = serie.find_element(By.CLASS_NAME, "ipc-html-content-inner-div").text
                    img_url = serie.find_element(By.TAG_NAME, "img").get_attribute("src")

                    series.append({
                        'title': title,
                        'year': year,
                        'rating': rating,
                        'description': description,
                        'img_url': img_url
                    })
                except Exception as e:
                    st.error("Error getting serie info: " + str(e))
                    continue
        except Exception as e:
            st.error("Error getting series: " + str(e))

        # browser.quit()

        # Store and Display the series
        store_series_in_db(series, search_genre)
        st.write(series)


show_series()
