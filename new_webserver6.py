from flask import Flask, render_template, request, url_for, redirect, session
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from datetime import date

import requests
from requests import get

from math import exp #e

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas
import folium

from random import randint

import statistics


app = Flask(__name__)

Sorted_bigdata = 0
Sorted_bigdata_top = 0
Sorted_bigdata_top_6 = 0

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/price", methods=['GET', 'POST'])
def prices():
    global Sorted_bigdata
    destination_city = str(request.form['destination city'])
    check_in_month = str(request.form['check-in month'])
    check_in_day = str(request.form['check-in day'])
    check_in_year = str(request.form['check-in year'])
    check_out_month = str(request.form['check-out month'])
    check_out_day = str(request.form['check-out day'])
    check_out_year = str(request.form['check-out year'])
    no_rooms = str(request.form['number rooms'])
    group_adults = str(request.form['adults'])

    for i in range(1,10):
        if int(check_in_day) == i:
            check_in_day = '0' + check_in_day
        if int(check_in_month) == i:
            check_in_month = '0' + check_in_month
        if int(check_out_day) == i:
            check_out_day = '0' + check_out_day
        if int(check_out_month) == i:
            check_out_month = '0' + check_out_month

    #scrape of Booking.com and Airbnb.com
    page = 1
    results = {}
    check_in = check_in_year + '-' + check_in_month + '-' + check_in_day
    check_out = check_out_year + '-' + check_out_month + '-' + check_out_day

    search_data = {
    'query': destination_city,
    'checkin':check_in,
    'checkout':check_out,
    'adults': group_adults,
    'min_bedrooms': no_rooms,
    }
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
    opts.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=opts)

    def get_source(url):
        driver.get(url)
        time.sleep(2.5)
        html = driver.page_source
        lxml_parsed = BeautifulSoup(html, "lxml")
        return (lxml_parsed)

    page = 1
    results = {}
    url = '''https://www.airbnb.com/s/homes?refinement_paths%5B%5D=%2Fhomes&
checkin='''+search_data['checkin']+'''&
checkout='''+search_data['checkout']+'''&
adults='''+search_data['adults']+'''&
query='''+search_data['query']+'''&
min_bedrooms='''+search_data['min_bedrooms']+'''&
allow_override%5B%5D=&
s_tag=QTowvaiu'''
    pages = ['','&section_offset=4&items_offset=18','&section_offset=4&items_offset=36','&section_offset=4&items_offset=54','&section_offset=4&items_offset=72','&section_offset=4&items_offset=90']
    #pages = pages = ['']
    airbnb_dict = {}

    misses = 0
    page = 0
    while page < 6 and (misses < 7):
        try:
            lxml = get_source(url + pages[page])

            homes = lxml.find_all('div', attrs={'class':'_8ssblpx'})
            for home in homes:
                try:
                    try:
                        name = home.find_all('div', attrs={'class':'_2izxxhr'})[0]
                        print('name',name.text)
                        name= name.text
                        airbnb_dict[name]={}
                    except:
                        try:
                            name = home.find_all('span', attrs={'class':'_1m8bb6v'})[0]
                            print('name',name.text)
                            name= name.text
                            airbnb_dict[name]={}
                        except Exception as e:
                            print(e)
                    try:
                        price = home.find_all('span', attrs={'class':'_pd52isb'})[0]
                        print('price',price.text)
                        airbnb_dict[name]['price']=price.text
                    except:
                        try:
                            price = home.find_all('div', attrs={'class':'_61b3pa'})[0].text.split('/')[0]
                            print('price',price)
                            airbnb_dict[name]['price']=price
                        except Exception as e:
                            print(e)

                    total_reviews = home.find_all('span', attrs={'class':'_1gvnvab'})[0]
                    print('total reviews',total_reviews.text)
                    airbnb_dict[name]['total reviews']=total_reviews.text

                    score = home.find_all('span', attrs={'class':'_q27mtmr'})[0]
                    print('score',score.span.get('aria-label'))
                    airbnb_dict[name]['score']=score.span.get('aria-label')

                    #---
                    image = home.find_all('div', attrs={'class':'_1df8dftk'})[0]['style'].split('url("')[1].strip('");')
                    airbnb_dict[name]['image'] = image
                    print(image)

                    room = home.find_all('a', attrs={'class':'_1ol0z3h'})[0]['href']
                    listing_url = 'https://airbnb.com' + room
                    airbnb_dict[name]['listing url'] = listing_url
                    #---

                except Exception as e:
                    print(e)
                    print('one attribute not found')

            page += 1
        except Exception as e:
            misses += 1
            print(e)


    #-------------------------------------------------------------------------------------
    time.sleep(2)


    session = requests.session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'

    #url = 'https://www.booking.com/'
    url = 'https://www.booking.com/searchresults.html'

    offsets = ['0','50','100','150', '200']
    #offsets = ['0']

    hotel_dict = {}
    adults = int(group_adults)
    for offset in offsets:
        try:
            #'sb_travel_purpose':'leisure',
            search_data = {
                'ss': destination_city,
                'checkin_monthday': check_in_day,
                'checkin_year': check_in_year,
                'checkin_month': check_in_month,
                'checkout_monthday':check_out_day,
                'checkout_month': check_out_month,
                'checkout_year': check_out_year,
                'no_rooms': no_rooms,
                'group_adults': group_adults,
                'group_children':'0',
                'sb_travel_purpose':'leisure',
                'offset':offset
            }

            #print(search_data)
            r = requests.post(url, search_data)
            html = r.text
            #parsed_html = BeautifulSoup(html, "html.parser")
            lxml_parsed = BeautifulSoup(html, "lxml")
            print('done')

        #-------------------------------------------------------------------------------------




            #hotels = lxml_parsed.select("#hotellist_inner div.sr_item.sr_item_new")
            hotels = lxml_parsed.find_all('div', attrs={'data-et-view':' eWHJbWPNZWEHXT:5'})

            for hotel in hotels:
                try:
                    name = hotel.select_one("span.sr-hotel__name").text.strip()
                    print(name)
                    hotel_dict[name] = {}

                    try:
                        score_num = hotel.select_one("div.bui-review-score__badge").text
                        hotel_dict[name]['score_num'] = float(score_num)
                    except:
                        hotel_dict[name]['score_num'] = 'Not Available'
                    try:
                        score_total_reviews = hotel.select_one("div.bui-review-score__text").text.strip(' reviews').replace(',','')
                        hotel_dict[name]['score_total_reviews'] = int(score_total_reviews)
                    except:
                        try:
                            score_total_reviews = hotel.select_one("div.bui-review-score__text").text.strip(' reviews').replace(',','')
                            hotel_dict[name]['score_total_reviews'] = int(score_total_reviews)
                        except Exception as e:
                            print(e)

                    link = hotel.find('a', attrs={"class":"hotel_name_link url"}).get('href')
                    hotel_dict[name]['listing_url'] = 'https://www.booking.com/' + link[2:]
                    # dont forget about this one right below, might be a third one
                    #price = hotel.select_one('div.sr_gs_rack_rate_and_price')
                    #price = hotel.select_one('div.sr_gs_rackrate_total')


                    try:
                        price = hotel.select_one('b.sr_gs_price_total').text
                        hotel_dict[name]['price'] = float(price.replace('\n','').replace('$','').replace(',',''))
                    except:
                        try:
                            price = hotel.find('div', attrs={"class":" totalPrice totalPrice_no-rack-rate entire_row_clickable"}).text
                            hotel_dict[name]['price'] = float(price.split('$')[1].replace('\n','').replace(',',''))

                        except:
                            try:
                                price = hotel.find('div', attrs={"class":"price availprice no_rack_rate"})
                                hotel_dict[name]['price'] = float(price.split('$')[1].replace('\n','').replace(',',''))

                                print('here')
                            except:
                                try:
                                    price = hotel.find('div', attrs={"class":"js_rackrate_animation_anchor smart_price_style gray-icon b_bigger_tag animated"}).text
                                    hotel_dict[name]['price'] = float(price.replace('\n','').replace(',','').split('$')[1])
                                except Exception as e:
                                    hotel_dict[name]['price'] = 'Not Available'
                                    print('not found here')
                                    print(e)

                    try:
                        image = hotel.find('img', attrs={"class":"hotel_image"}).get('src')
                        hotel_dict[name]['image'] = image
                    except Exception as e:
                        print(e)

                except Exception as e:
                    print(e)
                    print('location unavailable')

        except Exception as e:
            print('likely no more pages')
            print(e)


    for i in list(hotel_dict.keys()):
        if (hotel_dict[i]['price'] == 'Not Available') or (hotel_dict[i]['score_num'] == 'Not Available'):
            del hotel_dict[i]
        else:
            b = date(int(check_out_year), int(check_out_month), int(check_out_day))
            a = date(int(check_in_year), int(check_in_month), int(check_in_day))
            delta = (b-a)
            hotel_dict[i]['price'] = hotel_dict[i]['price']/float(delta.days)
            hotel_dict[i]['price/person'] = hotel_dict[i]['price']/adults


    #----------- Airbnb Dataframe -------------------------------------------------------------------------

    airbnb_df = pd.DataFrame.from_dict(airbnb_dict, orient='index')
    airbnb_df = airbnb_df.rename(index=str, columns={"score": "rating score"})
    airbnb_df["location name"] = airbnb_df.index
    airbnb_df=airbnb_df.reset_index().drop(['index'],1)
    airbnb_df=airbnb_df.dropna()
    airbnb_df


    #----------- Booking Dataframe -------------------------------------------------------------------------

    hotel_df = pd.DataFrame.from_dict(hotel_dict, orient='index')
    #hotel_df = hotel_df.drop(['score_text'],1)
    hotel_df['price/person'] = hotel_df['price']//int(adults)
    #hotel_df.columns = ['total reviews','rating score','listing url','image','price','price/person']
    hotel_df = hotel_df.rename(index=str, columns={"listing_url":'listing url', "score_total_reviews": "total reviews","score_num": "rating score"})
    hotel_df["location name"] = hotel_df.index
    hotel_df=hotel_df.reset_index().drop(['index'],1)
    hotel_df


    # In[8]:

    #making DF cosistent and floats after,
    #get Gabe to do it before but for now just clean like this
    for i, row in airbnb_df.iterrows():
        airbnb_df.at[i, 'company'] = 'airbnb'

        if type(row.price) == str:
            airbnb_df.at[i, 'price'] = float(row.price.replace('Price','').replace('$','').replace(',',''))

        if type(row['rating score']) == str:
            score = float(row['rating score'].replace(',','').replace('Rating ','').split(' out of')[0])
            times_2 = score *2
            airbnb_df.at[i, 'rating score'] = int(times_2)

        if type(row['total reviews']) == str:
            airbnb_df.at[i, 'total reviews'] = float(row['total reviews'].replace(' reviews','').replace(',',''))
    airbnb_df['price/person'] = airbnb_df['price']/adults
    

    for i, row in hotel_df.iterrows():
        hotel_df.at[i, 'company'] = 'booking'

        if type(row['rating score']) == str:
            hotel_df.at[i, 'rating score'] = float(row['rating score'].replace(' stars','').replace(',','').replace('Rating ','').split(' out of')[0])
        if type(row['total reviews']) == str:
            hotel_df.at[i, 'total reviews'] = float(row['total reviews'].replace(' reviews','').replace(',',''))

    bigdata = airbnb_df.append(hotel_df, ignore_index=True)
    bigdata=bigdata[bigdata['total reviews']>5]

