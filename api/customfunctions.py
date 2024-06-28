import requests
MODEL = "llama3:8b-instruct-q8_0"
#MODEL = "llama3:8b-instruct-q6_k"
URL = 'http://localhost:11434/api/generate'
def languagetest(transcription):
    prompt = transcription[0:200] + "What is the language of it. For example if the language is english please return {\n\"language\": \"eng\"}.Return it in JSON < '''json"
    url = URL
    payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            }
    response = requests.post(url,json=payload)
    response = response.json()
    response = response.get('response')
    start_index = response.find('{') 
    end_index = response.rfind('}')+1

    # Extract the JSON string
    response = response[start_index:end_index]
    print(response)
    return response

def translatelanguage(transcription):
    prompt = transcription + "\nTranslate the above sentences in English. If the whole language is English then do not translate. For example return {\n\"translation\": I emailed you back a couple days ago and I was waiting for a response. And you got moved on a dress down? Let me check again. Also, I can't really hear you like well. It's so muffled. Oh, okay. Hang on a moment. Hey, is that better? Yeah, much better. Alright, crappy Bluetooth. \"\"}.Return it in JSON < '''json"
    url = URL
    payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            }
    response = requests.post(url,json=payload)
    response = response.json()
    response = response.get('response')
    start_index = response.find('{') 
    end_index = response.rfind('}')+1

    # Extract the JSON string
    response = response[start_index:end_index]

    return response

def makesummary(trascription):
    prompt = "You are an assistant who would make a summary of the sentence in 15 words. This is a phone transcription so there might be conversation about other things, but I want summary about the most important parts of the conversation. Then things that affects the business."
    prompt += "Return the summary in json with a key summary. Here is the transcription: "
    prompt += trascription + "<<<json"
    model = "llama3:70b"
    url = URL
    print("I am before sending it to 70b")
    payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }
    response = requests.post(url,json=payload)
    response = response.json()
    response = response.get('response')
    print(response)
    start_index = response.find('{') 
    end_index = response.rfind('}')+1
    # Extract the JSON string
    response = response[start_index:end_index]

    return response



def risk_analysis_function(policy):
    url = 'https://crm.uwinsure.com/Api/bisapi_sql.php'


    def  cleanup(a):
        # Remove JSON symbols
        symbols_to_remove = ['{', '}', '[', ']', ':', ',', '"',"\n"]
        plain_text = a
        for symbol in symbols_to_remove:
            plain_text = plain_text.replace(symbol, ' ')

        return plain_text

    def split_string_into_chunks(big_string, chunk_size=2000):
        # Create a list to hold the chunks
        chunks = []
        # Loop over the string, extracting chunks of the specified size
        for i in range(0, len(big_string), chunk_size):
            chunks.append(big_string[i:i + chunk_size])
        return chunks

    # Creating of json, started with transactiono
    data = {
        "action":"History",
        "subdet":"trans",
        "policy":policy,
        "cookie":"xxx",
        "xtoken":"ddd"
    }
    result = {}
    # Making the POST request to get the transaction
    transaction = requests.post(url, json=data)

    transaction = transaction.content.decode()
    transaction = cleanup(transaction)
    print(transaction)


    #changing the subdeatails to policy
    data["subdet"] = "policy"
    # Making the POST request to get the transaction
    policy = requests.post(url, json=data)
    policy = policy.content.decode()
    print(policy)
    policy = cleanup(policy)
    result["policy"] = policy
    policy = "policy: " + policy
    print(policy)

    #changing the subdeatails to service
    data["subdet"] = "service"
    # Making the POST request to get the notes
    service = requests.post(url, json=data)
    service = service.content.decode()
    service = cleanup(service)
    #print(service)


    #changing the subdeatails to claim
    data["subdet"] = "claim"
    # Making the POST request to get the notes
    claim = requests.post(url, json=data)
    claim = claim.content.decode()
    claim = cleanup(claim)
    #print(claim)

    #changing the subdeatails to profit
    data["subdet"] = "profit"
    # Making the POST request to get the notes
    profit = requests.post(url, json=data)
    profit = profit.content.decode()
    profit = cleanup(profit)
    result["profit"] = profit
    profit = "profit: "+profit
    
    #print(profit)

    url = 'http://localhost:11434/api/generate'
    model = 'llama3:8b-instruct-fp16'
    
    transaction_main = split_string_into_chunks(transaction)
    transaction_big = ""
    for i in transaction_big:
        prompt = "Below is a transaction drawn by a insurance company. Through the transaction we can understand, what kind of car they drive, how old is the car, current address, and the previous address, what kind of property they have, have they rented out the property, who are they with for the mortgage, with the star rating we can get how many years they have drove. The class of the vehicle is also important. If the class is 01 then it is not used for work, if it is 02 then they drive to work every day, if it is 03 then it is for business. If you see class 36 then it is for commercial use. Try to match the policy number and date of entry to understand how long the car is being driven. Or how old the car was when it was taken. How often they change the address? Do they have any kids? How long is the policy stayed with us. Do they change the policy a lot. Have they add a car and moved a car often. Customer with a lot of transaction without major change of vehicle is generally a high maintenance customer. How loyal are they. How many cancellations they have."
        prompt += "The transaction is given below. You have to extract what you have found from the conditions given above."
        prompt += i

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        response = requests.post(url,json=payload)
        response = response.json()
        transaction = response.get('response')
        transaction_big += transaction
    result["transaction"] = transaction_big
    transaction = "transaction: " + transaction_big



    claim_main = split_string_into_chunks(claim)
    claim_big = ""
    for i in claim_main:
        prompt = "Anything within a range of 7 days, is usually a same claim. When you have open and close on the same date, usually it is a declined claim. Occasionally you might get how much money we paid up."
        prompt += "Below is the info of the claims. Now write what you have found out from the rules stated above with reasoning"
        prompt += i

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        response = requests.post(url,json=payload)
        response = response.json()
        claim = response.get('response')
        claim_big += claim
    result["claims"] = claim_big
    claims = "claims: "+ claim_big



    service_main = split_string_into_chunks(service)
    service_big = ""
    for i in service_main:
        prompt = "Below is the info of the service history of a customer. From this info I want you to analyze it and fine the following this. "
        prompt += "From, it gives you the number of calls and notes. It tells you how frequently we interact with the customer and if they have payment issues. They may have missed a payment. They have changed the bank. From it you can judge if this customer is a high maintenance. This might be a trouble guy who always tries to get claims or missed payments.  "
        prompt += "Now write a small report with reasoning."
        prompt += i


        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        response = requests.post(url,json=payload)
        response = response.json()
        service = response.get('response')
        service_big += service

    result["service"] = service_big
    service = "service: " + service_big
    

    prompt += "I have consolidated few reports of claims, transaction, service, profit, policy of a insurance customer. You are a insurance risk assessment model. You will analyze the whole report and give a score from -100 to +100. Write the reasons why are you giving this score. Definitely give a score from -100 to +100"
    prompt += transaction+claims+service+profit+policy

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(url,json=payload)
    response = response.json()
    final = response.get('response')
    result["analysis"] = final
    
    return result

    