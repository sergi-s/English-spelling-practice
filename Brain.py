from sys import exit
import os
import datetime

from Word import Word
from TextToSpeech import *
from Colors import bcolors
from FileManagment import FileManagement
from functools import cmp_to_key
import random


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
        userInput = input("Spell the word\t 'if you want to repeat press `r`'\n\n")
        if userInput.lower().strip() == "r":
            self.processWord(word)
            return
        if userInput.lower().strip() == word.word:
            print(f"{bcolors.OKGREEN}{bcolors.BOLD}\n3a4\n{bcolors.ENDC}")
            word.rightCount += 1
        else:
            print(f"{bcolors.FAIL}{bcolors.BOLD}\nsad\n{bcolors.ENDC}")

            print(
                f"{bcolors.OKGREEN}{bcolors.BOLD}\n{word.word} != {bcolors.WARNING}{userInput}\n{bcolors.ENDC}"
            )
            word.wrongCount += 1
        word.asked += 1

    # --------------------------------------------------------------------------------
    def addWord(self):
        word = input("Insert the word\n")
        newWord = Word(word)
        for savedWord in self.words:
            if savedWord.word == newWord.word:

                print(f"{bcolors.BOLD}{bcolors.WARNING}Already Exists\n{bcolors.ENDC}")

                continue

        self.words.append(newWord)
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

            # for word in temp:
            #     print(word.word + ": " + str(word.getPercentage()), end="\t")
            # print()

            if bool(random.getrandbits(1)):
                self.processWord(temp[0])
            else:
                self.processWord(random.choice(temp))

    # --------------------------------------------------------------------------------
    def miniReport(self):
        print(
            f"Total Number of words Saved = {bcolors.BOLD}{bcolors.WARNING}{len(self.words)}{bcolors.ENDC}"
        )
        temp = sorted(self.words, key=cmp_to_key(cmp))

        print("Your worst word is ")
        [print(word) for word in temp[0:2]]

    # --------------------------------------------------------------------------------

    def mainSystemLoop(self):
        choice = input(
            "Press 1  to start a training session, Press 2 to add a new word, Press 3 to reset score, Press 4 to clear the console: (1,2,3,4):\t"
        )

        if choice == "6":
            while True:
                self.addWord()
            return
        elif choice == "5":
            self.miniReport()
            self.mainSystemLoop()
            return
        elif choice == "4":
            os.system("cls")
            self.mainSystemLoop()
            return
        elif choice == "3":
            self.resetScore()
            self.mainSystemLoop()
            return
        elif choice == "2":
            self.addWord()
            self.mainSystemLoop()
            return
        elif choice == "1":
            self.wordLoop()

    # --------------------------------------------------------------------------------
    def resetScore(self):
        now = str(datetime.datetime.now())
        newName = f"Archive-{now}.json"
        newName = newName.replace(":", "-")
        os.rename("sample.json", newName)
        for word in self.words:
            word.asked = 0
            word.rightCount = 0
            word.wrongCount = 0
        self.fileMang.saveWords(self.words)


def cmp(word1, word2):
    if word1.getPercentage() < word2.getPercentage():
        return -1
    elif word1.getPercentage() > word2.getPercentage():
        return 1
    else:
        if word1.asked > word2.asked:
            return -1
        elif word1.asked <= word2.asked:
            return 1
