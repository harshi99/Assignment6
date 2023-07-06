import pygame
import os
from pygame.locals import *
from flask import Flask, render_template, request, redirect, url_for
from flask import session


# Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Set up game variables
piles = [0, 0, 0]  # Number of stones in each pile (initialized to 0)
player1_turn = True
min_stones = 1
max_stones = 3
player1_name = ""
player2_name = ""
player1_score = 0
player2_score = 0

# Route for the judge web page
@app.route('/', methods=['GET', 'POST'])
def judge_page():
    global piles, min_stones, max_stones, player1_name, player2_name
    if request.method == 'POST':
        piles[0] = int(request.form['pile1'])
        piles[1] = int(request.form['pile2'])
        piles[2] = int(request.form['pile3'])
        min_stones = int(request.form['min_stones'])
        max_stones = int(request.form['max_stones'])
        return redirect(url_for('play_game'))
    return render_template('judge.html')

# Function to validate the number of stones picked by a player
def validate_stones_picked(pile_index, stones_picked):
    if stones_picked < min_stones or stones_picked > max_stones:
        return False
    if piles[pile_index] < stones_picked:
        return False
    return True

# Function to update scores
def update_scores():
    global player1_score, player2_score
    player1_score = sum(piles) if player1_turn else player1_score + sum(piles)
    player2_score = sum(piles) if not player1_turn else player2_score + sum(piles)

# Route for the game web page
@app.route('/play', methods=['GET', 'POST'])
def play_game():
    global player1_turn, piles, player1_score, player2_score

    if request.method == 'POST':
        # Get the player names from the form
        player1_name = request.form['player1_name']
        player2_name = request.form['player2_name']

        # Store the player names in the session
        session['player1_name'] = player1_name
        session['player2_name'] = player2_name

        return redirect(url_for('game_window'))

    return render_template('game.html')

# Function to update the scores based on the remaining stones in each pile
def update_scores():
    global piles, player1_score, player2_score
    player1_score = sum(piles[::2])
    player2_score = sum(piles[1::2])

# Route for the game web page
@app.route('/game', methods=['GET', 'POST'])
def game_window():
    global player1_turn, piles, player1_score, player2_score

    if request.method == 'POST':
        pile_index = int(request.form['pile_index'])
        stones_picked = int(request.form['stones_picked'])

        if validate_stones_picked(pile_index, stones_picked):
            piles[pile_index] -= stones_picked
            if player1_turn:
                player1_score += stones_picked
            else:
                player2_score += stones_picked
            player1_turn = not player1_turn

    if sum(piles) == 0:
        # Game over, determine the winner
        winner = session.get('player1_name') if player1_score > player2_score else session.get('player2_name')
        return render_template('game_over.html', player1_name=session.get('player1_name'), player2_name=session.get('player2_name'), player1_score=player1_score, player2_score=player2_score, winner=winner)

    # Retrieve player names from the session
    player1_name = session.get('player1_name')
    player2_name = session.get('player2_name')

    return render_template('game_window.html', player1_name=player1_name, player2_name=player2_name, piles=piles, player1_turn=player1_turn, player1_score=player1_score, player2_score=player2_score)

         
if __name__ == '__main__':
    app.run(debug=True)
