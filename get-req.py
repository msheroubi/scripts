from bs4 import BeautifulSoup
import urllib.request
import pyodbc
import re
import time
import json


def getRankings():	
	overall_url = 'https://www.macleans.ca/education/canadas-top-school-by-reputation-2020/'
	program_url = 'https://www.macleans.ca/?p={}'

	### Page id for 
	dict_programs = {1184826:'Biology', 1184828:'Business', 1184829:'Computer Science', 1184830:'Education', 1184831:'Engineering', 1184832:'Environmental-Science', 1184833:'Mathematics', 1184834:'Medicine', 1184835:'Nursing', 1184836:'Psychology'}

	try:
	    page = urllib.request.urlopen(overall_url) #Make Connection
	except:
	    print("An error occured.")

	soup = BeautifulSoup(page, 'html.parser')

	table = soup.find("table", {'class': 'footable rdm-footable'})

	table_body = table.find('tbody')

	data = []

	rows = table_body.find_all('tr')
	for row in rows:
	    cols = row.find_all('td')
	    cols = [ele.text.strip() for ele in cols]
	    data.append([ele for ele in cols if ele]) # Get rid of empty values

	top_universities = []
	for i in range(0, len(data)):
		top_universities.append(data[i][:2])

	print('Overall Ranking')
	return (top_universities)	

	print('\nBy Program')
	for key, program in dict_programs.items():
		print(program)
		try:
			page = urllib.request.urlopen(program_url.format(key)) #Make Connection
		except:
			print("An Error has occured.")

		soup = BeautifulSoup(page, 'html.parser')
		table = soup.find("table", {'class': 'footable rdm-footable'})
		table_body = table.find('tbody')
		data = []
		rows = table_body.find_all('tr')
		for row in rows:
		    cols = row.find_all('td')
		    cols = [ele.text.strip() for ele in cols]
		    data.append([ele for ele in cols if ele]) # Get rid of empty values
		overall_rank = []
		for row in data:
			overall_rank.append(row[:2])
		print(overall_rank)

def getTuition():
	url = 'https://www.univcan.ca/universities/facts-and-stats/tuition-fees-by-university/'

	try:
	    page = urllib.request.urlopen(url) #Make Connection
	except:
	    print("An error occured.")

	soup = BeautifulSoup(page, 'html.parser')

	table = soup.find("tbody")
	data = []

	rows = table.find_all('tr')
	for row in rows:
	    cols = row.find_all('td')
	    cols = [ele.text.strip() for ele in cols]
	    data.append([ele for ele in cols if ele]) # Get rid of empty values
	
	tuition_summary = []
	for row in data:
		for i in range(0, len(row)):
			row[i] = row[i].replace('\xa0', '')
		tuition_summary.append(row)
	return tuition_summary

def connectDB():
	endpoint = 'database-unifind.ccyugazvu1zd.ca-central-1.rds.amazonaws.com'
	user = 'admin'
	pw = 'root1972'

	conn = 0
	try:
		conn = pyodbc.connect(
			driver = 'ODBC Driver 17 for SQL Server',
			server = endpoint,
			port = 3306,
			user = user,
			password = pw,
			timeout = 5
			)
		print('Connection Successful')
		sql = 'CREATE TABLE Test( id INT PRIMARY KEY);'
		crsr = conn.cursor()
		crsr.execute(sql)
		row = crsr.fetchone()
		print (row[0])
	except:
		print("An Error has occured.")
	finally:
		conn.close()

	# sql = 'select @@version'
	# conn.close()