#     print('$$$$$$$$$$$$$$$$$$$$$$$')
#     print(bigdata.price.min())
#     print(bigdata.price.mean())
#     print(bigdata.price.max())
#     print('$$$$$$$$$$$$$$$$$$$$$$$')

    #booking had a lot more reviews than airbnb, so we used this statistical procedure:
    #educate the class on how amazon does it and how we do it, because its important (reddit uses this for comment rating)
    #explain why both do and why we do (amazon likely because u can see all products, also one source...)
    #based on the differences in num reviews of booking and airbnb
    #^^ get a lot more 5 stars in airbnb
    # site https://www.evanmiller.org/how-not-to-sort-by-average-rating.html
    # and really be able toe xplain it, bernouli n shit

    #also not saying tis is perfect cuz... so then we moved to another approach...
    #and as u can see by the data... chose Q to be 30 cuz...

    def stats_approach(wins, total):
        Q =30 #30 is a good benchmark
        return 5*wins/10+5*(1-(exp(-total/Q)))
    bigdata['stats approach'] = bigdata.apply(lambda x: stats_approach(x['rating score'], x['total reviews']), axis = 1)

    Sorted_bigdata = bigdata.sort_values(['stats approach'], ascending=[0])

    #-------- Cleaning up floats --------------------------------------------------
    Sorted_bigdata['stats approach'] = Sorted_bigdata['stats approach'].astype(float).round()
    Sorted_bigdata['price/person'] = Sorted_bigdata['price/person'].astype(float).round()
    #-------- Average Prices Calculations ---------------------------------------------
    bigdata_ave_price = int(Sorted_bigdata.price.mean())
    bigdata_min_price = int(Sorted_bigdata.price.min())
    bigdata_max_price = int(Sorted_bigdata.price.max())

    #------- Price/Count Graph --------------------------------------------------------
    tag1 = str(randint(1000,9999))

    plt.style.use('ggplot')

    np.random.seed(0)
    df = Sorted_bigdata

    fig, ax = plt.subplots()

    a_heights, a_bins = np.histogram(df.price)
    width = (a_bins[1] - a_bins[0])/1

    ax.bar(a_bins[:-1], a_heights, width=width, facecolor='#FA6969')
    #seaborn.despine(ax=ax, offset=10)

    fig.suptitle('Total Homes per Price Bucket (All Homes)',fontsize=12)
    ax.set_xlabel('Price')
    ax.set_ylabel('Number of homes')

    fig = ax.get_figure()
    filename_path = 'static/price-count_graph' + tag1 + '.png'
    fig.savefig(filename_path)
    fig.clear()
    filename = filename_path.replace('static/','')

    return render_template("price.html", ave_price=bigdata_ave_price, min_price=bigdata_min_price, max_price=bigdata_max_price, image=filename)

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    global Sorted_bigdata_top
    global Sorted_bigdata_top_6

    #------ Cleaning the DF based on input --------------------------------
    input_min = int(request.form['input_min'])
    input_max = int(request.form['input_max'])
