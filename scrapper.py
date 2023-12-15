import streamlit as st
import os
import pandas as pd
from utils.db import DataBase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.firefox import GeckoDriverManager
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
    options.add_argument("--incognito")
    options.binary_location = BRAVE_PATH
    service = Service(GeckoDriverManager().install())
    # options.add_argument("--headless") # The button "See more" is not visible in headless mode
    #service = Service(executable_path=DRIVER_PATH)
    return webdriver.Firefox(service=service, options=options)


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
    st.sidebar.title("CARON Thomas")

    # Image on sidebar
    st.sidebar.image("https://www.pngall.com/wp-content/uploads/13/Capybara-PNG-Image.png", width=200)

    # Deployment link
    st.sidebar.markdown("Lien vers le déploiement: https://imdb-scrapper.streamlit.app/")

    st.sidebar.markdown("IMDB: " + IMDB_BASE_URL)

    # Describe the app
    st.write("## Description de l'application")
    st.write("""
    Cette application permet de trouver des séries sur IMDB.
    Vous pouvez choisir le genre de la série et le nombre de pages à parcourir.
    """)

    st.write(IMDB_BASE_URL)

    # Why Selenium?
    st.write("## Pourquoi Selenium ?")
    st.write("""
    Pourquoi Selenium ? Car IMDB utilise du JavaScript pour charger les séries au fur et à mesure que l'on descend sur la page.
    Il faut donc simuler un scroll pour charger toutes les séries.
    """)
    st.write("---")

    # List of genres
    genres = [
        "Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary", "Drama", "Family",
        "Fantasy", "Film-noir", "History", "Horror", "Music", "Musical", "Mystery", "News",
    ]

    # Dropdown for genre selection
    search_genre = st.selectbox("Choisissez un genre", genres)

    num_pages = st.slider("Combien de page à prendre en compte ? Une page équivaut à 50 résultats en plus !", 1, 30, 1)
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

        # Navigate through pages to load all series
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
                    # Initialize default values
                    title = 'Unknown Title'
                    year = 'Unknown Year'
                    rating = 'Unknown Rating'
                    description = 'No Description Available'
                    img_url = 'Default_Image_URL'

                    # Try to extract each field, if not found, keep the default value
                    try:
                        title = serie.find_element(By.CLASS_NAME, "ipc-title__text").text
                        title = str(title[3:])
                    except Exception:
                        pass

                    try:
                        year = serie.find_element(By.CLASS_NAME, "dli-title-metadata-item").text
                    except Exception:
                        pass

                    try:
                        rating = serie.find_element(By.CLASS_NAME, "ipc-rating-star").text
                        rating = str(rating.split(" ")[:3])
                    except Exception:
                        pass

                    try:
                        description = serie.find_element(By.CLASS_NAME, "ipc-html-content-inner-div").text
                    except Exception:
                        pass

                    try:
                        img_url = serie.find_element(By.TAG_NAME, "img").get_attribute("src")
                    except Exception:
                        pass

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

        browser.quit()

        # Store and Display the series
        store_series_in_db(series, search_genre)

        # Display the series in a table
        st.write("Tableau des séries")
        df = pd.DataFrame(series)
        st.dataframe(df)

        # Download as CSV
        st.download_button(
            label="Télécharger les résultats au format CSV",
            data=df.to_csv().encode('utf-8'),
            file_name='dataframe.csv',
            mime='text/csv',
        )


show_series()
