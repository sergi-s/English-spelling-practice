class Word:
    def __init__(self, word, rightCount=0, wrongCount=0, asked=0) -> None:
        self.word = word.lower().strip()
        self.rightCount = rightCount
        self.wrongCount = wrongCount
        self.asked = asked

    def getPercentage(self):
        if self.asked == 0:
            return 0
        else:
            return self.rightCount / self.asked

    def __str__(self) -> str:
        retuStr = ""
        if self.asked > 0:

            retuStr = "\n\t I asked {:d} times\n\t you got it {:d} times right and {:d} times wrong \n\t averaging of {:.2f}%".format(
                self.asked,
                self.rightCount,
                self.wrongCount,
                (self.rightCount / self.asked * 100),
            )
        else:
            retuStr = "\t Did ask you yet"

        return "Word: " + self.word + retuStr
