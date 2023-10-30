# IMDB-BI-Assitant
Table Question Answering<br>
Query IMDB (non-commercial) dataset using ChatGPT

Example question:

How many movies are there in the dataset?
How many actors died last year?
What is the series with the most episodes?
In how many drama movies sean connary performed?
What is the highest rating movie and series?
What are the titles that sean connary is known for?',
How many movies were released last year?
How many actors were born in 2000?
What is the language of the movie "pulp fiction"?
             
## Install:
git clone https://github.com/drknowsall/IMDB-BI-Assitant.git<br>
cd biassist
mkdir data 
cd data

Download the preprocessed dataset from:<br>
gdown https://drive.google.com/file/d/1b0RR4BykPIBe8PMeGNueYGyM5vvggAG5/view?usp=sharing
Alternatively run: python preprocess_imdb_ds.py --path data

pip install -r requirements.txt<br>

## Usage:
Get your OpenAI key<br>
python bi_assist.py --api_key key

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

   
