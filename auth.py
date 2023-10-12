import requests
import anvil.server
import sys

anvil.server.connect("server_65AETVAAR2ECR7NHUNXRVTFU-VNSFI7HNPKP4C2H3")


def getAccess():
	UID = "u-s4t2ud-058e90a7f8903709a87ec8ea12f10f9ee8a4bb4aa9d16bc40eb9670f03169689"
	SECRET = "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"
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


def getCoalitioninfo():
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
			if response.status_code == 200 and len(response.json()) > 0:
				arr.append(response.json())
				page += 1
			else:
				break
	return arr


def getActive(coalitions_users):
	coalitionsList = coalitions_users
	arr = []
	for i in coalitionsList:
		[arr.append(x) for x in i if x['active?']]
	return arr


student_json = getStudentInfo()
coalitions_json = getCoalitioninfo()
active_json = getActive(coalitions_json)


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


anvil.server.wait_forever()
