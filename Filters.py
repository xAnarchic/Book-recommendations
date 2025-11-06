import requests
import math
import pandas as pd



def book_database_urls(genres_of_interest):

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


        main_url = f'https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject={genres_of_interest}&limit={limit}&offset={offset}&language=eng'

        created_urls.append(main_url)

    return created_urls



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




def user_profile_filter(above_average_df, url_genres):

    series_list = []

    for i, v in enumerate(above_average_df['subjects']):
        check = all(x in v.lower() for x in url_genres)

        if check:
            series_list.append(above_average_df.iloc[i])

    if series_list is [] or series_list == []:
        print('The combination of genres you are interested in could not be found in any books you have read previously. As a result, your recommendations will be based on your entire book history.')
        return above_average_df

    else:

        filtered_user_df = pd.concat(series_list, axis=1).transpose()
        return filtered_user_df


#function that accepts a list of dataframes and merges them

def dataframe_merging(dataframes):    #This is a filtering function; so it needs to be moved to the new filtering file

    num_of_pages = len(dataframes)

    if num_of_pages > 1:

        merged = dataframes[0].merge(how='outer', right=dataframes[1])
        page_counter = 1
        while num_of_pages > page_counter + 1:
            page_counter += 1
            merged = merged.merge(how='outer', right=dataframes[page_counter])

    else:
        merged = dataframes[0]


    return merged

