import streamlit as st
import soundfile as sf
import librosa
import librosa.display
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load your pre-trained deep learning model
model = tf.keras.models.load_model('model_dl.h5')

n_mfcc = 40

def extract_features(file_path):
    audio, sample_rate = librosa.load(file_path, sr=22050)
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=n_mfcc)
    mfccs_mean = pd.DataFrame(mfccs.mean(axis=1)).transpose()
    return mfccs_mean

def predict_emotion(mfccs_mean):
    # Preprocess the MFCC features if required
    # ...

    # Make the prediction using your model
    prediction = model.predict(mfccs_mean)
    return prediction

def create_waveplot(data, sampling_rate):
    plt.figure(figsize=(10, 4))
    plt.plot(data)
    plt.title('Waveplot')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.show()

def create_spectrogram(data, sampling_rate):
    plt.figure(figsize=(10, 4))
    spectrogram = librosa.amplitude_to_db(np.abs(librosa.stft(data)), ref=np.max)
    librosa.display.specshow(spectrogram, sr=sampling_rate, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    plt.show()

st.title("Telugu Speech Emotion Detection")
st.sidebar.title("Team -19  [AIE]")
st.sidebar.title("Aditya Rajesh Sakri")
st.sidebar.title("Vaka Satwik Reddy")
st.sidebar.title("Vamsi Krishna Vunnam")

uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])

if uploaded_file is not None:
    # Save the uploaded file
    file_path = "uploaded_audio" + uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    data, sampling_rate = librosa.load(file_path)
    
    
    st.subheader("Audio Waveform")
    wave_plot = create_waveplot(data, sampling_rate)
    st.pyplot(wave_plot)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    
    
    st.subheader("Spectrogram")
    spect = create_spectrogram(data, sampling_rate)
    st.pyplot(spect)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    
    
    st.subheader("Emotion Prediction")
    mfccs = extract_features(file_path)
    prediction = predict_emotion(mfccs)
    # Display your predicted emotion labels or probabilities
    st.write(prediction)
    # Define the emotion classes
    emotion_classes = ["Angry", "Sad", "Happy", "Fear"]

# Get the index of the class with the highest probability
    predicted_index = np.argmax(prediction)
 
# Get the predicted emotion label
    predicted_emotion = emotion_classes[predicted_index]

# Display the predicted emotion
    st.write("Predicted Emotion: ", predicted_emotion)
 
