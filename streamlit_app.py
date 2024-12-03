import streamlit as st
import openai

# Configure page layout
st.set_page_config(page_title="Mr Hurting - Your Negotiation Partner", page_icon="💬", layout="centered")

# Transparent background for the content
st.markdown(
    """
    <style>
    .transparent-container {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 2rem;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.container():
    st.markdown('<div class="transparent-container">', unsafe_allow_html=True)

    # Title with Emoji
    st.markdown(
        "<h1 style='text-align: center; color: #1F4E79;'>💬 Mr Hurting - Your Negotiation Partner</h1>",
        unsafe_allow_html=True
    )

    # Add a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)

    # Description with larger font and color
    st.markdown(
        "<h3 style='text-align: center; color: #1F4E79;'>This Chatbot will help you to train your negotiation skills.</h3>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align: center; font-size: 18px;'>Read the role card provided below and adapt to your role. The Chatbot will play the role of Mr. Hurting.</p>",
        unsafe_allow_html=True
    )

    # Role card in an expandable section
    with st.expander("📝 Show Your Role Card"):
        st.write("""
        **Your Role Card:**  
        The company Zusetzer (located only 50 km away from your place of business) has been supplying the chemical additive 435 in 25 kg containers for 5 years because it is easier to handle. Suddenly the company is complaining about impurities in the process. Previously there were no such defects. The last delivery consisted of 100 buckets of 25 kg, 6,- EUR/kg. In the last process, 25 buckets from the last delivery were used at the same time.

        Since you were only able to neutralize the impurities that you detected after filling by purchasing and adding the brightener Blendi, you incurred additional costs of 10% of the purchase price and treatment costs, the amount of which was stated by your production department to be EUR 4,500. Of this, EUR 1,200 are wages, the rest relates to cleaning the system. The only approved competitor, Chemie AG, charges 15 % more than Zusetzer because it is 300 km away from your place of business and has to charge higher freight costs.

        You occupy 20% of Zusetzer's capacity with your orders.  
        Your annual turnover is approx. 1,200 buckets of 25 kg each, you cannot process larger units!  
        **Goal:**  
        The quality must return to its former state.  
        You must achieve reimbursement of the additional price and treatment costs.  
        The remaining stock quantity must be exchanged for the old quality.
        """)

    # Prompt to start the conversation
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='text-align: center;'>Just start the conversation with Mr. Hurting here:</h3>",
        unsafe_allow_html=True
    )

# Footer with image or logo
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px;">
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSldpssSMyDjL8BK9N7EW2gjodVa0GjsW2wVg&s" alt="Logo" width="150">
    </div>
    """,
    unsafe_allow_html=True
)
### Code für die Konversation: 

#lesen des Open AI Keys 
openai.api_key = st.secrets["openai_api_key"]

# Vollständiger Prompt für den Chatbot
bot_instructions = """
Role and Goal: - You are Salesperson, Mr. Hurtig. - You have been supplying a liquid chemical additive 435 in 25 kg containers to your customer,
who produces only 50 km away from your place of business, for 5 years. - Due to cost increases, the price of the additive needs to rise by 8%. - 
Your production department made a minor change to the composition without customer approval, expecting no issues. 
- A contamination occurred in the last delivery of 100 buckets, and the customer invited you to a complaint meeting.
- The customer uses 25 buckets per process. - Your competitor, CHEMIE AG, is approximately 300 km away and likely more expensive by an estimated 10%.
- Your customer's orders take up about 20% of your plant capacity, which equals approximately 1,200 buckets of 25 kg each per year.
- Your current sales price is EUR 6 per kilogram. Behavior: 
- Start the conversation with some small talk to build rapport.
- Engage in prolonged negotiation with the customer. 
- Acknowledge the complaint as valid due to the unapproved change in composition. 
- After addressing the refund or other concerns, always introduce and defend the need for an 8-10% price increase to avoid losses. 
- Aim to retain the customer while achieving the price increase. 
- Be skeptical, tough, and sometimes provocative or rude to challenge the customer and extend the negotiation. 
- Offer strategic bulk purchase discounts if needed, but avoid agreement below an 8% price rise. - End the relationship if the offer above 8% isn’t accepted. 
- Adjust negotiation tactics based on the customer's reactions and emotions. Guidelines: 
- Use a direct and firm tone, maintaining awareness of the customer's emotions. - Tailor arguments to the customer’s reactions. 
- Respond human-like to the customer's concerns and arguments. - Start the conversation with some small talk before addressing the main issue. 
- Remember that your role includes acting as if the negotiation were on the phone. - Avoid bullet points and do not give long answers. Clarification: 
- Ask for clarification if unsure about the customer’s responses or concerns.
"""

# Initialisiere den Sitzungszustand nur beim ersten Start
if "messages" not in st.session_state: ## Testet ob schon etwas in der messages list ist
    st.session_state.messages = [{"role": "system", "content": bot_instructions}] ## speichert die Nachrichten hier 

# Zeige bisherige Benutzer- und Assistenten-Nachrichten an (ohne den system prompt)
for message in st.session_state.messages: ## alle Messages die in der messages List sind werden auf dem Interface angezeigt chat_message ist ein widget von streamlit
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat-Eingabefeld für Benutzernachrichten
if user_input := st.chat_input("Start the conversation with ..Hello Mr. Hurting.."): ## wenn der Nuter etwas antwortet, mache das: chat_iput - streamlit input for chatbots, user_input ist eine Variable die den nutzer input speichert
    # Benutzer-Nachricht hinzufügen
    st.session_state.messages.append({"role": "user", "content": user_input}) ###streamlit erwartet eine rolle und einen inhalt, in dieser liste
    with st.chat_message("user"): ## zeigt den User input auf dem Screen an
        st.markdown(user_input)

    # API-Anfrage zur Generierung der Antwort basierend auf der Konversation
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  
            messages=st.session_state.messages,
            temperature=0.5
            # max_tokens=50 könnte man noch reinnehmen, bei Bedarf.
            )

        # Extrahiere die Antwort
        assistant_response = response.choices[0].message.content
        
        # Antwort anzeigen und im Sitzungszustand speichern
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    except Exception as e:
        st.error("Ein Fehler ist aufgetreten. Bitte überprüfe die API-Konfiguration oder versuche es später erneut.")
        st.write(e)


