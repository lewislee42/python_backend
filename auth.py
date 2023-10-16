import requests
import anvil.server
import sys
from dotenv import load_dotenv
import os

load_dotenv()
anvil.server.connect(os.getenv("SERVER"))


def getAccess():
	UID = os.getenv("UID")
	SECRET = os.getenv("SECRET")
	url = 'https://api.intra.42.fr/v2/oauth/token'

	payload = {
			"client_id": UID,
			"client_secret": SECRET,
			"grant_type": "client_credentials"
			}

	headers = {
			"Cache-Control": "no-store"
			}

	response = requests.post(url, data=payload, headers=headers)

	if response.status_code == 200:
		response_json = response.json()
		access_token = response_json.get("access_token")
		return (access_token)
	else:
		print("Error:", response.status_code, response.text)


def getStudentInfo():
	access_token = getAccess()
	page = 1
	url = "https://api.intra.42.fr/v2/campus/34/users"

	arr = []

	while (True):
		params = {
				"access_token": access_token,
				"page[size]": 100,
				"page[number]": page,
				"filter[staff?]": "false"
				}
		response = requests.get(url, params=params)
		if response.status_code == 200:
			data = response.json()
			if len(data) == 0:
				break
			for student in data:
				if "email" in student and student["email"].endswith("42kl.edu.my"):
					arr.append(student)
		else:
			break
		page += 1
	return arr


#def getCoalitioninfo():
#	access_token = getAccess()
#	arr = []
#	for i in range(180, 184):
#		url = "https://api.intra.42.fr/v2/coalitions/" + str(i) + "/users"
#		page = 1
#		while (True):
#			params = {
#				"access_token": access_token,
#				"page[size]": 100,
#				"page[number]": page,
#			}
#			response = requests.get(url, params=params)
#			if response.status_code == 200 and len(response.json()) > 0:
#				arr.append(response.json())
#				page += 1
#			else:
#				break
#	return arr


def getActive(coalitions_users):
	arr = []
	for i in coalitions_users:
		[arr.append(x) for x in i if x['active?']]
	return arr


def getAllCoalition():
	access_token = getAccess()
	arr = []
	for i in range(180, 184):
		url = "https://api.intra.42.fr/v2/coalitions/" + str(i) + "/users"
		page = 1
		while (True):
			params = {
					"access_token": access_token,
					"page[size]": 100,
					"page[number]": page,
					}
			response = requests.get(url, params=params)
			if response.status_code != 200 or len(response.json()) == 0:
				break
			response_json = response.json()
			if page == 1:
				arr.append(response_json)
			else:
				for j in response_json:
					arr[i - 180].append(j)
			page += 1
	return arr


def getActive(coalitions_users):
	arr = []
	for i in coalitions_users:
		[arr.append(x) for x in i if x['active?']]
	return arr


month_to_number = {
		'january': 1,
		'february': 2,
		'march': 3,
		'april': 4,
		'may': 5,
		'june': 6,
		'july': 7,
		'august': 8,
		'september': 9,
		'october': 10,
		'november': 11,
		'december': 12
		}

def get_birth_month(student):
	year = student['pool_year']
	month = student['pool_month']
	if (year == None):
		year = 1990
	else:
		year = int(year)
	if (month == None):
		month = 1
	else:
		month = int(month_to_number[month])
	return (year, month)

def getBatches(students):
	sorted_students = sorted(students, key=get_birth_month)
	return sorted_students


student_json = getStudentInfo()
print("Loaded " + str(len(student_json)) + " Students")
#coalitions_json = getCoalitioninfo()
coalitions_json = getCoalitionStudents()
print("Loaded data from " + str(len(coalitions_json)) + " coalitions")
#active_json = getActive(coalitions_json)
#print("Active Students loaded")
#batch_json = getBatches(coalitions_json[0] + coalitions_json[1] + coalitions_json[2] + coalitions_json[3])


@anvil.server.callable
def getStudentObject():
	cdat = [[x for x in cdat if x['active?'] and x['kind'] == 'student'] for cdat in coalitions_json]
	#print(len(cdat))
	#print("cdat0 ", len(cdat[0]))
	#print("cdat1 ", len(cdat[1]))
	#print("cdat2 ", len(cdat[2]))
	#print("cdat3 ", len(cdat[3]))
	#print("cdat4 ", len(cdat[4]))

	#print(cdat[0])
	return cdat


@anvil.server.callable
def getStudentCoalition(id):
	access_token = getAccess()
	url = "https://api.intra.42.fr/v2/users/" + id + "/coalitions"
	params = {
			"access_token": access_token,
			}
	response = requests.get(url, params=params)
	if response.status_code == 200:
		response_json = response.json()
		return (response_json)
	else:
		print("Error:", response.status_code, response.text)


@anvil.server.callable
def getStudentByLogin(login):
	access_token = getAccess()
	url = "https://api.intra.42.fr/v2/users/" + login
	params = {"access_token": access_token}
	response = requests.get(url, params=params)
	if response.status_code == 200 and len(response.json()) > 0:
		return response.json()


@anvil.server.callable
def numberToWords(number):
	digit_to_word = {
			'0': 'zero',
			'1': 'one',
			'2': 'two',
			'3': 'three',
			'4': 'four',
			'5': 'five',
			'6': 'six',
			'7': 'seven',
			'8': 'eight',
			'9': 'nine'
			}
	return ' '.join([digit_to_word[digit] for digit in str(number)])


@anvil.server.callable
def monthToNumber(month):
	return (month_to_number[month])

#getStudentObject()
print("len of coalitions_json", len(coalitions_json))
print(type(coalitions_json[0]))
print("len of coalitions_json arr 1", len(coalitions_json[0]))
print("len of coalitions_json arr 2", len(coalitions_json[1]))
print("len of coalitions_json arr 3", len(coalitions_json[2]))
print("len of coalitions_json arr 4", len(coalitions_json[3]))
#print("len of coalitions_json arr 5", len(coalitions_json[4]))
#print(coalitions_json[1][0])
# # print(getStudentByLogin('lewlee'))
# # print(getStudentByLogin('zhwong'))
# # print(getStudentByLogin('hang'))

# GETTING THE STUDENT TO SEE IF THEY HAVE ENTERED CORE
# hang = getStudentByLogin('zhwong')
# hang_c = [x['cursus']['name'] for x in hang['cursus_users']]
# if "42cursus" in hang_c:
#	print("yess")
# print(hang_c)


#anvil.server.wait_forever()
