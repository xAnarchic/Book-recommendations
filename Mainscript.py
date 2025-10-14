import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns


    #Filtering needs to happen first to create the URL, which is used to create a response object that is then fed into this function to make a book database
def database_collection(response):

    if response.status_code == 200:

        books_per_author = len(response.json()['docs'])

        titles = []
        authors = []
        released_dates = []
        ratings = []
        subjects = []
        ratings_counts = []

        for num in range(books_per_author):

            try:
                book_title = response.json()['docs'][num]['title']
            except Exception as e:
                book_title = 'N/A'

            try:
                if len(response.json()['docs'][num]['author_name']) == 1:
                    author_name = response.json()['docs'][num]['author_name'][0]
                else:
                    author_name = ','.join(response.json()['docs'][num]['author_name'])
            except Exception as e:
                author_name = 'N/A'

            try:
                date_published = int(response.json()['docs'][num]['first_publish_year'])
            except Exception as e:
                date_published = 'N/A'

            try:
                ratings_average = round(response.json()['docs'][num]['ratings_average'], 2)
            except KeyError as e:
                ratings_average = 'N/A'

            try:
                ratings_count = response.json()['docs'][num]['ratings_count']
            except Exception as e:
                ratings_count = 0   #can't show vals in plot if it's a string, consider changing this back to 'N/A

            try:
                if len(response.json()['docs'][num]['subject']) == 1:
                    subject = response.json()['docs'][num]['subject'][0]
                else:
                    subject = ','.join(response.json()['docs'][num]['subject'])
            except Exception as e:
                subject = 'N/A'


            titles.append(book_title)
            authors.append(author_name)
            released_dates.append(str(date_published))
            ratings.append(ratings_average)
            subjects.append(subject)
            ratings_counts.append(ratings_count)

        all_books = {
             'title' : titles,
             'author' : authors,
             'released' : released_dates,
             'avg_rating' : ratings,
             'subjects' : subjects,
            'ratings_counts' : ratings_counts
            }


        df = pd.DataFrame(all_books)
        # print(df['ratings_counts'].value_counts())
        # ratings_count_df = df['ratings_counts'].value_counts().sort_index()[:50].to_frame()
        # ratings_count_df.plot(kind = 'barh', rot = 0, figsize = (16,10))
        # plt.show()

        df['combined_book_data'] = df['title'] + ' ' + df['author'] + ' ' + df['released'] + ' ' + df['subjects'] + ' ' + df['subjects']
        # df.loc[-1, 'combined_book_data'] = 'checking check'


        return df

    else:
        print(f'An error has occurred collecting the book database: {response.status_code}')

def user_data_collection(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    user_response = requests.get(url = url, headers = headers)

    if user_response.status_code == 200:

        soup = BeautifulSoup(user_response.text, 'html.parser')

        reviews = soup.find_all('tr', class_ = 'bookalike review')

        titles = []
        authors = []
        released = []
        genres = []
        ratings = []

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

            rating_tag = review.find('td', class_ = 'field rating')
            rating_text = rating_tag.find('span', attrs = {'class' : 'staticStars, ', 'class' : 'notranslate'}).get('title')

            rating_text_vals = {
                'it was amazing' : 5,
                'really liked it' : 4,
                'liked it' : 3,
                'it was ok' : 2,
                'did not like it' : 1
            }

            if rating_text in rating_text_vals:
                rating_num = rating_text_vals[rating_text]
                ratings.append(rating_num)
            else:
                ratings.append('N/A')


            book_link = title_tag.find('a', href = True).get('href')
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

            try:
                book_released = book_soup.find('p', attrs = {'data-testid' : 'publicationInfo'}).get_text()
                print(book_released)
                print(released.append(book_released[-4:]))
            except AttributeError:
                book_released = 'N/A'
                released.append(book_released)

        user_books = {
            'title': titles,
            'author': authors,
            'released': released,
            'avg_rating': ratings,
            'subjects': genres
        }

        df = pd.DataFrame(user_books)
        return df

    else:
        print(f'An error occurred while trying to get this page\'s information: {url}')

def url_generator(url, links):

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url=url, headers=headers)
        #print(response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        next_page = soup.find('a', class_ = 'next_page', href = True).get('href')

        next_page_link = 'https://www.goodreads.com/' + next_page
        links.append(next_page_link)

        url_generator(next_page_link, links)
    except AttributeError:
        print('All review pages from the user have been retrieved.')

    return links


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # user_response = requests.get(url = 'https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added', headers = headers)
    # user_data_collection(user_response)


    # These lines should go into the filtering file once proven to work
    database_response = requests.get(url = 'https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject=young+adult&limit=100&language=eng',
                                     headers = headers)

    print(database_collection(database_response).to_string())



    number_of_books = database_response.json()['numFound']
    limit_num = number_of_books
    new_url = f'https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject=young+adult&limit={limit_num}&language=eng'

    new_database_response = requests.get(url = new_url, headers = headers)

    print(database_collection(new_database_response).to_string())



    pass

#https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject=young+adult&language=eng




