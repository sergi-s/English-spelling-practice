
from datetime import datetime
import json
from distutils.log import error
from Word import Word
from PhrasalVerb import PhrasalVerb
import os

class FileManagement:
    def __init__(self) -> None:
        self.wordsFileName="data/words.json"
        self.phrasalVerbFileName="data/phrasal_verbs.json"
        
        if not os.path.exists("data"):
            os.makedirs("data")
        
    def writeInFile(self, data, fileName):
        try:
            # Writing to sample.json
            with open(fileName, "w") as outfile:
                outfile.write(data)
            return True
        except (error):
            print(error)
            return False

    def arryOfWordsToJson(self, words):
        return json.dumps([word.__dict__ for word in words]
                        # , indent=4
                          )

    def saveWords(self, words):
        self.writeInFile(self.arryOfWordsToJson(words), self.wordsFileName)

    def readWordsFromJson(self):
        words = []
        try:
            with open(self.wordsFileName, "r") as f:
                data = json.load(f)
                for wordData in data:
                    word = Word(
                        wordData["word"],
                        wordData.get("rightCount", 0),
                        wordData.get("wrongCount", 0),
                        wordData.get("asked", 0),
                        wordData.get("streak", 0),
                        wordData.get("difficulty"),
                        wordData.get("category")
                    )
                    words.append(word)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"No existing file found at {self.wordsFileName} or invalid JSON. Starting with empty word list.")
        return words
    
    def readPhrasalVerbsFromJson(self):
        phrasal_verbs = []
        try:
            with open(self.phrasalVerbFileName, "r") as f:
                data = json.load(f)
                for pvData in data:
                    pv = PhrasalVerb(
                        pvData["phrasal_verb"],
                        pvData.get("rightCount", 0),
                        pvData.get("wrongCount", 0),
                        pvData.get("asked", 0),
                        pvData.get("streak", 0),
                        pvData.get("difficulty"),
                        pvData.get("category")
                    )
                    phrasal_verbs.append(pv)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"No existing file found at {self.phrasalVerbFileName} or invalid JSON. Starting with empty phrasal verb list.")
        return phrasal_verbs

    def savePhrasalVerbs(self, phrasal_verbs):
        data = []
        for pv in phrasal_verbs:
            pvData = {
                "phrasal_verb": pv.phrasal_verb,
                "rightCount": pv.rightCount,
                "wrongCount": pv.wrongCount,
                "asked": pv.asked,
                "streak": pv.streak,
                "difficulty": pv.difficulty,
                "category": pv.category
            }
            data.append(pvData)
        with open(self.phrasalVerbFileName, "w") as f:
            json.dump(data, f, indent=4)
            
    def resetScore(self, fileName, type):
        # Archive and reset words
        words_archive_name = f"data/Archive-{type}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        if os.path.exists(fileName):
            os.rename(fileName, words_archive_name)
        for word in self.words:
            word.asked = word.rightCount = word.wrongCount = word.streak = 0
            word.category = Word.CATEGORY_AVERAGE
        self.fileMang.saveWords(self.words, fileName)
    
    def resetWordScore(self):
        self.resetScore(self.wordsFileName, "Words")
    
    def resetPhrasalVerbScore(self):
        self.resetScore(self.phrasalVerbFileName, "PhrasalVerbs")
    

    
