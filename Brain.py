from sys import exit
import os
import datetime
import signal

from Word import Word
from TextToSpeech import *
from Colors import bcolors
from FileManagment import FileManagement
from functools import cmp_to_key
import random
import nltk
nltk.download('words')


class Management:

    words = []

    def __init__(self, fileName="sample.json", language="en") -> None:
        self.exit_flag = False
        self.fileName = fileName
        self.fileMang = FileManagement()
        self.language = language
        self.soundEngine = PYTTS()
        # self.soundEngine = GTTS()

        self.words = self.fileMang.readFromJson()
        self.in_menu = True  # Flag to track if we're in the main menu

    # --------------------------------------------------------------------------------
    def processWord(self, word):
        # Mark that we're not in the menu
        self.in_menu = False
        
        try:
            self.soundEngine.sayWord(word.word)
            
            while True:
                userInput = input("Spell the word\t 'if you want to repeat press `r`'\n\n")
                
                if userInput.lower().strip() == "r":
                    self.processWord(word)
                    return
                
                if userInput.lower().strip() == word.word:
                    print(f"{bcolors.OKGREEN}{bcolors.BOLD}\nCorrect!\n{bcolors.ENDC}")
                    word.rightCount += 1
                    word.streak += 1  # Increase the streak
                
                    break  
                else:
                    print(f"{bcolors.FAIL}{bcolors.BOLD}\nIncorrect, try again.\n{bcolors.ENDC}")
                    print(
                        f"{bcolors.OKGREEN}{bcolors.BOLD}\n{word.word} != {bcolors.WARNING}{userInput}\n{bcolors.ENDC}"
                    )
                    word.wrongCount += 1
                    word.streak = 0  # Reset the streak on incorrect attempt
                
                word.asked += 1
            
            # Adjust the difficulty based on performance after each interaction
            word.calculate_difficulty()
        except KeyboardInterrupt:
            # Simply propagate the KeyboardInterrupt to be caught by wordLoop
            print("\nInterrupted. Returning to main menu...")
            raise KeyboardInterrupt


    # --------------------------------------------------------------------------------
    def addWord(self):
        word = input("Insert the word\n")
        newWord = Word(word)
        for savedWord in self.words:
            if savedWord.word == newWord.word:

                print(f"{bcolors.BOLD}{bcolors.WARNING}Already Exists\n{bcolors.ENDC}")
                return

        self.words.append(newWord)
        self.fileMang.saveWords(self.words)

    # --------------------------------------------------------------------------------
    def saveOnExit(self, signal_received, frame):
        # If we're in the main menu, exit the application
        # Otherwise, return to the main menu
        if self.in_menu:
            self.fileMang.saveWords(self.words)
            print("CTRL-C detected. Exiting gracefully and saving")
            exit(0)
        else:
            # We're in a loop, not in the menu
            # Just raise KeyboardInterrupt to be handled by the try-except blocks
            raise KeyboardInterrupt

    # --------------------------------------------------------------------------------
    def wordLoop(self):
        # Mark that we're not in the menu
        self.in_menu = False
        
        try:
            while True:
                # Sort the words based on their dynamically adjusted difficulty for the user
                temp = sorted(self.words, key=cmp_to_key(Word.cmp))
                chosenWord = temp[0] if bool(random.getrandbits(1)) else random.choice(temp)
                try:
                    self.processWord(chosenWord)
                except KeyboardInterrupt:
                    # Catch KeyboardInterrupt from processWord and propagate it up
                    raise
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            self.fileMang.saveWords(self.words)  # Save words before returning to menu
            self.in_menu = True  # Mark that we're back in the menu
            self.mainSystemLoop()

    # --------------------------------------------------------------------------------
    def miniReport(self):
        print(
            f"Total Number of words Saved = {bcolors.BOLD}{bcolors.WARNING}{len(self.words)}{bcolors.ENDC}"
        )
        temp = [word for word in self.words if word.asked > 1]
        
        sorted(temp, key=cmp_to_key(Word.cmp))

        print("Your worst words are:")
        worst_words = [word for word in temp if word.asked > 1]
        
        for word in worst_words:
            print(f"{word.word}: {word.getPercentage():.2f}% performance, Streak: {word.streak}")

    # --------------------------------------------------------------------------------

    def mainSystemLoop(self):
        # Mark that we're in the menu
        self.in_menu = True
        
        try:
            choices = input(
                '''Press 1  to start a training session, \n
                Press 2 to add a new word, \n
                Press 3 to reset score, \n
                Press 4 to show your performance report, \n
                Press 5 to clear the console\n
                press 6 to add a word (LOOP)\n
                \t'''
            )

            if choices == "6":
                self.in_menu = False  # Mark that we're not in the menu
                try:
                    while True:
                        self.addWord()
                except KeyboardInterrupt:
                    print("\nReturning to main menu...")
                    self.in_menu = True  # Mark that we're back in the menu
                    self.mainSystemLoop()
                    return
            elif choices == "4":
                self.miniReport()
                self.mainSystemLoop()
                return
            elif choices == "5":
                os.system("clear")
                self.mainSystemLoop()
                return
            elif choices == "3":
                self.resetScore()
                self.mainSystemLoop()
                return
            elif choices == "2":
                self.addWord()
                self.mainSystemLoop()
                return
            elif choices == "1":
                self.wordLoop()
        except KeyboardInterrupt:
            # This should only happen if we're in the main menu
            self.saveOnExit(None, None)

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
            word.streak = 0
            word.difficulty = word.calculate_difficulty()
        self.fileMang.saveWords(self.words)