#     print("!!!!!!!!!!!!!!!")
#     print(input_min)
#     print(input_max)
#     print("!!!!!!!!!!!!!!!")
#     Sorted_bigdata_top = Sorted_bigdata[Sorted_bigdata['price'] > input_min]
#     Sorted_bigdata_top = Sorted_bigdata[Sorted_bigdata['price'] < input_max]
    Sorted_bigdata_top = Sorted_bigdata[Sorted_bigdata.price.between(input_min, input_max, inclusive=True)]
    Sorted_bigdata_top_6 = Sorted_bigdata_top.head(6) # top 6 choices


#     print("!!!!!!!!!!!!!!!")
#     print(Sorted_bigdata_top_6)
#     print("!!!!!!!!!!!!!!!")

    #------- Airbnb vs Booking comparison ----------------------------------------
    tag2 = str(randint(1000,9999))

    plt.style.use('ggplot')

    # Make it interactive with any matplotlib widgets

    np.random.seed(0)
    df = Sorted_bigdata_top
    df_airbnb = df[df['company'] == 'airbnb']
    df_booking = df[df['company'] == 'booking']

    fig, ax = plt.subplots()

    a_heights, a_bins = np.histogram(df_airbnb.price)
    b_heights, b_bins = np.histogram(df_booking.price)

    width = (a_bins[1] - a_bins[0])/3.5
    ax.bar(a_bins[:-1], a_heights, width=width, facecolor='#FA6969',label='Airbnb')
    ax.bar(b_bins[:-1]+width, b_heights, width=width, facecolor='#267BFC',label='Booking')

    fig.suptitle('Total Homes per Price Bucket (by Company)',fontsize=12)
    ax.set_xlabel('Price')
    ax.set_ylabel('Number of homes')
    ax.legend(['Airbnb','Booking.com'],fontsize=10)

    filename_path2 = 'static/airbnb_vs_booking_graph' + tag2 + '.png'
    fig.savefig(filename_path2)
    fig.clear()
    filename2 =filename_path2.replace('static/','')

    #----------- Price/Rating Analysis-------------------------------------------------------------
    tag3 = str(randint(1000,9999))

    minrate = float(Sorted_bigdata_top['rating score'].min())
    maxrate = float(Sorted_bigdata_top['rating score'].max())

    #creating bins based on price and rating
    bins = []
    bin_num = 5
    bin_num_float = 5.0
    step = ((maxrate - minrate)/bin_num_float)
    for i in range(bin_num):
        bins.append(minrate)
        minrate+= step
    bins.append(maxrate)

    bin_dict={}
    for i in bins:
        bin_dict[i] = []
    for col, row in Sorted_bigdata_top.iterrows():
        row_bin = min(bins, key=lambda x:abs(x-row['rating score']))
        bin_dict[row_bin].append(row['price'])
    for i in bin_dict:
        bin_dict[i]=np.mean((bin_dict[i]))

    bin_prices =[]
    bin_ratings = []
    for i in bin_dict:
        round(i, 2) #ROUNDING error around here
        bin_ratings.append(i)
        bin_prices.append(bin_dict[i])
    bin_prices.sort()
    bin_ratings.sort()


    final_dict = {'price':bin_prices, 'rating':bin_ratings}
    price_rating_df = pd.DataFrame.from_dict(final_dict)

    #make it say average rating
    ax = price_rating_df.plot.bar(x='rating', y='price', rot=0, facecolor='#267BFC')


    ax.set_title('Average Price by Rating Score',fontsize=12)
    ax.set_xlabel('Rating Score of Home')
    ax.set_ylabel('Price')
    ax.get_legend().remove()


    fig = ax.get_figure()

    filename_path3 = 'static/price-rating' + tag3 + '.png'
    fig.savefig(filename_path3)
    fig.clear()
    filename3 = filename_path3.replace('static/','')
    #----------------------------------------------------------------------------------------------



    tag4 = str(randint(1000,9999))


    marginal_dict = {'price':[],'rating increase':[]}
    for i in range(len(final_dict['price']) - 1):
        #print(final_dict['price'][i+1] - final_dict['price'][i])
        marginal_dict['price'].append(final_dict['price'][i+1] - final_dict['price'][i])
        marginal_dict['rating increase'].append(str(final_dict['rating'][i])[0:3] + ' to ' + str(final_dict['rating'][i+1])[0:3])

    marginal_df = pd.DataFrame.from_dict(marginal_dict)
    ax = marginal_df.plot.bar(x='rating increase', y='price', rot=0, facecolor='#FA6969')

    ax.set_title('Marginal Price Increase by Rating Increase',fontsize=12)
    ax.set_xlabel('Rating Movement')
    ax.set_ylabel('Price')
    ax.get_legend().remove()

    fig = ax.get_figure()

    filename_path4 = 'static/marginal_price-rating' + tag4 + '.png'
    fig.savefig(filename_path4)
    fig.clear()
    filename4 = filename_path4.replace('static/','')



       #----------------------------------------------------------------------------------------------


    tag5 = str(randint(1000,9999))

    fig, ax = plt.subplots()

    ax.scatter(Sorted_bigdata_top.head(6).price, Sorted_bigdata_top.head(6)['stats approach'],facecolor='red',marker='o')
    ax.scatter(Sorted_bigdata_top.iloc[6:].price, Sorted_bigdata_top.iloc[6:]['stats approach'],facecolor='#267BFC')

    ax.set_title('Out Top Picks Against Total',fontsize=12)
    ax.set_xlabel('Price')
    ax.set_ylabel('Our Rating score')
    ax.legend(['Top 6 Homes','Other Homes'],fontsize=10)

    filename_path5 = 'static/top_vs_total' + tag5 + '.png'
    fig.savefig(filename_path5)
    fig.clear()
    filename5 = filename_path5.replace('static/','')



       #----------------------------------------------------------------------------------------------

    Sorted_bigdata_html = Sorted_bigdata_top.to_html(classes = ["table", "table-striped", "table-bordered", "table-hover"])
    return render_template("dashboard.html", results = Sorted_bigdata_top_6, table=Sorted_bigdata_html, image1=filename2, image2=filename3, image3=filename4, image4=filename5)

