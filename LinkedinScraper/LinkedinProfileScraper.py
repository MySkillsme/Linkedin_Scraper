#! /usr/bin/env python

# Author : Khaled Dallah
# Email : khaled.dallah0@gmail.com
# Date : 8-12-2018


import scrapy 
from scrapy.crawler import CrawlerProcess
import re , os
import json
from jsonAnalyser import JA
import html
import pprint 
from bs4 import BeautifulSoup

class LPS(scrapy.Spider):
	name='LPS'
	allowed_domains=['www.linkedin.com']
	root_url = 'https://www.linkedin.com/'
	custom_settings ={
		'ROBOTSTXT_OBEY' : False,
		'DOWNLOAD_DELAY' : 0.25 ,
 		'COOKIES_ENABLED' : True,
		'COOKIES_DEBUG' : True,
		'SESSION_COOKIE_VALUE': 'AQEDASNTQzkBETY2AAABeYcXflwAAAF5qyQCXFYAVmetu67uQnTTo8J3',
		'USER_AGENT':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
	}

	incookies=dict()
	inheaders=dict()
	profileUrls=[]
	temp_output=[]
	outputFile=''
	FinalRess=[]
	numOfp=0
	format1=''

	def start_requests(self):
		self.inheaders['csrf-token']=self.incookies['JSESSIONID']
		# print('\n... LPS cookies reached to LS : \n',self.incookies)
		print('\n... LPS Request of LS Spider')
		yield scrapy.Request(url=self.root_url,
				cookies=self.incookies,
				callback =self.reqProfiles)


	def reqProfiles(self,response):
		print('\n... LPS reqProfiles running')
		# print('\n... LPS profileUrls is \n',self.profileUrls)
		self.chechCacheDir()
		for req in reversed(self.profileUrls[:self.numOfp]):
			yield scrapy.Request(url=req,headers=self.inheaders,callback=self.parse)

		
	#get Data Section from response
	def parse(self,response):
		#search between lines about dataJson line
		done=False
		nameOfProfile=response.url.split('/')[4]
		res=[]
		strr=response.text;
		# with open('readme1.txt', 'w') as f:
    	# 		f.write(strr)
		str22=strr.replace("&quot;", "'")
		res=str22.split('\n');
		# print('________________________',type(str22))
		# for eachRow in res:
		# 		eachRow.replace('&quot;', "'")
		t=[];
		countnumber=0
		schoolArray=[]
		companyArray=[]
		mySkills=[]
		userProfile={
			# 'firstName':'',
			# 'LastName':'',
			# 'headLine':'',
			# 'summary':''
		}
		# with open('readme2.txt', 'w') as f:
    	# 		f.write(str22)
		tes=str22.split('class="datalet-bpr-guid')
		try:
			lengthArray=len(tes)
			data1=tes[12].split('>')
			data2=data1[2].replace('</code','')
			data3=data2.replace('\n',"")
			data4=data3.replace("'",'"')
			dataJson=json.loads(data4)
			
			# print('t2 works',tes[12])
			for arrayObj in dataJson["included"]:
    				# print('________________________',arrayObj)
					if 'schoolName' in arrayObj:
    						# print('_-------------------',arrayObj)
							schoolArray.append({
								'schoolName':arrayObj['schoolName'],
								'degree':arrayObj['degreeName'],
								'field':arrayObj['fieldOfStudy'],
								'description':arrayObj['description'],
								'startYear':arrayObj['dateRange']['start']['year'],
								'endYear':arrayObj['dateRange']['end']['year'],
							})
					if 'companyUrn' in arrayObj and 'title' in arrayObj:
    						# print('_-------------------',arrayObj)
							company={}
							company={
								'companyName':arrayObj['companyName'],
								'position':arrayObj['title'],
								'startMonth':arrayObj['dateRange']['start']['month'],
								'startYear':arrayObj['dateRange']['start']['year'],
								'location':arrayObj['locationName']
							}
							if 'end' in arrayObj['dateRange']:
    								company['endMonth']=arrayObj['dateRange']['end']['month']
    								company['endYear']=arrayObj['dateRange']['end']['year']
							companyArray.append(company)
							

					if '$type' in arrayObj:
    						if arrayObj["$type"]=="com.linkedin.voyager.dash.identity.profile.Skill":
    								mySkills.append({
										'name':arrayObj["name"]
									})
					if 'firstName' in arrayObj:
    						# if arrayObj["$type"]=="com.linkedin.voyager.dash.identity.profile.Skill":
    						userProfile['firstName']=arrayObj['firstName']
    						userProfile['lastName']=arrayObj['lastName']
    						userProfile['summary']=arrayObj['summary']
    						userProfile['headline']=arrayObj['headline']
									# mySkills.append(arrayObj)
    							# print('_-------------------',arrayObj)


			# t2=html.unescape(tes[lengthArray-2])
			userProfile['experience']=companyArray
			userProfile['education']=schoolArray
			userProfile['skills']=mySkills
			print('---------general---------',userProfile)
			dataJson=userProfile
			done=True

		except Exception as e: 
			print("\n!!! ERROR in json loads DATA to dataJson :\n",e)
		if(done):

			# self.parseImpData(dataJson,nameOfProfile)
			self.saveJsonFile(nameOfProfile+'_new.json',dataJson)
		else:
			print('\n... Profile : ',response.url)
			print('\n!!! ERROR in find Data Section in Profile')

    					


	#Save Json file of jsonData
	def saveJsonFile(self,name,dataJson):
		directory='Output'
		filePath='/'.join([directory,name])
		with open(filePath, "w+") as json_file:
			try:
				json.dump(dataJson, json_file, indent=4, ensure_ascii = False)
				#json_file.write("\n")
			except:
				print('\n!!! ERROR in Json extractor')


	#Get ImpData Of ImpSection Of Data
	def parseImpData(self,dataJson,nameOfProfile):
    	
		sw={
		'fs_profile':[{'firstName':'', 'lastName':'','summary':'', 'locationName':'', 'headline':''}],
		'fs_position':[{'title':'', 'companyName':'', 'locationName':'' }],
		'fs_education':[{'degreeName':'', 'schoolName':'', 'fieldOfStudy':'', 'activities':''}],
		'fs_volunteerExperience':[{'companyName':'', 'role':'', 'cause':''}],
		'fs_skill':[{'name':''}],
		'fs_certification':[{'authority':'', 'name':'', 'licenseNumber':''}],
		'fs_course':[{'name':''}],
		'fs_language':[{'name':'','proficiency':''}],
		'fs_project':[{'title':'', 'description':'', 'url':''}],
		'fs_honor':[{'description':'', 'title':'', 'issuer':''}],
		'fs_miniProfile':[{'picture':{},'firstName':''}]
			}
		print('-----------------------',self)
		ja=JA(dataJson,nameOfProfile,sw)
		ja.run()
		FinalData=self.dataExtractor(ja.saveRes(),sw)
		print('\n............................................\n')
		FinalData['fs_miniProfile']=[self.diu(FinalData['fs_miniProfile'],FinalData['fs_profile'][0]['firstName'])]
		self.saveJsonFile(nameOfProfile+'_finalRes',FinalData)
		self.FinalRess.append(FinalData)



	#Filter Important Section from plus Data
	def dataExtractor(self,impData,sw):
		#Final Data
		fData=impData
		#loop for all data
		for i in impData:
			#loop for saved list in single essential key
			for j in range(len(impData[i])):
				#loop for single item in list
				for k in list(impData[i][j]):
					if k not in sw[i][0]:
						del fData[i][j][k]

		return(fData)




	#Get Img Url
	def diu(self,imgSection,name):
		tempUrl=''
		for i in imgSection:
			if (i['firstName']==name):
				try:
					firstSec=i['picture']['rootUrl']
					secondSec=html.unescape(i['picture']['artifacts'][-1]['fileIdentifyingUrlPathSegment'])
					tempUrl=firstSec+secondSec
				except:
					print('\n!!! ERROR in parse picture')
		return(tempUrl)




	def chechCacheDir(self):
		directory='cache'
		if not os.path.exists(directory):
			print('\n... LPS Directory created')
			os.makedirs(directory)		



	def closed( self, reason ):
		#save output.json in Output Dir
		if(self.format1=='all' or self.format1=='json'):
			self.saveJsonFile('../Output/'+self.outputFile+'.json',self.FinalRess)
