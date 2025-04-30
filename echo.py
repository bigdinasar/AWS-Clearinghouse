import json
import boto3
import urllib.request
import socket  # Needed to check for socket.timeout
import botocore.auth
import botocore.awsrequest
import botocore.credentials

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Merchant")
log_table = dynamodb.Table("Transactions")

    # function_url = "https://l4biqzlvcftgrvndcqbixb64x40bzkxj.lambda-url.us-west-1.on.aws"
    # citibank_url = "https://3p6ek2m7p4mrlraaxnw7qc7rry0hxvwf.lambda-url.us-west-1.on.aws/"

def getUrl(bank):
    if bank == "Chase":
        return "https://l4biqzlvcftgrvndcqbixb64x40bzkxj.lambda-url.us-west-1.on.aws"
    elif bank == "Citibank":
        return "https://3p6ek2m7p4mrlraaxnw7qc7rry0hxvwf.lambda-url.us-west-1.on.aws"
    elif bank == "US Bank":
        return "https://a7vm2pj2pvahxep24lytel2ije0vfbyv.lambda-url.us-west-1.on.aws"
    elif bank == "Wells Fargo":
        return "https://iyxdo7ia13.execute-api.us-west-1.amazonaws.com/prod/process_txn"
    elif bank == "Capital One":
        return "https://rci67emykr4r6ywr2jualcy7hu0gvoyj.lambda-url.us-west-1.on.aws/"

