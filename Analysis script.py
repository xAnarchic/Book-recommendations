"""
1) More titles than expected are appearing in the output - double check if only the top 15 books are really being taken from each set of 1000 books



"""

import math
from Mainscript import database_collection, user_data_collection, url_generator
from Filters import book_database_urls, database_dataframe_merge
from multiprocessing import Pool
import pandas as pd
import matplotlib.pyplot as plt
import re
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import seaborn as sns
import psutil


#function that accepts a list of dataframes and merges them

def dataframe_filtering(dataframes):    #This is a filtering function; so it needs to be moved to the new filtering file

    num_of_pages = len(dataframes)

    if num_of_pages > 1:

        merged = dataframes[0].merge(how='outer', right=dataframes[1])
        n = 1
        while num_of_pages > n + 1:
            n += 1
            merged = merged.merge(how='outer', right=dataframes[n])

    else:
        merged = all_page_data[0]

    clean_merged = merged[merged['avg_rating'] != 'N/A']
    ratings_vals = clean_merged['avg_rating'].values
    print(len(ratings_vals))
    average_user_rating = sum(ratings_vals) / len(ratings_vals)

    print(f'Across all of the user\'s ratings, they have given an average rating of: {average_user_rating}')

    above_average_df = clean_merged[clean_merged['avg_rating'] >= average_user_rating]


    return {'full_profile_df' : merged, 'above_average_profile_df' : above_average_df}


#function that performs some analysis using the user's book profile (above their average

def analysis(full_profile_df):

    print('Performing analysis...')

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




    user_dates = full_profile_df['released']
    prep_user_dates = user_dates.values
    prep_user_dates = [x for x in prep_user_dates if x != 'N/A']
    prep_user_dates1 = [int(x) for x in prep_user_dates]
    sns.kdeplot(prep_user_dates1, color='green', label='Normal Distribution')

    # Labels and title
    plt.xlabel('X')
    plt.ylabel('Density')
    plt.legend()
    plt.grid()
    # plt.show()

    # released_df = merged_dataframe['released'].value_counts()[:10].to_frame()
    # released_df.plot(kind = 'barh', rot = 0, figsize = (16,10))
    # plt.show()


    return

def cosine_score_computations(database_user_series):

    vectoriser = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectoriser.fit_transform(combined_book_series)
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)


    sim_list = list(enumerate(cosine_sim[-1]))
    sim_scores = sorted(sim_list, key=lambda x: x[1], reverse=True)    #Sorts list based on the cosine sim score in reverse order (descending - higher cosine scores shown first)
    #print('Top 15 book recommendations in order: \n')

    recommended_book_list = []

    for book in sim_scores:
        if book[1] < 0.999: #Condition is met provided the cosine sim score is less than 1 (ie: it's not the user profile string itself)
            idx = book[0]   #index
            book_title = merged_dataframes.loc[idx]['title']
            year_released = merged_dataframes.loc[idx]['released']
            author = merged_dataframes.loc[idx]['author']

            if not book_title in user_dataframe['title'].to_list()[:15]:
                recommended_book_info = {
                    'Title' : book_title,
                    'Release year' : year_released,
                    'Author' : author,
                    'Sim score' : book[1]
                                        }
                recommended_book_list.append(recommended_book_info)

    # for book in recommended_book_list[:15]:
    #     print(f'Book title: {book['Title']} \n Year released: {book['Release year']} \n Author : {book['Author']} \n Sim score : {book['Sim score']} \n ------------------')

    return recommended_book_list



#function that accepts a dataframe to perform some EDA with

