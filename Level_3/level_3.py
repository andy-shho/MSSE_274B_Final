"""
lve 3
scheduling payments with some cashbacks and
checking the status of the scheduled payments


"""
#need 
from Level_1.banking_system import BankingSystem

class Account:
    def __init__(self, timestamp: str, account_id: str):
        self._timestamp = timestamp
        self._account_id = account_id
        
        self._balance = 0 

    def print_account_details(self):
        print(f"Timestamp:{self._timestamp}")
        print(f"Account id: {self._account_id}")
        print(f"Balance: {self._balance}\n")

class BankingSystemImpl(BankingSystem):
    def __init__(self):
        self._accounts_list =[]
        self._withdraw =0 #withdraws from payment ids
        self._schedule = {}
        self._withdraw_total = {} #depends account_id

        def _find_account(self, account_id:str):
            for account in self._accounts_list:
                if account._account_id == account_id:
                    return account
            return None
        
        def _all_accounts(self):
            for account in self._accounts_list:
                account.print_account_details()

        def _cashbacks_due(self,timestamp:int):
            if timestamp not in self._schedule:
                return
            pending_list = self._schedule.pop(timestamp)
            for account_id, cashback_amount in pending_list:
                account = self._find_account(account_id)
                if account is not None:
                    account._balance += cashback_amount
                    #print(f"amount not valid {cashback_amount}")

        def create_account(self,timestamp:int, account_id:str) -> bool:
            if self._find_account(account_id) is not None:
                print(f"not valid: account id {account_id} already exists")
                return False
            new_account = Account(timestamp, account_id)
            self._accounts_list.append(new_account)
            print(f"new account created")
            print(f"\ntimestamp ⌚{timestamp}\n account id: {account_id}\n")
            return True
     """   
    #level 2 deposit: need to transfer into new schedule account
        #def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        #! Can allow negative numbers to represent withdraws? 
        #if amount <= 0:
            print("Error: Please enter a valid amount.")
            return None
        
        target_account = self._find_account(account_id)
        print(f"Timestamp: {timestamp} \nStarting account balance: {target_account._balance}")
        target_account._balance += amount 
        print(f"Timestamp: {timestamp} \nNew account balance: {target_account._balance}\n")
        return None
        """
    
    def deposit(self, timestamp:int, account_id:str, amount:int) -> int:
        self._process_due_cashbacks(timestamp)
        if amount <= 0 or source_account_id == target_account_id:
            print("error: please enter valid source id")
            return None
        source = self._find_account(source_account_id)
        target = self._find_account(target_account_id)


    if source._balance < amount:
        print(f"⌚{timestamp}\n transfer complete!")
        print(f"new balance: {source._balance} -> \n new target balance: {target._balance}\n")
        return None
    
    #payment/cashbacks from accounts