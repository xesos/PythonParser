from __future__ import print_function
import urllib2, sys
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import csv
import time
links = []
 
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
    	print("Encountered a start tag:", tag)
 
def extract():
    if len(sys.argv) != 2:
        print('Usage: {} CSV'.format(sys.argv[0]))
        return
    csvFile = sys.argv[1]
 
    #Read file first 
    write_file="output.csv"
    with open(write_file, "w") as output:
		fieldnames = ['ID Exposition','Title', 'Place','Start Date','End Date','Exposition URL','Artist','Date of Birth','Place of Birth','Gender','ArtistUrl']
		writer = csv.DictWriter(output, fieldnames=fieldnames)
		writer.writeheader()
		file=csv.reader(open(csvFile,'r'))
		expoID = ""
		expoCounter = 000
		for row in file:
			max_attempts=6
			r=0
			html=None
			while html is None and r<max_attempts:
				try:
					f = urllib2.urlopen(row[2],timeout=30)
					html = f.read()
					f.close()
				except Exception as e:
					r=r+1
        			print("Re-trying, attempt -- ",r)
        			time.sleep(5)
        			pass
			soup = BeautifulSoup(html)
			if (expoID != row[0] or row[0]!="" ):
				expoCounter = 000
				expoID=row[0][-3:]
			#exhibition = soup.findAll("ul", {"class": "exhibition"})
			for (ptagTitle,ptagDate) in zip(soup.find_all("span", attrs={"class" : "title"}),soup.find_all("span", attrs={"class" : "time"})):
				# prints the p tag content
				print(ptagTitle.text)
				print(ptagTitle.find("a").get("href"))
				print(ptagDate.text)
				expoURL= "http://www.artlinkart.com" + ptagTitle.find("a").get("href")
				keywords = ["2015", "2016", "2017","2018","2019"]
				isDateCorrect = 0
				for text in keywords:
					if text in ptagDate.text:
						isDateCorrect = 1
				if (isDateCorrect):
					if "solo" in ptagTitle.text:
						max_attempts=6
						r=0
						html1=None
						while html1 is None and r<max_attempts:
							try:
								f1 = urllib2.urlopen(expoURL,timeout=30)
								html1 = f1.read()
								f1.close()
							except Exception as e:
								r=r+1
								print("Re-trying, attempt -- ",r)
								time.sleep(5)
								pass 
						soupArtist = BeautifulSoup(html1) 
						table_soup = soupArtist.find_all("table" ,attrs={"class":"wowa_overview"})
						tr = table_soup[0].find_all("tr")
						artistUrl=""						
						for trs in tr:
							for tds in trs.find_all(['th','td']):
								if "Artist(s)" in tds:
									artistUrl=trs.find_all(['td'])
									artistUrl=artistUrl[0].find("a").get("href")
						
						authorName=""
						if artistUrl:
							artistUrl="http://www.artlinkart.com" + artistUrl
							max_attempts=6
							r=0
							html2=None
							while html2 is None and r<max_attempts:
								try:
									f2=urllib2.urlopen(artistUrl,timeout=30)
									html2=f2.read()
									f2.close()
								except Exception as e:
									r=r+1
									print("Re-trying, attempt -- ",r)
									time.sleep(5)
									pass 
							soupArtistName = BeautifulSoup(html2) 
							table_soup2 = soupArtistName.find_all("h1" ,attrs={"class":"overview"})
							authorName=table_soup2[0].text.encode('utf8')
							table_soup3 = soupArtistName.find_all("table" ,attrs={"class":"text_table"})
							tr5 = table_soup3[0].find_all("tr")
							DoB=""
							PoB=""
							gender=""
							for trs in tr5:
								for tds in trs.find_all(['th','td']):
									if "Date of Birth" in tds:
										DoB=trs.find_all(['td'])
										if DoB != "":
											DoB=DoB[0].text.encode('utf8')
									if "Place of Birth" in tds:
										PoB=trs.find_all(['td'])
										if PoB != '':
											PoB=PoB[0].text.encode('utf8')
									if "Gender" in tds:
										gender=trs.find_all(['td'])
										if gender != "":
											gender=gender[0].text.encode('utf8')
						tr = table_soup[0].find_all("tr")
						expoCounter = expoCounter+1
						if expoCounter>9: 
							expo = expoID + "0" + str(expoCounter)
						else: 
							expo = expoID + "00" + str(expoCounter)
						startDate, endDate = ptagDate.text.split(' - ', 1)
						writer.writerow({'ID Exposition' : expo, 'Title': ptagTitle.text.encode('utf8').rstrip("\n").rstrip("\"").rstrip("\n"), 'Place':row[1], 'Start Date':startDate.encode('utf8'),'End Date': endDate.encode('utf8'),'Exposition URL': expoURL, 'Artist':authorName,"Date of Birth":DoB.split(',')[-1],'Place of Birth':PoB.split(',')[-1],'Gender':gender, "ArtistUrl": artistUrl})

 
extract()
