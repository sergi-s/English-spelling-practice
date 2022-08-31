from gtts import gTTS
import pyttsx3
import os

class TextToSpeech:
    def sayWord(wrod, language="en"):
        pass


class GTTS(TextToSpeech):
    def __init__(self, language="en") -> None:
        super().__init__()
        self.language = language

    def sayWord(self, word):
        mySound = gTTS(text=word, lang=self.language, slow=False)
        mySound.save("welcome.mp3")
        os.system("start welcome.mp3")


class PYTTS(TextToSpeech):
    def __init__(self, language="en") -> None:
        super().__init__()
        self.engine = pyttsx3.init()

    def sayWord(self, word):
        self.engine.say(word)
        self.engine.runAndWait()
