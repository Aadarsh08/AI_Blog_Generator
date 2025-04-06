from langchain_huggingface import HuggingFaceEndpoint  # Import Hugging Face endpoint class
from langchain.prompts import PromptTemplate  # Import PromptTemplate class from langchain
import urllib.parse

import os  # Import the 'os' module for potential system interactions
import streamlit as st  # Import Streamlit for web app development

from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env
API_KEY = os.getenv("API_KEY")
print(API_KEY)  # To verify the API key is loaded

# Define the Hugging Face model repository ID
repo_id = "meta-llama/Meta-Llama-3-8B-Instruct"

# Create a Hugging Face Endpoint instance
llm = HuggingFaceEndpoint(
    repo_id=repo_id,  # Specify the model repository ID
    temperature=0.6,  # Set the temperature parameter (controls randomness)
    token=API_KEY,  # Use the API key for authentication
)

# Prompt for title suggestions
prompt_template_for_title_suggestion = PromptTemplate(
    input_variables=['topic'],
    template='''
        I'm planning a blog post on the topic: {topic}.
        Always start your response with the sentence: "Here are the 10 top values." 
        Then, provide a **list of exactly 10 creative and attention-grabbing titles** for this blog post.
        The response must:
        - Be presented as a numbered list (1 to 10).
        - Contain **only** the introductory sentence and the list of titles with no additional comments, explanations, notes, or greetings.
        - Do not include any additional words like "Thanks", "Best regards", or closing remarks.
    '''
)

title_suggestion_chain = prompt_template_for_title_suggestion | llm


# Define a PromptTemplate for blog content generation
prompt_template_for_title = PromptTemplate(
    input_variables=['title', 'keywords', 'blog_length', 'tone', 'style'],  # Include new input variables
    template='''
   Write a {tone} and {style} blog post on the topic: "{title}".
    Target the content towards a beginner audience.
    Use a conversational writing style and structure the content with an introduction, body paragraphs, and a conclusion.
    Try to incorporate these keywords: {keywords}.
    Aim for a content length of {blog_length} words.
    
    **Important Instructions:**
    - Do NOT include any additional notes, disclaimers, best regards, or explanations.
    - Provide ONLY the blog content without commentary or metadata.
    - Maintain natural readability and smooth flow without unnecessary filler text.
    '''
)

title_chain = prompt_template_for_title | llm  # Create a chain for title generation

# Streamlit UI
title = "AI Blog Content Assistant 🤖"
st.title(title)
st.header("Create High-Quality Blog Content with AI")
st.subheader('Title Generation') # Display a subheader for the title generation section
topic_expander = st.expander("Input the topic") # Create an expander for topic input
# Create a content block within the topic expander
with topic_expander:
    topic_name = st.text_input("", key="topic_name") # Get user input for the topic name
    submit_topic = st.button('Submit topic') # Button for submitting the topic

if submit_topic: # Handle button click (submit_topic)
    title_selection_text = '' # Initialize an empty string to store title suggestions
    title_suggestion_str = title_suggestion_chain.invoke({topic_name}) # Generate titles using the title suggestion chain
    for sentence in title_suggestion_str.split('\n'): 
        title_selection_text += (sentence.strip() + '\n') # Clean up each sentence and add it to the selection text
    st.text(title_selection_text) # Display the generated title suggestions


st.subheader('Blog Generation')

title_of_the_blog = st.text_input("Enter blog title")
num_of_words = st.slider('Number of Words', min_value=100, max_value=1000, step=50)

# Tone Selection
tone = st.selectbox("Select Tone", ["formal", "casual", "professional", "funny"])

# Writing Style Selection
style = st.selectbox("Select Writing Style", ["news", "storytelling", "listicle"])

if 'keywords' not in st.session_state:
    st.session_state['keywords'] = []

keyword_input = st.text_input("Enter a keyword:")
if st.button("Add Keyword"):
    st.session_state['keywords'].append(keyword_input)
    st.session_state['keyword_input'] = ""
    for keyword in st.session_state['keywords']:
        st.write(f"✅ {keyword}")

if st.button('Generate Blog'):
    formatted_keywords = ', '.join(st.session_state['keywords'])
    blog_content = title_chain.invoke({'title': title_of_the_blog, 'keywords': formatted_keywords, 'blog_length': num_of_words, 'tone': tone, 'style': style})
    
    st.subheader(title_of_the_blog)
    st.write(blog_content)
    
    # Encode content for URL
    encoded_content = urllib.parse.quote(blog_content)

    # LinkedIn Share URL
    linkedin_share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_content}"

    # Medium Share URL (Direct posting requires Medium API, so we'll guide the user)
    medium_guide_url = "https://medium.com/new-story"

    # Share buttons
    st.subheader("Share Your Blog")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"[![Share on LinkedIn](https://img.shields.io/badge/Share%20on-LinkedIn-blue?style=for-the-badge&logo=linkedin)]({linkedin_share_url})", unsafe_allow_html=True)

    with col2:
        st.markdown(f"[![Post on Medium](https://img.shields.io/badge/Post%20on-Medium-black?style=for-the-badge&logo=medium)]({medium_guide_url})", unsafe_allow_html=True)

