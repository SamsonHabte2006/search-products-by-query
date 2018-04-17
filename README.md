# search-products-by-query

The purpose of the program is first to read products.json.gz, that is located in an AWS S3 bucket. The file contains a list of products. It is in JSON format and is compressed with GZIP. For each product the following unstructured-text fields are available: title, description, and merchant. Secondly, it ingests the product data, and creates an IR system by indexing them. 


To run the program:
First make sure that the current working directory contains  InformationRetrieval.py

python InformationRetrieval.py

