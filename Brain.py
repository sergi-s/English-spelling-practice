from sys import exit
import os
from datetime import datetime
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
        self.fileName = f"data/{fileName}"
        self.fileMang = FileManagement()
        self.language = language
        self.soundEngine = PYTTS()
        self.words = self.fileMang.readFromJson()
        self.in_menu = True

    def processWord(self, word):
        self.in_menu = False
        try:
            while True:
                self.soundEngine.sayWord(word.word)
                userInput = input("Spell the word\t 'if you want to repeat press `r`'\n\n").strip().lower()
                if userInput == "r":
                    continue
                word.asked += 1
                if userInput == word.word:
                    print(f"{bcolors.OKGREEN}{bcolors.BOLD}\nCorrect!\n{bcolors.ENDC}")
                    word.rightCount += 1
                    word.streak += 1
                    break
                else:
                    print(f"{bcolors.FAIL}{bcolors.BOLD}\nIncorrect, try again.\n{bcolors.ENDC}")
                    print(f"{bcolors.OKGREEN}{bcolors.BOLD}\n{word.word} != {bcolors.WARNING}{userInput}\n{bcolors.ENDC}")
                    word.wrongCount += 1
                    word.streak = 0
            word.update_category()
        except KeyboardInterrupt:
            print("\nInterrupted. Returning to main menu...")
            raise

    def addWord(self):
        word = input("Insert the word\n").strip()
        if any(savedWord.word == word for savedWord in self.words):
            print(f"{bcolors.BOLD}{bcolors.WARNING}Already Exists\n{bcolors.ENDC}")
            return
        self.words.append(Word(word))
        self.fileMang.saveWords(self.words)

    def saveOnExit(self, signal_received, frame):
        if self.in_menu:
            self.fileMang.saveWords(self.words)
            print("CTRL-C detected. Exiting gracefully and saving")
            exit(0)
        else:
            raise KeyboardInterrupt

    def filterWordsByCategory(self, category_filter):
        if category_filter:
            filtered_words = [w for w in self.words if w.category == category_filter]
            if not filtered_words:
                print(f"\n{bcolors.WARNING}No words in the {category_filter} category! Using all words instead.{bcolors.ENDC}")
                return self.words
            return filtered_words
        return self.words

    def wordLoop(self):
        self.in_menu = False
        print("\nWhich category would you like to focus on?")
        print(f"1. {bcolors.FAIL}Struggling words{bcolors.ENDC}")
        print(f"2. {bcolors.WARNING}Average words{bcolors.ENDC}")
        print(f"3. {bcolors.OKGREEN}Mastered words{bcolors.ENDC}")
        print(f"4. All words (mixed)")
        choice = input("\nEnter your choice (1-4): ").strip()
        category_filter = {
            "1": Word.CATEGORY_STRUGGLING,
            "2": Word.CATEGORY_AVERAGE,
            "3": Word.CATEGORY_MASTERED
        }.get(choice)
        filtered_words = self.filterWordsByCategory(category_filter)
        try:
            while True:
                temp = sorted(filtered_words, key=cmp_to_key(Word.cmp))
                chosenWord = temp[0] if random.random() < 0.7 and temp else random.choice(filtered_words)
                self.processWord(chosenWord)
                self.fileMang.saveWords(self.words)
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            self.fileMang.saveWords(self.words)
            self.in_menu = True
            self.mainSystemLoop()

    def miniReport(self):
        print(f"Total Number of words Saved = {bcolors.BOLD}{bcolors.WARNING}{len(self.words)}{bcolors.ENDC}")
        categories = {
            Word.CATEGORY_MASTERED: "Mastered Words",
            Word.CATEGORY_AVERAGE: "Average Words",
            Word.CATEGORY_STRUGGLING: "Struggling Words"
        }
        categories_colors = {
            Word.CATEGORY_MASTERED: "OKGREEN",
            Word.CATEGORY_AVERAGE: "WARNING",
            Word.CATEGORY_STRUGGLING: "FAIL"
        }
        for category, label in categories.items():
            count = len([w for w in self.words if w.category == category])
            print(f"{getattr(bcolors, categories_colors[category])}{label}:{bcolors.ENDC} {count}")
        struggling_words = [w for w in self.words if w.category == Word.CATEGORY_STRUGGLING and w.asked > 1]
        struggling_words = sorted(struggling_words, key=cmp_to_key(lambda a, b: a.getPercentage() - b.getPercentage()))
        mastered_words = [w for w in self.words if w.category == Word.CATEGORY_MASTERED and w.asked > 1]
        
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}Your struggling words are:{bcolors.ENDC}")
        print("\n".join(f"{w.word}:\t {w.getPercentage():.2f}%,\t Streak: {w.streak}" for w in struggling_words) or "No struggling words identified yet!")
        print(f"\n{bcolors.OKGREEN}{bcolors.BOLD}Your mastered words are:{bcolors.ENDC}")
        print("\n".join(f"{w.word}:\t {w.getPercentage():.2f}%, \t Streak: {w.streak}" for w in mastered_words[:5]) or "No mastered words yet - keep practicing!")
        if len(mastered_words) > 5:
            print(f"...and {len(mastered_words) - 5} more mastered words.")

    def mainSystemLoop(self):
        self.in_menu = True
        menu_options = {
            "1": self.wordLoop,
            "2": self.addWord,
            "3": self.resetScore,
            "4": self.miniReport,
            "5": lambda: os.system("clear"),
            "6": self.addWordLoop,
            "7": self.recategorizeWords
        }
        try:
            choice = input(
                "Press 1 to start a training session,\n"
                "Press 2 to add a new word,\n"
                "Press 3 to reset score,\n"
                "Press 4 to show your performance report,\n"
                "Press 5 to clear the console,\n"
                "Press 6 to add a word (LOOP),\n"
                "Press 7 to re-categorize all words\n"
            ).strip()
            action = menu_options.get(choice)
            if action:
                action()
            else:
                print(f"{bcolors.FAIL}Invalid choice!{bcolors.ENDC}")
            self.mainSystemLoop()
        except KeyboardInterrupt:
            self.saveOnExit(None, None)

    def addWordLoop(self):
        self.in_menu = False
        try:
            while True:
                self.addWord()
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            self.in_menu = True
            self.mainSystemLoop()

    def recategorizeWords(self):
        for word in self.words:
            word.update_category()
        self.fileMang.saveWords(self.words)
        print(f"{bcolors.OKGREEN}All words have been recategorized!{bcolors.ENDC}")
        self.mainSystemLoop()

    def resetScore(self):
        archive_name = f"data/Archive-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        os.rename("data/sample.json", archive_name)
        for word in self.words:
            word.asked = word.rightCount = word.wrongCount = word.streak = 0
            word.category = Word.CATEGORY_AVERAGE
        self.fileMang.saveWords(self.words)