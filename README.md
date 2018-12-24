# Booking-Buddy

Booking Buddy is a trip planning solution. It allows the user to input the location of the trip, how long they are going to stay, as well as specify the number of people that are coming along. It then scrapes two of the most popular websites for finding accomodations: Airbnb, and Booking.com. 

Booking Buddy gives the best option in the price range that the user had selected before (according to our algorithm) based on the number of reviews and the rating. It also provides the user with 5 other great options based on that same algorithm.


## Instructions

In order to run the code locally one needs to have chromedriver installed. Instructions on how to do so can be found: https://sites.google.com/a/chromium.org/chromedriver/downloads 


Fruthermore, one needs to make sure that the path where the maps and graphs are saved mathces the filepath where the folder is stored locally. This modifications needs to be made in the new_webserver6.py file. For example if the directory containing the relevant code and associated directories is called "Flask_frontv5" and it's saved in home and then ubuntu and then notebooks, the saving of the map would look as follows:

```
my_map.save(outfile="/home/ubuntu/notebooks/Flask_frontv5/templates/"+ filename_path10)
```

Lastly, in order to run the code simply go to the directory where the new_webserver6.py is saved and type:

```
python3 new_webserver6.py
```

## Contributors 

* **Teona Ristova**
* **Gabriel Garcia**
* **Vladyslav Cherevkov**
* **Chris Osufsen**
