import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd


def items(link):
    req = requests.get(link)
    bs = BeautifulSoup(req.text, 'html.parser')
    
    a = bs.findAll('div', {'class':'title_wrapper'})[0]
    b = a.find('div', {'class':'subtext'}).text.split('|')
    c = bs.findAll('div', {'class':'credit_summary_item'})[0].find_next_sibling()
    d = c.find_next_sibling().findAll('a')
    e = bs.findAll('div', {'class':'see-more inline canwrap'})[0].findAll('a')
    f = bs.findAll('div', {'id':'titleDetails'})[0].findAll('div', {'class':'txt-block'})
    
    title = str(a.find('h1').text.strip())
    name = title[:-7]
    year = title[-5:-1]
    
    censor = b[0].replace(' ', '').replace('\n', '')
    if len(censor) > 5:
        censor = ''
    
    length = b[-3].replace(' ', '').replace('\n', '')
    genre = b[-2].replace(' ', '').replace('\n', '')
    if ',' in genre:
        genre = genre.split(',')
    release = b[-1].replace('\n', '').strip()
    
    rating = bs.findAll('div', {'class':'ratingValue'})[0].text[:-4].replace('\n' ,'')
    review_count = bs.findAll('div', {'class':'imdbRating'})[0].find('a').text.replace(',', '')
    summary = bs.findAll('div', {'class':'summary_text'})[0].text.strip()
    director = bs.findAll('div', {'class':'credit_summary_item'})[0].find('a').text
    
    writer1 = c.findAll('a')[0].text
    writer2 = ''
    if len(c.findAll('a')) > 1:
        writer2 = c.findAll('a')[1].text
    
    cast1 = d[0].text
    cast2 = d[1].text
    cast3 = d[2].text
    
    kw = ''
    if str(e[0].get('href'))[8] is 'k':
        kw = e[0].find('span').text + ' | '
        kw += e[1].find('span').text + ' | '
        kw += e[2].find('span').text + ' | '
        kw += e[3].find('span').text + ' | '
        kw += e[4].find('span').text
        
    budget = ''
    gross_usa = ''
    gross_ww = ''
    company = ''
    for div in f:
        if div.find('h4', text=re.compile('Budget:')):
            budget = div.text[9:-12].replace(' ', '').replace('\n', '')
            
        elif div.find('h4', text=re.compile('Gross USA:')):
            gross_usa = div.text[13:].replace(',', '')
        
        elif div.find('h4', text=re.compile('Cumulative Worldwide Gross:')):
            gross_ww = div.text[30:].replace(',', '')
            
        elif div.find('h4', text=re.compile('Production Co:')):
            company = div.text[17:-19].strip()
            
    budget = re.sub('\D', '', budget)
    
    if ' ' in gross_usa:
        gross_usa = gross_usa.split(' ')[0][:-1]
        
    if ' ' in gross_ww:
        gross_ww = gross_ww.split(' ')[0][:-1]
      
    if ',' in company:
        company = company.split(',')[0]
    
    genre0 = ''
    genre1 = ''
    genre2 = ''
    genre3 = ''
    
    if isinstance(genre, list):
        for i in range(len(genre)):
            if i is 0:
                genre0 = genre[0]
            elif i is 1:
                genre1 = genre[1]
            elif i is 2:
                genre2 = genre[2]
            elif i is 3:
                genre3 = genre[3]
    else:
        genre0 = genre
        
    lst = [name, link, year, rating, review_count, censor, length, genre0, genre1, genre2, genre3, release, summary, director, writer1, writer2, '', cast1, cast2, cast3, '', '', kw, budget, gross_usa, gross_ww, company]
    return(lst)



def spider():
    movies = []
    req = requests.get('https://www.imdb.com/chart/top?ref_=nv_mv_250')
    bs = BeautifulSoup(req.text, 'html.parser')
    for i in range(250):
        link = 'https://www.imdb.com' + str(bs.findAll('td', {'class':'titleColumn'})[i].find('a').get('href'))
        lst = items(link)
        movies.append(lst)
    return movies



movies = spider()

arr = np.array(movies)
df = pd.DataFrame(arr, columns=['Name of the movie', 'Link', 'Year released', 'IMDB rating', 'Number of reviewers', 'Censor board rating', 'Length of the movie', 'Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Release date', 'story summary', 'Director Name', 'Writer 1', 'Writer 2', 'Writer 3', 'Star 1', 'Star 2', 'Star 3', 'Star 4', 'Star 5', 'Plot Keywords list', 'Budget', 'Gross USA', 'Cumulative worlwide Gross', 'Production company'])
df.to_csv('imdb.csv')