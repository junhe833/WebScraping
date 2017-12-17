from bs4 import BeautifulSoup
import urllib.request
import re
import codecs
import math
import time
from operator import attrgetter

def getHTML(url):
    req = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    return html

##find episode countdown in website with url: (livechart.me) https://www.livechart.me
def findAnimeCountdown(URL):
    html = getHTML(URL)
    soup = BeautifulSoup(html,'html.parser')

    animeTags = soup.find_all('div',{"class":"anime-card"}) ##find tag 'div' with attribute 'class=anime-card'
    allAnimes = []
    
    for tag in animeTags:
        name = tag.find('h3').contents ##its name
        name = name[0]
    
        nextEp_countdown = tag.find('div',{"class":"episode-countdown"})
        if nextEp_countdown is None:
             nextEpisodeInfo = 'N/A'
        else: ##tag format:  <div class="episode-countdown">EP5: <time data-timestamp="1469883600000" datetime="2016-07-30T13:00:00Z">01d 17h 30m 30s</time></div>
             nextEpNum = nextEp_countdown.contents[0]
             nextEpDate = nextEp_countdown.time.string
             daysCountdown = nextEp_countdown.time.string
             nextEpisodeInfo = " ".join((nextEpNum,daysCountdown,nextEpDate))
           
        allAnimes.append((name,{'countdown':nextEpisodeInfo}))
    return allAnimes


##find rating in different website with url: (myanimelist.net) http://myanimelist.net/anime/season
def findAnimeRatings(URL):
    html = getHTML(URL)
    soup = BeautifulSoup(html,'html.parser')

    seasons = soup.find_all('div',{"class":"seasonal-anime-list js-seasonal-anime-list js-seasonal-anime-list-key-1 clearfix"})
    allAnimes = []
    for animes in seasons:
        for eAnime in animes.find_all('div',{"class":"seasonal-anime js-seasonal-anime"}):        
            name = eAnime.find('a',{"class":"link-title"}) 
            name = name.string

            rating = eAnime.find('span',{'class':'score'})
            rating = rating.string
            rating = rating.split()
            rating = rating[0]
            
######      <span class="genre">
######        <a href="/anime/genre/23/School" title="School">School</a>
######      </span>
            genre = ",".join(x.a['title'] for x in eAnime.find_all('span',{"class":"genre"})) 
            
            allAnimes.append((name,{'rating':rating},{'countdown':None},{'genre':genre}))
    return allAnimes

def findCountdown(lst,name):
    for x,d in lst:
        if x.lower() == name.lower():
            return(d['countdown'])
    return 'N/A'
 
def writeTextFile(animeList,fileName = time.strftime('%Y-%B')+'.txt',nameMaxLength=10,genreMaxLength=10):
    with codecs.open(fileName,'w','UTF-16') as f:
        date = time.strftime("%a, %d/%m/%Y")
        f.write('The following data were extracted on: '+date+'\r\n-----------------------------------------------------------------------------------------------------------\r\n')
        
        for x in animeList:
            msg = "{:{}} =>> rating:{:6} -genre:{:{}} -countdown:{:50} \r\n\r\n".format(x[0],(nameMaxLength+3),x[1]['rating'],x[3]['genre'],(genreMaxLength+3),x[2]['countdown'])
            f.write(msg)
                   
                     
if __name__ == "__main__":
    animeCountdown = findAnimeCountdown(URL='https://www.livechart.me')
    allAnimes = findAnimeRatings(URL='http://myanimelist.net/anime/season')

    ##Fill the countdown stats
    nameMaxLength = 10
    genreMaxLength = 10
    for anime in allAnimes:
        name = anime[0]
        anime[2]['countdown']= findCountdown(animeCountdown,name)
        if len(name) > nameMaxLength:
            nameMaxLength = len(name)    
        genre = anime[3]['genre']
        if len(genre) > genreMaxLength:
            genreMaxLength = len(genre)
    
    ##sort the list by ratings
    rating_NA_list = []
    rating_list = []
    for anime in allAnimes:
        if anime[1]['rating'] == 'N/A':
            rating_NA_list.append(anime)
        else:
            rating_list.append(anime)

    sortedAnimeList = sorted(rating_list, key =lambda tup: tup[1]['rating'], reverse = True)
    sortedAnimeList.extend(rating_NA_list)

    writeTextFile(sortedAnimeList,fileName=time.strftime('%Y-%B')+'.txt',nameMaxLength=nameMaxLength,genreMaxLength=genreMaxLength)
     
