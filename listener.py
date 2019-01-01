import time
from commands import command_handler

import speech_recognition as sr


def listen():
    r = sr.Recognizer()
    m = sr.Microphone()
    with m as source:
        r.adjust_for_ambient_noise(source)  # calibration
    # start listening in the background
    stop_listening = r.listen_in_background(m, _callback)
    # `stop_listening` は関数で、読んだら止まる
    print("start listening")
    while True:
        # ずっとlistenし続ける
        time.sleep(0.1)

    # 何らかの原因でwhileを抜け出したら止める
    print("stop listening")
    stop_listening(wait_for_stop=False)


def _callback(recognizer, audio):
    """
    音声認識をして、その結果からコマンドを実行する
    """
    message = _audio_recognition(recognizer, audio)
    command_handler(message)


def _audio_recognition(recognizer, audio, google=True, sphinx=False):
    google_message = ''
    sphinx_message = ''

    if google:
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            google_message = recognizer.recognize_google(audio)
            print("Google Speech Recognition thinks you said: " + google_message)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    if sphinx:
        try:
            sphinx_message = recognizer.recognize_sphinx(audio)
            print("Sphinx thinks you said: " + sphinx_message)
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))

    return google_message + ":" + sphinx_message
