##Modules:
##1)webbrowser: regular browser (GUI browser)
##2)phantomJS: headless browser (GUIless browser)
##3)beautifulSoup: parsing HTML
##4)selenium? (contains phantomJS): webdriver
##5)request?  (request vs selenium webdriver)
##Phantomjs is just as Chrome except you cannot see it's UI.
##
##Selenium is like your hand controlling Chrome which page to go, what to
##enter to the text box,..


##check if site is responding. only check for animes up till "[season] leftovers"
##what it does
##1) find all animes from 1 website
##2) find the genre of each anime (filter out those that are not interested)
##3) find the date of upcoming episode for each anime
##4) go to a new website and find their ratings (filter low ratings)
##5) sort them from highest ranked to lowest


from bs4 import BeautifulSoup
from selenium import webdriver
import time
##phantomjs_path = r'C:\Phantom\phantomjs-2.0.0-windows\bin\phantomjs.exe'
##driver = webdriver.PhantomJS(phantomjs_path)

def findAnimeCountdown():
    driver = webdriver.Firefox()
    driver.get('https://www.livechart.me')

    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')

    animeTags = soup.find_all('div',{"class":"anime-card"}) ##find tag 'div' with attribute 'class=anime-card'
    allAnimes = []
    try:
        for tag in animeTags:
            name = tag.find('h3').contents ##its name
            name = name[0]
    
            nextEp_countdown = tag.find('div',{"class":"episode-countdown"})
            if nextEp_countdown is None:
                nextEpisodeInfo = None
            else: ##tag format:  <div class="episode-countdown">EP5: <time data-timestamp="1469883600000" datetime="2016-07-30T13:00:00Z">01d 17h 30m 30s</time></div>
                nextEpNum = nextEp_countdown.contents[0]
                nextEpDate = nextEp_countdown.time['datetime']
                daysCountdown = nextEp_countdown.time.string
                nextEpisodeInfo = " ".join((nextEpNum,daysCountdown,nextEpDate))
           
            allAnimes.append((name,{'countdown':nextEpisodeInfo}))
    finally:
        driver.quit() ##close the browser
    return allAnimes


##find rating in different website url: (myanimelist.net) http://myanimelist.net/anime/season
def findAnimeRatings():
    driver = webdriver.Firefox()
    driver.get('http://myanimelist.net/anime/season')

    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')

    seasons = soup.find_all('div',{"class":"seasonal-anime-list js-seasonal-anime-list js-seasonal-anime-list-key-1 clearfix"})
    allAnimes = []
    try:
        for animes in seasons:
            for eAnime in animes.find_all('div',{"class":"seasonal-anime js-seasonal-anime"}):        
                name = eAnime.find('a',{"class":"link-title"}) 
                name = name.string

                rating = eAnime.find('span',{'class':'score'})
                rating = rating.string
                rating = rating.split()
            
    ######      <span class="genre">
    ######        <a href="/anime/genre/23/School" title="School">School</a>
    ######      </span>
                genre = ",".join(x.a['title'] for x in eAnime.find_all('span',{"class":"genre"})) 
            
                allAnimes.append((name,{'rating':rating},{'countdown':None},{'genre':genre}))
    finally:
        driver.quit() ##close the browser
    return allAnimes

def findCountdown(lst,name):
    for x,d in lst:
        if x.lower() == name.lower():
            return(d['countdown'])
    return None

if __name__ == "__main__":
    animeCountdown = findAnimeCountdown()
    allAnimes = findAnimeRatings()
    time.sleep(3)
    ##Fill the countdown stats
    for anime in allAnimes:
        name = anime[0]
        anime[2]['countdown']= findCountdown(animeCountdown,name)
        print(anime)

    ##sort the list by ratings