########### Feedback generierung

conversation_text = "\n".join(
    [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages if msg['role'] != "system"]
)

if st.button("📝 Feedback zu Ihrer Konversation erhalten"):
    # Konstruiere den Prompt für das Feedback
    feedback_prompt = f"""
    The conversation is below.

    Konversation:
    {conversation_text}
    """


    ### Feedback 
  # API-Anfrage zur Generierung der Antwort basierend auf der Konversation
    try:
        feedback_response = openai.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": """
                This GPT is a negotiation expert designed to analyze uploaded negotiation scripts involving two parties. 
                It identifies and evaluates negotiation tactics used by the user role, for example BATNA, avoiding urgency, or specific strategies like 'Last-Minute Deal Embellishment.' 
                The GPT provides detailed, constructive feedback for the user, naming the tactics used, how effectively they were applied, and assigning points based on their usage.
                It references specific lines from the script as evidence, ensuring feedback is clear and substantiated. 
                The feedback includes recommendations for improvement and alternative tactics for future negotiations.
                The GPT addresses the user with "you", the user is the person that startes the conversation with hello Mr. Hurting
               """},
                {"role": "user", "content": feedback_prompt}
            ],
            temperature=0.5
            # max_tokens=50 könnte man noch reinnehmen, bei Bedarf.
        )

        # Extrahiere die Antwort
        feedback_response = feedback_response.choices[0].message.content ## choise sagt es soll nur eine antwort generieren 
        st.markdown(feedback_response);

    except Exception as e:
        st.error("Ein Fehler ist aufgetreten. Bitte überprüfen Sie die API-Konfiguration oder versuchen Sie es später erneut.")
        st.write(f"Details: {e}")

#### Sentiment analyse
if st.button("📝 Sentimentanalyse zu Ihrer Konversation erhalten (Open AI)"):
    # API-Anfrage zur Generierung der Antwort basierend auf der Konversation
    try:
        feedback_response = openai.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": """
            You are an AI assistant designed to perform a detailed sentiment and emotion analysis of a conversation between the user.
            
            **Your Tasks:**
            - **Emotion Detection:** Identify the specific emotions (e.g., joy, anger, frustration, satisfaction, surprise) you expressed in each of your messages.
            - **Intensity Assessment:** Rate the intensity of each identified emotion on a scale from 1 (very weak) to 5 (very strong).
            - **Impact on Negotiation:** Describe how these emotions influenced the course and outcome of the negotiation.
            - **Include Quotes:** Use specific examples and quotes from the conversation to support your analysis.
            - **Provide Recommendations:** Offer you constructive feedback on how you can improve your emotional communication in future negotiations.
            
            **Guidelines:**
            - Focus primarily on analyzing your messages, but consider Mr. Hurting's responses where relevant.
            - Address you directly in the analysis and feedback.
            - Present your findings in clearly structured sections.
            - Use a professional and helpful tone.
            """ },
                {"role": "user", "content": conversation_text}
            ],
            temperature=0.5
            # max_tokens=50 könnte man noch reinnehmen, bei Bedarf.
        )

        # Extrahiere die Antwort
        feedback_response = feedback_response.choices[0].message.content ## choise sagt es soll nur eine antwort generieren 
        st.markdown(feedback_response);

    except Exception as e:
        st.error("Ein Fehler ist aufgetreten. Bitte überprüfen Sie die API-Konfiguration oder versuchen Sie es später erneut.")
        st.write(f"Details: {e}")

#### Emotion analysis j-hartman Model
from transformers import pipeline

# Emotion analysis using the j-hartmann Model
if st.button("📝 Emotion analysis with the j-hartman Model: Overall Emotionscore of the userinputs"):
    # Collect all user messages (excluding system and assistant messages)
    user_messages = [msg['content'] for msg in st.session_state.messages if msg['role'] == 'user']

    # Combine all user messages into one text
    user_text = " ".join(user_messages)

    # Initialize the classifier
    classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

    # Perform emotion analysis
    results = classifier(user_text)

    # Display the results
    st.write("### Emotion Analysis Results:")
    for emotion in results[0]:
        label = emotion['label']
        score = emotion['score']
        st.write(f"{label}: {score:.2f}")

# Emotion analysis using the j-hartmann Model every message
if st.button("📝 Emotion analysis of each message with the j-hartmann Model"):
    # Collect all user messages (excluding system and assistant messages)
    user_messages = [msg['content'] for msg in st.session_state.messages if msg['role'] == 'user']

    # Initialize the classifier
    classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

    # Display the results
    st.write("### Emotion Analysis Results for Each User Input:")

    for idx, message in enumerate(user_messages):
        st.write(f"#### Message {idx+1}: {message}")

        # Perform emotion analysis
        results = classifier(message)

        # Display the results
        for emotion_score in results[0]:
            label = emotion_score['label']
            score = emotion_score['score']
            st.write(f"- **{label}**: {score:.2f}")
        st.write("---")  # Separator between messages
