import requests
import json
import openpyxl
url = "https://cogito.brokeraid.top/api/retriveinfolatest/"

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
    
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    
    
    sheet['A1'] = "Policy Number"
    sheet['B1'] = "Broker ID"
    sheet['C1'] = "Start Date"
    sheet['D1'] = "End Date"
    
    
    sheet['A2'] = json_data.get("PolicyNumber", "N/A")
    sheet['B2'] = json_data.get("BrokerID", "N/A")
    sheet['C2'] = json_data.get("StartDate", "N/A")
    sheet['D2'] = json_data.get("EndDate", "N/A")

    # Save the Excel file
    workbook.save("output.xlsx")
    print("Data has been written to output.xlsx")
    

except Exception as e:
    print("No valid JSON data found:", e)
    
    
    
