import requests
import json
import re

url = "http://127.0.0.1:8000/api/retriveinfolatest/"

content = ""
with open("test.txt",'r',encoding='utf-8') as file:
            content = file.read(16000)
payload = {
    "document":content,
    "queries" : "Policy Number, Broker ID, Start Date, Expiry Date"
}



response = requests.post(url, data=payload)
            
response = response.json()



# Attempt to parse JSON using the first method
try:
    # Find the start and end indices of the JSON string within the triple backticks
    start_index = response.find('{') 
    end_index = response.rfind('}')+1

    # Extract the JSON string
    json_string = response[start_index:end_index]

    # Parse the JSON string
    json_data = json.loads(json_string)

    # Print the parsed JSON data
    print("Policy Number:", json_data["PolicyNumber"])
    print("Broker ID:", json_data["BrokerID"])
    print("Start Date:", json_data["StartDate"])
    print("End Date:", json_data["EndDate"])

except Exception as e:
    print("No valid JSON data found:", e)
    
    
    
