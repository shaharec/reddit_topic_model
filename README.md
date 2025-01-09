# Topic Modeling Project

This project involves applying topic modeling techniques to categorize Reddit posts by topic and analyze real-world events over time. The project is implemented using Python and Jupyter Notebook.

## Project Structure

```        
data/
    reddit_data.csv
Topic modeling.ipynb
```

## Components

1. **Data Cleaning**: Basic data cleaning techniques are applied to preprocess the Reddit posts.
2. **Topic Modeling**: A topic modeling approach is used to categorize posts by topic without using the subreddit column.
3. **Event Detection**: The topic modeling outputs are used to find real-world events in the data over time.
4. **Evaluation**: The topic modeling results are evaluated using the subreddit column.

## Instructions

### Prerequisites

- Python 3.x
- Jupyter Notebook
- Required Python libraries (listed in `requirements.txt`)

### Setup

1. Clone the repository.
2. Navigate to the project directory.
3. Install the required libraries:

```sh
pip install -r requirements.txt
```

### Running the Code

1. Open Jupyter Notebook:

```sh
jupyter notebook
```

2. Open the 

mana_assignment.ipynb

 notebook and run all cells to perform data cleaning, topic modeling, and evaluation.
3. Open the `Topic modeling.ipynb` notebook and run all cells to explore and preprocess the data, apply topic modeling, and visualize the results.

### Data

- `reddit_data.csv`: The original Reddit dataset, containing Reddit posts and subreddit data from 2008-2009.


### Notebooks

- `Topic modeling.ipynb`: Contains the main implementation of data cleaning, topic modeling, and evaluation.

## Key Functions

- `preprocess_text`: Preprocesses the text by removing URLs, emails, hashtags, and stopwords, and lemmatizing the text.
- `BERTopic`: Applies BERT-based topic modeling to extract topics from the cleaned text.

## Results

The results of the topic modeling and event detection are visualized in the notebooks. The evaluation of the topic modeling results using the subreddit column is also included.

## License

This project is licensed under the MIT License.

---
