# Importing libraries
import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from weasyprint import HTML
from datetime import datetime
import credentials
import os
import openai

# Setting API keys
openai.api_key = credentials.OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = credentials.OPENAI_API_KEY
apikey = credentials.OPENAI_API_KEY

st.set_page_config(page_title="Book of Life", page_icon="📘")

# Initialize the session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'result_answers' not in st.session_state:
    st.session_state.result_answers = ''


def go_to_form():  # Navigates to form page
    st.session_state.page = 'form'


def go_to_result():  # Navigates to result page
    st.session_state.page = 'result'


# Defines prompts for how answers should be generated based on form
def handle_form_submission(input_object):
    quote_prompt = """
    Give me a famous quote from a famous figure which relates directly to the description below. It
    should ideally be a piece of wisdom or inspiration. It should preferably not be from an anonymous figure.
    Only return the quote and the figure who said it, NOT any part of the day description itself.
    Description: {day_description}
    """

    quote_template = PromptTemplate(
        template=quote_prompt,
        input_variables=["day_description"],
    )

    quote_final_prompt = quote_template.format(
        day_description=input_object['day_description'])

    llm = OpenAI(temperature=0.7)
    quote_of_the_day = llm(quote_final_prompt)

    summarization_prompt = """
    Summarize the day that is described below in about 150 words (a paragraph). Write in the point of view
    (either first person or second person) indicated below. Include a comment about the kind of day it was:
    busy, peaceful, enjoyable, etc.
    Point of View: {pov}
    Description: {day_description}
    """

    summarization_template = PromptTemplate(
        template=summarization_prompt,
        input_variables=["day_description", "pov"],
    )

    summarization_final_prompt = summarization_template.format(
        day_description=input_object['day_description'], pov=input_object['pov'])

    llm = OpenAI(temperature=0.7)
    day_summarization = llm(summarization_final_prompt)

    tasks_prompt = """
    Extract what tasks the user completed based on the description of his day below. The tasks should be 
    career/academic oriented and related to work in some sense. For example, going to dinner would not be 
    a task you should include. If the task list is empty, don't output anything. The tasks should be relatively 
    short. Each task should start with a verb in the past tense, to indicate that the task was completed. The output
    should be a comma separated list of tasks, where each task starts with a capital letter. Don't include a period at the end.
    Day: {day_description}
    """

    tasks_template = PromptTemplate(
        template=tasks_prompt,
        input_variables=["day_description"],
    )

    tasks_final_prompt = tasks_template.format(
        day_description=input_object['day_description'])

    llm = OpenAI(temperature=0.4)
    list_tasks = llm(tasks_final_prompt)
    list_tasks = list_tasks.split(", ")

    user_learning_prompt = """
    Give an interesting fact from the topic below that the user wants to learn about. 
    Topic: {user_learning}
    """

    user_learning_template = PromptTemplate(
        template=user_learning_prompt,
        input_variables=["user_learning"],
    )

    user_learning_final_prompt = user_learning_template.format(
        user_learning=input_object['user_learning'])

    llm = OpenAI(temperature=0.4)
    fun_fact = llm(user_learning_final_prompt)

    goals_prompt = """
    Reword the goals below in a sentence in the point of view listed below. Be encouraging.
    The first word in the sentence you output should be a verb. Include some advice about 
    how to achieve the goal in one or two more sentences as well.
    Point of View: {pov}
    Goals: {goals}
    """

    goals_template = PromptTemplate(
        template=goals_prompt,
        input_variables=["goals", "pov"],
    )

    goals_final_prompt = goals_template.format(
        goals=input_object['goals'], pov=input_object['pov'])

    llm = OpenAI(temperature=0.4)
    final_goals = llm(goals_final_prompt)

    # Save generated outputs for the session so they can still be accessed in result page
    output_object = {
        'name': input_object['name'],
        'month_day': input_object['month_day'],
        'current_year': input_object['current_year'],
        'day_rating': input_object['day_rating'],
        'day_summarization': day_summarization,
        'list_tasks': list_tasks,
        'quote_of_the_day': quote_of_the_day,
        'fun_fact': fun_fact,
        'final_goals': final_goals,
    }

    st.session_state.result_answers = output_object
    st.session_state.page = 'result'


