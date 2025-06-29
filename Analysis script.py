from Mainscript import database_collection, user_data_collection, url_generator
from multiprocessing import Pool

if __name__ == '__main__':



    url = 'https://www.goodreads.com/review/list/174990394?shelf=read'
    #https://www.goodreads.com/review/list/174990394?shelf=read
    #https://www.goodreads.com/review/list/58617011-saeda?page=1&shelf=read&sort=date_added
    links = [url]
    all_pages = url_generator(url, links)

    print(all_pages)

    num_of_pages = len(all_pages)

    pool = Pool(processes=num_of_pages)
    all_page_data = pool.map(user_data_collection, all_pages)   #list of dataframes


    if num_of_pages > 1:

        merged = all_page_data[0].merge(how = 'outer', right = all_page_data[1])
        n = 1
        while num_of_pages > n+1:

            n += 1
            merged = merged.merge(how = 'outer', right = all_page_data[n])

        print(merged.to_string())

    else:
        print(all_page_data[0].to_string())