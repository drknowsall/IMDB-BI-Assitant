import pandas as pd
from pandasql import sqldf
import numpy as np
import sys
import argparse

def detect_lang(s):
    try:
        return detect(s)
    except:
        return 'NA'
    
pysqldf = lambda q: sqldf(q, globals())
parser = argparse.ArgumentParser(description='BI Assitant')
parser.add_argument('-r','--max_rows', type=int, help='Maximum rows to read from the IMDB tables', required=False, default=sys.maxsize)
parser.add_argument('-p','--path', type=str, help='IMDB non commercial dataset path', required=False, default='data')
args = vars(parser.parse_args())
nrows = args['max_rows']
path = args['path']

print('Loading Data - It Will Take Some Time...')

title_basics_df = pd.read_table(f'{path}/title.basics.tsv', nrows=nrows) 
title_akas_df = pd.read_table(f'{path}/title.akas.tsv', nrows=nrows)  
title_crew_df = pd.read_table(f'{path}/title.crew.tsv', nrows=nrows) 
title_episode_df = pd.read_table(f'{path}/title.episode.tsv', nrows=nrows) 
title_principals_df = pd.read_table(f'{path}/title.principals.tsv', nrows=nrows) 
title_ratings_df = pd.read_table(f'{path}/title.ratings.tsv', nrows=nrows) 
name_basics_df = pd.read_table(f'{path}/name.basics.tsv', nrows=nrows) 

print('Done!')

# Remove all non relevant types
title_basics_df = title_basics_df[(title_basics_df.titleType == 'movie') | (title_basics_df.titleType == 'tvSeries') | (title_basics_df.titleType == 'tvMovie') | (title_basics_df.titleType == 'tvMiniSeries')]
name_basics_df.drop_duplicates(subset=['primaryName'], inplace=True)
print('Replacing \\N...')
title_basics_df=title_basics_df.replace(r'^\\N$', np.nan, regex=True)
title_akas_df=title_akas_df.replace(r'^\\N$', np.nan, regex=True)
title_crew_df=title_crew_df.replace(r'^\\N$', np.nan, regex=True)
title_episode_df=title_episode_df.replace(r'^\\N$', np.nan, regex=True)
title_ratings_df=title_ratings_df.replace(r'^\\N$', np.nan, regex=True)
name_basics_df=name_basics_df.replace(r'^\\N$', np.nan, regex=True)
title_basics_df[title_basics_df.runtimeMinutes == 'Reality-TV']=0

name_basics_df.dropna(subset=['primaryName'], inplace=True)
title_basics_df=title_basics_df.astype({
        "tconst": 'string',
        "titleType": 'string',
        "primaryTitle": 'string',
        "originalTitle": 'string',
        "isAdult": bool,
        "startYear": float,
        "endYear": float,
        "runtimeMinutes": float,
        "genres": "category"
    })
title_akas_df=title_akas_df.astype({
        "titleId": 'string',
        "ordering": 'int',
        "title": 'string',
        "region": 'string',
        "language": 'string',
        "types": "category",
        "attributes": "category",
        "isOriginalTitle": bool
    })
title_crew_df=title_crew_df.astype({
        "tconst": 'string',
        "directors": 'string',
        "writers": 'string'
    })

title_episode_df=title_episode_df.astype({
        "tconst": 'string',
        "parentTconst": 'string',
        "seasonNumber": float,
        "episodeNumber": float
    })
title_principals_df=title_principals_df.astype({
        "tconst": 'string',
        "ordering": int,
        "nconst": 'string',
        "category": 'string',
        "job": 'string',
        "characters": 'string'
    })
title_ratings_df=title_ratings_df.astype({
    "tconst": 'string',
    "averageRating": float,
    "numVotes": float
})

name_basics_df=name_basics_df.astype({
        "nconst": 'string',
        "primaryName": 'string',
        "birthYear": float,
        "deathYear": float,
        "primaryProfession": "category",
        "knownForTitles": "category"
    }) 

