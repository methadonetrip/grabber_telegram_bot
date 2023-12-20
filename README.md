**Telegram GRABBER Bot - README

Overview**
This Telegram Bot Parser is designed to interact with users, process channel data, and integrate with YooKassa for payment processing. It's built using Python and incorporates several modules for its operation.

Files Description
1. config.py
	•Purpose: Contains configuration settings for the bot.
	•Details:
	•MySQL database connection settings (host, user, password, db_name).
	•API settings including api_id, api_hash, and bot_token.
 
2. db.py
	•Purpose: Manages database operations.
	•Details:
	•Establishes a connection to the MySQL database.
	•Includes imports for pymysql and Pyrogram-related modules.
 
3. final.py
	•Purpose: The main script for the bot's functionality.
	•Details:
	•Imports necessary modules for text processing, database interaction, and bot operation.
	•Includes Pyrogram client setup and various bot functionalities like message handling and command processing.
 
4. yookassa_integration.py
	•Purpose: Handles integration with YooKassa payment service.
	•Details:
	•Class YooKassaIntegration to create payment requests and handle transactions.
	•Methods for payment creation and management.
 
5. requerments.txt
	•Purpose: Lists all the Python package dependencies.
	•Details:
	•Includes Pyrogram, pymysql, nltk, and other required packages.
	•Ensure all these packages are installed for proper bot operation.
 
Installation & Setup
	Install Dependencies:
	•Run pip install -r requerments.txt to install all necessary Python packages.
	Configuration:
	•Update config.py with your MySQL database and Telegram API credentials.
	Database Setup:
	•Ensure your MySQL database is set up according to the schema required by db.py.
	Running the Bot:
	•Execute final.py to start the bot.
 
Usage
	•The bot can process commands, interact with users, and handle channel data.
	•For payment processing, set up YooKassa details in yookassa_integration.py.
 
Note
	•Replace placeholders in config.py and yookassa_integration.py with your actual credentials.
