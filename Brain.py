from sys import exit
import os
from datetime import datetime
from Word import Word
from PhrasalVerb import PhrasalVerb
from TextToSpeech import *
from Colors import bcolors
from FileManagment import FileManagement
from functools import cmp_to_key
import random
import nltk
nltk.download('words')


class Management:

    words = []
    phrasal_verbs = []

    def __init__(self) -> None:
        self.exit_flag = False
        self.fileMang = FileManagement()
        self.language = "en"
        self.soundEngine = PYTTS()
        self.words = self.fileMang.readWordsFromJson()
        self.phrasal_verbs = self.fileMang.readPhrasalVerbsFromJson()
        self.in_menu = True

    def processWord(self, word):
        self.in_menu = False
        try:
            while True:
                print(f"{word.asked} times asked, {word.rightCount} times correct, {word.wrongCount} times wrong, {word.streak} streak, {word.getPercentage():.2f}%, category: {word.category}, difficulty:{word.difficulty}")
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

    # New method to process phrasal verbs similar to processWord
    def processPhrasalVerb(self, phrasal_verb):
        self.in_menu = False
        try:
            while True:
                self.soundEngine.sayWord(phrasal_verb.phrasal_verb)
                userInput = input("Spell the phrasal verb\t 'if you want to repeat press `r`'\n\n").strip().lower()
                if userInput == "r":
                    continue
                phrasal_verb.asked += 1
                if userInput == phrasal_verb.phrasal_verb:
                    print(f"{bcolors.OKGREEN}{bcolors.BOLD}\nCorrect!\n{bcolors.ENDC}")
                    phrasal_verb.rightCount += 1
                    phrasal_verb.streak += 1
                    break
                else:
                    print(f"{bcolors.FAIL}{bcolors.BOLD}\nIncorrect, try again.\n{bcolors.ENDC}")
                    print(f"{bcolors.OKGREEN}{bcolors.BOLD}\n{phrasal_verb.phrasal_verb} != {bcolors.WARNING}{userInput}\n{bcolors.ENDC}")
                    phrasal_verb.wrongCount += 1
                    phrasal_verb.streak = 0
            phrasal_verb.update_category()
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

    # New method to add a phrasal verb
    def addPhrasalVerb(self):
        phrasal_verb = input("Insert the phrasal verb\n").strip()
        if any(saved_pv.phrasal_verb == phrasal_verb for saved_pv in self.phrasal_verbs):
            print(f"{bcolors.BOLD}{bcolors.WARNING}Already Exists\n{bcolors.ENDC}")
            return
        self.phrasal_verbs.append(PhrasalVerb(phrasal_verb))
        self.fileMang.savePhrasalVerbs(self.phrasal_verbs)

    def saveOnExit(self, signal_received, frame):
        if self.in_menu:
            self.fileMang.saveWords(self.words)
            self.fileMang.savePhrasalVerbs(self.phrasal_verbs)
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

    # New method to filter phrasal verbs by category
    def filterPhrasalVerbsByCategory(self, category_filter):
        if category_filter:
            filtered_pvs = [pv for pv in self.phrasal_verbs if pv.category == category_filter]
            if not filtered_pvs:
                print(f"\n{bcolors.WARNING}No phrasal verbs in the {category_filter} category! Using all phrasal verbs instead.{bcolors.ENDC}")
                return self.phrasal_verbs
            return filtered_pvs
        return self.phrasal_verbs

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
                print(len(self.words))
                temp = sorted(filtered_words, key=cmp_to_key(Word.cmp))
                chosenWord = temp[0] if random.random() < 0.7 and temp else random.choice(filtered_words)
                self.processWord(chosenWord)
                self.fileMang.saveWords(self.words)
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            self.fileMang.saveWords(self.words)
            self.in_menu = True
            self.mainSystemLoop()
            
    def phrasalVerbLoop(self):
        self.in_menu = False
        print("\nWhich category would you like to focus on?")
        print(f"1. {bcolors.FAIL}Struggling phrasal verbs{bcolors.ENDC}")
        print(f"2. {bcolors.WARNING}Average phrasal verbs{bcolors.ENDC}")
        print(f"3. {bcolors.OKGREEN}Mastered phrasal verbs{bcolors.ENDC}")
        print(f"4. All phrasal verbs (mixed)")
        choice = input("\nEnter your choice (1-4): ").strip()
        category_filter = {
            "1": PhrasalVerb.CATEGORY_STRUGGLING,
            "2": PhrasalVerb.CATEGORY_AVERAGE,
            "3": PhrasalVerb.CATEGORY_MASTERED
        }.get(choice)
        filtered_pvs = self.filterPhrasalVerbsByCategory(category_filter)
        try:
            while True:
                if not filtered_pvs:
                    print(f"\n{bcolors.WARNING}No phrasal verbs available! Please add some first.{bcolors.ENDC}")
                    break
                temp = sorted(filtered_pvs, key=cmp_to_key(PhrasalVerb.cmp))
                chosen_pv = temp[0] if random.random() < 0.7 and temp else random.choice(filtered_pvs)
                self.processPhrasalVerb(chosen_pv)
                self.fileMang.savePhrasalVerbs(self.phrasal_verbs)
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            self.fileMang.savePhrasalVerbs(self.phrasal_verbs)
            self.in_menu = True
            self.mainSystemLoop()

    def miniReport(self):
        print(f"Total Number of words Saved = {bcolors.BOLD}{bcolors.WARNING}{len(self.words)}{bcolors.ENDC}")
        print(f"Total Number of phrasal verbs Saved = {bcolors.BOLD}{bcolors.WARNING}{len(self.phrasal_verbs)}{bcolors.ENDC}")
        
        # Process words
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
        
        print("\n--- WORDS REPORT ---")
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
            
        # Process phrasal verbs
        print("\n--- PHRASAL VERBS REPORT ---")
        pv_categories = {
            PhrasalVerb.CATEGORY_MASTERED: "Mastered Phrasal Verbs",
            PhrasalVerb.CATEGORY_AVERAGE: "Average Phrasal Verbs",
            PhrasalVerb.CATEGORY_STRUGGLING: "Struggling Phrasal Verbs"
        }
        for category, label in pv_categories.items():
            count = len([pv for pv in self.phrasal_verbs if pv.category == category])
            print(f"{getattr(bcolors, categories_colors[category])}{label}:{bcolors.ENDC} {count}")
        struggling_pvs = [pv for pv in self.phrasal_verbs if pv.category == PhrasalVerb.CATEGORY_STRUGGLING and pv.asked > 1]
        struggling_pvs = sorted(struggling_pvs, key=cmp_to_key(lambda a, b: a.getPercentage() - b.getPercentage()))
        mastered_pvs = [pv for pv in self.phrasal_verbs if pv.category == PhrasalVerb.CATEGORY_MASTERED and pv.asked > 1]
        
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}Your struggling phrasal verbs are:{bcolors.ENDC}")
        print("\n".join(f"{pv.phrasal_verb}:\t {pv.getPercentage():.2f}%,\t Streak: {pv.streak}" for pv in struggling_pvs) or "No struggling phrasal verbs identified yet!")
        print(f"\n{bcolors.OKGREEN}{bcolors.BOLD}Your mastered phrasal verbs are:{bcolors.ENDC}")
        print("\n".join(f"{pv.phrasal_verb}:\t {pv.getPercentage():.2f}%, \t Streak: {pv.streak}" for pv in mastered_pvs[:5]) or "No mastered phrasal verbs yet - keep practicing!")
        if len(mastered_pvs) > 5:
            print(f"...and {len(mastered_pvs) - 5} more mastered phrasal verbs.")

    def mainSystemLoop(self):
        self.in_menu = True
        menu_options = {
            "1": self.wordLoop,
            "2": self.addWord,
            "3": self.fileMang.resetWordScore,
            "4": self.miniReport,
            "5": lambda: os.system("clear"),
            "6": self.addWordLoop,
            "7": self.recategorizeWords,
            "8": self.phrasalVerbLoop,
            "9": self.addPhrasalVerb,
            "10": self.addPhrasalVerbLoop,
            "11": self.fileMang.resetPhrasalVerbScore,
        }
        try:
            choice = input(
                "Press 1 to start a word training session,\n"
                "Press 2 to add a new word,\n"
                "Press 3 to reset words score,\n"
                "Press 4 to show your performance report,\n"
                "Press 5 to clear the console,\n"
                "Press 6 to add a word (LOOP),\n"
                "Press 7 to re-categorize all words\n"
                "Press 8 to start a phrasal verb training session,\n"
                "Press 9 to add a new phrasal verb,\n"
                "Press 10 to add phrasal verbs (LOOP)\n"
                "Press 11 to reset phrasal verbs score\n"
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

    # New method for adding phrasal verbs in a loop
    def addPhrasalVerbLoop(self):
        self.in_menu = False
        try:
            while True:
                self.addPhrasalVerb()
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            self.in_menu = True
            self.mainSystemLoop()

    def recategorizeWords(self):
        for word in self.words:
            word.update_category()
        self.fileMang.saveWords(self.words)
        
        # Also recategorize phrasal verbs
        for pv in self.phrasal_verbs:
            pv.update_category()
        self.fileMang.savePhrasalVerbs(self.phrasal_verbs)
        
        print(f"{bcolors.OKGREEN}All words and phrasal verbs have been recategorized!{bcolors.ENDC}")
        self.mainSystemLoop()

        # Archive and reset phrasal verbs
        pv_archive_name = f"data/Archive-PhrasalVerbs-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        if os.path.exists(self.phrasalVerbFileName):
            os.rename(self.phrasalVerbFileName, pv_archive_name)
        for pv in self.phrasal_verbs:
            pv.asked = pv.rightCount = pv.wrongCount = pv.streak = 0
            pv.category = PhrasalVerb.CATEGORY_AVERAGE
        self.fileMang.savePhrasalVerbs(self.phrasal_verbs, self.phrasalVerbFileName)
        
        print(f"{bcolors.OKGREEN}All scores have been reset and previous data archived!{bcolors.ENDC}")