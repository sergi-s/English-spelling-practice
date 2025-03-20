
import json
from distutils.log import error
from Word import Word

class FileManagement:
    def __init__(self, fileName="sample.json") -> None:
        self.fileName = fileName
        
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
        self.writeInFile(self.arryOfWordsToJson(words), self.fileName)

    def readFromJson(self):
        words = []
        with open(self.fileName, "r") as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            for word in json_object:
                words.append(
                    Word(
                        word["word"],
                        word["rightCount"],
                        word["wrongCount"],
                        word["asked"],
                        word["streak"],
                        word["difficulty"],
                        word["category"]
                    )
                )
        print("words loaded successfully")
        return words
