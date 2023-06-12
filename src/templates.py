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

RELEVANT_COLS_TEMPLATE = """Execute the following three steps:
    [STEP 1: Analyze the list of transactions below and find the columns that contain the following information]
    - date: typically the column labeled 'Date' or 'Transaction Date'
    - description: select the column that contains the transaction description (groceries, travel, etc.), not the transaction type (debit, credit, etc.). This column is sometimes labeled 'Description' or 'Transaction Description'.
    - amount: this is the amount of the transaction; often it is a negative number for debits and a positive number for credits. This column is sometimes labeled 'Amount' or 'Transaction Amount'.
    - type: this is the type of transaction (debit, credit, etc.); it sometimes contains only the first letter of the type (D, C, etc.). If you are not sure, then don't include this column (e.g. the output should have only three items)
    
    [LIST OF TRANSACTIONS]
    {tx_list}
    
    [STEP 2: Verify your answer column by column and ensure they are correct]

    [STEP 3: Format your answer]
    Give me an array containing only the names of the columns. Your output should consist of one valid python list parse-able by the command ast.literal_eval(your response). Don't include any commentary or anything other info in the output.
     
    [VALID PYTHON ARRAY EXAMPLES]
    ['Date', 'Description', 'Amount'], ['date', 'description', 'amount', 'type']"""

FIX_OUTPUT_TEMPLATE = """The output you provided is not valid. Please follow this instructions to fix it:
    - Your output should be a valid list of lists (e.g. [[(]description1, category1], [description2, category2), ...]] parse-able by the command ast.literal_eval(output)
    - Don't include any kind of commentary or other characters in the output
    - If you see a valid list of lists in these results, return it and discard other elements"""

CHECK_SPLIT_CREDITS_DEBITS = """There are two types of files:
    - Files where the transaction amount is in a single column (e.g. 'Amount')
    - Files where the transaction amounts are split in two columns (e.g. 'Debit' and 'Credit')

    You are a senior financial analyst. Your job is to look at the list of transactions below, \
    determine which type of file you have, and return a python list following the instructions below:
    - If the amount is in a single column, return an empty list (e.g. [])
    - If the amount is split in two columns, return a list with the names of those two columns that contain transaction amounts (e.g. ['Debit', 'Credit'])
    
    [LIST OF FINANCIAL TRANSACTIONS]
    {tx_list}
    
    [FORMATTING INSTRUCTIONS]
    - Your output should be a valid python list parse-able by the command ast.literal_eval(output)
    - Don't include any kind of commentary or other characters in the output
    - If your output contains any column names, it's important to ensure those columns exist in the input data
    - Your output should be either an empty list of a list with two strings. Examples: [], ['Debit', 'Credit']"""