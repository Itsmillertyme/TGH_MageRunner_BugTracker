import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

#CONSTANT VARIABLES
DATA_FILE = "bugs.csv"
developers = ["Corey", "Jacob", "Unassigned"]
priorities = ["High", "Medium", "Low"]
systems = ["Animation", "ProGen", "Player Controller", "Spells", "Other", "Unassigned"]
statuses = ["Open", "In Progress", "Closed"]

#FUNCTION DEFINITIONS
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        # Return default ticket if file not found
        return pd.DataFrame([{
            "ID": "TICKET-00000",
            "Issue": "DEFAULT BUG TICKET",
            "System": "Unassigned",
            "Status": "Open",
            "Priority": "High",
            "Developer": "Unassigned",
            "Date Submitted": datetime.datetime.now().strftime("%m-%d-%Y, %H:%M")
        }])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)


#MAIN PROGRAM
st.set_page_config(page_title="MageRunner Bug Tracker", page_icon="🐛", layout="wide")
st.title("🐛 MageRunner Bug Tracker")

#Setup session_state
if "df" not in st.session_state:
    st.session_state.df = load_data()

#*Add a bug*
st.header("Add a Bug to Track")

with st.form("add_bug_form"):
    col1,col2,col3,col4 = st.columns([6,3,3,1])

    with col1:
        issue = st.text_area("Describe the issue")
    
    with col2:
        priority = st.selectbox("Priority", priorities, index = len(priorities)-1)
        developer = st.selectbox("Developer", developers, index = len(developers)-1)
    
    with col3:
        system = st.selectbox("System", systems, index = len(systems)-1)
    
    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    status = statuses[0]
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "System": system,
                "Status": status,
                "Priority": priority,
                "Developer": developer,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("Bug submitted! Here are the details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

    #Save entry to data file
    save_data(st.session_state.df)

#*Existing Tickets*
st.header("Existing tickets")

st.write(f"Number of tickets: `{len(st.session_state.df)}`")

st.info(
    "You can edit the tickets by double clicking on a cell. You can also sort the table by clicking on the column headers.",
    icon="✍️",
)

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Issue" : st.column_config.TextColumn(
            "Issue",
            help="Description of issue"
        ),
        "System": st.column_config.SelectboxColumn(
            "System",
            help="System",
            options=["Animation", "ProGen", "Player Controller", "Spells", "Other", "Unassigned"],
            required=True,
        ),        
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Bug status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
        "Developer": st.column_config.SelectboxColumn(
            "Developer",
            help="Developer",
            options=["Cory", "Jacob", "Unassigned"],
            required=True,
        ),
    },
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)

if not edited_df.equals(st.session_state.df):
    st.session_state.df = edited_df
    save_data(edited_df)
    st.success("Changes saved.")

#*Stats for nerds*
st.header("Statistics")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
col1.metric(label="Number of open tickets", value=num_open_tickets, delta=10)
col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
col3.metric(label="Average resolution time (hours)", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### Ticket status per month")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Current ticket priorities")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")


col1,col2,col3 = st.columns([3,2,3])
with col2:
    st.write("TeamGiantHamster Studios 2025")