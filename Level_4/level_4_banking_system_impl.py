import math

class Account:
    def __init__(self, timestamp: str, account_id: str):
        self._timestamp = timestamp
        self._account_id = account_id
        self._balance = 0

        #Track the balance history as dictionary: {key: timestamp, value: (account_id, balance at timestamp)}
        self._balance_history = {
            account_id: {
                timestamp : self._balance
            }
        }

        #Track accounts merged into current account as dictionary: {key: account_id, value: timestamp}
        self._merged_accounts = {}

    # helper function for testing only
    def print_account_details(self):
        print(f"Timestamp: {self._timestamp}")
        print(f"Account ID: {self._account_id}")
        print(f"Balance: {self._balance}\n")

class BankingSystemImpl:

    def __init__(self):
        self._accounts_list = []
        self._outgoing = {} # dict, track outgoing transfers + withdrawals

        self._transaction_number = 0 # counter to keep track of transaction number for unique transac id
        self._payment_ids = {} # dict(key: payment_id; value: account_id) -> track unique payment id's and corresponding account

        # track pending cash back as dict: {key: payment_id; value: [timestamp, account_id, cashback_amount, status]} \
        self._pending_cashback = {} # status is either "IN_PROGRESS" or "CASHBACK_RECEIVED"
        self._completed_cashback = {}

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

        self._process_cash_back(timestamp)

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

        #Add change from deposit to balance history
        account._balance_history[account_id][timestamp] = account._balance

        return account._balance


    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:

        self._process_cash_back(timestamp)

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

        #Add change to balance history for both source and target account
        source._balance_history[source_account_id][timestamp] = source._balance
        target._balance_history[target_account_id][timestamp] = target._balance

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
        processed = [] # track for removal

        # look thru all pending items
        for payment_id, data in self._pending_cashback.items(): # {payment_id : (timestamp, account_id, cashback_amount, status)}
            if curr_timestamp >= data[0] + 86400000: # waiting period elapsed
                account = self._find_account(data[1])
                account._balance += data[2]
                print(f"Cashback has been processed for account {account._account_id}")

                #Add change from processed cash back to balance history
                account._balance_history[data[1]][data[0] + 86400000] = account._balance

                # mark for deletion once processing is complete so no longer pending
                processed.append(payment_id)

                # move to completed with updated status
                self._completed_cashback[payment_id] = [data[0], data[1], data[2], "CASHBACK_RECEIVED"]

        for p in processed:
            del self._pending_cashback[p] # remove payment from dict once processed


    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:

        self._process_cash_back(timestamp)

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

        #Add change from withdraw to balance history
        account._balance_history[account_id][timestamp] = account._balance

        # added functionality: top_spenders() to account for withdrawals
        self._outgoing[account_id] += amount

        # successful withdrawals return string with unique payment_id
        self._transaction_number += 1
        payment_id = "payment" + str(self._transaction_number)
        self._payment_ids[payment_id] = account_id # add new entry
        print(f"Payment of {amount} to account {account_id} was successful | Payment ID: {payment_id}")

        # add cashback
        cashback_owed = self._calculate_cashback(amount)
        self._pending_cashback[payment_id] = [timestamp, account_id, cashback_owed, "IN_PROGRESS"]

        return payment_id


    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:

        self._process_cash_back(timestamp)

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

        # is waiting to be processed
        if payment in self._pending_cashback:
            return self._pending_cashback[payment][3]

        # has already been processed
        elif payment in self._completed_cashback:
            return self._completed_cashback[payment][3]

        # if not in either list (i.e., payment_id does not exist)
        else:
            return None

    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        #Check whether both account ids are the same
        if account_id_1 == account_id_2:
            return False

        account_1 = self._find_account(account_id_1)
        account_2 = self._find_account(account_id_2)

        #Check where both accounts exist
        if account_1 is None or account_2 is None:
            return False

        #Deposit balance from account 2 to account 1
        self.deposit(timestamp, account_id_1, account_2._balance)


        #Combine the total outgoing transactions for merged accounts
        self._outgoing[account_id_1] += self._outgoing[account_id_2]

        #Change pending cashbacks of account_id_2 to account_id_1
        for cashback_key in self._pending_cashback:
            if self._pending_cashback[cashback_key][1]== account_id_2:
                self._pending_cashback[cashback_key][1] = account_id_1

        #Change the payment transaction ids of account_id_2 to account_id_1
        for payment_key in self._payment_ids:
            if self._payment_ids[payment_key] == account_id_2:
                self._payment_ids[payment_key] = account_id_1

        #Combine balance histories of accounts
        for account_id_key in account_2._balance_history:
            account_1._balance_history[account_id_key] = account_2._balance_history[account_id_key]

        #Track the account being merged and any other previous merges
        account_1._merged_accounts[account_id_2] = timestamp
        for account_id_key in account_2._merged_accounts:
            account_1._merged_accounts[account_id_key] = account_2._merged_accounts[account_id_key]

        #Remove account_id_2 from system after the merge
        del self._outgoing[account_id_2]
        self._accounts_list.remove(account_2)

        return True

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int|None:
        account = None

        #Check if account_id is in acccount_list
        if account_id in self._accounts_list:
            account = self._find_account(account_id)
        #If it is not, check if account_id was merged into different account
        else:
            for each_account in self._accounts_list:
                if account_id in each_account._balance_history:
                    account = each_account

        #Check that a balance history was found for account_id or return None
        if account is None:
            return None

        #Edge case for time_at to check if time_at is after the account has been merged
        if account_id in account._merged_accounts and account._merged_accounts[account_id] <= time_at:
            return None

        #Edge case for time_at to check if account was created before time_at
        if list(account._balance_history[account_id].keys())[0] > time_at:
            return None

        #Process cash back before getting balance
        self._process_cash_back(time_at)

        #Variables to store account._balance_history and its keys
        balance_history = account._balance_history[account_id]
        balance_history_keys = list(balance_history.keys())

        #Iterate through each timestamp key in the balance history
        for index in range(len(balance_history_keys)):
            #Returns balance if timestamp is equal to time_at
            if balance_history_keys[index] == time_at:
                return balance_history[balance_history_keys[index]]
            #Returns balance at previous timestep if current timestep is greater than time_at
            #Python dictionaries are ordered
            elif time_at < balance_history_keys[index]:
                return balance_history[balance_history_keys[index - 1]]

        #Returns most recent balance in balance history if time_at is greater than
        if balance_history_keys[-1] < time_at:
            return balance_history[balance_history_keys[-1]]

        return None