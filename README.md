# BookOfLife
Final project for MGT 802. Low-effort journal using generative AI. By Neil Mathew.

## About
So many moments of our lives go forgotten. We rarely remember that peaceful park walk or that time listening to a nostalgic song a few weeks ago. Journaling offers a solution, but demands both time and effort. The Book of Life app helps people make journal entries in seconds by generating a PDF for them based on a few key responses. 

## Installation
Download this Github repository and create a file called "credentials.py" in the repo with a field called OPENAI_API_KEY. Insert your api key for Open AI as a string here. To run the program, install the Python packages listed below in your environment and then execute "streamlit run app.py" in the terminal.

## Packages
- streamlit
- langchain
- weasyprint
- openai

## Future
Now that the basic prototype of the app has been created, many new features can be added in the near future. I hope to eventually add a map to the journal entry with markers for every location a person visited. I also hope to help people view trends over time i.e. the ratings of their days in a given week, who they spent time with the most, etc.
