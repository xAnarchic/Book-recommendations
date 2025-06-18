import requests
import pandas as pd
from bs4 import BeautifulSoup as bs


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



# db_response = requests.get('https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,subject&subject=young+adult&limit=10&language=eng')
# database_collection(db_response)


def user_data_collection(response):




user_response = requests.get('https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added')
print(user_response.status_code)
user_data_collection(user_response)