@app.route("/more_info_1", methods=['GET', 'POST'])
def more_info_1():

    return render_template("more_info_1.html", results = Sorted_bigdata_top_6)

@app.route("/more_info_2", methods=['GET', 'POST'])
def more_info_2():

    return render_template("more_info_2.html", results = Sorted_bigdata_top_6)

@app.route("/more_info_3", methods=['GET', 'POST'])
def more_info_3():

    return render_template("more_info_3.html", results = Sorted_bigdata_top_6)

@app.route("/more_info_4", methods=['GET', 'POST'])
def more_info_4():

    return render_template("more_info_4.html", results = Sorted_bigdata_top_6)

@app.route("/more_info_5", methods=['GET', 'POST'])
def more_info_5():

    return render_template("more_info_5.html", results = Sorted_bigdata_top_6)

@app.route("/more_info_6", methods=['GET', 'POST'])
def more_info_6():

    return render_template("more_info_6.html", results = Sorted_bigdata_top_6)


@app.route("/map_2", methods=['GET', 'POST'])
def map_2():
    tag8 = str(randint(1000,9999))

    index = Sorted_bigdata_top_6['company'].iloc[[1]].index.values[0]

    if(Sorted_bigdata_top_6['company'][index] == 'booking'):
        print("BOOKING HERE")
        visit_link = Sorted_bigdata_top_6['listing url'][index].replace('#hotelTmpl','')

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK" + visit_link)
        print("VISIT LINK", type(visit_link))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        session1 = requests.session()
        r1 = session1.get(visit_link)
        print("R IS:", r1)
        lat_html = r1.content
        lat_lon = BeautifulSoup(lat_html,'lxml').find('a', attrs={"class":"map_static_zoom show_map map_static_hover jq_tooltip map_static_button_hoverstate maps-more-static-focus "}).get('style')
        subject_lat = float(lat_lon.split('center=')[1].split('&')[0].split(',')[0])
        subject_lon = float(lat_lon.split('center=')[1].split('&')[0].split(',')[1])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)


        filename_path8 = 'output_map_booking' + tag8 + '.html'


        my_map.save(outfile="/home/ubuntu/notebooks/Flask_frontv5/templates/"+ filename_path8)

        return render_template(filename_path8)

    else:

