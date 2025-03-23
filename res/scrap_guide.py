import bs4
from urllib.request import urlopen
import requests
import os

base_url = "https://coc.guide"
url = "https://coc.guide/resource"
# url = "https://coc.guide/defense"
# url = "https://coc.guide/trap"
# url = "https://coc.guide/other"
# url = "https://coc.guide/troop"
# url = "https://coc.guide/spell"


response = urlopen(url)
html = response.read().decode('utf-8')

def scrap_spell_troop():
    soup = bs4.BeautifulSoup(html, "html.parser")

    doc_title = soup.find('h1').text.lower()

    if (os.path.exists(doc_title) is False):
        os.makedirs(doc_title)

    grid = soup.find('div', class_='items')

    for item in grid.children:
        if isinstance(item, bs4.element.Tag):
            item_name = item.text.lower().replace(' ', '_')
            item_source = item.find('a')['href']
            item_image = item.find('img')['src']

            headers = {
                "Referer": "https://coc.guide/resource",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
            }

            image = requests.get(base_url + item_image, headers=headers)
            with open(f'{doc_title}/{item_name}.png', 'wb') as file:
                file.write(image.content)


def scrap_guide():
    soup = bs4.BeautifulSoup(html, "html.parser")

    doc_title = soup.find('h1').text.lower()

    if (os.path.exists(doc_title) is False):
        os.makedirs(doc_title)
    
    if (os.path.exists(f'{doc_title}/images') is False):
        os.makedirs(f'{doc_title}/images')

    grid = soup.find('div', class_='items')

    for item in grid.children:
        if isinstance(item, bs4.element.Tag):
            item_name = item.text.lower().replace(' ', '_')
            item_source = item.find('a')['href']
            item_image = item.find('img')['src']

            if not os.path.exists(f'{doc_title}/images/{item_name}'):
                os.makedirs(f'{doc_title}/images/{item_name}')

            headers = {
                "Referer": "https://coc.guide/resource",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
            }

            # use selenium to scrap table
            item_response = requests.get(base_url + item_source, headers=headers)
            

            item_soup = bs4.BeautifulSoup(item_response.text, "html.parser")

            image_grid = item_soup.find('div', class_='image-levels')
            
            for image in image_grid.children:
                if isinstance(image, bs4.element.Tag):
                    image_name = image.text.lower().replace(' ', '_')
                    image_url = image.find('img')['src']

                    image_response = requests.get(base_url + image_url, headers=headers)
                    with open(f'{doc_title}/images/{item_name}/{image_name}.png', 'wb') as file:
                        file.write(image_response.content)


if __name__ == "__main__":
    scrap_guide()
