from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *

import time
import schedule
from datetime import datetime
import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

# Import the required library
from geopy.geocoders import Nominatim

import threading

# Initialize Nominatim API
geolocator = Nominatim(user_agent="MyApp")

cron_flag = True
d_time_one = '00:17'
d_time_two = '00:22'
d_action = 'DISABLE'

# FUNCTION TO START CRON JOB/SCHEDULER
def cron():
    print("Thread start")
    def do_job():
            if cron_flag:
                print("Scraping Data!!")
                data = scrape_cities()
                print(data)
            global msg
            msg = "After cron job"

    schedule.every().day.at(d_time_one).do(do_job)
    schedule.every().day.at(d_time_two).do(do_job)

    print("Job is done successfully")
    while cron_flag:
            schedule.run_pending()
            time.sleep(50)
    
    # DISABLING CRON JOB
    if not cron_flag:
         print("Cron disabled")
    print("Thread end")
cron_thread = threading.Thread(target=cron, )
cron_thread.start()

# FUNCTION TO ITIRATE OVER ALL CITIES
def scrape_cities():
        job_start_time = datetime.now()

        # DELETE BACKUP TABLE
        PropertyBkp.objects.all().delete()
        list_of_cities = ['Delhi','Lucknow', 'Pune', 'Mumbai', 'Agra', 'Ahmedabad', 'Kolkata', 'Jaipur', 'Chennai', 'Bengaluru']

        # TRANSFER PROPERTY TABLE TO PROPERTY BACKUP
        transfer_data(Property, PropertyBkp)

        # DELETE PROPERTY TABLE
        Property.objects.all().delete()

        # EXCEPTION HANDLING FOR ERROR WHILE SCRAPING
        try:
            tracker_lst = []
            tracker_response = []
            for city in list_of_cities:

                # EXCEPTION HANDLING FOR ERROR WHILE SCRAPING EACH CITY
                try:
                    scrape_for_city(city)
                
                    transfer_data(PropertyTemp, Property)

                    # SAVING THE RECORDS FOR CURRENT SCRAPING
                    tracker_lst.append(Tracker(execution_time = job_start_time
                                            ,city = city
                                            ,num_records = PropertyTemp.objects.count()))
                    tracker_response.append({'execution_time' : job_start_time
                                            ,'city' : city
                                            ,'num_records' : PropertyTemp.objects.count()})
                
                except:
                    tracker_lst.append(Tracker(execution_time = job_start_time
                                        ,city = city
                                        ,num_records = -99999))
                    tracker_response.append({'execution_time' : job_start_time
                                            ,'city' : city
                                            ,'num_records' : -99999})
                    
            # ADDING CURRENT RECORDS TO TRAKER TABLE
            Tracker.objects.bulk_create(tracker_lst)
            msg = f"Data has been scrapped successfully!! {tracker_response}"
        
        except:
            msg = "Error encountered during the scrape progress. Rolling back the data from previous execution."
            
            # TRANSFER BACKUP DATA BACK TO PROPERTY TABLE
            transfer_data(PropertyBkp, Property)
            Tracker.objects.create(execution_time = job_start_time
                                        ,city = ",".join(list_of_cities)
                                        ,num_records = -99999)
        return msg

