<br/>

<div align="center" style="margin: 30px;">
<a href="cost-estimates">
  <img src="https://github.com/pablovazquezg/expense_manager/blob/master/media/cost_estimates.png"  align="left" />
</a>
<br />
<br />

<div align="center">
    <a href="https://refine.dev">Home Page</a> |
    <a href="https://discord.gg/refine">Discord</a> |
    <a href="https://refine.dev/examples/">Examples</a> |
    <a href="https://refine.dev/blog/">Blog</a> |
    <a href="https://refine.dev/docs/">Documentation</a>
</div>
</div>

<br />

# Expense Manager ![Static Badge](https://img.shields.io/badge/Made_with_love_in-NYC-red)

> `expense-manager` is a utility that consolidates and categorizes all your income/expenses, and helps you get a clear picture of where your money comes from, and where it goes 



#TODO: Add logo and .gif file
#TODO: Install requirements
#TODO: Add info re token usage


![Shallow Backup GIF Demo](img/shallow-backup-demo.gif)

## Contents

 * [What is this?](#what-is-this) 
 * [What can it do for me?](#what-can-it-do-for-me)
 * [How does it work?](#how-does-it-work)
 * [How can I use it?](#how-can-i-use-it)
 * [What else should I know?](#what-else-should-i-know)
 * [License (MIT)](#git-integration)


## What is this?
If you are here, you probably want me to give you the basics about `expense-manager`. In short, it is a free utility that can:
1. **Read all those account activity .csv files** you download from your bank and credit card companies (even if they are in different formats)

2. **Consolidate all your transactions** into a single, standardized view

3. **Assign a type (i.e. credit/debit) and a category** (e.g. groceries) to each of them (it comes with standard category list, which you could customize to meet your needs) which allows you to **see exactly where your money comes from, and where it goes**


## WHY would I use this?
You want to know what's in for you, so you can decide if you should keep reading or leave now; I'll help you decide in three paragraphs:

`Context`: You find value in understanding how much money you are making, how much you are spending, and in which categories. It makes you feel in control, increases your financial awareness, and helps you gradually refine/improve your decision-making abilities. In other words, it contributes to your meta-goal in life: slowly but surely steer reality towards outcomes ranking higher in your personal preferences.

`Problem`: Your financial life has become quite complex, and you use multiple banking accounts and credit cards over any given period. You can easily download the activity/transactions for any of them, but **the .csv files you get are in slightly different formats**, and they either don't categorize your expenses, or they do but using different "buckets" and hierarchies. Consolidating all this information manually is time-consuming and error prone, and **you end up not doing it for months at a time or at all**.

`Solution:` With this utility, **you simply download the transactions for the period you want to analyze** (last month, year-to-date, last year, etc.), you drop the files in the input folder, you run a script, **and voilà!, you get a beautiful consolidated list with all the expenses categorized consistently**. This list is in .csv format, so you can easily analyze it using a tool like Excel (see the [What else should I know?](#what-else-should-i-know) section to see what I do)

## HOW does it work?

This sounds interesting and you want to know more right? You've come to the right section:
### Prerequisites
+ Python 3
+ OpenAI API key added to your environment variables ([instructions](https://www.immersivelimit.com/tutorials/adding-your-openai-api-key-to-system-environment-variables))
+ These dependencies will be installed by the setup script:
    - `openai, langchain, tenacity, pydantic`: used to make and validate LLM API calls
    - `rapidfuzz`: used to find similar descriptions that have been categorized in the past
    - `python-dotenv`: used to load environment variables; you know this one
    - `dateparser`: date standardization

### Process outline:
1. **Read all (.csv) files** from the input folder and extract the key information required from each transaction (date, type, description, amount).

1. **Consolidate all transactions** into a single list; this typically involves some level of data wrangling.

1. Transaction descriptions are sent in batches to an OpenAI LLM (gpt-3.5-turbo), which returns the **appropriate category for each transaction**; the category list can be customized -- see next section for details.

1. The new **description-category pairs** obtained from the LLM are **stored into a reference file**.

1. In all future runs, the utility first looks up each description in this reference file. If it finds one that is similar enough, it picks up the associated category and it moves on to the next transaction; **this materially reduces the number of API calls** required over time, since many transactions are repetitive in nature (we are creatures of habit).

1. The **final list** of categorized transactions is **saved into a .csv file**.  


> **NOTE:**
> `expense-manager` fully respects your privacy and doesn't collect any data at all. However, it does send the transaction descriptions (and only the descriptions) to an OpenAI LLM to obtain the associated category. OpenAI claims not to sell or use this data for any purposes, (starting on March 1st, 2023, not even to train their own models) but just be aware that's how the program works.


## HOW can I use it?
At this point you are sold and want to use this. Here's how to do it:
### Installation

```bash
$ git clone https://github.com/pablovazquezg/expense_manager.git
$ cd expense-manager
$ ./setup.sh
```


### Usage
---
+ Drop your .csv files in the `/data/tx_data/input` folder

+ If you want to add the new set of transactions to your historical file, you can simple run `expense-manager` now:
    ```bash
    python expense-manager.py
    ```
+ Alternatively, if you want to overwrite your historical file and create a new one, you can use the -n flag (n as in 'new'): 
    ```bash
    python expense-manager.py -n
    ```
> **NOTE:**
> Results are saved to the `/data/tx_data/output` folder

## What else should I know?
In case you don't already know, you can create a nice income/expense tracker very easily taking the output of the `expense-manager` and creating an Excel Pivot table with it; you can see an example [here](https://www.vertex42.com/blog/excel-tips/using-pivot-tables-to-analyze-income-and-expenses.html)

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)