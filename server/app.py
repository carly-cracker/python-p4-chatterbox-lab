from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages' ,methods=['GET'])
def messages():
    messages=Message.query.order_by(Message.created_at.asc()).all()
    response = [m.to_dict()for m in messages]
    return make_response (jsonify(response),200)

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()

    if not data or not all(j in data for j in ("body", "username")):
        return make_response(jsonify({'error':'missing details'})) 
    new_message = Message(body=data['body'], username=data['username'])
    db.session.add(new_message)
    db.session.commit()
    return make_response(jsonify(new_message.to_dict()),201)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def message_by_id(id):
    message = Message.query.filter(Message.id==id).first()

    if message is None:
        response_body={
            "message": f"This message {id} does not exist in our database. Please try again."
        }
        return make_response(response_body, 404)
    
    if request.method == 'PATCH':
        data = request.get_json()
        for attr,value in data.items():
            setattr(message, attr, value)
        db.session.commit()
        return make_response(message.to_dict(), 200)
    
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        response_body={
            'message':'The message {id} has been deleted successfully'
        }
        return make_response(response_body, 204)



if __name__ == '__main__':
    app.run(port=5555)
