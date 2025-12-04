import math
from Mainscript import database_collection, user_data_collection, url_generator, book_database_urls, database_dataframe_merge, user_profile_filter
from multiprocessing import Pool
import pandas as pd
import re
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


#Performs some analysis using the user's book profile and returns a dataframe containing only books they rated above average.
def analysis(full_profile_df):

    print('Performing analysis...')

    clean_merged = full_profile_df[full_profile_df['avg_rating'] != 'N/A']
    ratings_vals = clean_merged['avg_rating'].values
    average_user_rating = sum(ratings_vals) / len(ratings_vals)
    above_average_df = clean_merged[clean_merged['avg_rating'] >= average_user_rating]

    print(f'Across all of the user\'s ratings, they have given an average rating of: {round(average_user_rating, 2)}')

    user_profile_authors = full_profile_df['author'].value_counts()[:3]
    top_3_authors = user_profile_authors.index.to_list()
    print(f'The user\'s top 3 authors are: {top_3_authors[0]} , {top_3_authors[1]} and {top_3_authors[2]}.')

    subjects_list = full_profile_df['subjects'].values.tolist()
    cleaned_nested_lists = re.sub('\'', '', str(subjects_list)[1:-1])   #remove brackets using index, remove quotation marks too
    list_separation = re.sub(', ', ',', cleaned_nested_lists)
    individual_subjects = list_separation.split(',')
    subject_counts = pd.Series(individual_subjects).value_counts()[:3]
    top_3_genres = subject_counts.index.to_list()
    print(f'The user\'s top 3 genres are: {top_3_genres[0]} , {top_3_genres[1]} and {top_3_genres[2]}.')

    return above_average_df


#Computes cosine score similarity between a detailed string of the user's filtered books against each individual book of the filtered book database. Returns a list of recommended books.
def cosine_score_computations(user_and_database_combination):

    vectoriser = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectoriser.fit_transform(user_and_database_combination)
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    #Converts the sim scores into an ordered list, with higher sim scores representing more highly recommended books.
    sim_list = list(enumerate(cosine_sim[-1]))
    sim_scores = sorted(sim_list, key=lambda x: x[1], reverse=True)

    recommended_book_list = []

    for book in sim_scores:

        #Condition ensures only books are shown and not the detailed user string.
        if book[1] < 0.999:
            idx = book[0]
            book_title = merged_dataframes.loc[idx]['title']
            year_released = merged_dataframes.loc[idx]['released']
            author = merged_dataframes.loc[idx]['author']

            #Prevents recommending books that are already found in the user's reading history.
            if not book_title in full_user_dataframe['title'].to_list()[:15]:
                recommended_book_info = {
                    'Title' : book_title,
                    'Release year' : year_released,
                    'Author' : author,
                    'Sim score' : book[1]
                                        }
                recommended_book_list.append(recommended_book_info)

    return recommended_book_list


#Takes the user dataframe of books rated above average and returns a single, detailed string of their information. To be used for cosine similarity score computations.
def user_profile_string(above_average_df):

    combined_book_data = (above_average_df['title'] + ' ' + above_average_df['author'] + ' ' + above_average_df['released'] + ' ' + above_average_df['subjects']).values.tolist()
    cleaned_nested_lists = re.sub('\'', '', str(combined_book_data)[1:-1])  # remove brackets using index, remove quotation marks too
    list_separation1 = re.sub(', ', ' ', cleaned_nested_lists)
    string_of_user_profile = re.sub(',', ' ', list_separation1)

    return string_of_user_profile


