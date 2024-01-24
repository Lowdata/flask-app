from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta

app = Flask(__name__)


connection_string = "postgresql://ayush:vhezVMT5znQK5mKCDwOL2w@database-1-8345.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/leaderboard?sslmode=verify-full"
conn = psycopg2.connect(connection_string)
cursor = conn.cursor()

@app.route('/api/current-week-leaderboard', methods=['GET'])
def current_week_leaderboard():
    # Calculate the start date of the current week
    start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())

    query = f"SELECT * FROM leaderboard WHERE TimeStamp >= '{start_of_week}' ORDER BY Score DESC LIMIT 200;"
    cursor.execute(query)
    results = cursor.fetchall()

    leaderboard = []
    for row in results:
        leaderboard.append({
            'UID': row[0],
            'Name': row[1],
            'Score': row[2],
            'Country': row[3],
            'TimeStamp': row[4].strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'leaderboard': leaderboard})

@app.route('/api/last-week-leaderboard/<country>', methods=['GET'])
def last_week_leaderboard(country):
    # Calculate the start date of the previous week
    start_of_last_week = datetime.now() - timedelta(days=datetime.now().weekday() + 7)

    query = f"SELECT * FROM leaderboard WHERE TimeStamp >= '{start_of_last_week}' AND Country = '{country}' ORDER BY Score DESC LIMIT 200;"
    cursor.execute(query)
    results = cursor.fetchall()

    leaderboard = []
    for row in results:
        leaderboard.append({
            'UID': row[0],
            'Name': row[1],
            'Score': row[2],
            'Country': row[3],
            'TimeStamp': row[4].strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'leaderboard': leaderboard})

@app.route('/api/user-rank/<user_id>', methods=['GET'])
def user_rank(user_id):
    query = f"""
        SELECT UID, Name, Score, Country, TimeStamp, Position
        FROM (
            SELECT UID, Name, Score, Country, TimeStamp, ROW_NUMBER() OVER (ORDER BY Score DESC) AS Position
            FROM leaderboard
        ) AS ranked_users
        WHERE UID = '{user_id}';
    """
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        user_info = {
            'OverAll Rank': result[5]
        }
        return jsonify(user_info)
    else:
        return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=False,use_reloader=False,host="0.0.0.0")