#         opts = Options()
#         opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
#         driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",options=opts)
#         #driver.set_window_position(-2000, 0)
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=opts)
        #driver.set_window_position(-2000, 0)

        def get_source(url):
            driver.get(url)
            time.sleep(2.5)
            html = driver.page_source
            lxml_parsed = BeautifulSoup(html, "lxml")
            return (lxml_parsed)

        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK", visit_link)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        lxml_parsed_listing = get_source(visit_link)
        location = str(lxml_parsed_listing.find('div', attrs = {'class':'_59m2yxn'})).split('center=')[1]
        subject_lat = float(location.split(',')[0])
        subject_lon = float(location.split(',')[1].split('&')[0])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)

        filename_path8 = 'output_map_booking' + tag8 + '.html'
        my_map.save(outfile="/home/ubuntu/notebooks/Flask_frontv5/templates/"+ filename_path8)

        return render_template(filename_path8)

@app.route("/map_3", methods=['GET', 'POST'])
def map_3():
    tag9 = str(randint(1000,9999))

    index = Sorted_bigdata_top_6['company'].iloc[[2]].index.values[0]

    if(Sorted_bigdata_top_6['company'][index] == 'booking' == 'booking'):
        print("BOOKING HERE")
        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK" + visit_link)
        print("VISIT LINK", type(visit_link))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        session2 = requests.session()
        r2 = session2.get(visit_link)
        print("R IS:", r2)
        lat_html = r2.content
        lat_lon = BeautifulSoup(lat_html,'lxml').find('a', attrs={"class":"map_static_zoom show_map map_static_hover jq_tooltip map_static_button_hoverstate maps-more-static-focus "}).get('style')
        subject_lat = float(lat_lon.split('center=')[1].split('&')[0].split(',')[0])
        subject_lon = float(lat_lon.split('center=')[1].split('&')[0].split(',')[1])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)


        filename_path8 = 'output_map_booking' + tag9 + '.html'


        my_map.save(outfile="/home/ubuntu/notebooks/Flask_frontv5/templates/"+ filename_path9)

        return render_template(filename_path9)

    else:

