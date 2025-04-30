Data Organization:

Merchant Table - Used to keep track of merchant information. Storing an id in addition to name will help if there is more than one merchant with a similar name. I chose to store bank info here to keep queries simple and thought it unlikely for merchants to need more than one bank account.

Partition Key - Merchant Name (String)
	
Sort Key - Merchant Token (String)

Merchant id (String)
	
Merchant Account Number (String)
	
Merchant Bank (String)


Transaction Table - Used to keep track of transaction information. For PCI compliance, the table will only keep track of the last 4 digits of the card number. Keeping track of the cardholder name, date of sale, and merchant id  will help query for transactions more effectively

Partition Key - Merchant id (String)
	
Sort Key - Sale date (String)

Cardholder name (String)
	
Last 4 digits card # (String)