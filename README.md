
<div align="center">
<h1 align="center">
<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" />
<br>
expense_manager
</h1>
<h3>◦ Manage your expenses with ease: Expense Manager!</h3>
<h3>◦ Developed with the software and tools listed below.</h3>

<p align="center">
<img src="https://img.shields.io/badge/GNU%20Bash-4EAA25.svg?style&logo=GNU-Bash&logoColor=white" alt="GNU%20Bash" />
<img src="https://img.shields.io/badge/OpenAI-412991.svg?style&logo=OpenAI&logoColor=white" alt="OpenAI" />
<img src="https://img.shields.io/badge/Python-3776AB.svg?style&logo=Python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style&logo=Docker&logoColor=white" alt="Docker" />
<img src="https://img.shields.io/badge/JSON-000000.svg?style&logo=JSON&logoColor=white" alt="JSON" />
<img src="https://img.shields.io/badge/Markdown-000000.svg?style&logo=Markdown&logoColor=white" alt="Markdown" />
</p>


---

## 📚 Table of Contents

- [� Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [⚙️ Features](#️-features)
- [📂 Project Structure](#-project-structure)
- [🧩 Modules](#-modules)
- [🚀 Getting Started](#-getting-started)
  - [✅ Prerequisites](#-prerequisites)
  - [🖥 Installation](#-installation)
  - [🤖 Using expense\_manager](#-using-expense_manager)
  - [🧪 Running Tests](#-running-tests)
- [📄 License](#-license)
- [👏 Acknowledgments](#-acknowledgments)

---

## 📍 Overview

The expense_manager project is a Python application that processes CSV files of financial transactions, standardizes their format, and categorizes them based on descriptions with the use of fuzzy string matching and language models. The application provides value by automating a tedious and error-prone task, reducing the time and effort required for financial data analysis. Additionally, its use of language models enables it to learn from new data, improving categorization accuracy over time.

---

## ⚙️ Features

Feature | Description |
|-----|-----|
| **🏗 Architecture** | The codebase follows a modular architecture that separates concerns and responsibilities into different files and functions. It uses Python's asyncio library for asynchronous processing to improve performance. The codebase also implements a language model for transaction categorization and fuzzy string matching for improved accuracy. |
| **📑 Documentation** | The codebase provides comments and docstrings to explain the purpose and functionality of each file and function. The repository also includes a README file with setup instructions and an overview of the application. However, some of the comments lack detail, and there is no documentation for some of the functions. |
| **🧩 Dependencies** | The codebase relies on several third-party libraries, including pandas, numpy, PyYAML, and langchain, a language modeling library used for transaction categorization. Dependencies are managed using pip and are listed in the requirements.txt file. The codebase also uses a Dockerfile for consistent development environments. |
| **♻️ Modularity** | The codebase follows a modular design pattern, separating code into smaller functions and files that can be reused and tested independently. There are clear separation of concerns between file processing, transaction categorization, and standardization. However, a few functions are longer than desirable and could be further broken down. |
| **✔️ Testing** | The codebase includes a test directory with unit tests for each function. The tests use the pytest testing framework and mock objects to simulate behavior. Tests are designed to run independently and can be run all together with the pytest command. Test coverage is not comprehensive, but it covers a significant portion of the codebase. |
| **⚡️ Performance** | The codebase uses the asyncio library for asynchronous processing and parallelism to improve performance when processing multiple files. It also uses langchain for language modeling and fuzzy string matching to improve the accuracy of transaction categorization. However, the codebase does not implement caching or other optimizations for improved performance. |
| **🔒 Security** | The codebase does not appear to have any significant security vulnerabilities. It does not handle user input, and file paths are constructed using pathlib to eliminate path traversals. The codebase does make use of environment variables and secret data, but they are loaded and used correctly. |
| **🔀 Version Control** | The codebase is version controlled using Git and hosted on GitHub. The repository includes a.gitignore file to exclude unnecessary files from version control. The Git commit messages are descriptive and follow a consistent format. |
| **🔌 Integrations** | The codebase does not appear to have any significant integrations with other systems or APIs. However, it does use langchain for language modeling and includes functions for integrating with other machine learning libraries.|
| **📈 Scalability** | The codebase's use of asyncio and langchain for parallel processing and language modeling provide

---

## 📂 Project Structure

---

## 🧩 Modules

<details closed><summary>.devcontainer</summary>

| File       | Summary                                                                                                                                                                                                                                                                                                                                                                                                                           | Module                   |
|:-----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------|
| Dockerfile | The provided code snippet is a Dockerfile which sets up a Python development environment. It sets the PYTHONUNBUFFERED environment variable to 1, installs Python 3.11 from Microsoft's devcontainers, and allows for the installation of OS packages and Python packages through the use of apt-get and pip3 commands. The sections for installing OS packages and Python requirements are currently commented out and optional. | .devcontainer/Dockerfile |

</details>

<details closed><summary>Logs</summary>

| File    | Summary                                                                                                                                                                                                                                                                                                             | Module       |
|:--------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------|
| app.log | The code snippet shows a series of error messages that occurred while attempting to extract transaction data. The errors range from the input file not matching any known format to a missing date column in the input data. The code suggests that there might be issues with the input data format and structure. | logs/app.log |

</details>

<details closed><summary>Root</summary>

| File     | Summary                                                                                                                                                                                                                                                                                                                                                                                 | Module   |
|:---------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| main.py  | This code snippet is a Python script that processes CSV files in a specified input folder asynchronously using asyncio. It configures logging, sets the debug level for langchain, and archives the processed files. The results are saved to an output file using the save_results function from the file_processing module. The script uses environment variables loaded with dotenv. | main.py  |
| setup.sh | The provided Bash script creates several directories needed for a data processing operation, including subfolders beneath "data" and a log folder with a corresponding app log file. The script uses the "mkdir" command to create these folders and "touch" to create the log file. Once completed, a success message is printed to the console.                                       | setup.sh |

</details>

<details closed><summary>Src</summary>

| File                  | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Module                    |
|:----------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------|
| temp.py               | The provided code snippet is a Python function that categorizes a list of financial transactions using a combination of fuzzy matching and a language model. The function reads and updates a reference file for transaction categorization. Any uncategorized transactions are sent to the language model, and new description-category pairs are added to the reference file. The function returns the original transaction list with an additional column for transaction category.                                                                                                                                                                                                                                    | src/temp.py               |
| file_processing.py    | The provided code snippet defines three functions used for processing, standardizing, and categorizing transaction data from input files. The "process_file" function reads and cleans the input file data, and then calls "categorize_tx_list" to categorize transaction data. The "standardize_tx_format" function standardizes the transaction data format, including dates, types, and amounts, and adds a source column to indicate the input file. The "save_results" function concatenates and writes valid transaction data to an output file, creates a reference file, and prints error messages for any invalid input files. Additionally, the "archive_files" function archives input files after processing. | src/file_processing.py    |
| config.py             | The code snippet defines data folders, string variations, LLM configuration, and log configuration for a transaction processing application. The string variations are used for identifying transaction data in input files, while LLM configuration controls how many transactions are processed in each run. Log configuration sets the log file and level for the application.                                                                                                                                                                                                                                                                                                                                         | src/config.py             |
| extract_tx_data.py    | The provided code snippet contains a function that analyses a transaction DataFrame and determines its format and column positions. It checks for columns containing date, description, amount, and credit/debit keywords and determines the format based on their presence and values. The function raises a ValueError if the DataFrame does not match any known format.                                                                                                                                                                                                                                                                                                                                                | src/extract_tx_data.py    |
| categorize_tx.py      | The provided code snippet contains functions for categorizing transaction descriptions using fuzzy string matching and a language model. The `fuzzy_match_list_categorizer` function finds the most similar known description and returns its associated category. The `llm_list_categorizer` function asynchronously processes a list of transactions using a language model and returns a DataFrame mapping descriptions to inferred categories. The `llm_sublist_categorizer` function categorizes a batch of transactions using the language model and retries on failure with exponential backoff.                                                                                                                   | src/categorize_tx.py      |
| categorize_tx_list.py | The provided code snippet defines a function for categorizing a list of transactions using a combination of fuzzy matching and a language model. The function uses a reference file to minimize API calls and adds new description-category pairs to the reference file. Uncategorized transactions are sent to the language model, and remaining NaN values in the'category' column are filled with'Other'.                                                                                                                                                                                                                                                                                                              | src/categorize_tx_list.py |
| templates.py          | This code provides a template for an advanced data analysis model to categorize a list of financial transactions based on keywords in their description. The template includes a list of categories and keywords commonly seen in transaction descriptions, as well as formatting instructions for the output. The input data should be included in the "financial_transactions" section of the template.                                                                                                                                                                                                                                                                                                                 | src/templates.py          |

</details>

---

## 🚀 Getting Started

### ✅ Prerequisites

Before you begin, ensure that you have the following prerequisites installed:
>
> - [ℹ️ Requirement 1]
> - [ℹ️ Requirement 2]
> - [...]

### 🖥 Installation

1. Clone the expense_manager repository:

```sh
git clone https://github.com/pablovazquezg/expense_manager.git
```

2. Change to the project directory:

```sh
cd expense_manager
```

3. Install the dependencies:

```sh
pip install -r requirements.txt
```

### 🤖 Using expense_manager

```sh
python main.py
```

### 🧪 Running Tests

```sh
pytest
```

---

## 📄 License

This project is licensed under the `[ℹ️  MIT]` License. See the [LICENSE] file for additional info.

---

## 👏 Acknowledgments

> - [ℹ️  I may be a tiny little speck, but I stand on the shoulders of giants. From this position, I strive to build good things and leave my corner of the world just a little better than how I found it. I would like to express my heartfelt thanks to the talented folks working hard at Langchain. I would also like to extend my gratitude to all those brave souls who have contributed to the libraries used by this project and to the Python programming language itself. Hat tip to you all!
]

---
