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
        access_key = os.environ.get('METEUM_API_KEY')

        headers = {
            'X-Meteum-API-Key': access_key
        }

        response_ = requests.get('https://api.meteum.ai/v1/forecast?lat=10.0452&lon=105.7469', headers=headers)

        return Response({'data': response_.json()})

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
        url = "https://moveek.com"  # Replace this with your actual URL
        response = requests.get(url, verify=True) 
        print(response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        
        content  = soup.find_all("div", class_ = "bg-white border-top border-bottom mt-3 pt-4")
        print(content)
        items = content.find("div", class_ = "col item")

        print(items)
        for i in items[:5]:
            print(i)
            # rs.append({
            #     "name" : i.find("dl", class_ = "list_text").find("a").text,
            #     "href" : i.find("a")["href"],
            #     "img" : i.find("img")["src"]
            # })
        # print(rs)
        return  Response({"data" : "rs"})