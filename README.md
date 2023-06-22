# Expense Manager

Expense Manager is a Python application that helps manage personal expenses. It takes multiple personal expense files in CSV format, converts them to a standardized format, and uses a language model to categorize the expenses based on user-defined categories.

## Features

- **CSV File Processing**: The application can process multiple CSV files containing personal expense data. It supports both lowercase and uppercase file extensions (`.csv` and `.CSV`).
- **Standardized Format**: The application converts the input files to a standardized format suitable for further processing. It performs cleaning, standardization, and categorization of the expense data.
- **Language Model Integration**: Expense Manager leverages the power of the LangChain language model library for expense categorization. It uses a pre-trained language model to analyze the expense descriptions and assign appropriate categories.
- **User-Defined Categories**: Users can customize the expense categories used for classification. The application supports a user-defined category list, allowing flexibility in categorizing expenses based on individual preferences.
- **Output Generation**: The processed expense data is saved to an output file in CSV format. The output file contains the standardized expense information, including the date, description, amount, and assigned category.
- **File Archiving**: The application archives the processed input files for record-keeping purposes. The archived files are moved to a designated archive folder, ensuring a clean and organized workspace.

## Dependencies

The Expense Manager application relies on the following dependencies:

- `dotenv`: A Python library for loading environment variables from a `.env` file.
- `langchain`: A language model library used for expense categorization.
- `pandas`: A powerful data manipulation library for working with tabular data.
- `dateparser`: A library for parsing various date formats.

## Usage

To use the Expense Manager application, follow these steps:

1. Ensure that Python is installed on your system.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Create a folder to hold your personal expense CSV files.
4. Customize the expense categories by modifying the `config.py` file.
5. Place your personal expense CSV files inside the designated folder.
6. Open a terminal or command prompt and navigate to the Expense Manager directory.
7. Run the application by executing `python main.py`.
8. The application will process the CSV files, categorize the expenses, and generate an output file with the results.
9. The processed input files will be archived in a separate folder for record-keeping.

**Note**: Make sure to update the `TX_INPUT_FOLDER`, `TX_ARCHIVE_FOLDER`, `LOG_FILE`, and other relevant configurations in the `config.py` file to match your system setup.

## Configuration

The Expense Manager application provides configuration options in the `config.py` file. You can customize the following settings:

- `TX_INPUT_FOLDER`: The folder path where your personal expense CSV files are located.
- `TX_ARCHIVE_FOLDER`: The folder path where the processed input files will be archived.
- `LOG_FILE`: The file path for the application's log file.
- `LOG_LEVEL`: The logging level for the application's log messages.
- Other relevant configurations related to categories and file extensions.

## File Structure

The Expense Manager application follows a modular file structure to organize its functionality. The key modules and their responsibilities are as follows:

- `main.py`: The main entry point of the application. It initializes the environment, processes the CSV files, saves the results, and archives the input files.
- `file_processing.py`: Contains functions for processing the CSV files, cleaning and standardizing the expense data, and performing expense categorization.
- `config.py`: Stores the configuration settings for the application, including folder paths