# FUNCTION TO SCRAPE DATA FOR EACH CITY
def scrape_for_city(city_name):

    # DELETE TEMP PROPERTY TABLE
    PropertyTemp.objects.all().delete()

    # ACCESSING LATITUDE AND LONGITUDE OF CURRENT CITY
    location = geolocator.geocode(city_name)
    lat = str(location.latitude)
    lon = str(location.longitude)

    website = f"https://www.99acres.com/search/property/buy?latitude={location.latitude}&search_type=LS&longitude={location.longitude}&latlongsearchdistance=50&preference=S&area_unit=1&res_com=R"

    # ONLY USED IF CHROME DRIVER IS INSTALLED IN LOCAL ENVIRONMENT
    path = r"C:\Users\HP\Downloads\chromedriver-win64\chromedriver-win64\chromedriver"

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    driver.get(website)
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    itemTarget = 100
    items=[]

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

    time.sleep(4)

    new_height = driver.execute_script("return document.body.scrollHeight")

    last_height = new_height
    i = 1
    limit = driver.find_element("xpath", '//*[@id="app"]/div/div/div[5]/div[3]/div[3]/div[1]').text

    # FINDING NUMBER OF PAGES FOR CURRENT CITY
    ar = limit.strip().split(' ')
    limit=ar[-1]
    
    # FOR TESTING
    # limit=1

    listOfLinks=[]
    
    # VARIABLES TO STORE DATA
    g_names = []
    g_cost = []
    g_type = []
    g_area = []
    g_locality = []
    g_city = []
    g_link = []

    while i <= int(limit):
            print(f"Scraping page {i}")
            i+=1

            property_names = driver.find_elements("xpath", "//a[@class='projectTuple__projectName  projectTuple__pdWrap20 ellipsis']")
            # print(f"No of prop names {len(property_names)}")
            for property_name in property_names:
                link = property_name.get_property('href')
                listOfLinks.append(link)
            
            next_button = driver.find_element("xpath", "//*[@id='app']/div/div/div[5]/div[3]/div[3]/div[3]/a")
            next_button.click()
            time.sleep(3)
            # print(len(items))
    
    # FOR DEBUGING
    print(f"No of links fetched {len(listOfLinks)}")

    # FOR TESTING
    # if len(listOfLinks)>7:
    #     listOfLinks = listOfLinks[:7]

    for i in listOfLinks[:2]:
        time.sleep(3)
        driver.get(i)
        try:   
            ok_got_it_btn = driver.find_element("xpath", '//*[@id="app"]/div/div[3]/div/div[2]/button/span')
            ok_got_it_btn.click()
        except:
            pass
        prop_nm_loc = driver.find_element("xpath", '//*[@id="project-details"]/h1').text.split('\n')
        property_name = prop_nm_loc[0]
        property_loc = prop_nm_loc[1]

        # NAME
        print(prop_nm_loc)
        driver.execute_script('scrollBy(0,175)')
        condition = True
        property_types = []
        property_areas = []
        property_prices = []
        property_prices_elements = []

        # CHECKING FOR RIGHT ARROW
        while condition:
            types = driver.find_elements("xpath", "//span[@class='list_header_semiBold configurationCards__configBandLabel']")
            areas = driver.find_elements("xpath",'//span[@class="caption_subdued_medium configurationCards__cardAreaSubHeadingOne"]')
            prices_elements = driver.find_elements("xpath",'//span[@class="list_header_semiBold configurationCards__cardPriceHeading"]')
            
            for type in types:
                if type.text not in property_types and type.text != '':
                    property_types.append(type.text)
            
            for area in areas:
                if area.text not in property_areas and area.text != '':
                    property_areas.append(area.text)
            
            for p in prices_elements:
                price = unicodedata.normalize("NFKD", p.text.strip())
                price = price.replace("₹", "INR")
                if price not in property_prices: 
                    if price != '':
                        property_prices.append(price)
            
            try:
                right_arrow = driver.find_element("xpath", '//i[@class="iconS_Common_20 icon_arrowWhite carousel__rightArrow"]')
                right_arrow.click()
            
            except:
                condition = False

        # FOR DEBUGING
        # print(property_types)
        # print(property_areas)
        # print(property_prices)

        lst_nm = [property_name]*len(property_types)
        lst_loc = [property_loc]*len(property_types)
        lst_city = [city_name]*len(property_types)
        lst_link = [i]*len(property_types)
        
        g_names += lst_nm
        g_cost += property_prices
        g_type += property_types
        g_area += property_areas
        g_locality += lst_loc
        g_city += lst_city
        g_link += lst_link
        
        # print(i)
        # print("*"*100)

        for cnt in range(len(property_types)):
            # SAVING DATA IN TEMP TABLE
            p = PropertyTemp.objects.create(name = property_name
                        ,cost = property_prices[cnt]
                        ,type = property_types[cnt]
                        ,area = property_areas[cnt]
                        ,locality = property_loc
                        ,city = city_name
                        ,link = i)
            p.save()
            print(f"Saved {property_name} {property_types[cnt]}")
            

    driver.quit()
    print(items)
   
def fetch_logs():
    logs = Tracker.objects.all()
    tracks = []
    for log in logs:
        tracks.append({"time": log.execution_time ,"city": log.city, "num": log.num_records})
    return tracks[::-1]
     
# Create your views here.

def home(request):
    if request.method == 'POST':
        
        # GLOBAL VARIABLES
        global cron_flag
        global cron_thread
        global d_action
        global d_time_one
        global d_time_two

        # ACCESSING TIME FROM USER
        d_time_one = request.POST['time1']
        d_time_two = request.POST['time2']

        # STARTING THE THREAD
        d_action = "ENABLE"
        cron_flag = not cron_flag
        if cron_flag:
            d_action = "DISABLE"
            cron_thread.join()
            cron_thread = threading.Thread(target=cron, )
            cron_thread.start()
    
    
    print("Reloaded")
    print(cron_flag)
    
    # FETCHING THE RECORDS TABLE
    tracks = fetch_logs()
    return render(request, 'home.html', {"msg": d_action, "t1": d_time_one, "t2": d_time_two, "data": tracks})


def scrape_now(request):
    if request.method == 'POST':
        data = scrape_cities()
        # print(data)

    return redirect('/')
     

def transfer_data(SourceModel, DestinationModel):
    source_objects = SourceModel.objects.all()

    # Create a list of DestinationModel instances by converting source objects
    destination_objects = [DestinationModel(**{field.name: getattr(source_object, field.name) for field in source_object._meta.fields}) for source_object in source_objects]

    # Bulk insert the destination objects into DestinationModel
    DestinationModel.objects.bulk_create(destination_objects)
    
