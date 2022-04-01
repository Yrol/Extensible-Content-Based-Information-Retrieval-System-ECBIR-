# Extensible-Content-Based-Information-Retrieval-System-ECBIR-
Extensible Content Based Information Retrieval System (ECBIR) which enable the users to retrieve information of images by comparing features of the query images. The query images will be submitted to a backend interface via an Android based mobile device. The knowledge base of the system can be extended through both backend and front-end portals. 
 
The backend was developed using Python to run on a Tornado web server, this will increase its scalability as well as multiple request handling capability. Image processing and clustering algorithms including **SURF**, **SIFT**, **KNN** and **K-Means** were used for the core functionality of feature comparison.


### Launching the backend server
 Execute the follwoing command within the `Cloud_Python` project directory.
 ```
 python webserver.py
 ```
