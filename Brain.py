from sys import exit

from Word import Word
from TextToSpeech import *
from Colors import bcolors
from FileManagment import FileManagement
from functools import cmp_to_key


class Management:

    words = []

    def __init__(self, fileName="sample.json", language="en") -> None:
        self.fileName = fileName
        self.fileMang = FileManagement()
        self.language = language
        self.soundEngine = PYTTS()
        # self.soundEngine = GTTS()

        self.words = self.fileMang.readFromJson()

    # --------------------------------------------------------------------------------
    def processWord(self, word):
        self.soundEngine.sayWord(word.word)
        userInput = input("Spell the word\t 'if you want to repeat press `r`'\n")
        if userInput.lower().strip() == "r":
            self.processWord(word)
            return
        if userInput.lower().strip() == word.word:
            print(f"{bcolors.OKGREEN}{bcolors.BOLD}\n3a4\n{bcolors.ENDC}")
            word.rightCount += 1
        else:
            print(f"{bcolors.FAIL}{bcolors.BOLD}\nsad\n{bcolors.ENDC}")
            word.wrongCount += 1
        word.asked += 1

    # --------------------------------------------------------------------------------
    def addWord(self):
        word = input("Insert the word\n")
        self.words.append(Word(word))
        self.fileMang.saveWords(self.words)

    # --------------------------------------------------------------------------------
    def saveOnExit(self, signal_received, frame):
        self.fileMang.saveWords(self.words)
        print("CTRL-C detected. Exiting gracefully and saving")
        exit(0)

    # --------------------------------------------------------------------------------
    def wordLoop(self):
        while True:
            temp = sorted(self.words, key=cmp_to_key(cmp))
            # self.words.sort(key=lambda x: x.getPercentage, reverse=True)
            # self.words.sort(key=cmp)

            for word in temp:
                print(word.word + ": " + str(word.getPercentage()))

            self.processWord(self.words[0])

    # --------------------------------------------------------------------------------
    def mainSystemLoop(self):
        choice = input(
            "Press 1  to start a training session, Press 2 to add a new word, Press 3 to reset score\t"
        )

        match choice:
            case "3":
                self.resetScore()
                self.mainSystemLoop()
                return

            case "2":
                self.addWord()
                self.mainSystemLoop()
                return
            case "1":
                self.wordLoop()

    def resetScore(self):
        for word in self.words:
            word.asked = 0
            word.rightCount = 0
            word.wrongCount = 0
        self.fileMang.saveWords(self.words)


def cmp(word1, word2):
    # print(
    #     "========="
    #     + str(word1.getPercentage())
    #     + " vs "
    #     + str(word2.getPercentage())
    #     + "=========="
    # )
    return word1.getPercentage() > word2.getPercentage()
    # if word1.getPercentage() < word2.getPercentage():
    #     return -1
    # elif word1.getPercentage() > word2.getPercentage():
    #     return 1
    # else:
    #     return 0
