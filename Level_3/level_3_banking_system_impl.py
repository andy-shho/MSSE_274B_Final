import math


class Account:
    def __init__(self, timestamp: str, account_id: str):
        self._timestamp = timestamp
        self._account_id = account_id
        
        self._balance = 0
        
    
    # helper function for testing only 
    def print_account_details(self):
        print(f"Timestamp: {self._timestamp}")
        print(f"Accound ID: {self._account_id}")
        print(f"Balance: {self._balance}\n")

class BankingSystemImpl:

    def __init__(self):
        self._accounts_list = []
        self._outgoing = {} # dict, track outgoing transfers + withdrawals 

        self._transaction_number = 0 # counter to keep track of transaction number for unique transac id
        self._payment_ids = {} # dict(key: payment_id; value: account_id) -> track unique payment id's and corresponding account 

        self._pending_cashback = {} # track pending cash back as dict: {key: payment_id; value: (timestamp, account_id, cashback_amount)}
        
    def _find_account(self, account_id: str): 
        for account in self._accounts_list:
            if account_id == account._account_id:
                return account # type: Account
        return None # if not account found 
    
    # helper function for testing only 
    def _all_accounts(self): 
        for account in self._accounts_list: 
            account.print_account_details()


    # TODO: implement interface methods here
    def create_account(self, timestamp: int, account_id: str) -> bool:
        if self._find_account(account_id) is not None:
            return False
        
        new_account = Account(timestamp, account_id)
        self._accounts_list.append(new_account)

        self._outgoing[account_id] = 0 #initialize outgoing transfer tracker
        return True
    
    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        account = self._find_account(account_id)
        if account is None:
            print(f"Timestamp: {timestamp} | Error: Account '{account_id}' not found.")
            return None

        if amount <= 0:
            print(f"Timestamp: {timestamp} | Error: Invalid deposit amount: {amount}")
            return None

        print(f"Timestamp: {timestamp} \nStarting account balance: {account._balance}")
        account._balance += amount
        print(f"Timestamp: {timestamp} \nNew account balance: {account._balance}\n")

        return account._balance


    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        
        source = self._find_account(source_account_id)
        target = self._find_account(target_account_id)
        
        #missing accounts 
        if source is None or target is None:
            print("Error: Please enter a valid amount or source/target account IDs.")
            return None

        #cannot transfer to self
        if source == target:
            print("Error: Please enter a valid amount or source/target account IDs.")
            return None
        
        #change >= to > so full balance transfers are allowed
        if amount <= 0 or amount > source._balance:
            print("Error: Please enter a valid amount or source/target account IDs.")
            return None
        
        print(f"Timestamp: {timestamp} \nStarting balance (source): {source._balance} \nStarting balance (target): {target._balance}\n")
        
        source._balance -= amount 
        target._balance += amount 

        self._outgoing[source_account_id] += amount 
        
        print(f"Timestamp: {timestamp} \nNew account balance (source): {source._balance} \nNew account balance (target): {target._balance}\n")

        return source._balance
    
    def top_spenders(self, timestamp: int, n: int) -> list[str]:

        #list of tuples: (account_id, outgoing_amount)
        data = [(acc._account_id, self._outgoing[acc._account_id]) 
                for acc in self._accounts_list]

        #outgoing desc, then account_id asc, return top n or fewere
        data.sort(key=lambda x: (-x[1], x[0]))
        data = data[:n]
        return [f"{acc_id}({amount})" for acc_id, amount in data]


    def _calculate_cashback(self, amount: int):
        return math.floor(amount * 0.02) # round down 
    

    def _process_cash_back(self, curr_timestamp): 
        processed = [] 
        # look thru all pending items 
        for payment_id, data in self._pending_cashback.items(): # {payment_id : (timestamp, account_id, cashback_amount}
            if curr_timestamp >= data[0] + 86400000: # waiting period elapsed 
                account = self._find_account(data[1])
                account._balance += data[2]
                print(f"Cashback has been processed for account {account._account_id}")
                processed.append(payment_id) # mark for deletion 

        for p in processed: 
            del self._pending_cashback[payment_id] # remove payment from dict once processed 

    
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        account = self._find_account(account_id)

        # check: accounts exists 
        if account is None:
            print(f"Timestamp: {timestamp} | Error: Account '{account_id}' not found.")
            return None
        
        # check: funds are sufficient 
        if amount > account._balance:
            print(f"Timestamp: {timestamp} | Error: Insufficient funds, withdrawal {amount} exceeds account current balance.")
            return None
        
        # withdraw given amount from specified account 
        account._balance -= amount 

        # add functionality: top_spenders() to account for withdraws 
        self._outgoing[account_id] += amount 

        # successful withdrawals return string with unique payment_id
        self._transaction_number += 1 
        payment_id = "payment" + str(self._transaction_number)
        
        # add cashback 
        cashback_owed = self._calculate_cashback(amount)
        self._pending_cashback[payment_id] = (timestamp, account_id, cashback_owed) 
        
        # TODO: cashback must be processed before next transaction? 
        # TODO: how to trigger cashback processing?

        self._payment_ids[payment_id] = account_id # add new entry 
        print(f"Payment of {amount} to account {account_id} was successful | Payment ID: {payment_id}")

        return payment_id 
    
    
    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        account = self._find_account(account_id)

        # check: accounts exists 
        if account is None:
            print(f"Timestamp: {timestamp} | Error: Account '{account_id}' not found.")
            return None
        
        # check: payment exists 
        if payment not in self._payment_ids: 
            print(f"Timestamp: {timestamp} | Error: Could not find payment with payment ID {payment}")
            return None 

        # check: payment id / account id mismatches
        if self._payment_ids[payment] != account_id:
            print(f"Timestamp: {timestamp} | Error: Payment ID {payment} could not be located for account {account_id}")
            return None

        # in progress vs complete -> timestamp 
            # use unique payment ids?

        return None