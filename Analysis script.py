from Mainscript import database_collection, user_data_collection, url_generator
from multiprocessing import Pool
from pandas import DataFrame as df
import matplotlib.pyplot as plt

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

    authors_df = merged_dataframe['author'].value_counts()[:10].to_frame()
    authors_df.plot(kind = 'barh', rot = 0, figsize = (16,10))
    plt.show()


    released_df = merged_dataframe['released'].value_counts().to_frame()
    released_df.plot(kind = 'barh', rot = 0, figsize = (16,10))
    plt.show()


    subjects_list = merged_dataframe['title', 'subjects'].values
    print(subjects_list)


    #create a plot for the distribution of publish dates, making a note for the lowest book year recorded
    #if the year is recent, with a large enough sample size, may suggest an interest in recent books - otherwise, the user may not care about when the book was released (so wouldn't filter the recommendations)
    #or could suggest that most of their read books are within an X year range, or in X year, and maybe they would want to filter results down to that year



    #create a plot for the different subjects/ genres being read, look for any distinctly different ones - esp the most popular ones
    #could recommend the user to search for a certain genre/subject to be recommended based on their book profile's most popular subjects/ genres



    return


if __name__ == '__main__':



    url = 'https://www.goodreads.com/review/list/174990394?shelf=read'
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
    exploratory_data_analysis(upper_ratings_dataframe)








    #data collection percentage progress / data collected message at end
    #