def user_profile_string(above_average_df):

    combined_book_data = (above_average_df['title'] + ' ' + above_average_df['author'] + ' ' + above_average_df['released'] + ' ' + above_average_df['subjects']).values.tolist()
    cleaned_nested_lists = re.sub('\'', '', str(combined_book_data)[1:-1])  # remove brackets using index, remove quotation marks too
    list_separation1 = re.sub(', ', ' ', cleaned_nested_lists)
    string_of_user_profile = re.sub(',', ' ', list_separation1)
    
    """Need to search through the user dataframe to only keep books that contain the genre/s that the user also searches through the book database for (make a function for this in the "filter" file)
    Then supply this new dataframe to this function"""
    
    return string_of_user_profile


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


    url = 'https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added'

    links = [url]
    all_pages = url_generator(url, links)

    page_num = len(all_pages)

    pool = Pool(processes=page_num)
    all_page_data = pool.map(user_data_collection, all_pages) # returns a list of dataframes
    output_dataframe = dataframe_filtering(all_page_data)

    user_dataframe = output_dataframe['full_profile_df']

    analysis(user_dataframe) # performs user profile analysis

    user_combination = user_profile_string(output_dataframe['above_average_profile_df'])


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }

    all_urls = book_database_urls()
    all_top_15_recommendations = []

    all_database_dataframes = []    #dataframes from the database are stored here

    for url in all_urls:    #initial database request - checks if API is working
        print('Attempt 1...')
        database_response = books_request(url)

        n = 1

        while database_response.status_code != 200 or database_response.json()['numFound'] == 0:

            n += 1
            print(f'Attempt {n}...')
            database_response = books_request(url)


        database_dataframes_combined = database_collection(database_response)  #upon a successful request, a dataframe is created and appended to an empty list

        all_database_dataframes.append(database_dataframes_combined) #has a column created from the concatenations of other columns

    num_of_dataframes = len(all_database_dataframes)

    if num_of_dataframes > 20:

        iterations = math.ceil(num_of_dataframes / 20)

    else:

        iterations = 1

    for num in range(iterations):

        if num == iterations - 1:

            endpoint = num_of_dataframes

        else:

            endpoint = (num + 1) * 20

        print((num * 20), ':', endpoint)

        merged_dataframes = database_dataframe_merge(all_database_dataframes[(num * 20) : endpoint])   #merges all the created dataframes together
        merged_dataframes.loc[-1, 'combined_book_data'] = user_combination    #sets last value of the dataframe an index of -1, with the value as the user's filtered book profile
        combined_book_series = merged_dataframes['combined_book_data']


        #print(combined_book_series)
        # print(combined_book_series.memory_usage())
        # print(psutil.virtual_memory())
        # print(f'Free memory remaining = {psutil.virtual_memory()[1] - combined_book_series.memory_usage()}')

        all_top_15_recommendations += cosine_score_computations(combined_book_series)

        print(psutil.virtual_memory())
        #print(cosine_score_computations(combined_book_series))

        #print('Check to see if this list of books is increasing by 15 each time')
        #print([x['Title'] for x in all_top_15_recommendations])
        #data collection percentage progress / data collected message at end


        # print('check 1')
        # print(all_top_15_recommendations)
        final_top_15_books_sorted = sorted(all_top_15_recommendations, key = lambda x : x['Sim score'], reverse = True)[0:15]
        # print(final_top_15_books_sorted)
        # print('check 2')

        print('Check to see if the overall top 15 books are changing')

        for book in final_top_15_books_sorted:

            print(f'Book title: {book['Title']} \n Year released: {book['Release year']} \n Author : {book['Author']} \n Sim score : {book['Sim score']} \n ------------------')



#svmem(total=8469581824, available=665677824, percent=92.1, used=7803904000, free=665677824) with 10 urls
#663193368 with 10 urls

#svmem(total=8469581824, available=681005056, percent=92.0, used=7788576768, free=681005056) with 5 urls
#680915784 with 5 urls

#17,722,416 for 5 urls?


"""
1) Find out max memory 
2) Calculate how many urls we can use for our cosine calculations
3) Iteratively perform cosine calculations, taking X of the top cosine scores from each calculation - with the goal of having 15 recommendations by the end of this process 

4) Filter user profile for the genre/s being used to create the book database\
"""