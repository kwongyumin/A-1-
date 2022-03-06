from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient("mongodb+srv://test:sparta@cluster0.u3t9k.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client.miniProject

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)