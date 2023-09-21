from datetime import datetime
import random ,pytz



class supporter:
    #get_indian time as time and date 
    get_india_datetime = lambda: (datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S'), datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y'))
    
    #transaction_id_generator
    transaction_id_generator = lambda: f"{int(datetime.now().timestamp())}-{random.randint(1, 100000)}"

class Questions:
    stock_questions = { 1: ("Enter the STOCK Imported", "STOCK"),
                        2: ("how many EMPTIES are returned", "EMPTIES"),
                        3: ("How many cans of DEPOSIT", "DEPOSIT"),
                        4: ("How many Damaged cans returned", "DAMAGE RETURN")}


    finance_questions = {
        "deduct available amount": ("Please input the amount you'd like to deduct from the available balance.", "available_amount"),
        "ecommerce amount received": ("Enter the amount you wish to deduct from your E-commerce funds.","e_commerce"),
        "deduct on_hold amount": ("Specify the amount you want to deduct from the On Hold Amount.","On_hold_amount"),
        "deduct expenses": ("Provide the amount you intend to deduct from your expenses.","Total_Expensives"),
        "deduct Deposit": ("How many cans should be subtracted from the Deposit can count?","Deposit")
    }