# Display the welcome page
if st.session_state.page == 'welcome':
    col1, col2 = st.columns(2)

    # Design structure for home page
    with col1:
        st.title("Book of Life")
        st.write(
            'Welcome to Book of Life. Use the power of generative AI to craft high-quality journal entries in seconds.')
        st.button('Start', on_click=go_to_form)

    # Logo created with DALLE
    with col2:
        st.image("img/DALLE-logo.png")


# Display the form page
elif st.session_state.page == 'form':
    st.title("Your Day")

    # Define questions in form
    with st.form("my_form"):
        name = st.text_input(
            "Name:")
        day_description = st.text_area("Tell me a bit about what you did today.",
                                       placeholder="Things you did, places you went, people you met, etc.")
        pov = st.radio(
            "What point of view do you want your day summary to have?",
            ["First Person", "Second Person"])
        user_learning = st.text_input(
            "What's something new you want to learn about?")
        # uploaded_files = st.file_uploader("Upload an important image from your day.", type=[
        #     'jpg', 'png'])
        rating = st.slider(
            "How would you rate this day?", 0, 10, 1)
        goals = st.text_input(
            "What are your goals and plans for tomorrow?")

        submitted = st.form_submit_button("Submit")

        # Complete form validation (ensure fields are nonempty)
        if submitted:
            if len(name) == 0:
                st.error("Please enter your name.")
            elif len(day_description) == 0:
                st.error("Please enter a description of your day.")
            elif len(user_learning) == 0:
                st.error("Please input what you would like to learn.")
            elif len(goals) == 0:
                st.error("Please input your goals for tomorrow.")
            else:
                current_time = datetime.now()

                month_day = current_time.strftime("%B %d")
                current_year = current_time.year

                input_object = {
                    "name": name,
                    "month_day": month_day,
                    "current_year": current_year,
                    'day_rating': rating,
                    "day_description": day_description,
                    "pov": pov,
                    "user_learning": user_learning,
                    "rating": rating,
                    "goals": goals
                }

                handle_form_submission(input_object)
                st.success("Journal page generated. Click Submit to view.")

# Display the result page
elif st.session_state.page == 'result':
    st.title("Enjoy!")
    st.write('Your personalized journal entry is available for download below.')

    # Read template HTML file
    with open('template.html', 'r') as file:
        html_content = file.read()

    user_task_string = ""

    # Writes HTML unordered list for all tasks
    for task in st.session_state.result_answers['list_tasks']:
        user_task_string += f"<li>{task}</li>"

    # Replace placeholders with actual generated values from LLMs
    html_content = html_content.replace('{{ date }}', str(st.session_state.result_answers['month_day']) + ", " + str(st.session_state.result_answers['current_year'])).replace('{{ name }}', str(st.session_state.result_answers['name'])).replace('{{ rating }}', str(st.session_state.result_answers['day_rating'])).replace(
        '{{ reflection }}', str(st.session_state.result_answers['day_summarization'])).replace('{{ completed_tasks }}', user_task_string).replace('{{ quote_of_the_day }}', str(st.session_state.result_answers['quote_of_the_day'])).replace('{{ fun_fact }}', str(st.session_state.result_answers['fun_fact'])).replace('{{ tomorrow_goals }}', str(st.session_state.result_answers['final_goals']))

    html = HTML(string=html_content)

    # Write HTML content to a file for logging purposes
    with open('output.html', 'w') as file:
        file.write(html_content)

    html.write_pdf('journal.pdf')

    # Allow user to save PDF
    with open("journal.pdf", "rb") as file:
        st.download_button(
            label="Download Entry",
            data=file,
            file_name="journal_entry.pdf",
            mime="application/octet-stream"
        )

    # Render HTML with CSS in Streamlit
    st.components.v1.html(html_content, height=600, scrolling=True)

    st.button("Back", on_click=go_to_form)
