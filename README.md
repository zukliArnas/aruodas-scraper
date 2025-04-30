#######################
Aruodas.lt Flat Scraper
#######################

This project is a web scraper for [Aruodas.lt](https://aruodas.lt), a popular real estate listings website in Lithuania. The script collects flat listings for a selected city (Vilnius, Kaunas, or Klaipėda) and extracts their URLs and details using [Playwright](https://playwright.dev/python/). The entire setup is containerized using Docker.


So actually this is upcoming future project and it is not done yet.
It supposed to collect all the flats information (now it only scprapes one page) and the apply the machine learning model to forecast flat price by given filters.


```bash
.
├── aruodas_scraper.py     # Main scraping script
├── utils.py               # Helper functions for scraping logic
├── logger_config.py       # Custom colored logger
├── locators.py            # City-specific selectors
├── entrypoint.sh          # Entrypoint script for Docker
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker build configuration
└── README.md              # This documentation
```

Instructions how to run the script:
1. Clone or download the project files and navigate to the project directory.
2. Build the Docker image:

`docker build -t aruodas-scraper .`

3. Run the container and start scraping (default city is Vilnius):

`docker run --rm -it aruodas-scraper`

4. To scrape a specific city (e.g. Kaunas, by default Vilnius is selected), pass the city name as an argument:

`docker run --rm -it aruodas-scraper --city Kaunas`

Supported cities:
   - Vilnius
   - Kaunas
   - Klaipeda

- The script prints scraping progress logs directly to the terminal.
- Data is currently scraped from **only the first page**.
- The project is a **work-in-progress** — machine learning price prediction will be added later.


Tech Stack:
- Python 3.11
- Playwright
- Docker (with `xvfb-run` for headless Chromium)