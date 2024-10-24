import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
from valorant_data_collector import ValorantDataCollector  # Ensure correct import
import logging

app = Flask(__name__)

# Setting the SECRET_KEY for your Flask app
# Use the environment variable in production or a fallback key for local development
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')  # Replace 'fallback-secret-key' with a secure key for local dev

# Initialize SocketIO
socketio = SocketIO(app)

# Initialize the data collector
collector = ValorantDataCollector()

# Handle default route
@app.route('/')
def index():
    return render_template('index.html')  # Create a simple HTML file for the chatbot interface

# Handle incoming messages (from the user)
@socketio.on('message')
def handle_message(msg):
    logging.info(f"Message: {msg}")
    
    # Parse the message and detect commands
    if msg.lower().startswith('stats for'):
        player_name = msg[len('stats for'):].strip()  # Extract player name
        player_url = collector.search_player(player_name)
        
        if player_url:
            player_stats = collector.get_player_stats(player_url)
            if player_stats:
                response = format_player_stats(player_stats)
                send(response)  # Send the stats as a response
            else:
                send(f"Could not retrieve stats for player {player_name}.")
        else:
            send(f"Player {player_name} not found.")
    
    else:
        send("I'm sorry, I can only provide player stats. Ask me something like 'Stats for [player name]'.")

def format_player_stats(player_data):
    """Format the player stats for easy reading in a chat interface."""
    formatted_stats = f"**Player Name**: {player_data['Name']}\n"
    formatted_stats += "Stats per Agent:\n"
    
    for stat in player_data['Stats']:
        formatted_stats += (
            f"Agent: {stat['Agent']}, Usage: {stat['Usage']}, Rounds Played: {stat['Rounds Played']}, "
            f"Rating: {stat['Rating']}, ACS: {stat['ACS']}, K:D: {stat['K:D']}, ADR: {stat['ADR']}, "
            f"KAST: {stat['KAST']}, KPR: {stat['KPR']}, APR: {stat['APR']}, "
            f"First Kills: {stat['First Kills']}, First Deaths: {stat['First Deaths']}\n"
        )
    
    return formatted_stats

if __name__ == '__main__':
    socketio.run(app)