#A function used to make requests to a database url (API is prone to returning false information so this function call may be called multiple times in some cases).
def books_request(database_url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(
        url = database_url,
        headers = header
    )

    return response



if __name__ == '__main__':

    #Gathers user's book profile and genres of interest (which will be used to create recommendations).
    print('Please provide the url of your goodreads profile\'s first page.')
    first_page_url = input()

    print('How many genres are you interested in?')
    genre_num = int(input())

    search_genres = []

    for num in range(genre_num):
        print(f'What is genre {num + 1}?')
        genre = input().replace(' ', '+')
        search_genres.append(genre)

    genres_of_interest = '+'.join(search_genres)

    #Creates a list containing each page of the user's profile, effectively containing their entire recorded book history on the website.
    links = [first_page_url]
    all_pages = url_generator(first_page_url, links)

    page_num = len(all_pages)

    #Concurrently processes user book data, then creates a dataframe for each page of their profile.
    pool = Pool(processes=page_num)
    all_page_data = pool.map(user_data_collection, all_pages) # returns a list of dataframes

    #These dataframes are subsequently merged.
    full_user_dataframe = database_dataframe_merge(all_page_data)

    #The user's book dataframe is filtered to only contain books with an above average rating.
    above_average_user_dataframe = analysis(full_user_dataframe)

    #The user's book dataframe is filtered to also only contain their genres of interest.
    genre_filtered_df = user_profile_filter(above_average_user_dataframe, search_genres)

    #Returns a detailed string of the remaining books in the user's dataframe. This will be used to compute cosine similarity scores.
    user_combination = user_profile_string(genre_filtered_df)

    #Returns a list of each database url that contains books of the user-specified genres.
    all_urls = book_database_urls(genres_of_interest)


    all_top_15_recommendations = []

    all_database_dataframes = []

    url_num = 0

    #Initial database url request.
    for url in all_urls:

        print('Attempt 1...')
        database_response = books_request(url)

        n = 1
        while database_response.status_code != 200 or database_response.json()['numFound'] == 0:

            n += 1
            print(f'Attempt {n}...')
            database_response = books_request(url)

        url_num += 1
        number_of_books = database_response.json()['numFound']

        #Progress display for book data extraction from database url list.
        database_extraction_progress = round(( (url_num / (number_of_books/1000)) * 100), 2)

        #Avoid showing progress completion beyond 100%.
        if database_extraction_progress > 100:
            database_extraction_progress = 100

        print(f'Percentage of book data extracted from database: {database_extraction_progress}% ... \n')

        #Upon a successful request, a dataframe is created and appended to a list of dataframes.
        database_dataframe = database_collection(database_response)
        all_database_dataframes.append(database_dataframe)

    print('Book data extraction from database is complete. \n')

    #Calculates the number of loops to perform.
    num_of_dataframes = len(all_database_dataframes)

    if num_of_dataframes > 20:
        iterations = math.ceil(num_of_dataframes / 20)

    else:
        iterations = 1

    print('Computing cosine scores and making recommendations... \n')

    #Precomputes the number of dataframes to merge at a time, where the maximum is 20 dataframes for any single merge.
    for num in range(iterations):
        if num == iterations - 1:
            endpoint = num_of_dataframes

        else:
            endpoint = (num + 1) * 20


        merged_dataframes = database_dataframe_merge(all_database_dataframes[(num * 20) : endpoint])

        #Sets the last value of the dataframe to an index of -1, with the value being the detailed user string of filtered book information.
        merged_dataframes.loc[-1, 'combined_book_data'] = user_combination

        #Filters the dataframe, now containing both database and user book information, to only contain the column with combined book details as a string.
        combined_book_series = merged_dataframes['combined_book_data']

        #Add the 15 books with the highest cosine sim scores to a list.
        #Since only 15 books will be displayed to the user, there is no need to keep all 1000 books from each computation.
        #Even if the highest 15 scores originated from a single dataframe, they would all still be captured and presented to the user.
        all_top_15_recommendations += cosine_score_computations(combined_book_series)

    #Sorts the list and returns the final 15 highest cosine sim scoring books.
    final_top_15_books_sorted = sorted(all_top_15_recommendations, key = lambda x : x['Sim score'], reverse = True)[0:15]

    #These 15 books are then displayed to the user.
    for final_book in final_top_15_books_sorted:
        print(f'Book title: {final_book['Title']} \n Year released: {final_book['Release year']} \n Author : {final_book['Author']} \n Sim score : {final_book['Sim score']} \n ------------------')
