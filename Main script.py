import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


def database_collection(response):
    #try/except statement
    print(response.status_code)

    books_per_author = len(response.json()['docs'])

    print('Total books in the \"Young Adult\" genre:', books_per_author)

    titles = []
    authors = []
    released_dates = []
    ratings = []
    subjects = []

    for num in range(books_per_author):

        book_title = response.json()['docs'][num]['title']

        if len(response.json()['docs'][num]['author_name']) == 1:
            author_name = response.json()['docs'][num]['author_name'][0]
        else:
            author_name = ','.join(response.json()['docs'][num]['author_name'])

        date_published = response.json()['docs'][num]['first_publish_year']

        ratings_average = response.json()['docs'][num]['ratings_average']

        if len(response.json()['docs'][num]['subject']) == 1:
            subject = response.json()['docs'][num]['subject'][0]
        else:
            subject = ','.join(response.json()['docs'][num]['subject'])

        titles.append(book_title)
        authors.append(author_name)
        released_dates.append(date_published)
        ratings.append(round(ratings_average,2))
        subjects.append(subject)


    all_books = {
         'title' : titles,
         'author' : authors,
         'released' : released_dates,
         'avg_rating' : ratings,
         'subjects' : subjects
        }


    df = pd.DataFrame(all_books)

    return print(df.to_string())


db_response = requests.get('https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject=young+adult&limit=10&language=eng')
database_collection(db_response)


def user_data_collection(response):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    print(user_response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    reviews = soup.find_all('tr', class_ = 'bookalike review')

    titles = []
    authors = []
    released = []
    genres = []

    for review in reviews:
        title_tag = review.find('td', class_ = 'field title')
        title_text = title_tag.find('div', class_ = 'value').get_text().strip()
        title_strip = re.sub('\n        ', ' ', title_text)
        title = re.sub(r'\s?\([a-zA-Z&,#0-9\s]+[)]', '', title_strip)
        titles.append(title)

        author_tag = review.find('td', class_ = 'field author')
        author_text = author_tag.find('div', class_ = 'value').get_text().strip()
        author_fullname = re.sub('[\n*,]', '', author_text).split()
        author = author_fullname[1] + ' ' + author_fullname[0]
        authors.append(author)

        # released_date_tag = review.find('td', class_ = 'field title')
        # released_text = released_date_tag.find('div', class_='value').get_text().strip()
        # released.append(released_text)

        book_link = title_tag.find('a', href = True)['href']
        book_response = requests.get(url = 'https://www.goodreads.com/' + book_link, headers = headers)
        book_soup = BeautifulSoup(book_response.text, 'html.parser')
        book_genres = book_soup.find_all('span', class_ = 'BookPageMetadataSection__genreButton')
        genre_list = []
        for x in book_genres:
            all_book_genres = x.find_all('span', class_ = 'Button__labelItem')
            for single_genre in all_book_genres:
                genre = single_genre.get_text()
                genre_list.append(genre)
        all_genres = ','.join(genre_list)
        genres.append(all_genres)






    return print(genres, titles, authors)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

user_response = requests.get(url = 'https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added', headers = headers)
user_data_collection(user_response)












