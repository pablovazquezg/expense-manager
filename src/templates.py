EXPENSE_CAT_TEMPLATE = """
    <context>
    You are an advanced data analysis model. Your task is to create a list of [description, category] lists, where in each list item:
    - the description is exactly the same you receive as input
    - the category of the transaction (choose one from the list below based on the description)
    </context>
    
    <categories>
    The following list contains the categories and associated keywords you often see in transaction descriptions:
    -ATM: atm, cash, withdraw
    -Auto: auto body
    -Bars: bar, pubs, irish, brewery
    -Beauty: body
    -Cashback: cashback, reward, bonus, cash back
    -Clothing: clothing, shoes, accessories
    -Coffee Shops: coffee, cafe, tea, Starbucks, Dunkin
    -Credit Card Payment: card payment, autopay
    -Education: kindle, tuition
    -Entertainment: event, show, movies, cinema, theater
    -Fees: Fee
    -Food: snack, Donalds, Burger King, KFC, Subway, Pizza, Domino, Taco Bell, Wendy, Chick-fil-A, Popeyes, Arby's, Chipotle
    -Fuel: fuel, gas, petrol
    -Gifts: donation, gift
    -Groceries: groceries, supermarket, food, familia
    -Gym: gym, fitness, yoga, pilates, crossfit
    -Home: Ikea
    -Housing: rent, mortgage
    -Income: refund, deposit, paycheck
    -Insurance: insurance
    -Medical: medical, doctor, dentist, hospital, clinic
    -Pets: vet, veterinary, pet, dog, cat
    -Pharmacy: pharmacy, drugstore, cvs, walgreens, rite aid, duane
    -Restaurants: restaurant, lunch, dinner
    -Services: service, laundry, dry cleaning
    -Shopping: shopping, amazon, walmart, target, safeway
    -Streaming: Netflix, Spotify, Hulu, HBO
    -Taxes: tax, irs
    -Technology: technology, software, hardware, electronics
    -Transportation: bus, train, subway, metro, airline, uber, lyft, taxi
    -Travel: travel, holiday, trip, airbnb, kiwi, hotel, hostel, resort, kiwi, kayak, expedia, booking.com
    -Transfer: payment from
    -Utilities: electricity, water, gas, ting, verizon, comcast, sprint, t-mobile, at&t, mint
    -Other: use this when very uncertain about the category
    </categories>

    <formatting_instructions>
    Your output should be a valid list of lists (e.g. [[description1, category1], [description2, category2], ...]] parse-able by the command ast.literal_eval(output)
    Don't include any kind of commentary, return carriages, spaces or other characters in the output
    Fill all categories; if you don't know which one to choose, choose 'Other'
    </formatting_instructions>
    
    
    <financial_transactions>
    {input_data}
    </financial_transactions>"""