def lambda_handler(event, context):
    # Parse the body if the event comes from API Gateway
    if "body" in event:
        try:
            body = json.loads(event["body"])  # Convert string to dictionary
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON format in request body"})
            }
    else:
        body = event  # Direct invocation or other AWS service events

    # print("body: ", body)

    # Extract parameters from the parsed body
    bank = body.get("bank")
    merchant_name = body.get("merchant_name")
    merchant_token = body.get("merchant_token")
    merchant_bank = body.get("merchant_bank")
    merchant_bank_acct = body.get("merchant_bank_acct")
    customer_name = body.get("customer_name")
    cc_num = body.get("cc_number")
    card_type = body.get("card_type")
    cvv = body.get("cvv")
    amount = body.get("amount")
    card_zip = body.get("card_zip")
    timestamp = body.get("timestamp")

    
    if not merchant_name or not merchant_token:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Declined - Invalid Merchant Credentials."})
        }


    # Get merchant details from DynamoDB

    # print("Merchant Name: ", merchant_name)
    # print("Merchant Token: ", merchant_token)
    # print("Merchant Bank: ", merchant_bank)
    
    response = table.get_item(Key={"MerchantName": merchant_name, "Token": merchant_token})

    # Check if merchant exists
    if "Item" not in response:
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "Declined - Invalid Merchant Credentials."})
        }

    # print("table response item: ", response["Item"])

    # Merchant authorized! Now send request to clearinghouse API
    if bank == "US Bank":
        # print("Merchant is US")
        payload = {
            "clearinghouse_account": "Thomas Jensen",
            "clearinghouse_token": "261224",
            "bank_account": cc_num,
            "amount": amount,
            "type": True
        }
    
    else:
        # print("Merchant is not US/Wells Fargo")
        payload = {
            "ch_acct_num": "Thomas Jensen",
            "ch_token": "261224",
            "bank_acct_num": cc_num,
            "amount": amount,
            "deposit": False
        }

    print("payload: ", payload)

    headers = {'Content-Type': 'application/json'}

    print("headers: ", headers)

    function_url = getUrl(bank)
    print("function_url: ", function_url)



    try:
        # Prepare and execute the HTTP request
        print("bank is: ", bank, "invoking...")

        if bank == "Wells Fargo":

            payload = {
            "api_user": "Thomas Jensen",
            "api_key": "261224",
            "txn_account": cc_num,
            "amount": amount,
            "type": "withdraw"
            }
 

            access_key = "AKIATHVQK5TDMVDBXOOF"
            fake_key = 2

            credentials = botocore.credentials.Credentials(access_key, fake_key)

            request = botocore.awsrequest.AWSRequest(
                method='POST',
                url=function_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            region = 'us-west-1'
            signer = botocore.auth.SigV4Auth(credentials, 'execute-api', region)
            signer.add_auth(request)

            signed_request = urllib.request.Request(
                url=function_url,
                method='POST',
                headers=dict(request.headers),
                data=request.body
            )

            with urllib.request.urlopen(signed_request, timeout=5) as response:

                status_code = response.getcode()  # Get the status code correctly
                response_data = response.read().decode('utf-8')  # Read and decode the response

                print("Wells Fargo Status Code:", status_code)
                print("Wells Fargo Response Data:", response_data)

                # Parse the response JSON if the status code is 200
                if status_code == 200:
                    response_payload = json.loads(response_data)

                    

                    log_entry = {
                    "MerchantName": merchant_name,
                    "BankName": bank,
                    "CCNum": cc_num,
                    "amount": amount,
                    "DateTime": timestamp,
                    "Status": response_payload["result"]
                    }
                    
                    try:
                        log_table.put_item(Item=log_entry)

                    except:
                        print("Error logging transaction")

                    if response_payload["result"] != "Success":
                        reason = response_payload["result"]

                        return {
                            "statusCode": 403,
                            "body": "Declined - " + reason + "."
                        }
                    
                    return {
                        "statusCode": 200,
                        "body": 'Accepted.'
                    }
                else:
                    return {
                        "statusCode": status_code,
                        "body": json.dumps({"error": "Error - Bank not available."})
                    }
            




            
        if bank == "Capital One":

            print("making a session request")

            session_payload = {
                "account_num": "Thomas Jensen",
                "token": "261224"
            }

            session_headers = {
            "Content-Type": "application/json"
            }

            session_req = urllib.request.Request(
            function_url, 
            method='POST', 
            headers=session_headers, 
            data=json.dumps(session_payload).encode('utf-8')
            )

            with urllib.request.urlopen(session_req, timeout=5) as session_response:
                session_status_code = session_response.getcode()
                session_response_data = session_response.read().decode('utf-8')                

                print("Session Status Code:", session_status_code)
                print("Session Response Data:", session_response_data)

                if session_status_code != 200:
                    raise Exception(f"Failed to obtain session for Capital One. Status: {session_status_code}, Details: {session_response_data}")


                session_payload_response = json.loads(session_response_data)

                # print("session_payload_response type:", type(session_payload_response))

                session_id = session_payload_response["session"]

                print("session_id", session_id)

                if not session_id:
                    raise Exception("Session ID not found in session response.")

                print("Obtained session_id:", session_id)

                # Attach the session_id to your original payload
                payload["session"] = session_id
                payload = {
                    "session": session_id,
                    "bank_account": cc_num,
                    "withdrawl": amount

                }

                print("payload with session_id: ", payload)


        req = urllib.request.Request(function_url, method='POST', headers=headers, data=json.dumps(payload).encode('utf-8'))
        print("req headers", req.headers)
        print("req method: ", req.method)
        print("req data: ", req.data)
        print("req full_url: ", req.full_url)
        with urllib.request.urlopen(req, timeout=5) as response:
            print("response in with block: ", response)
            status_code = response.getcode()  # Get the status code correctly
            response_data = response.read().decode('utf-8')  # Read and decode the response

            print("Status Code:", status_code)
            print("Response Data:", response_data)

            # Parse the response JSON if the status code is 200
            if status_code == 200:
                response_payload = json.loads(response_data)

                print("response_payload: ", response_payload)

                if bank == "Capital One":

                    log_entry = {
                        "MerchantName": merchant_name,
                        "BankName": bank,
                        "CCNum": cc_num,
                        "amount": amount,
                        "DateTime": timestamp,
                        "Status": response_payload["response"]
                    }
                
                else:

                    # print("not capital one")

                    log_entry = {
                        "MerchantName": merchant_name,
                        "BankName": bank,
                        "CCNum": cc_num,
                        "amount": amount,
                        "DateTime": timestamp,
                        "Status": response_payload["message"]
                    }

                # print("log_entry: ", log_entry)

                try:
                    log_table.put_item(Item=log_entry)

                except:
                    print("Error logging transaction")

                if bank == "Capital One":
                    if response_payload["response"] != "Success":

                        reason = response_payload["response"]

                        return {
                            "statusCode": 403,
                            "body": "Declined - " + reason + "."
                        }
                    
                    else:
                        return {
                            "statusCode": 200,
                            "body": 'Accepted.'
                }


                elif response_payload["message"] != "Approved" or response_payload["message"] != "Transaction Complete" or response_payload["message"] != "Accepted":

                    reason = response_payload["message"]

                    return {
                        "statusCode": 403,
                        "body": "Declined - " + reason + "."
                    }

                return {
                    "statusCode": 200,
                    "body": 'Accepted.'
                }
            else:

                reason = response_payload["message"]

                return {
                    "statusCode": status_code,
                    "body": "Declined - " + reason + "."
                }
            
    except urllib.error.HTTPError as e:
        # Handle HTTP errors
        error_message = e.read().decode('utf-8')
        print("you got the e")
        print(f"HTTP Error: {e.code}")
        print(f"Error Message: {error_message}")
        raise Exception("Error - Bank Not Available.")

    except TimeoutError as e:
        print("you got the timeout")
        print(f"Transaction timed out bank: {bank}")
        return {
            "statusCode": 504,
            "body": "Error - Bank Not Available."
        }