# Imports
from textblob import TextBlob
import json
import pandas as pd
import gzip
import requests
import io
from collections import Counter
import nltk
from difflib import SequenceMatcher

def get_product_data(zip_file_url):
    """
        Read zip file and ingest data into a data frame.
        :param zip_file_url: url of the zipped json file.
        :return: data frame
    """
    r = requests.get(zip_file_url)
    with gzip.open(io.BytesIO(r.content), 'r') as json_file:
        return pd.read_json(json_file)

def get_product_data_locally(file_path):
    """
        Read local json file and ingest data into a data frame.
        :param file_path: file path of local json file.
        :return: data frame
    """
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

def get_stop_words():
    # Get default English stopwords
    stopwords = nltk.corpus.stopwords.words('english')
    return stopwords

def extract_keywords(raw_text,stop_words):
    """
    To extract key words by removing stop words from a raw text.
    :param raw_text:
    :return:  a set of key words
    """
    raw_words= TextBlob(raw_text).words
    keywords = set()
    for x in raw_words:
        if x.string.lower() not in stop_words:
            keywords.add(x.string.lower())

    return keywords

def index_products(products_df,stop_words):
    """
        Indexes keywords from a data frame that contains product details.
        :param products_df: product details
        :return: a dict of keywords and their associated set of records that contains the keyword.
    """
    index_keywords = {}
    print("Indexing products...:")
    for key, value in products_df.iterrows():
        keywords = []
        keywords= extract_keywords(value['description'], stop_words)
        for word in keywords:
            if word in index_keywords.keys():
                index_keywords[word].add(key)
            else:
                index_keywords[word] = set([key])

        keywords = extract_keywords(value['title'],stop_words)
        for word in keywords:
            if word in index_keywords.keys():
                index_keywords[word].add(key)
            else:
                index_keywords[word] = set([key])
        if value['merchant'] in index_keywords.keys():
            index_keywords[value['merchant']].add(key)
        else:
            index_keywords[value['merchant']] = set([(key)])
    print("Indexing products is done successfully.")
    return index_keywords

def search_products(query,index_keywords,stop_words):
    """
    Searches relevant products based on a query from users.
    :param query: a search query text
    :param index_keywords: a dict of keywords and their associated set of records that contains the keyword.
    :param stop_words:  a list of stop words.
    :return: a dict of product indexes and the number of appearances of the keywords of the search query text.
    """
    # parse query
    keywords = extract_keywords(query,stop_words)
    # initialise empty list
    matched_documents = []
    # Find the index of the product record that contains the keyword.
    for keyword in keywords:
        for key in index_keywords.keys():
            if get_similarity_match(keyword, key):
                matched_documents.extend(index_keywords[key])
                break
    return Counter(matched_documents)

def get_similarity_match(word1, word2, threshold = 0.70):
    """
        Checks if two words are similar.
        :param word1:  the first word
        :param word2:  the second word
        :param threshold the value to decide whether they are similar or not. Its default value is 0.70
        :return: true if they are similar, otherwise it returns false
    """
    return SequenceMatcher(None, word1.lower(), word2.lower()).ratio() > threshold

def print_search_results(query_text, result,products):
    """
        Prints search results.
    :param products  a data frame of products.
    :param query_text:  query text
    :param result: a dict of product indexes and the number of appearances of the keywords of the search query text.
    """
    print("Search result for query: "  + query_text)
    for index, count in result.most_common(10):
        print(products.loc[index]['title'])
if __name__ == '__main__':


    # Get stop words
    stop_words = get_stop_words()

    # Url of the compressed products json file stored in amazon s3
    url =  'https://s3-eu-west-1.amazonaws.com/pricesearcher-code-tests/software-engineer/products.json.gz'

    # Ingest products into a data frame.
    products = get_product_data(url)

    # Create index of products by keywords.
    indexed_products = index_products(products,stop_words)

    #  Search products
    while(True):

        query_text = input("Please enter the search query text:")
        ranked_matched_products = search_products(query_text, indexed_products,stop_words)
        print_search_results(query_text, ranked_matched_products, products)
        option = input("Do you want to continue?(y/n)")
        if 'n' in option:
            break