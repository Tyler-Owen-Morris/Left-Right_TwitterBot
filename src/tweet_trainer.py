import pandas as pd
import numpy as np
import logging, os
import re
import boto3
import sys
import pickle
import random
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.callbacks import LambdaCallback

right_tweets = pd.read_csv('../data/right_tweets.csv')
tweet_string = '  |  '.join(right_tweets.tweets.to_numpy())

def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def on_epoch_end(epoch, _):
    # Function invoked at end of each epoch. Prints generated text.
    print('''                                                       
@@@@@@@@  @@@@@@@    @@@@@@    @@@@@@@  @@@  @@@  @@@  
@@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  @@@  @@@  @@@  
@@!       @@!  @@@  @@!  @@@  !@@       @@!  @@@  @@!  
!@!       !@!  @!@  !@!  @!@  !@!       !@!  @!@  !@   
@!!!:!    @!@@!@!   @!@  !@!  !@!       @!@!@!@!  @!@  
!!!!!:    !!@!!!    !@!  !!!  !!!       !!!@!!!!  !!!  
!!:       !!:       !!:  !!!  :!!       !!:  !!!       
:!:       :!:       :!:  !:!  :!:       :!:  !:!  :!:  
:: ::::   ::       ::::: ::   ::: :::  ::   :::   ::  
: :: ::    :         : :  :    :: :: :   :   : :  :::  
                                                ''')
    print('----- Generating text after Epoch: %d' % epoch)

    if epoch >=10 and epoch % 2 == 0:
        start_index = random.randint(0, len(processed_text) - maxlen - 1)
        for temperature in [1.0]:
            print('----- temperature:', temperature)

            generated = ''
            sentence = processed_text[start_index: start_index + maxlen]
            generated += sentence
            print('----- Generating with seed: "' + sentence + '"')
            sys.stdout.write(generated)

            for i in range(2000):
                x_pred = np.zeros((1, maxlen, len(chars)))
                for t, char in enumerate(sentence):
                    x_pred[0, t, char_indices[char]] = 1.

                preds = model.predict(x_pred, verbose=0)[0]
                next_index = sample(preds, temperature)
                next_char = indices_char[next_index]

                generated += next_char
                sentence = sentence[1:] + next_char

                sys.stdout.write(next_char)
                sys.stdout.flush()
            with open('../data/raw_generated_text_aws.txt', "a+") as f:
                f.write(generated[maxlen:]+"\n")
            print()
    else:
        pass
    pass

def spit_out_text():
    # Function invoked at end of each epoch. Prints generated text.
    print("****************************************************************************")
    #print('----- Generating text after Epoch: %d' % epoch)
    
    start_index = random.randint(0, len(processed_text) - maxlen - 1)
    for temperature in [0.5,1.0,1.5,2.0]:
        print('----- temperature:', temperature)

        generated = ''
        sentence = processed_text[start_index: start_index + maxlen]
        #sentence = 'the matrix  |  the fifth element  |  han'
        generated += sentence
        print('----- Generating with seed: "' + sentence + '"')
        sys.stdout.write(generated)

        for i in range(1000):
            x_pred = np.zeros((1, maxlen, len(chars)))
            for t, char in enumerate(sentence):
                x_pred[0, t, char_indices[char]] = 1.

            preds = model.predict(x_pred, verbose=0)[0]
            next_index = sample(preds, temperature)
            next_char = indices_char[next_index]

            generated += next_char
            sentence = sentence[1:] + next_char

            sys.stdout.write(next_char)
            sys.stdout.flush()
        with open('../data/raw_generated_text_aws.txt', "a+") as f:
              f.write(generated[maxlen:]+"\n")
        print()

# ***************** EVERYTHING BELOW HERE RUNS AFTER ALL FUNCTIONS AND DATA HAVE BEEN LOADED ****************

processed_text = tweet_string.lower().replace('\r','').replace('%','').replace('(','').replace(')','').replace('*','').replace('/','').replace('\\','').replace('[','').replace(']','').replace('^','').replace('_','').replace('`','').replace('~','')
processed_text = re.sub(r'[^\x00-\x7f]',r'', processed_text)
chars = sorted(list(set(processed_text)))
print(chars)
print('total chars:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

# cut the text in semi-redundant sequences of maxlen characters
maxlen = 40
step = 1
sentences = []
next_chars = []
for i in range(0, len(processed_text) - maxlen, step):
    sentences.append(processed_text[i: i + maxlen])
    next_chars.append(processed_text[i + maxlen])

x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

print('Build model...')
model = Sequential()
model.add(LSTM(256, input_shape=(maxlen, len(chars))))
#model.add(Dense(len(chars)*2, activation='softmax'))
model.add(Dropout(0.2))
model.add(Dense(len(chars), activation='softmax'))
optimizer = RMSprop(lr=0.02)
model.compile(loss='categorical_crossentropy', optimizer="adam")

# print('Load model...')
# model = keras.models.load_model('../data/tweet_generator_right')

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Fit the model
print_callback = LambdaCallback(on_epoch_end=on_epoch_end)
print("fitting model")
model.fit(x, y,
        batch_size=256,
        epochs=20,
        callbacks=[print_callback])


print("***************")
print("MODEL FINISHED TRAINING!")

model.save('../data/tweet_generator_right')
for _ in range(5):
    spit_out_text()

print("Script finished")