#         opts = Options()
#         opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
#         driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",options=opts)
#         #driver.set_window_position(-2000, 0)
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=opts)
        #driver.set_window_position(-2000, 0)

        def get_source(url):
            driver.get(url)
            time.sleep(2.5)
            html = driver.page_source
            lxml_parsed = BeautifulSoup(html, "lxml")
            return (lxml_parsed)

        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK", visit_link)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        lxml_parsed_listing = get_source(visit_link)
        location = str(lxml_parsed_listing.find('div', attrs = {'class':'_59m2yxn'})).split('center=')[1]
        subject_lat = float(location.split(',')[0])
        subject_lon = float(location.split(',')[1].split('&')[0])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)

        filename_path9 = 'output_map_booking' + tag9 + '.html'
        my_map.save(outfile="/home/ubuntu/notebooks/Flask_frontv5/templates/"+ filename_path9)

        return render_template(filename_path9)

@app.route("/map_4", methods=['GET', 'POST'])
def map_4():
    tag10 = str(randint(1000,9999))

    index = Sorted_bigdata_top_6['company'].iloc[[3]].index.values[0]

    if(Sorted_bigdata_top_6['company'][index] == 'booking' == 'booking'):
        print("BOOKING HERE")
        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK" + visit_link)
        print("VISIT LINK", type(visit_link))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        session3 = requests.session()
        r3 = session3.get(visit_link)
        print("R IS:", r3)
        lat_html = r3.content
        lat_lon = BeautifulSoup(lat_html,'lxml').find('a', attrs={"class":"map_static_zoom show_map map_static_hover jq_tooltip map_static_button_hoverstate maps-more-static-focus "}).get('style')
        subject_lat = float(lat_lon.split('center=')[1].split('&')[0].split(',')[0])
        subject_lon = float(lat_lon.split('center=')[1].split('&')[0].split(',')[1])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)


        filename_path10 = 'output_map_booking' + tag10 + '.html'


        my_map.save(outfile="/home/ubuntu/notebooks/Flask_frontv5/templates/"+ filename_path10)

        return render_template(filename_path10)

    else:

