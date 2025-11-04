from Mainscript import database_collection
import requests
import math


def book_database_urls():

    print('How many genres are you interested in?')
    genre_num = int(input())

    url_genres = []

    for num in range(genre_num):

        print(f'What is genre {num + 1}?')
        genre = input().replace(' ', '+')
        url_genres.append(genre)

    genres_of_interest = '+'.join(url_genres)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    base_url = f'https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject={genres_of_interest}&limit=1&language=eng'

    database_response = requests.get(
        url=base_url,
    headers=headers)

    books_found = database_response.json()['numFound']

    n = 0
    while books_found == 0:
        n += 1
        database_response = requests.get(
            url=base_url,
            headers=headers)
        books_found = database_response.json()['numFound']
        print(books_found)

    total_url_num = math.ceil(books_found/1000)

    created_urls = []

    for iteration in range(total_url_num):
        limit = 1000
        url_num = iteration + 1

        if url_num == 1:
            offset = 0

        elif url_num == total_url_num:
            offset = math.floor(books_found/1000) * 1000

        else:
            offset = (url_num *1000) - 1000
        #print(f'URL number {url_num}: \n Limit = {limit} \n offset = {offset} ')

        main_url = f'https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject={genres_of_interest}&limit={limit}&offset={offset}&language=eng'

        created_urls.append(main_url)

    return created_urls  # ------------------------------Testing cosine score computation on a single dataframe of 1000 books -----------------------

def database_dataframe_merge(dataframes):

    if len(dataframes) > 1:

        merged = dataframes[0].merge(dataframes[1], how='outer')

        num = 1

        while num < len(dataframes) - 1:

            merged = merged.merge(dataframes[num + 1], how='outer')

            num += 1

        return merged

    else:

        return dataframes[0]

""""
1) Get a full dataframe for any single genre/ combination of genres
2) Implement the url builder + dataframe merging functions into the analysis script
3) Check if cosine scores are being calculated
4) Create the below "user_profile_filter" function - check if the user has read X%/ X books of a certain genre that were reviewed positively, then use these to create book recommendations for the user

"""







def user_profile_filter(user_df):




    return

if __name__ == '__main__':

    all_urls = ['https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject=fantasy&limit=1000&offset=66000&language=eng']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    database_dataframes = []

    for url in all_urls:
        print('Attempt 1...')
        database_response = requests.get(
            url = url,
            headers = headers
        )

        n = 1

        while database_response.json()['numFound'] == 0:
            n += 1
            print(f'Attempt {n}...')
            database_response = requests.get(
                url=url,
                headers=headers
            )

        database_dataframes.append(database_collection(database_response))

    print(database_dataframe_merge(database_dataframes))


"""
1) Merge the dataframes - function
2) Set a limit to the number of dataframes getting merged, so we can test to see if the cosine scores still work - temp function edit
"""



