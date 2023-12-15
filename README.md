# Streamlit Web Application
## Overview
This project is a Streamlit-based web application designed to showcase a variety of functionalities including database management, web scraping, and language processing. 

The application provides an intuitive user interface for data interaction and processing tasks.

## Features

- Database Interaction: Utilizes SQLAlchemy for database operations, allowing for efficient data storage and retrieval.
- Web Scraping: Implements Selenium for web scraping, facilitating the collection of dynamic web content.
- Language Processing: Integrates OpenAI's language processing capabilities for tasks such as translation.

## Installation
To get started with this project, follow these steps:

```bash
git clone https://github.com/your-repository.git
cd your-repository
pip install -r requirements.txt
```

## Usage
Run the Streamlit application locally:

```bash
streamlit run app.py
```

## File Structure
- app.py: The main Streamlit application file.
- historique.py: Manages the history and display of search results.
- db.py: Contains the database operations using SQLAlchemy.
- functions.py: Includes additional functionalities like language processing.

## Dependencies
Streamlit
SQLAlchemy
Selenium
OpenAI
