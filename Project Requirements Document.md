**Semester Project Requirements Document**

**Project Title:** Swype Hype

**Developer Name:** Marie Sewell, Griffin Peterson, Heidi Fawson, Thomas Jensen, Thomas Hicken

**Business Context:**

We are building a credit card clearing house. The primary driver for this product is the need for a payment processing system between the point of sale, credit card clearing house, and customer banking. This should be an efficient and quick process.

**Problem Statement:**

POS systems need to talk to thousands of banks/ credit unions, and that is a lot of work. Our clearing house will sit in between POS systems and the banks to properly route the transaction. This means that POS only needs to talk to us and we will handle talking to thousands of banks.

**Scope:**

Our scope involves creating an API for POS systems to talk to, and talking to all available banks/ credit unions. We do not need to worry about POS and banking software, just their API endpoints. We do not need to save cards or users. We do not have to worry about fraudulent behavior. Storing transactions (who, where, when) is in scope.

**Functional Requirements (15-20):**

* Authenticate merchant via POS token (encryption)  
* Ensure sufficient funds  
* Ensure credit balance  
* Keep track of transaction responses and requests  
  * Example: Marie at Amazon.com \-$10,000,000 tuesday, bank said yes.  
  * Request: business id, timestamp, transaction id, amount sent, cc info  
  * Response: success/failure, amount received  
* Ensure compliance with Payment Card Industry Data Security Standards (PCI DSS) to protect cardholder data.  
* Adhere to regulations specific to the regions of operation, such as GDPR for data protection in Europe or the Gramm-Leach-Bliley Act (GLBA) in the U.S.  
* Offer customer support for POS systems and banks  
* Develop efficient onboarding processes for merchants and payment processors.  
* Lightweight system that can handle transactions quickly and efficiently.  
* Offer detailed error messages in API responses to help merchants and banks diagnose issues quickly.  
* Merchant dashboard, a dashboard where merchants can view transaction history and API usage.  
* Send notifications to merchants and banks for successful or failed transactions.  
* Batch processing, for submissions of multiple transactions at once.  
* Timeout management, enforce transaction timeouts to handle unresponsive endpoints and prevent system lag.  
* Rollback functionality for transactions that failed mid-process.

**Non-Functional Requirements (10+):**

* Authentication should occur in less than three seconds  
* Lightweight processing  
* Will not store cc data   
* Highly available  
* Highly scalable/elastic  
* Build trust with business (They provide valid requests, we provide a working service)  
* Easy to upkeep  
* Compatibility verification with different POS to allow a seamless process  
* Maintain security to relevant levels  
* Handle sudden spikes in transaction volume with minimal impact on performance