from bs4 import BeautifulSoup
from selenium import webdriver
import re
import codecs
import math
import time

def getHTML(browserType,URL):
    if 'phantomjs' == browserType:
        phantomjs_path = r'C:\Phantom\phantomjs-2.1.1-windows\bin\phantomjs.exe'
        driver = webdriver.PhantomJS(executable_path = phantomjs_path)
    elif 'firefox' == browserType:
        driver = webdriver.Firefox()
    elif 'chrome' == browserType:
        driver = webdriver.Chrome()
  
    driver.get(URL)
    html = driver.page_source
    driver.quit() ##close the browser
    return html

##find episode countdown in website with url: (livechart.me) https://www.livechart.me
def findAnimeCountdown(browserType,URL):
    html = getHTML(browserType,URL)
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
             nextEpDate = nextEp_countdown.time['datetime']
             daysCountdown = nextEp_countdown.time.string
             nextEpisodeInfo = " ".join((nextEpNum,daysCountdown,nextEpDate))
           
        allAnimes.append((name,{'countdown':nextEpisodeInfo}))
 
    return allAnimes


##find rating in different website with url: (myanimelist.net) http://myanimelist.net/anime/season
def findAnimeRatings(browserType,URL):
    html = getHTML(browserType,URL)
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
 
def writeTextFile(animeList,fileName,nameMaxLength):
    with codecs.open(fileName,'w','UTF-16') as f:
        date = time.strftime("%a, %d/%m/%Y")
        f.write('The following data were extracted on: '+date+'\r\n-----------------------------------------------------------------------------------------------------------\r\n')
        
        for x in animeList:
            msg = "{:{}} =>> rating:{:6} -- countdown:{:50} -- genre:{}\r\n\r\n".format(x[0],(nameMaxLength+5),x[1]['rating'],x[2]['countdown'],x[3]['genre'])
            f.write(msg)
                     
def buildSortedList(animeList,ratingList):
    sortedAnimeList = []
    for rating in ratingList:    
        tempList = [anime for anime in animeList if anime[1]['rating'] != 'N/A' and math.isclose(float(anime[1]['rating']), float(rating),abs_tol=0.005)]               
        sortedAnimeList.extend( tempList ) ##add the element by index
        
    tempList = [anime for anime in animeList if anime[1]['rating'] == 'N/A']                  
    sortedAnimeList.extend( tempList ) ##append the remaining list
    return sortedAnimeList
                     
if __name__ == "__main__":
    browserList = ['firefox','chrome','phantomjs']
    while True:
        browserType = input('Please enter the desired web browser (firefox/chrome/phantomJS): ')
        browserType = browserType.lower()
        if browserType in browserList:
            break
        
    animeCountdown = findAnimeCountdown(browserType,URL='https://www.livechart.me')
    allAnimes = findAnimeRatings(browserType,URL='http://myanimelist.net/anime/season')

    ##Fill the countdown stats
    nameMaxLength = 0
    for anime in allAnimes:
        name = anime[0]
        anime[2]['countdown']= findCountdown(animeCountdown,name)
        if len(name) > nameMaxLength:
            nameMaxLength = len(name)
   
    ##sort the list by ratings
    sortedRatingList = sorted([float(anime[1]['rating']) for anime in allAnimes if (re.match('[0-9][.][0-9]+',anime[1]['rating']))],reverse=True) 
  
    sortedAnimeList = buildSortedList(allAnimes,sortedRatingList)

    fileName = "output.txt"
    writeTextFile(sortedAnimeList,fileName,nameMaxLength)

        
