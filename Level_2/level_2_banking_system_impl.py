#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 08:06:44 2025

@author: karaha
"""

from banking_system import BankingSystem

class Account:
    def __init__(self, timestamp: str, account_id: str):
        self._timestamp = timestamp
        self._account_id = account_id
        
        self._balance = 0

    #def get_account_id(self): return self._account_id
    
    def print_account_details(self):
        print(f"Timestamp: {self._timestamp}")
        print(f"Accound ID: {self._account_id}")
        print(f"Balance: {self._balance}\n")

class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        self._accounts_list = []
        
    def _find_account(self, account_id: str): 
        for account in self._accounts_list:
            if account_id == account._account_id:
                return account
        return None # if not account found 
    
    # helper function for testing only 
    def _all_accounts(self): 
        for account in self._accounts_list: 
            account.print_account_details()


    # TODO: implement interface methods here
    def create_account(self, timestamp: int, account_id: str) -> bool:
        new_account = Account(timestamp, account_id)
        
        # Require unique account_id
        for a in self._accounts_list: 
            if account_id == a._account_id: 
                print(f"Error: Account ID {account_id} already exists!")
                return False 
            
        self._accounts_list.append(new_account)
        print(f"New account successfully created! \nTimestamp: {timestamp} \nAccount ID: {account_id}\n")
        #print(len(self._accounts_list))
        return True

    
    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        #! Can allow negative numbers to represent withdraws? 
        if amount <= 0:
            print("Error: Please enter a valid amount.")
            return None
        
        target_account = self._find_account(account_id)
        print(f"Timestamp: {timestamp} \nStarting account balance: {target_account._balance}")
        target_account._balance += amount 
        print(f"Timestamp: {timestamp} \nNew account balance: {target_account._balance}\n")
        return None
        

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        if amount <= 0 or source_account_id == target_account_id:
            print("Error: Please enter a valid amount or source/target account IDs.")
            return None
        
        source = self._find_account(source_account_id)
        target = self._find_account(target_account_id)

        #! condition required to prevent "overdraft"?
        
        print(f"Timestamp: {timestamp} \nStarting balance (source): {source._balance} \nStarting balance (target): {target._balance}\n")
        source._balance -= amount 
        target._balance += amount 
        print(f"Timestamp: {timestamp} \nNew account balance (source): {source._balance} \nNew account balance (target): {target._balance}\n")
        return None
    
    