import Colors
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

            retuStr = "\n\t I asked {cyan}{:d} times{end}\t you got it {green}{:d} times right {end} and {red}{:d} times wrong \t {end}averaging of {yellow}{:.2f}% {end}".format(
                self.asked,
                self.rightCount,
                self.wrongCount,
                (self.rightCount / self.asked * 100),
                cyan=Colors.bcolors.OKCYAN,
                green=Colors.bcolors.OKGREEN,
                red=Colors.bcolors.FAIL,
                yellow=Colors.bcolors.WARNING,
                end=Colors.bcolors.ENDC,
            )
        else:
            retuStr = f"\t {Colors.bcolors.WARNING}Did ask you yet{Colors.bcolors.ENDC}"

        return "Word: " + self.word + retuStr
