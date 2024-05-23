import config
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import pywhatkit
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import google.generativeai as genai
import webbrowser
import re
import threading

maquina = pyttsx3.init()
audio = sr.Recognizer()
comando = ''

genai.configure(api_key=config.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

generative_config={
    'candidate_count': 1,
    'temperature': 0.5,
}

safety_settings={
    'HARASSMENT': 'BLOCK_NONE',
    'HATE': 'BLOCK_NONE',
    'SEXUAL': 'BLOCK_NONE',
    'DANGEROUS': 'BLOCK_NONE',
}

model = genai.GenerativeModel(model_name='gemini-1.0-pro',
                                generation_config=generative_config,
                                safety_settings=safety_settings)

def remove_before(text, word):

  return re.sub(r"(.*?)(?<!\b%s\b)\b%s\b" % (word, word), "", text)

def listen_command():

    try:
        with sr.Microphone(device_index=1) as source:
            print('Escutando...')
            voz = audio.listen(source)
            comando= audio.recognize_google(voz, language='pt-BR')
            comando = comando.lower()

            if 'luna' in comando:
                comando = remove_before(comando,'luna')

                maquina.runAndWait()
    except Exception as e:
        print(f'O microfone não esta OK {e}')
    return comando


os.environ['SPOTIPY_CLIENT_ID'] = config.client_id
os.environ['SPOTIPY_CLIENT_SECRET'] = config.client_secret
os.environ['SPOTIPY_REDIRECT_URI'] = 'https://example.com/callback'

scope = 'user-read-playback-state,user-modify-playback-state'
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

def execute_command(comando):
    comando = listen_command()

    if 'procure por' in comando:
        procurar = comando.replace('procure por', '')
        wikipedia.set_lang('pt')
        resultado = wikipedia.summary(procurar,2)
        print(resultado)
        maquina.say(resultado)
        maquina.runAndWait()

    elif 'pesquise por' in comando:
        procurar = comando.replace('pesquise por', '')
        wikipedia.set_lang('pt')
        resultado = wikipedia.summary(procurar,2)
        print(resultado)
        maquina.say(resultado)
        maquina.runAndWait()

    elif 'toque no youtube' in comando:
        musica = comando.replace('toque', '')
        resultado = pywhatkit.playonyt(musica)
        maquina.say(f'Tocando {musica} no YouTube')
        maquina.runAndWait()

    elif 'responda' in comando:
        procurar = comando.replace('responda','')
        resposta = model.generate_content(procurar)
        maquina.say(resposta.text)
        maquina.runAndWait()

    elif 'toque no spotify' in comando:
        musica = comando.replace('toque no spotify', '')
        query = musica
        result = sp.search(query, 1, 0, 'track')
        playback_state = sp.current_playback()
        if sp.currently_playing() and playback_state['is_playing']:
            sp.pause_playback()
        uri = result['tracks']['items'][0]['uri']
        webbrowser.open_new_tab(uri)
        maquina.runAndWait()

    elif 'adicione a fila' in comando:
        musica = comando.replace('adicione a fila','')
        query = musica
        result = sp.search(query, 1, 0, 'track')
        uri = result['tracks']['items'][0]['uri']
        sp.add_to_queue(uri)
        maquina.say(f'{musica} adicionada a fila')
        maquina.runAndWait()

    elif 'repita' in comando:
        sp.repeat(state='track')
        maquina.runAndWait()

    elif 'próxima' in comando:
        sp.next_track()

    elif 'anterior' in comando:
        sp.previous_track()

    elif 'pausar' in comando:
        sp.pause_playback()

    elif 'continue' in comando:
        sp.start_playback()

    elif 'obrigado' in comando:
        #model.start_chat(history='Você é uma assistente virtual chamada Luna')
        resposta = model.generate_content(comando)
        maquina.say(resposta.text)
    else:
        pass
while True:
    execute_command(comando)

