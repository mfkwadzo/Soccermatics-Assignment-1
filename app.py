import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch, Sbopen, VerticalPitch

st.set_page_config(page_title="Alex Greenwood Analysis", layout="wide")

st.title("⚽ Alex Greenwood Analysis in UEFA Women's Euro 2025 Final Against Spain")

# Load data
@st.cache_data
def load_data():
    parser = Sbopen()
    df_competition = parser.competition()
    df_match = parser.match(competition_id=53, season_id=315)
    df_lineup = parser.lineup(4020846)
    df_event, related, freeze, tactics = parser.event(4020846)
    return df_event, df_lineup, parser

df_event, df_lineup, parser = load_data()

# Extract passes and shots
passes = df_event.loc[df_event['type_name'] == 'Pass'].set_index('id')
shots = df_event.loc[df_event['type_name'] == 'Shot'].set_index('id')


st.write("""
    This application analyzes the performance of Alex Greenwood in the UEFA Women's Euro 2025 final 
    between England and Spain. The analysis uses StatsBomb open data to explore match statistics, 
    player lineups, and event data.
    """)


# st.header("Pass Analysis - Alex Greenwood")
# Load event data
# df, related, freeze, tactics = parser.event(match_id)

# Filter for passes (excluding throw-ins)
# passes = df.loc[df['type_name'] == 'Pass'].loc[df['sub_type_name'] != 'Throw-in'].set_index('id')

# Filter for Alex Greenwood's passes
alex_passes = passes[passes['player_name'] == 'Alex Greenwood']
alex_shots = shots[shots['player_name'] == 'Alex Greenwood']

st.header("Alex Greenwood  Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Passes", len(alex_passes))
with col2:
    if len(alex_passes) > 0:
        avg_pass_length = alex_passes['pass_length'].mean() if 'pass_length' in alex_passes.columns else "N/A"
        st.metric("Avg Pass Length", f"{avg_pass_length:.1f}" if isinstance(avg_pass_length, (int, float)) else avg_pass_length)
    else:
        st.metric("Avg Pass Length", "N/A")

with col3:
        st.metric("Total Shots", len(alex_shots))

    

with col4:
        st.metric("Total xG", round(alex_shots['shot_statsbomb_xg'],2))
   


# Section 1: Competition Data
# st.header("Competition Data")
# df_competition = parser.competition()
# st.dataframe(df_competition)

# Section 2: Match Data
# st.header("Match Data")
# df_match = parser.match(competition_id=53, season_id=315)
# st.dataframe(df_match)

# Section 3: Lineup Data
# st.header("Lineup Data")
# st.dataframe(df_lineup)

# Section 4: Plotting Passes
# st.header("Plotting Passes")
# pitch = Pitch(line_color="black")
# fig, ax = pitch.draw(figsize=(10, 7))

# for i, thepass in passes.iterrows():
#     if thepass['player_name'] == 'Alex Greenwood':
#         x = thepass['x']
#         y = thepass['y']
#         passCircle = plt.Circle((x, y), 2, color="blue")
#         passCircle.set_alpha(.2)
#         ax.add_patch(passCircle)
#         dx = thepass['end_x'] - x
#         dy = thepass['end_y'] - y
#         passArrow = plt.Arrow(x, y, dx, dy, width=3, color="green")
#         ax.add_patch(passArrow)

# ax.set_title("Alex Greenwood Passes", fontsize=24)
# fig.set_size_inches(10, 7)
# st.pyplot(fig)

#second version of pass plot
if not alex_passes.empty:
    st.subheader("Alex Greenwood Passes Data")
    pass_cols = ['minute', 'second', 'pass_recipient_name', 'pass_length', 'pass_height_name', 'outcome_name']
    available_cols = [col for col in pass_cols if col in alex_passes.columns]
    
    if available_cols:
        st.dataframe(alex_passes[available_cols].head(20), use_container_width=True)
    
    # Create a pitch for visualization
    st.subheader("Pass Visualization")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#E8E8E8', line_color='#000000', 
                    line_zorder=2, linewidth=1)
    pitch.draw(ax=ax)
    
    # Plot passes
    for _, pass_row in alex_passes.iterrows():
        if pd.notna(pass_row.get('x')) and pd.notna(pass_row.get('y')) and \
            pd.notna(pass_row.get('end_x')) and pd.notna(pass_row.get('end_y')):
            
            # Determine color based on outcome
            color = 'green' if (pass_row.get('outcome_name') == 'Complete' or 
                                pd.isna(pass_row.get('outcome_name'))) else 'red'
            
            # Plot pass arrow
            pitch.arrows(pass_row['x'], pass_row['y'], 
                        pass_row['end_x'], pass_row['end_y'],
                        width=2, headwidth=4, headlength=6, color=color, 
                        ax=ax, alpha=0.7)
    
    ax.set_title("Alex Greenwood's Passes in the Match", fontsize=16, fontweight='bold')
    st.pyplot(fig)
    
    # Pass height distribution
    if 'pass_height_name' in alex_passes.columns and not alex_passes['pass_height_name'].isna().all():
        st.subheader("Pass Height Distribution")
        height_counts = alex_passes['pass_height_name'].value_counts()
        
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        height_counts.plot(kind='bar', ax=ax2, color=['blue', 'green', 'red'])
        ax2.set_title("Alex Greenwood Pass Height Distribution")
        ax2.set_ylabel("Count")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)

# Section 5: Plotting Shots with xG
st.header("Alex Greenwood Shots with xG (Circle Size = xG)")
pitch = Pitch(line_color="black")
fig, ax = pitch.draw(figsize=(10, 7))

alex_shots = shots[shots['player_name'] == 'Alex Greenwood']

for i, shot in alex_shots.iterrows():
    x = shot['x']
    y = shot['y']
    goal = shot['outcome_name'] == 'Goal'
    xg = shot['shot_statsbomb_xg']

    circleSize = 4 + (xg * 5)

    if goal:
        shotCircle = plt.Circle((x, y), circleSize, color="green")
    else:
        shotCircle = plt.Circle((x, y), circleSize, color="red", alpha=0.3)

    ax.add_patch(shotCircle)
    plt.text(x + 1, y + 1, f"{xg:.2f}", fontsize=8, color="black")

fig.suptitle("Alex Greenwood Shots with xG (Circle Size = xG)", fontsize=22)
fig.set_size_inches(10, 7)
st.pyplot(fig)

# Section 6: Player Comparison
st.header("Comparing Alex with Spain Defenders (Olga and Irene)")

players = ["Alex Greenwood", "Irene Paredes Hernandez", "Olga  Carmona García"]

def is_pass(row):
    return str(row["type_name"]).lower() == "pass"

def is_goal(row):
    return (str(row["type_name"]).lower() == "shot") and (row["outcome_name"] == "Goal")

results = []

for p in players:
    df_p = df_event[df_event["player_name"] == p]
    passes_count = df_p[df_p.apply(is_pass, axis=1)]
    goals = df_p[df_p.apply(is_goal, axis=1)]

    results.append({
        "Player": p,
        "Passes": len(passes_count),
        "Goals": len(goals)
    })

compare_df = pd.DataFrame(results)
st.dataframe(compare_df)

# Display comparison chart
st.bar_chart(compare_df.set_index('Player'),color=['#ff0000',"#1b6806"])
