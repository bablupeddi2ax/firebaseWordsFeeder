import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time

# Initialize Firebase app
import Utils

cred = credentials.Certificate("C:\\Users\\bablu\\PycharmProjects\\firebaseWordsFeeder\\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': Utils.dbUrl
})


# Function to check if all required fields are present
def check_fields(word_data):
    if ('word' in word_data and 'meanings' in word_data and
            len(word_data['meanings']) > 0 and 'partOfSpeech' in word_data['meanings'][0] and
            'phonetic' in word_data):
        return True
    return False

# Main loop to continuously generate words and send API requests
while True:
    # Generate random word
    response = requests.get("https://random-word-api.herokuapp.com/word")
    word = response.json()[0]

    # Send API request to dictionary API
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)

    # Check if all required fields are present
    if response.status_code == 200:
        word_data = response.json()[0]
        if check_fields(word_data):
            # Add word data to Firebase Realtime Database
            ref = db.reference('words')
            word_ref = ref.push()
            word_ref.set({
                'word': word_data['word'],
                'definition': word_data['meanings'][0]['definitions'][0]['definition'],
                'synonym': word_data['meanings'][0]['definitions'][0]['synonyms'],
                'antonym': word_data['meanings'][0]['definitions'][0]['antonyms'],
                'partsofspeech': word_data['meanings'][0]['partOfSpeech'],

                'audio': word_data['phonetic'],
                'timestamp': int(time.time() * 1000)
            })

            print(f"Added word '{word_data['word']}' to database")
        else:
            print(f"Word '{word}' did not meet required conditions")
    else:
        print(f"Failed to retrieve data for word '{word}'")

    # Wait for 10 seconds before generating the next word
    time.sleep(5)
