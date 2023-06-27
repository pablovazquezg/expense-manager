![Expense Generator Logo](https://github.com/pablovazquezg/expense_manager/blob/master/media/readmemd-header.png)

# Expense Manager ![Static Badge](https://img.shields.io/badge/Made_with_love_in-NYC-red)

> **`expense-manager` is an LLM-powered utility** that can consolidate and categorize all your personal financial transactions and **helps you get a clear picture of where your money comes from, and where it goes 💸**



## Contents
  - [What is this?](#what-is-this)
  - [What can it do for me?](#what-can-it-do-for-me)
  - [How does it work?](#how-does-it-work)
  - [How can I use it?](#how-can-i-use-it)
  - [What else should I know?](#what-else-should-i-know)
  - [License](#license)

## What is this?
**`expense-manager` is an LLM-powered utility** that can consolidate and categorize all your personal financial transactions (both income and expenses). To use it, you just need those transactions in .csv files, which you can typically download directly from your different financial accounts (see an example [here](https://github.com/pablovazquezg/expense_manager/blob/master/media/account_activity_example.csv))

Next, you pass those files to the `expense-manager`, which automatically consolidates them into a single view, and assigns a category to each of their transactions choosing from a common, standardized category list (which you could customize as needed). 
## What can it do for me?
You want to know what's in for you, so you can decide if you should keep reading or leave now; I'll help you decide in three paragraphs:

ℹ️ **Context:** Knowing exactly how much money you are making and spending (in each category) increases your financial awareness and helps you gradually refine/improve your decision-making abilities. This contributes to your meta-goal in life: slowly but surely steer reality towards outcomes ranking higher in your personal preferences.

🚩 **Problem:** Your financial life has become quite complex, and you use multiple banking accounts and credit cards over any given period. You can easily download the activity/transactions for any of them, but **the .csv files you get are in slightly different formats**, and they either don't categorize your expenses, or they do but using different "buckets" and hierarchies. Consolidating all this information manually is **time-consuming and error prone, and you end up not doing it for months at a time or at all**.

🔥 **Solution:** With `expense-manager`, **you can just download the transactions for the period you want to analyze** (last month, year-to-date, last year, etc.), drop the files in the input folder, **run a script, and voilà!, you get a beautiful consolidated list with all the expenses categorized consistently**. This output will look like [this](https://github.com/pablovazquezg/expense_manager/blob/master/media/output-example.png) and will be in .csv format, allowing you to further analize it using a tool like Excel (see the [What else should I know?](#what-else-should-i-know) to see how).

## How does it work?

This sounds interesting and you want to know more right? You've come to the right section:
### Prerequisites
- Python 3
- OpenAI API key added to your environment variables ([instructions](https://www.immersivelimit.com/tutorials/adding-your-openai-api-key-to-system-environment-variables))
- These dependencies will be installed by the setup script:
    - `openai, langchain, tenacity, pydantic`: used to make and validate LLM API calls
    - `rapidfuzz`: used to find similar descriptions that have been categorized in the past
    - `python-dotenv`: used to load environment variables; you know this one
    - `dateparser`: date standardization

### Process outline:

1. **Read all (.csv) files** from the input folder and extract the key information required from each transaction (date, type, description, amount).

1. **Consolidate all transactions** into a single list; this typically involves some level of data wrangling.

1. Transaction descriptions are sent in batches to an OpenAI LLM (gpt-3.5-turbo), which returns the **appropriate category for each transaction**; the category list can be customized -- see the [What else should I know?](#what-else-should-i-know) section for details.

1. The new **description-category pairs** obtained from the LLM are **stored into a reference file**.

1. In all future runs, the utility first looks up each description in this reference file. If it finds one that is similar enough, it picks up the associated category and it moves on to the next transaction; **this materially reduces the number of API calls** required over time, since many transactions are repetitive in nature (we are creatures of habit).

1. The **final list** of categorized transactions is **saved into a .csv file**.  


> **NOTE:**
> `expense-manager` fully respects your privacy and doesn't collect any data at all. However, it does send the transaction descriptions (and only the descriptions) to an OpenAI LLM to obtain the associated category. OpenAI claims not to sell or use this data for any purposes, (starting on March 1st, 2023, not even to train their own models) but just be aware that's how the program works.

### Cost estimates
The OpenAI API cost per run will depend on two factors:
1. Total number of calls required
1. Cost per call, which will depend on the number of tokens per call, and the price per token (established by OpenAI)

As a point of reference, I've been using this for my own purposes with data from around 10+ different US institutions, and the average call has required around 1300 tokens. This includes both the prompt and the completion required to process 10 transactions, since we send 10 descriptions to the LLM in each call.

This means that in theory, the cost of processing a month of transactions will be around 6 to 13 cents (assuming 250 - 500 transactions per month; see table below for details). In practice the cost should be lower, since `expense-manager` will not invoke the LLM if it has seen a similar transaction before (go back to the [Process outline section](#process-outline) for details)

> NOTE: These estimates are based on the pricing of the `gpt-3.5-turbo` model as of July 1st 2023 ($0.002 / 1K tokens)

![API Cost Estimates](https://github.com/pablovazquezg/expense_manager/blob/master/media/cost_estimates.png)

## How can I use it?
At this point you are sold and want to use `expense-manager`. Here's how to do it:
### Installation
**Step 1:** Clone the repository and `cd` into the `expense-manager` folder:
```bash
git clone https://github.com/pablovazquezg/expense_manager.git
cd expense-manager
```
**Step 2:** Execute the `setup.sh` script:
```bash
./setup.sh
```


### Usage

**Step 1:** Drop your .csv file(s) in the `/data/tx_data/input` folder

**Step 2:** Run `expense-manager`:

```bash
python expense-manager.py
```

By default, `expense-manager` will append its output to its previous output, effectively creating a historical view of your transactions. To create a new file instead, use the `-n` flag (n as in 'new'):

```bash
python expense-manager.py -n
```

> **NOTE:**
> The output file is saved to the `/data/tx_data/output` folder
> 

<br/>

By default, input files will be moved from `/data/tx_data/input` to `/data/tx_data/archive` after each execution; if you prefer to delete them instead, you can do that using the `-d` flag (as in 'delete'). **Please note this will also delete files processed in previous executions.**

```bash
python expense-manager.py -d
```

Last but not least, you can combine the `-n` (create new file) and the `-d` (delete / don't archive) flags

```bash
python expense-manager.py -nd
```
    

## What else should I know?
- You can very easily use the output you receive from `expense-manager` to create a nice income/expense tracker that puts you back in charge of your personal finances; example [here](https://www.vertex42.com/blog/excel-tips/using-pivot-tables-to-analyze-income-and-expenses.html)
- The description-category pairs obtained from the LLM are stored in `/data/ref_data/ref_master_data.csv`. If in the future you want `expense-manager` to pick a different category for a specific description, you can simply update this file
- `expense-manager` automatically detects and supports American (1,234.56) and European formats (1.234,56), as well as many different date formats
- If you want to update the income/expense categories (or their associated keywords), you can do that in the `<categories>` section of the `/src/templates.py` file
- If there are execution errors, they will be loggged in the `/logs` folder

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)