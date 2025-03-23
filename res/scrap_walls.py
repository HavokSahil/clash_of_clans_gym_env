from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

response = urlopen("https://clashofclans.fandom.com/wiki/Wall/Home_Village")
html = response.read().decode('utf-8')

def scrap_walls():
    soup = BeautifulSoup(html, "html.parser")
    wall_table = soup.find_all('table', class_='wikitable')[0]
    wall_rows = wall_table.find_all('tr')
    wall_head = wall_rows[0]
    wall_data = wall_rows[1:]

    head_names = [head.text.strip() for head in wall_head.find_all('th')]
    wall_data = [[data.text.strip() for data in row.find_all('td')] for row in wall_data]

    # convert to csv
    import csv
    with open('walls.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(head_names)
        writer.writerows(wall_data)


def scrap_wall_counts():
    soup = BeautifulSoup(html, "html.parser")
    wall_table = soup.find_all('table', class_='article-table')[0]
    wall_rows = wall_table.find_all('tr')
    wall_head = wall_rows[0]
    wall_data = wall_rows[1:]

    head_names = [[head.text.strip() for head in wall_head.find_all('th')][0]] + ['Count']
    wall_data = [[data.text.strip() for data in row.find_all('td')] for row in wall_data]
    wall_data = wall_data[0] + wall_data[2]
    wall_data = [[i+1, wall_data[i]] for i in range(len(wall_data))]

    import csv
    with open('wall_counts.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(head_names)
        writer.writerows(wall_data)

def scrap_icons():
    # Use selenium to scrap icons
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://clashofclans.fandom.com/wiki/Wall/Home_Village")
    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "html.parser")
    wall_div = soup.find_all('div', class_='flexbox-display')[0]
    wall_span = wall_div.find_all('span')
    wall_icons = set([span.find('img')['src'] for span in wall_span])

    # dump into csv
    import csv
    with open('wall_icons.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Level', 'Icon'])
        writer.writerows([[icon.split('.png')[0][-2:].lstrip('l'), icon] for icon in wall_icons])

if __name__ == '__main__':
    # scrap_walls()
    # scrap_wall_counts()
    scrap_icons()
