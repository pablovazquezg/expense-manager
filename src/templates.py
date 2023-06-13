EXPENSE_CAT_TEMPLATE = """Create a list of [description, category] lists, where in each list item:
    - the description is exactly the same you receive as input
    - the category most appropriate based on that description (see instructions below)

    [LIST OF CATEGORIES]
    The following list contains the categories  and keywords you often see in transaction descriptions:
    -ATM: atm, cash, withdraw
    -Auto: auto body
    -Bars: bar, pubs, irish, brewery
    -Beauty: body
    -Clothing: clothing, shoes, accessories
    -Coffee Shops: coffee, cafe, tea, Starbucks, Dunkin
    -Credit Card Payment: card payment
    -Dry Cleaning: cleaners, dry, cleaning
    -Education: kindle, tuition
    -Entertainment: event, show, movies, cinema, theater
    -Fees: Fee
    -Food: snack, Donalds, Burger King, KFC, Subway, Pizza, Domino, Taco Bell, Wendy, Chick-fil-A, Popeyes, Arby's, Chipotle
    -Fuel: fuel, gas, petrol
    -Gifts: donation, gift
    -Groceries: groceries, supermarket, food
    -Gym: gym, fitness, yoga, pilates, crossfit
    -Home: Ikea
    -Housing: rent, mortgage
    -Income: refund, deposit, paycheck, cashback, reward
    -Insurance: insurance
    -Medical: medical, doctor, dentist, hospital, clinic
    -Pets: vet, veterinary, pet, dog, cat
    -Pharmacy: pharmacy, drugstore, cvs, walgreens, rite aid, duane
    -Restaurants: restaurant, lunch, dinner
    -Shopping: shopping, amazon, walmart, target, safeway
    -Streaming: Netflix, Spotify, Hulu, HBO
    -Taxes: tax, irs
    -Technology: technology, software, hardware, electronics
    -Transportation: bus, train, subway, metro, airline, uber, lyft, taxi
    -Travel: travel, holiday, trip, airbnb, hotel, hostel, resort, kiwi, kayak, expedia, booking.com
    -Transfer: payment from
    -Utilities: electricity, water, gas, phone, internet
    -Other: use this when very uncertain about the category


    [FORMATTING INSTRUCTIONS]
    Your output should be a valid list of lists (e.g. [[description1, category1], [description2, category2], ...]] parse-able by the command ast.literal_eval(output)
    Don't include any kind of commentary, return carriages, spaces or other characters in the output
    Fill all categories; if you don't know which one to choose, choose 'Other'

    
    
    [LIST OF TRANSACTIONS]
    {tx_descriptions}"""

RELEVANT_COLS_TEMPLATE = """You are an advanced AI model. Your task is to follow the two \
following steps, and return a correctly formatted output (see instructions below).
[STEP 1]
Analyze this dataset and identify the four columns that contain the following key information:

'date': This columns is often labeled 'Date' or 'Transaction Date'. If there are multiple date columns, choose only the most appropriate.
'description': This column contains details about the transaction, such as 'groceries' or 'travel'. It does not refer to the transaction type. The column is often labeled as 'Description' or 'Transaction Description'.
'amount': This column reflects the amount involved in the transaction. Debits usually appear as negative numbers and credits as positive. The column is often labeled 'Amount' or 'Transaction Amount'.
'type': This column indicates the type of transaction, such as 'debit', 'credit', etc. In some instances, it may contain only the initial letter of the type, like 'D' for debit or 'C' for credit. \
If you're uncertain about this column, do not include it in your output.

[STEP 2: Create your answer]
Return a python list containing the names of the three or four columns you identified in STEP 1. \

[OUTPUT FORMATTING INSTRUCTIONS]
Ensure every name in your output list is in fact a column name in the data. \
The list must be valid Python syntax and should be parse-able using the command ast.literal_eval(your response). \
Refrain from including any additional commentary or information in your output."""

FIX_OUTPUT_TEMPLATE = """The output you provided is not valid. Please follow this instructions to fix it:
    - Your output should be a valid list of lists (e.g. [[(]description1, category1], [description2, category2), ...]] parse-able by the command ast.literal_eval(output)
    - Don't include any kind of commentary or other characters in the output
    - If you see a valid list of lists in these results, return it and discard other elements"""

CHECK_SPLIT_CREDITS_DEBITS = """You are an advanced AI model and you are tasked with following three steps. \
    Take your time and think step by step: \
    [STEP 1]
    Analyze this list of financial transactions, and determine if the transaction amounts are \
    under one column, or if they are split between two columns (one for credits and one for debits).

    [STEP 2]
    If the amounts are split between two columns, return a python list that contains the names of those two columns. On the \
    contrary, if the amounts are under one column, return an empty python list (i.e. []). \
    
    [OUTPUT FORMATTING INSTRUCTIONS]
    Your output must be a valid Python list and parse-able using the command ast.literal_eval(your response). \
    Refrain from including any additional commentary or information in your output."""