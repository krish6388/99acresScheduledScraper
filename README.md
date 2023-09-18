# 99acresScheduledScraper
## Setup environment
1. Clone the repo
2. Install requirements.txt file

## TABLES USED:

### 1. Property
This table is used to store the current version of data for all cities

### 2. PropertyBkp
This table is used to store the previous version of data for all cities

### 3. PropertyTemp
This table is used to store the new data before saving it in Property table

### 4. ScraperTracker
This table is used to store the track record of all the scraping along with the timing

## DATABASE FLOW
Whenever new data is entered then the current data is saved in the PropertyBkp table and the new data is stored in the PropertyTemp table. 
After the successful execution of the above process we will save the PropertyTemp data into Property table. 