def normalizeUniNames(data):
	dict_names = {
	'UBC':'The University of British Columbia',
	'Toronto': 'University of Toronto',
	'Waterloo': 'University of Waterloo',
	'McGill' : 'McGill University',
	'McMaster': 'McMaster University',
	'Alberta': 'University of Alberta',
	"Queen's" : "Queen's University",
	'Western' : 'Western University (excludes colleges)',
	'Simon Fraser' : 'Simon Fraser University',
	'Montreal' : 'Université de Montréal',
	'Calgary' : 'University of Calgary',
	'Guelph': 'University of Guelph',
	'Victoria' : 'University of Victoria',
	'Dalhousie' : 'Dalhousie University',
	'Laval' : 'Université Laval',
	'Ryerson' : 'Ryerson University',
	'Concordia': 'Concordia University',
	'Ottawa' : 'University of Ottawa',
	'Sherbrooke' : 'Université de Sherbrooke',
	'Saskatchewan' : 'University of Saskatchewan',
	'York' : 'York University' ,
	'Memorial' : 'Memorial University' ,
	'Manitoba' : 'University of Manitoba' ,
	'Carleton' : 'Carleton University' ,
	'Wilfrid Laurier' : 'Wilfrid Laurier University' ,
	'UQAM' : 'Université du Québec à Montréal' ,
	'Mount Allison' : 'Mount Allison University' ,
	'St. Francis Xavier' : 'St. Francis Xavier University' ,
	'Acadia' : 'Acadia University' ,
	'Trent' : 'Trent University' ,
	'New Brunswick' : 'New Brunswick University' ,
	'Ontario Tech' : 'University of Ontario Institute of Technology' ,
	'Regina' : 'University of Regina' ,
	'UNBC' : 'University of Northern British Columbia' ,
	'Lethbridge' : 'University of Lethbridge' ,
	'Saint Mary\'s' : 'Saint Mary\'s University' ,
	'Winnipeg' : 'University of Winnipeg' ,
	'Brock' : 'Brock University' ,
	'Bishop\'s' : 'Bishop\'s University' ,
	'Windsor' : 'University of Windsor' ,
	'UPEI' : 'University of Prince Edward Island' ,
	'Lakehead' : 'Lakehead University' ,
	'Mount Saint Vincent' : 'Mount Saint Vincent University' ,
	'Moncton' : 'Université de Moncton' ,
	'Laurentian' : 'Laurentian University' ,
	'Cape Breton' : 'Cape Breton University' ,
	'St. Thomas' : 'St. Thomas University' ,
	'Brandon' : 'Brandon University' ,
	'Nipissing' : 'Nipissing University' 
	}

	for i in range(0,len(data)):
		if data[i][1] in list(dict_names.keys()):
			data[i][1] = dict_names.get(data[i][1])

	return data

def mergeTuitionRankingData(tuition_data, ranking_data):
	output = []
	for i in range(0, len(tuition_data)):
		for j in range(0, len(ranking_data)):
			if ranking_data[j][1] == tuition_data[i][0]:
				tuition_data[i].append(ranking_data[j][0])
				output.append(tuition_data[i])
	return output


tuition_data = getTuition()
ranking_data = getRankings()

normalized = normalizeUniNames(ranking_data)
merged = mergeTuitionRankingData(tuition_data, normalized)

with open('data.json', 'w') as f:
	aggregate = {}
	aggregate['universities'] = []
	for ele in merged:
		if len(ele) > 6:
			data = {}
			data[1] = ele[6]
			data[2] = ele[0]
			data[3] = ele[1]
			data[4] = ele[2]
			data[5] = ele[3]
			data[6] = ele[4]
			data[7] = ele[5]
	# 		data['rank'] = ele[6]
	# 		data['name'] = ele[0]
	# 		data['domestic-under'] = ele[1]
	# 		data['foreign-under'] = ele[2]
	# 		data['domestic-grad'] = ele[3]
	# 		data['foreign-grad'] = ele[4]
	# 		data['location'] = ele[5]
	# 		aggregate['universities'].append(data)
	# print(aggregate)
			row = '<tr>'
			for i in range(1,7):
				row = row + ('<td class="column{}">'.format(i)+data[i]+'</td>')
			row= row + ('</tr>')
			print(row)
	# json.dump(aggregate, f)
