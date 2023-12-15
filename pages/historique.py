import streamlit as st
from utils.db import DataBase
from utils.functions import Processor

# Streamlit history page
st.title("Historique des recherches")

# Processor
processor = Processor()


# DB functions
def get_series_from_db():
    database = DataBase()
    try:
        database.create_table('series', 'title', 'year', 'rating', 'description', 'img_url', 'genre')
    except Exception as e:
        st.error("Database error: " + str(e))
        return

    return database.select_table('series')


# Streamlit UI for History
def show_history():
    st.sidebar.title("CARON Thomas")

    # Image on sidebar
    st.sidebar.image("https://www.pngall.com/wp-content/uploads/13/Capybara-PNG-Image.png", width=200)

    # CSS Styles
    css_style = """
    <style>
        .serie { display: flex; flex-direction: column; align-items: flex-start; }
        .top { display: flex; flex-direction: row; align-items: center; }
        .top-container { display: flex; flex-direction: column; align-items: flex-start; margin-left: 10px; }
        .bottom { display: flex; flex-direction: column; align-items: flex-start; }
        .serie-title { font-size: 20px; font-weight: bold; }
        .serie-info { font-size: 16px; margin-bottom: 5px; }
        .serie-description { margin-top: 10px; }
        .serie-image { width: 100px; height: auto; }
        .separator { margin-top: 20px; margin-bottom: 20px; border-bottom: 1px solid #eee; }
    </style>
    """

    series = get_series_from_db()
    if not series:
        st.markdown(css_style + "<div class='serie-info'>Aucune recherche effectuée</div>", unsafe_allow_html=True)
        return

    # Displaying each serie
    for serie in series:
        st.markdown(f"""
            <div class='serie'>
                <div class='top'>
                    <img class='serie-image' src='{serie.img_url}' alt='Serie Image'>
                    <div class='top-container'>
                        <div class='serie-title'>{serie.title}</div>
                        <div class='serie-info'><strong>Année de sortie:</strong> {serie.year}</div>
                        <div class='serie-info'><strong>Note:</strong> {serie.rating}</div>
                        <div class='serie-info'><strong>Genre:</strong> {serie.genre}</div>
                    </div>
                </div>
                <div class='bottom'>
                    <div class='serie-description'>{serie.description}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Buttons for summary and translation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Résumé", key=f"summarize_{serie.title}"):
                summary = processor.summarize_text(serie.description)
                st.write(summary)

        with col2:
            if st.button("Traduire", key=f"translate_{serie.title}"):
                translation = processor.translate_text(serie.description)
                st.write(translation)

        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

    st.markdown(css_style + "<div class='serie-info'>## Recherchez une nouvelle série</div>", unsafe_allow_html=True)
    st.markdown("<div class='serie-info'>Utilisez le menu de gauche pour rechercher une nouvelle série</div>",
                unsafe_allow_html=True)


# Call the show_history function
show_history()
