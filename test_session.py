from flask import Flask, session, jsonify
import pytest

app = Flask(__name__)
app.secret_key = 'test'

@app.route('/login', methods=['POST'])
def login():
    session['user'] = 'test'
    return jsonify(status='ok')

@app.route('/check')
def check():
    if 'user' in session:
        return jsonify(status='ok')
    return jsonify(status='fail'), 401

def test_session_persistence():
    with app.test_client() as client:
        resp = client.post('/login')
        assert resp.status_code == 200
        resp = client.get('/check')
        assert resp.status_code == 200

if __name__ == '__main__':
    # run test
    try:
        test_session_persistence()
        print("Test PASSED")
    except AssertionError as e:
        print(f"Test FAILED: {e}")
