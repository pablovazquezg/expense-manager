EXPENSE_CAT_TEMPLATE = """
    <context>
    You are an advanced data analysis model. Your task is to create a list of [description, category] lists, where in each list item:
    - the description is exactly the same you receive as input
    - the category most appropriate based on that description (see instructions below)
    </context>
    
    <categories>
    The following list contains the categories and keywords you often see in transaction descriptions:
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
    </categories>

    <output_formatting_instructions>
    Your output should be a valid list of lists (e.g. [[description1, category1], [description2, category2], ...]] parse-able by the command ast.literal_eval(output)
    Don't include any kind of commentary, return carriages, spaces or other characters in the output
    Fill all categories; if you don't know which one to choose, choose 'Other'
    </output_formatting_instructions>
    
    
    <financial_transactions>
    {input_data}
    </financial_transactions>"""

RELEVANT_COLS_TEMPLATE = """
    <context>
    You are an advanced AI data analysis model. Your task is to analyze the list of \
    column names you are receiving as an input and follow a list of instructions to \
    to produce a correctly formatted output.
    </context>

    <column_names>
    {input_data}
    <column_names>

    <instructions>
    Look at the input list and create a python list with the names that better match the following:
    1. date: the date of the transaction; if there are multiple columns with dates, choose just one
    2. description: information about the transaction (e.g. the name of the store)
    3. amount: the amount of the transaction; make sure you choose the 'amount' column and not the 'balance' column
    </instructions>
    

    <output_formatting_instructions>
    Your output must be a valid Python list and parse-able using the command ast.literal_eval(your response).
    All the items in the list must match exactly the names of the columns in the input data.
    Refrain from including any additional commentary or information in your output.
    Examples: ['date', 'description', 'amount']
    </output_formatting_instructions>
    """

CHECK_SPLIT_CREDITS_DEBITS = """
    <context>
    You are an advanced AI data analysis model. Your task is to analyze different lists of financial \
    transactions and follow a list of instructions to produce a correctly formatted output.
    </context>

    <financial_transactions>
    {input_data}
    </financial_transactions>

    <instructions>
    If there are two different columns for credits and debits, return a python list containing the names \
    of the columns containing the credits and debits, respectively (e.g. ['credit', 'debit']).
    If, on the other hand, there is only one column for both credits and debits, return an empty python list.
    </instructions>
    

    <output_formatting_instructions>
    Your output must be a valid Python list and parse-able using the command ast.literal_eval(your response).
    Refrain from including any additional commentary or information in your output.
    Examples: ['credit', 'debit'], []
    </output_formatting_instructions>
    """