#         opts = Options()
#         opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
#         driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",options=opts)
#         #driver.set_window_position(-2000, 0)
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=opts)
        #driver.set_window_position(-2000, 0)

        def get_source(url):
            driver.get(url)
            time.sleep(2.5)
            html = driver.page_source
            lxml_parsed = BeautifulSoup(html, "lxml")
            return (lxml_parsed)

        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK", visit_link)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        lxml_parsed_listing = get_source(visit_link)
        location = str(lxml_parsed_listing.find('div', attrs = {'class':'_59m2yxn'})).split('center=')[1]
        subject_lat = float(location.split(',')[0])
        subject_lon = float(location.split(',')[1].split('&')[0])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)

        filename_path10 = 'output_map_booking' + tag10 + '.html'
        my_map.save(outfile="/home/ubuntu/notebooks/Flask_frontv5/templates/"+ filename_path10)

        return render_template(filename_path10)

@app.route("/map_5", methods=['GET', 'POST'])
def map_5():
    tag11 = str(randint(1000,9999))

    index = Sorted_bigdata_top_6['company'].iloc[[4]].index.values[0]

    if(Sorted_bigdata_top_6['company'][index] == 'booking' == 'booking'):
        print("BOOKING HERE")
        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK" + visit_link)
        print("VISIT LINK", type(visit_link))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        session4 = requests.session()
        r4 = session4.get(visit_link)
        print("R IS:", r4)
        lat_html = r4.content
        lat_lon = BeautifulSoup(lat_html,'lxml').find('a', attrs={"class":"map_static_zoom show_map map_static_hover jq_tooltip map_static_button_hoverstate maps-more-static-focus "}).get('style')
        subject_lat = float(lat_lon.split('center=')[1].split('&')[0].split(',')[0])
        subject_lon = float(lat_lon.split('center=')[1].split('&')[0].split(',')[1])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)


        filename_path11 = 'output_map_booking' + tag11 + '.html'


        my_map.save(outfile="/Users/chrisosufsen/Desktop/Booking_Buddy/templates"+ filename_path11)

        return render_template(filename_path11)

    else:

#         opts = Options()
#         opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
#         driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",options=opts)
#         #driver.set_window_position(-2000, 0)
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=opts)
        #driver.set_window_position(-2000, 0)

        def get_source(url):
            driver.get(url)
            time.sleep(2.5)
            html = driver.page_source
            lxml_parsed = BeautifulSoup(html, "lxml")
            return (lxml_parsed)

        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK", visit_link)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        lxml_parsed_listing = get_source(visit_link)
        location = str(lxml_parsed_listing.find('div', attrs = {'class':'_59m2yxn'})).split('center=')[1]
        subject_lat = float(location.split(',')[0])
        subject_lon = float(location.split(',')[1].split('&')[0])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)

        filename_path11 = 'output_map_booking' + tag11 + '.html'
        my_map.save(outfile="/home/ubuntu/notebooks/Flask_Maps/templates/"+ filename_path11)

        return render_template(filename_path11)

@app.route("/map_6", methods=['GET', 'POST'])
def map_6():
    tag12 = str(randint(1000,9999))

    index = Sorted_bigdata_top_6['company'].iloc[[0]].index.values[0]

    if(Sorted_bigdata_top_6['company'][index] == 'booking' == 'booking'):
        print("BOOKING HERE")
        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK" + visit_link)
        print("VISIT LINK", type(visit_link))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        session5 = requests.session()
        r5 = session5.get(visit_link)
        print("R IS:", r5)
        lat_html = r5.content

        lat_lon = BeautifulSoup(lat_html,'lxml').find('a', attrs={"class":"map_static_zoom show_map map_static_hover jq_tooltip map_static_button_hoverstate maps-more-static-focus "}).get('style')
        subject_lat = float(lat_lon.split('center=')[1].split('&')[0].split(',')[0])
        subject_lon = float(lat_lon.split('center=')[1].split('&')[0].split(',')[1])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)


        filename_path12 = 'output_map_booking' + tag12 + '.html'


        my_map.save(outfile="/Users/chrisosufsen/Desktop/Booking_Buddy/templates"+ filename_path12)

        return render_template(filename_path12)

    else:

#         opts = Options()
#         opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
#         driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",options=opts)
#         #driver.set_window_position(-2000, 0)
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=opts)
        #driver.set_window_position(-2000, 0)

        def get_source(url):
            driver.get(url)
            time.sleep(2.5)
            html = driver.page_source
            lxml_parsed = BeautifulSoup(html, "lxml")
            return (lxml_parsed)

        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK", visit_link)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        lxml_parsed_listing = get_source(visit_link)
        location = str(lxml_parsed_listing.find('div', attrs = {'class':'_59m2yxn'})).split('center=')[1]
        subject_lat = float(location.split(',')[0])
        subject_lon = float(location.split(',')[1].split('&')[0])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)

        filename_path12 = 'output_map_booking' + tag12 + '.html'
        my_map.save(outfile="/home/ubuntu/notebooks/Flask_Maps/templates/"+ filename_path12)

        return render_template(filename_path12)

