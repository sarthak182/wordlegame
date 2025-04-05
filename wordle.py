from flask import Flask, render_template, request, jsonify
import pickle as pk
import random
frddef=""
def r2(wordes):
    global frddef
    valid_rows = wordes.loc[150000:176000, 'Word'].dropna().reset_index(drop=True)
    resr = random.choice(valid_rows.values)
    frddef=wordes.loc[wordes['Word'] == resr, 'Definition'].values[0].replace('"','')
    print(frddef)
    return resr

def new_main_function(inputword, randomword):
    L = []
    inputword = inputword.lower()
    randomword = randomword.lower()

    matched_positions = [False] * 5
    randomword_counts = {}  # Track letter counts in randomword

    # Step 1: First pass - Mark green letters and track remaining counts
    for i in range(5):
        if inputword[i] == randomword[i]:
            L.append('#85E93B')  # Green
            matched_positions[i] = True
        else:
            L.append(None)  # Placeholder
            randomword_counts[randomword[i]] = randomword_counts.get(randomword[i], 0) + 1  # Count letters

    # Step 2: Second pass - Assign yellow shades based on distance
    for i in range(5):
        if L[i] is None:  # Process letters that weren't marked green
            if inputword[i] in randomword_counts and randomword_counts[inputword[i]] > 0:
                # Find all occurrences of inputword[i] in randomword
                indices = [j for j in range(5) if randomword[j] == inputword[i] and not matched_positions[j]]

                if indices:
                    # Find the closest misplaced position
                    closest_index = min(indices, key=lambda x: abs(i - x))
                    distance = abs(i - closest_index)

                    # Apply color based on distance
                    if distance == 1:
                        L[i] = '#FFD700'  # Darker yellow (1 block away)
                    elif distance == 2:
                        L[i] = '#FFC300'  # Slightly lighter yellow
                    elif distance == 3:
                        L[i] = '#FFA500'  # Orange-yellow
                    elif distance == 4:
                        L[i] = '#FF8C00'  # Dark orange

                    randomword_counts[inputword[i]] -= 1  # Reduce available count
                else:
                    L[i] = '#DCDCDC'  # Gray for incorrect letters
            else:
                L[i] = '#DCDCDC'  # Gray for incorrect letters

    return L, all(matched_positions)  # Returns win condition too

def main_function(inputword, randomword):
    L=[]
    inputword=inputword.lower()
    randomword=randomword.lower()
    matched_positions=[False]*5
    for i in range(5):
        if inputword[i]==randomword[i]:
            L.append('#85E93B')
            matched_positions[i]=True
        else:
            if inputword[i] in randomword:
                index=randomword.index(inputword[i])
                distance=abs(i-index)
                if distance==1:
                    L.append('#FFD700')
                elif distance==2:
                    L.append('#FFC300')
                elif distance==3:
                    L.append('#FFA500')
                elif distance==4:
                    L.append('#FF8C00')
            else:
                L.append('#DCDCDC')
    if all(matched_positions):
        L = ['#85E93B'] * 5
    return L, all(matched_positions)                    


fixedrandomword=""
input_words=[]
words_list=pk.load(open('five_letter_words.pkl', 'rb'))
words_list['Word']=words_list['Word'].str.lower()
valid_words=set(words_list['Word'])
words_dict=dict(zip(words_list['Word'],words_list['Word']))
current_word_count=0
app=Flask(__name__)
@app.route('/validate_word', methods=['POST'])
def validate_word():
    data=request.get_json()
    word=data.get('word','').lower()
    return jsonify({'valid':word in valid_words})

@app.route('/')
def home(): 
    global fixed_random_word
    fixed_random_word=r2(words_list)
    print("Computer selected word is: " +fixed_random_word)
    return render_template('index.html')

@app.route('/submit_word', methods=['POST'])
def submit_word():
    data=request.get_json()
    print(f"Raw data received: {data}")
    word=data.get('word')
    word=word.lower()
    if word in valid_words:
        color_list, winflag=main_function(word, fixed_random_word)
        print(color_list)
        definition=words_dict.get(word, 'Definition Unavailable')
        print(f"Word Entered: {word}")
        return jsonify({'status':'success', 'word':word, 'colors':color_list, 'definition':frddef, 'winflag':winflag})
    print("Invalid Word received.")
    return jsonify({'status':'failure', 'message':'invalid word'}), 400

@app.route('/win')
def win_page():
    return render_template('win.html')
if __name__=='__main__':
    app.run(debug=True, use_reloader=False)