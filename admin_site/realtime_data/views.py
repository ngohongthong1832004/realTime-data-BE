from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializers import *
# from undetected_chromedriver import uc
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import ssl
import datetime


import os


# craw data 
import requests
from bs4 import BeautifulSoup



class Register(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if User.objects.filter(email=request.data.get('email')).exists():
            return Response({'message': 'Email already exists'})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class Login(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        print(user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'first_name' : user.first_name,
        })
    

class Logout(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response({'message': 'Logout successful'})

        


class WeatherAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        rs = {
            "main" : {

            },
            "more" : {
                "title" : "More",
                "data" : []
            }
        }
        url = "https://www.timeanddate.com/weather/vietnam/ho-chi-minh"
        html  = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        rs["main"]["location"] = soup.find("h1", class_ = "headline-banner__title").text
        content  = soup.find("section", class_= "bk-focus")
        rs["main"]['icon'] = "https:"+content.find("img")["src"]
        rs["main"]['temp'] = content.find("div", class_= "h2").text
        rs["main"]['status'] = content.find_all("p")[0].text
        rs["main"]['wind'] = content.find_all("p")[1].text.split("Forecast")[0]
        rs["main"]["forecast"] = content.find_all("p")[1].find("span").text
        
        content  = soup.find("div", class_= "row pdflexi-b dashb")
        rs["more"]["title"] = content.find("h2").text
        table = content.find("table", id= "wt-5hr")
        tr = table.find_all("tr")    
        row = []    
    
        td = tr[0].find_all("td")
        for j in td :
            row.append(j.text)
        rs["more"]["data"].append(row)
        row = []

        td = tr[1].find_all("td")
        for j in td :
            row.append("https:"+j.find("img")["src"])
        rs["more"]["data"].append(row)
        row = []

        td = tr[2].find_all("td")
        for j in td :
            row.append(j.text)
        rs["more"]["data"].append(row)
        row = []

        return  Response({"data" : rs})
       
class FoodAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        rs  = {
            "breakfast" : [],
        }
        url = 'https://www.generatormix.com/what-to-make-for-breakfast'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            foods  = soup.find_all('div', class_='tile-block-inner')
            for i in foods :
                food = {
                    "name" : i.find('h3').text,
                    "image" : i.find('img')["data-src"]
                }
                rs["breakfast"].append(food)

        url = "https://yummly2.p.rapidapi.com/feeds/list"
        querystring = {"limit":"5","start":"0"}
        headers = {
            "X-RapidAPI-Key": "39c5cbcb03mshd365d3d3552f68ep1fa909jsn8e2ef6cdaeb1",
            "X-RapidAPI-Host": "yummly2.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        return Response({'data': response.json() if datetime.datetime.now().hour > 9 else rs})  
    
class QuotesAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        url = "https://random-quote-api3.p.rapidapi.com/"

        headers = {
            "X-RapidAPI-Key": os.environ.get('X-RapidAPI-Key'),
            "X-RapidAPI-Host": "random-quote-api3.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        return Response({'data': response.json()})
class MusicAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        rs = []
        url = "https://www.nhaccuatui.com/"
        html  = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        content  = soup.find("div", id = "top20-content")
        item = content.find_all("li")
        for i in item[:5]:
            rs.append({
                "name" : i.find("h3").text,
                "href" : i.find("a")["href"],
                "singer" : i.find("h4").text
            })

        return Response({"data" : rs})

class NewsAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        rs = {
            "hotNews" : {
                "title" : "",
                "content" : "",
                "image" : "",
                "href" : ""
            },
            "news" : []
        }
        url = "https://vnexpress.net/"
        html  = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        content  = soup.find("section", class_ = "section section_topstory")
        hotNews = content.find("article", class_ = "item-news full-thumb article-topstory")
        rs["hotNews"]["title"] = hotNews.find("h3", class_ = "title-news").text
        rs["hotNews"]["content"] = hotNews.find("p", class_ = "description").text
        rs["hotNews"]["image"] = hotNews.find("img")["src"]
        rs["hotNews"]["href"] = hotNews.find("a")["href"]

        news = content.find("ul", class_ = "list-sub-feature")
        news = news.find_all("li")
        # print(news)
        for i in news[:2]:
            # print(i.find("a")["title"])
            rs["news"].append({
                "title" : i.find("a")["title"],
                "content" : i.find("p", class_ = "description").text,
                "href" : i.find("a")["href"]
            })

        return Response({"data" : rs})

class BooksAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        rs = []
        url = "https://nhungcuonsachhay.com/trich-dan-hay/"
        html  = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        content  = soup.find("div", id = "tab2")
        item = content.find_all("li")
        for i in item[:5]:
            rs.append({
                "name" : i.find("h3").text,
                "href" : i.find("a")["href"],
                "img" : i.find("img")["src"]
            })
        print(rs)
        return  Response({"data" : rs})

class MoviesAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"MySelf": {
            "name": "Ngo Hong Thong",
            "age": datetime.datetime.now().year - 2004,
            "address": "HCM",
        }})

class NumberLuckySouthAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        rs = []
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://ketquaveso.mobi/xsmn-6-8-2023.html"  # Replace this with your actual URL
        response = requests.get(url, verify=True) 
        print(response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        content  = soup.find("div", id= "load_kq_mn_0")
        test  = content.find_all("tr")
        th = content.find_all("th")
        header = []
        for h in th[1:4]:
            header.append(h.text.strip())
        rs.append(header)
        for i in test[1:10]:
            td = i.find_all("td")
            row = []           
            for j in td:
                fields = j.find_all("div")
                for k in fields:
                    row.append(k.text.strip())
            rs.append(row)
            row = []
        # print(rs)
        return  Response({"data" : rs})

class NumberLuckyNorthAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        rs = []
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://ketquaveso.mobi/xsmb-8-8-2023.html"  # Replace this with your actual URL
        response = requests.get(url, verify=True) 
        print(response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        content  = soup.find("table", class_= "kqmb colgiai extendable")
        test  = content.find_all("tr")
        for i in test[1:]:
            td = i.find_all("td")
            row = []           
            for j in td:
                fields = j.find_all("span")
                for k in fields:
                    row.append(k.text.strip())
            rs.append(row)
            row = []
        # print(rs)
        return  Response({"data" : rs})

class PriceGoldAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        rs = []
        url = "https://www.24h.com.vn/gia-vang-hom-nay-c425.html?d=2023-08-09"
        html  = requests.get(url)
        
        soup = BeautifulSoup(html.text, 'html.parser')
        content  = soup.find("div", id= "container_tin_gia_vang")
        table = content.find("div", class_ = "tabBody")
        test  = table.find_all("tr")
        for i in test[1:]:
            td = i.find_all("td")
            row = []           
            for j in td:
                row.append(j.text.strip())
            rs.append(row)
            row = []
        # print(rs)
        return  Response({"data" : rs})
class PriceDollarsAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        rs = []
        url = "https://www.24h.com.vn/ty-gia-ngoai-te-ttcb-c426.html?d=2023-08-31"
        html  = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        content  = soup.find("table", class_= "gia-vang-search-data-table")
        test  = content.find_all("tr")
        for i in test[1:]:
            td = i.find_all("td")
            row = []           
            for j in td:
                row.append(j.text.strip())
            rs.append(row)
            row = []
        # print(rs)
        return  Response({"data" : rs})

class Home(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"MySelf": {
            "name": "Ngo Hong Thong",
            "age": datetime.datetime.now().year - 2004,
            "address": "HCM",
        }})




class ScrapeDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        rs = []
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://www.netflix.com/vn-en/browse/genre/34399"  # Replace this with your actual URL
        response = requests.get(url, verify=True) 
        print(response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        genre = {
            "title" : "",
            "movies" : []
        }

        content  = soup.find_all("section", class_= "nm-collections-row")
        for i in content[:-2]:
            genre["title"] = i.find("h2", class_ = "nm-collections-row-name").text.strip()
            content  = i.find("ul", class_= "nm-content-horizontal-row-item-container")
            test  = content.find_all("li")
            for i in test[1:]:
                genre['movies'].append({
                    "name" : i.find("span", class_ = "nm-collections-title-name").text.strip(),
                    "image" : i.find("img")["src"],
                    "href" : i.find("a")["href"]
                })
                # detail = requests.get(i.find("a")["href"])
                # soup = BeautifulSoup(detail.text, 'html.parser')
                # genre["movies"].append(soup.find("div", class_ = "title-info-synopsis").text.strip())
                # # genre["movies"].append(soup.find("div", class_ = "title-data-info-item item-starring").text.strip())
                # info = soup.find_all("div", class_ = "title-info-metadata-wrapper")
                # for i in info:
                #     genre["movies"].append(i.find("span", class_ = "title-info-metadata-item item-year").text.strip())
                #     genre["movies"].append(i.find("span", class_ = "title-info-metadata-item item-runtime").text.strip())

            rs.append(genre)
            genre = {
                "title" : "",
                "movies" : []
            }
        return  Response({"data" : rs})


        