@app.route("/map_1", methods=['GET', 'POST'])
def map_1():
    tag7 = str(randint(1000,9999))
#     if(Sorted_bigdata_top_6.head(1)['company'].item() == 'airbnb'):

#         index = Sorted_bigdata_top_6.head(1)['company'].index.values[0]

#         visit_link = Sorted_bigdata_top_6.head(1)['listing url'][index]

#         r = session.get(visit_link)
#         lat_html = r.content
#         lat_lon = BeautifulSoup(lat_html,'lxml').find('a', attrs={"class":"map_static_zoom show_map map_static_hover jq_tooltip map_static_button_hoverstate maps-more-static-focus "}).get('style')
#         subject_lat = float(lat_lon.split('center=')[1].split('&')[0].split(',')[0])
#         subject_lon = float(lat_lon.split('center=')[1].split('&')[0].split(',')[1])

#         my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
#         folium.Marker([subject_lat,subject_lon],
#                      popup=Sorted_bigdata_top_6.head(1)['location name'][index],
#                      icon=folium.Icon(color='red')
#                      ).add_to(my_map)
#         my_map.save(outfile='output_map_airbnb.html')

#         return render_template("output_map_airbnb.html")

#     else:

#         index = Sorted_bigdata_top_6.head(1)['company'].index.values[0]

#         opts = Options()
#         opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
#         driver = webdriver.Chrome(executable_path="/Users/vlad_cherevkov/chromedriver", options=opts)
#         #driver.set_window_position(-2000, 0)
#         visit_link = Sorted_bigdata_top_6.head(1)['listing url'][index]

#         lxml_parsed_listing = get_source(visit_link)
#         location = str(lxml_parsed_listing.find('div', attrs = {'class':'_1fmyluo4'})).split('center=')[1]
#         subject_lat = float(location.split(',')[0])
#         subject_lon = float(location.split(',')[1].split('&')[0])

#         my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
#         folium.Marker([subject_lat,subject_lon],
#                      popup=Sorted_bigdata_top_6.head(1)['location name'][index],
#                      icon=folium.Icon(color='red')
#                      ).add_to(my_map)

#     my_map.save(outfile='output_map_booking.html')

    index = Sorted_bigdata_top_6['company'].iloc[[5]].index.values[0]

    if(Sorted_bigdata_top_6['company'][index] == 'booking' == 'booking'):
        print("BOOKING HERE")
        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK" + visit_link)
        print("VISIT LINK", type(visit_link))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        session6 = requests.session()
        r6 = session6.get(visit_link)
        print("R IS:", r6)
        lat_html = r6.content
        lat_lon = BeautifulSoup(lat_html,'lxml').find('a', attrs={"class":"map_static_zoom show_map map_static_hover jq_tooltip map_static_button_hoverstate maps-more-static-focus "}).get('style')
        subject_lat = float(lat_lon.split('center=')[1].split('&')[0].split(',')[0])
        subject_lon = float(lat_lon.split('center=')[1].split('&')[0].split(',')[1])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)


        filename_path7 = 'output_map_booking' + tag7 + '.html'


        my_map.save(outfile="/Users/chrisosufsen/Desktop/Booking_Buddy/templates"+ filename_path7)

        return render_template(filename_path7)

    else:

#         opts = Options()
#         opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")
#         driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",options=opts)
#         #driver.set_window_position(-2000, 0)
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=opts)
        #driver.set_window_position(-2000, 0)

        def get_source(url):
            driver.get(url)
            time.sleep(2.5)
            html = driver.page_source
            lxml_parsed = BeautifulSoup(html, "lxml")
            return (lxml_parsed)

        visit_link = Sorted_bigdata_top_6['listing url'][index]

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("VISIT LINK", visit_link)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        lxml_parsed_listing = get_source(visit_link)
        location = str(lxml_parsed_listing.find('div', attrs = {'class':'_59m2yxn'})).split('center=')[1]
        subject_lat = float(location.split(',')[0])
        subject_lon = float(location.split(',')[1].split('&')[0])

        my_map=folium.Map(location=[subject_lat,subject_lon],zoom_start=15)
        folium.Marker([subject_lat,subject_lon],
                     popup=Sorted_bigdata_top_6['location name'][index],
                     icon=folium.Icon(color='red')
                     ).add_to(my_map)

        filename_path7 = 'output_map_booking' + tag7 + '.html'
        my_map.save(outfile="/home/ubuntu/notebooks/Flask_frontv5/templates/"+ filename_path7)

        return render_template(filename_path7)



app.run(host='0.0.0.0', port=5000, debug=True)
