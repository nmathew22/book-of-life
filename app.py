# Importing libraries
import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
import credentials
import os
import openai
import textwrap

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


def go_to_form():
    st.session_state.page = 'form'


def go_to_result():
    st.session_state.page = 'result'


def handle_form_submission(input_object):
    # # Access form variables from session state
    # input_object = st.session_state

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

    print(" - - - - - ")
    print(input_object)
    print(quote_prompt)
    print(input_object['day_description'])
    print(quote_final_prompt)
    print(quote_of_the_day)

    # print(textwrap.fill(quote_of_the_day, 75))
    # st.write(quote_of_the_day)

    summarization_prompt = """
    Summarize the day that is described below in about 150 words (a paragraph). Write in the point of view
    (either first person or second person) indicated below.
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

    # print(textwrap.fill(day_summarization, 75))
    # st.write(day_summarization)

    tasks_prompt = """
    Give me an array where every element of the array is a task that is included in the
    description below. If the task list is empty, don't output anything. The tasks should 
    be relatively short. Each task should start with a verb in the past tense, to indicate 
    that the task was completed.
    Tasks: {user_tasks}
    """

    tasks_template = PromptTemplate(
        template=tasks_prompt,
        input_variables=["user_tasks"],
    )

    tasks_final_prompt = tasks_template.format(
        user_tasks=input_object['user_tasks'])

    llm = OpenAI(temperature=0.4)
    list_tasks = llm(tasks_final_prompt)

    # print(textwrap.fill(list_tasks, 75))
    # st.write(list_tasks)

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

    # print(textwrap.fill(fun_fact, 75))
    # st.write(fun_fact)

    goals_prompt = """
    Based on the goals below, come up with first a broader goal that the user is looking to accomplish,
    and then the more small-scale tasks associated with what the user inputs. Return a JSON object with 
    a 'Mission' field and a 'Sub-Tasks' field. Make the sub-tasks adhere mostly to the goals below.
    Goals: {goals}
    """

    goals_template = PromptTemplate(
        template=goals_prompt,
        input_variables=["goals"],
    )

    goals_final_prompt = goals_template.format(goals=input_object['goals'])

    llm = OpenAI(temperature=0.4)
    final_goals = llm(goals_final_prompt)

    # print(textwrap.fill(final_goals, 75))
    # st.write(final_goals)

    if input_object['uploaded_files'] is None:
        st.write("No images uploaded.")
    elif len(input_object['uploaded_files']) < 4:
        for uploaded_file in input_object['uploaded_files']:
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()

            # Display the image
            st.image(bytes_data)
    else:
        st.write("Uploaded more than 3 images.")

    output_object = {
        'quote_of_the_day': quote_of_the_day,
        'day_summarization': day_summarization,
        'list_tasks': list_tasks,
        'fun_fact': fun_fact,
        'final_goals': final_goals,
        'uploaded_files': input_object['uploaded_files'],
    }

    st.session_state.result_answers = output_object
    st.session_state.page = 'result'


# Display the welcome page
if st.session_state.page == 'welcome':
    # Create two columns
    col1, col2 = st.columns(2)

    # Use the first column to display content
    with col1:
        st.title("Book of Life")
        st.write('Welcome to Book of Life, an app which uses the power of generative AI to help you craft high-quality journal entries in seconds.')
        st.button('Start', on_click=go_to_form)

    # Use the second column to display content
    with col2:
        st.image("img/DALLE-logo.png")


# Display the form page
elif st.session_state.page == 'form':
    max_photos = 3
    st.title("Your Day")

    with st.form("my_form"):
        day_description = st.text_area("Tell me a bit about what you did today.",
                                       placeholder="Things you did, places you went, people you met, etc.")
        pov = st.radio(
            "What point of view do you want your day summary to have?",
            ["First Person", "Second Person"])
        user_tasks = st.text_input(
            "What tasks did you complete?")
        user_learning = st.text_input(
            "What's something new you want to learn about?")
        uploaded_files = st.file_uploader("Upload images from your day. (Max: 3)", type=[
            'jpg', 'png'], accept_multiple_files=True)
        rating = st.slider(
            "How would you rate this day?", 0, 10, 1)
        goals = st.text_input(
            "What are your goals and plans for tomorrow?")

        submitted = st.form_submit_button("Submit")

        if submitted:
            input_object = {
                "day_description": day_description,
                "pov": pov,
                "user_tasks": user_tasks,
                "user_learning": user_learning,
                "uploaded_files": uploaded_files,
                "rating": rating,
                "goals": goals
            }

            print("from: \n")
            print(input_object)

            handle_form_submission(input_object)

        # if st.session_state.page != 'result':
        #     st.session_state.page = 'result'

# Display the result page
elif st.session_state.page == 'result':
    st.write("result")
    if st.session_state.result_answers:
        st.write(st.session_state.result_answers)
    st.button("Back", on_click=go_to_form)