# Creating merged dataframes with all relevant data
print('Joining...')
# titles_df - title related data
columns = ['tconst', 'language', 'titleType', 'primaryTitle', 'isAdult', 'startYear', 'endYear', 'runtimeMinutes', 'genres']
titles_df = title_basics_df.merge(title_akas_df, right_on='titleId', left_on= "tconst", how='left')[columns]
titles_df.language = titles_df.language.fillna('NA')
language_agg = titles_df.groupby('tconst')['language'].agg(list).reset_index()

titles_df.drop('language', axis=1, inplace=True)

language_agg['language'] = language_agg['language'].apply(lambda x: ', '.join(x)).astype('category')
titles_df=titles_df.merge(language_agg, on = "tconst", how='left')

titles_df = titles_df.drop_duplicates()
columns += ['directors', 'writers']
titles_df = titles_df.merge(title_crew_df, on= "tconst", how='left')[columns]

titles_df.directors = titles_df.directors.fillna('NA')
titles_df.writers = titles_df.writers.fillna('NA')

writers_agg = titles_df.groupby('tconst')['writers'].agg(list).reset_index()
directors_agg = titles_df.groupby('tconst')['directors'].agg(list).reset_index()

titles_df.drop('directors', axis=1, inplace=True)

titles_df.drop('writers', axis=1, inplace=True)

titles_df = titles_df.drop_duplicates()

writers_agg['writers'] = writers_agg['writers'].apply(lambda x: ', '.join(x)).astype('category')
directors_agg['directors'] = directors_agg['directors'].apply(lambda x: ', '.join(x)).astype('category')
titles_df=titles_df.merge(writers_agg, on = "tconst", how='left')
titles_df=titles_df.merge(directors_agg, on = "tconst", how='left')

columns += ['averageRating', 'numVotes']
titles_df = titles_df.merge(title_ratings_df, on="tconst", how='left')[columns]

grouped = title_episode_df.groupby('parentTconst')

# Aggregate the number of episodes and seasons for each series
agg_data = grouped.agg({
    'seasonNumber': 'max',
    'episodeNumber': 'count'
}).reset_index()

# Rename the columns for clarity
agg_data = agg_data.rename(columns={
    'seasonNumber': 'NumberSeasons',
    'episodeNumber': 'NumberEpisodes'
})

columns += ['NumberSeasons', 'NumberEpisodes']

titles_df = titles_df.merge(agg_data, left_on='tconst', right_on= "parentTconst", how='left')[columns]

titles_df.rename(columns={'primaryTitle':'title'}, inplace=True)
titles_df.rename(columns={'tconst':'titleId'}, inplace=True)

title_principals_df = title_principals_df[(title_principals_df.category == 'actor') | (title_principals_df.category == 'actress')]

title_principals_df = title_principals_df[['characters', 'nconst', 'tconst']]
title_principals_df['characters']  = title_principals_df['characters'].astype('category')
name_basics_df = name_basics_df[['nconst', 'primaryName', 'birthYear', 'deathYear', 'knownForTitles']]

# Setting indexes for faster queries
print('Set Indexes...')
titles_df=titles_df.set_index(['titleId', 'titleType', 'title', 'NumberSeasons', 'NumberEpisodes', 'genres','startYear', 'endYear'], inplace=True)
title_principals_df.set_index(['tconst', 'nconst'], inplace=True)
name_basics_df.set_index(['nconst', 'primaryName', 'birthYear', 'deathYear'], inplace=True)

titles_df.to_csv('imdb_titles.csv', index_label=['titleId', 'titleType', 'title', 'NumberSeasons', 'NumberEpisodes', 'genres','startYear', 'endYear'])
title_principals_df.to_csv('imdb_actors_titles.csv', index_label=['tconst', 'nconst', 'characters'])
name_basics_df.to_csv('imdb_actors_details.csv', index_label=['nconst', 'primaryName', 'birthYear', 'deathYear', 'knownForTitles'])