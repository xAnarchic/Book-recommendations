from Mainscript import database_collection, user_data_collection, url_generator
from multiprocessing import Pool
import pandas as pd
import matplotlib.pyplot as plt
import re
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import seaborn as sns


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

    user_profile_authors = full_profile_df['author'].value_counts()[:3]
    print(user_profile_authors.index.to_list())

    print(full_profile_df.to_string())
    subjects_list = full_profile_df['subjects'].values.tolist()
    print(subjects_list)
    cleaned_nested_lists = re.sub('\'', '', str(subjects_list)[1:-1])   #remove brackets using index, remove quotation marks too
    list_separation = re.sub(', ', ',', cleaned_nested_lists)
    individual_subjects = list_separation.split(',')
    subjects_df = pd.Series(individual_subjects)
    print(subjects_df.to_string())



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
    plt.show()

    # released_df = merged_dataframe['released'].value_counts()[:10].to_frame()
    # released_df.plot(kind = 'barh', rot = 0, figsize = (16,10))
    # plt.show()


    #Analysis idea: most recent/ oldest book read

    return


#function that accepts a dataframe to perform some EDA with

def user_profile_string(above_average_df):

    combined_book_data = (above_average_df['title'] + ' ' + above_average_df['author'] + ' ' + above_average_df['released'] + ' ' + above_average_df['subjects']).values.tolist()
    cleaned_nested_lists = re.sub('\'', '', str(combined_book_data)[1:-1])  # remove brackets using index, remove quotation marks too
    list_separation1 = re.sub(', ', ' ', cleaned_nested_lists)
    string_of_user_profile = re.sub(',', ' ', list_separation1)

    return string_of_user_profile


if __name__ == '__main__':



    url = 'https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added'
    #https://www.goodreads.com/review/list/174990394?shelf=read
    #https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added
    links = [url]
    all_pages = url_generator(url, links)

    page_num = len(all_pages)

    pool = Pool(processes=page_num)
    all_page_data = pool.map(user_data_collection, all_pages) # returns a list of dataframes
    # print(all_page_data[0])
    # print(all_page_data[0].to_string())
    output_dataframe = dataframe_filtering(all_page_data)



    analysis(output_dataframe['above_average_profile_df']) # performs user profile analysis
    user_combination = user_profile_string(output_dataframe['above_average_profile_df'])


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
    database_response = requests.get(
        url='https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject=young+adult&limit=500&language=eng',
        headers=headers)

    database_combined_book_data = database_collection(database_response)    #dataframe of filtered book database; filtering is performed via URL adjustments
    database_combined_book_data.loc[-1, 'combined_book_data'] = user_combination    #sets last value of the dataframe an index of -1, with the value as the user's filtered book profile
    combined_book_series = database_combined_book_data['combined_book_data']

    vectoriser = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectoriser.fit_transform(combined_book_series)
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)


    sim_list = list(enumerate(cosine_sim[-1]))
    sim_scores = sorted(sim_list, key=lambda x: x[1], reverse=True)[:14]    #Sorts list based on the cosine sim score in reverse order (descending - higher cosine scores shown first)
    for book in sim_scores:
        if book[1] < 1:     #Condition is met provided the cosine sim score is less than 1 (ie: it's not the user profile string itself)
            idx = book[0]   #index
            print(database_combined_book_data.loc[idx]) #uses the index of the books with the returned cosine scores to show their details from the main database's dataframe





    #data collection percentage progress / data collected message at end