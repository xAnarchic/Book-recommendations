from Mainscript import database_collection, user_data_collection, url_generator
from multiprocessing import Pool
import pandas as pd
import matplotlib.pyplot as plt
import re
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


#function that accepts a list of dataframes and merges them

def dataframe_filtering(dataframes):

    num_of_pages = len(dataframes)

    if num_of_pages > 1:

        merged = dataframes[0].merge(how='outer', right=dataframes[1])
        n = 1
        while num_of_pages > n + 1:
            n += 1
            merged = merged.merge(how='outer', right=dataframes[n])

        one_two_three_stars = merged.loc[merged['avg_rating'].isin([1, 2, 3])]
        four_five_stars = merged.loc[merged['avg_rating'].isin([4, 5])]

        dataframe_versions = {
            'full_merged' : merged,
            'lower_merged' : one_two_three_stars,
            'upper_merged' : four_five_stars
        }

        return dataframe_versions


    else:
        merged = all_page_data[0]

        return merged

#function that accepts a dataframe to perform some EDA with

def exploratory_data_analysis(merged_dataframe):

    # authors_df = merged_dataframe['author'].value_counts()[:10].to_frame()
    # authors_df.plot(kind = 'barh', rot = 0, figsize = (16,10))
    # plt.show()
    #
    #
    #
    # released_df = merged_dataframe['released'].value_counts()[:10].to_frame()
    # released_df.plot(kind = 'barh', rot = 0, figsize = (16,10))
    # plt.show()
    #
    #
    # subjects_list = merged_dataframe['subjects'].values.tolist()
    # cleaned_nested_lists = re.sub('\'', '', str(subjects_list)[1:-1])   #remove brackets using index, remove quotation marks too
    # list_separation = re.sub(', ', ',', cleaned_nested_lists)
    # individual_subjects = list_separation.split(',')
    # subjects_df = pd.Series(individual_subjects).value_counts()[:10].to_frame()
    # subjects_df.plot(kind='barh', rot = 0, figsize = (16,10))
    # plt.show()

    combined_book_data = (merged_dataframe['title'] + ' ' + merged_dataframe['author'] + ' ' + merged_dataframe['released'] + ' ' + merged_dataframe['subjects']).values.tolist()
    cleaned_nested_lists1 = re.sub('\'', '', str(combined_book_data)[1:-1])  # remove brackets using index, remove quotation marks too
    list_separation1 = re.sub(', ', ' ', cleaned_nested_lists1)
    list_separation2 = re.sub(',', ' ', list_separation1)


    #create a plot for the distribution of publish dates, making a note for the lowest book year recorded
    #if the year is recent, with a large enough sample size, may suggest an interest in recent books - otherwise, the user may not care about when the book was released (so wouldn't filter the recommendations)
    #or could suggest that most of their read books are within an X year range, or in X year, and maybe they would want to filter results down to that year



    #create a plot for the different subjects/ genres being read, look for any distinctly different ones - esp the most popular ones
    #could recommend the user to search for a certain genre/subject to be recommended based on their book profile's most popular subjects/ genres



    return list_separation2


if __name__ == '__main__':



    url = 'https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added'
    #https://www.goodreads.com/review/list/174990394?shelf=read
    #https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added
    links = [url]
    all_pages = url_generator(url, links)

    print(all_pages)

    page_num = len(all_pages)

    pool = Pool(processes=page_num)
    all_page_data = pool.map(user_data_collection, all_pages)   #list of dataframes

    output_dataframe = dataframe_filtering(all_page_data)
    upper_ratings_dataframe = output_dataframe['upper_merged']
    user_combination = exploratory_data_analysis(upper_ratings_dataframe)
    print(user_combination)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # user_response = requests.get(url = 'https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added', headers = headers)
    # user_data_collection(user_response)
    #url='https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject=young+adult&limit=100&language=eng',

    database_response = requests.get(
        url='https://openlibrary.org/search.json?fields=title,first_publish_year,author_name,ratings_average,ratings_count,subject&subject=young+adult&limit=500&language=eng',
        headers=headers)
    database_combined_book_data = database_collection(database_response)
    database_combined_book_data.loc[-1, 'combined_book_data'] = user_combination
    print(database_combined_book_data['combined_book_data'].to_string())
    #combined_book_series = database_combined_book_data['combined_book_data']

    # print(database_combined_book_data)
    # print(database_combined_book_data['combined_book_data'])

    vectoriser = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectoriser.fit_transform(database_combined_book_data['combined_book_data'])
    # tfidf_matrix_user = vectoriser.fit_transform(user_profile)

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    #print(cosine_sim)  # The 3rd item of each inner list is the similarity score each book's details shares with the user's profile

    sim_list = list(enumerate(cosine_sim[-1]))
    sim_scores = sorted(sim_list, key=lambda x: x[1], reverse=True)[:14]
    for book in sim_scores:
        if book[1] < 1:
            idx = book[0]
            # print(book)
            # print(idx)
            # print(database_combined_book_data.loc[405])
            print(database_combined_book_data.loc[idx])
    print(sim_scores)






    #data collection percentage progress / data collected message at end
    #