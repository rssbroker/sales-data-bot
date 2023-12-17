from bs4 import BeautifulSoup
import json
import main
import os
import requests


def get_data_from_website(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the table with the specified ID
    table = soup.find('table-scrollable', {'id': 'search-results'})
    records = []
    # Check if the table is found
    if table:
        # Find all rows in the table body

        rows = table.find('tbody').find_all('tr')

        # Iterate through rows and extract data
        for row in rows:
            record = {}
            columns = row.find_all('td')
            # Extracting data from each column

            record['domain'] = columns[0].find('a').get('href')
            record['price'] = columns[1].text.replace(' USD', '')
            record['date'] = columns[2].text
            record['venue'] = columns[3].text

            # Print or store the extracted data as needed
            records.append(record)

    return records


def set_database_records():
    scraper_api_url = 'https://flask.therssbroker.repl.co/get_url'
    data = {'email': os.environ["NAMEBIO_EMAIL"],
           'password': os.environ["NAMEBIO_PASSWORD"],
           'website_url': "https://namebio.com"}

    response = requests.post(scraper_api_url, json=data)
    response_data = json.loads(response.text)
    received_url = response_data.get('received_url')
    
    records_list = get_data_from_website(received_url)
    main.r.delete('records_data')
    for record in records_list:
        # Convert the dictionary to a JSON string
        json_data = json.dumps(record)
    # Use RPUSH to push the JSON string to the end of a list
        main.r.rpush('records_data', json_data)
