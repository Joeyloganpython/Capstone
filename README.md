# Opioid Overdose Analysis


## Project Overview
The goal of the project is to get overdose data from CDC, PA and other states in order to analyze drug overdose, and the relationship between the use of Naloxone and survival rate. It was created as a Capstone project for the the Master of Science in Data Science program at Drexel University

## Setup
1. Create a virtual environment:
    ```
    python3 -m venv [name]
    ```

2. Change directory to the new environment and clone repository
    ```
    cd [name]
    ```

3. Activate the virtual environment running the following command:
    ```
    # On macOS
    source ./bin/activate
    ```

4. Run the following command to install requirements:
    ```
    pip install -r requirements.txt
    ```
5. Generate new API Keys (Census, and PAGOV), and store them as environment variables:
    - On macOS open terminal and run the following:
        ```
        open ~/.bash_profile
        ```
      This command will open the file in a text edit. Simply add the following lines to the end of file:
        ```
        export CENSUS_API_KEY={Your Census key}
        export SOCRATA_APP_TOKEN={Your Socrata key}
        ```
      Then, save the file and run the following command in the terminal:
        ```
        source ~/.bash_profile
        ```
      To make sure it worked run the following command in the terminal:
        ```
        echo $CENSUS_API_KEY
        ```
      It should print the api key.

    - On Windows simply run the following command in CMD:
        ```
        setx CENSUS_API_KEY {Your Census API Key} /m
        setx SOCRATA_APP_TOKEN {Your Socrata API Key} /m
        ```
      To make sure it worked run the following command in CMD:
        ```
        set CENSUS_API_KEY
        ```
      It should print the api key.
