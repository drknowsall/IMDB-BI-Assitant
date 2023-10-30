# IMDB-BI-Assitant
Table Question Answering
Query IMDB (non-commercial) dataset using ChatGPT

## Install:
git clone https://github.com/drknowsall/IMDB-BI-Assitant.git<br>
cd biassist
pip install -r requirements.txt<br>
Download the preprocessed dataset from:<br>

## Usage:
First prepare the OpenAI key
python bi_assist.py --api_key <API key>

## Design:
### A.  Preprocessed IMDB dataset:
  
  - Remove not relevant columns
  - Remove non english titles
  - Aggregate certain columns in order to enable more relevant queries
  - Index columns for faster queries

### B.  Infer:
  0. recieve question from the user
  1. Using a prompt request from ChatGPT the relevant query for the question
  2. Post process to remove certain tokens
  3. Run the query on the dataset
  4. Send the result dataframe to ChatGPT for a final answer
  5. Present the answer to the user

   
