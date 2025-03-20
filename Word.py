import syllapy
from metaphone import doublemetaphone
from nltk.corpus import words as corpus_words
from nltk.probability import FreqDist
import Colors

class Word:
    # Define category constants
    CATEGORY_MASTERED = "mastered"      # Words the user consistently gets right
    CATEGORY_AVERAGE = "average"        # Words with average performance
    CATEGORY_STRUGGLING = "struggling"  # Words the user frequently gets wrong
    
    def __init__(self, word, rightCount=0, wrongCount=0, asked=0, streak=0, difficulty=None, category=None) -> None:
        self.word = word.lower().strip()
        self.rightCount = rightCount
        self.wrongCount = wrongCount
        self.asked = asked
        self.streak = streak
        
        # Set difficulty
        self.difficulty = difficulty if difficulty else None 
        self.calculate_difficulty()
            
        # Set category
        self.category = category if category else self.CATEGORY_AVERAGE
        self.update_category()
    
    def update_category(self):
        if self.asked < 3:
            # Not enough data to categorize yet
            self.category = self.CATEGORY_AVERAGE
            return
        
        percentage = self.getPercentage()
        
        if percentage >= 95 and self.streak > 4:
            self.category = self.CATEGORY_MASTERED
        elif percentage <= 80 or (self.wrongCount > self.rightCount):
            self.category = self.CATEGORY_STRUGGLING
        else:
            self.category = self.CATEGORY_AVERAGE
    
    # Calculate difficulty based on various factors
    def calculate_difficulty(self):
        
        if self.difficulty is not None:
            return self.difficulty
        
        difficulty = 0
        
        # Add difficulty from length of word
        difficulty += self.calculate_difficulty_by_length()

        # Add difficulty from phonetic complexity
        difficulty += self.calculate_difficulty_by_phonetics()

        # Add difficulty from word frequency
        difficulty += self.calculate_difficulty_by_frequency()

        # Add difficulty from number of syllables
        difficulty += self.calculate_difficulty_by_syllables()
        
        # Normalize difficulty to be between 1 and 5
        max_possible_difficulty = 4 + 4 + 4 + 3  # maximum possible scores for each factor
        normalized_difficulty = (difficulty / max_possible_difficulty) * 5
        self.difficulty = normalized_difficulty

    # Difficulty based on length of word
    def calculate_difficulty_by_length(self):
        length = len(self.word)
        if length <= 4:
            return 1  # Easy
        elif length <= 7:
            return 2  # Medium
        elif length <= 10:
            return 3  # Hard
        else:
            return 4  # Very hard

    # Difficulty based on phonetics (using metaphone)
    def calculate_difficulty_by_phonetics(self):
        primary, secondary = doublemetaphone(self.word)
        if len(primary) > 4 or len(secondary) > 4:
            return 4  # Harder
        return 2  # Easier

    # Difficulty based on frequency
    def calculate_difficulty_by_frequency(self):
        word_list = corpus_words.words()
        frequency = FreqDist(word_list)
        if self.word not in frequency:
            return 4  # Word is rare or unknown, hence difficult
        word_freq = frequency[self.word]
        if word_freq > 100:
            return 1  # Common word
        elif word_freq > 50:
            return 2  # Uncommon
        else:
            return 3  # Rare word

    # Difficulty based on syllables
    def calculate_difficulty_by_syllables(self):
        syllables = syllapy.count(self.word)
        if syllables <= 2:
            return 1  # Easy
        elif syllables <= 4:
            return 2  # Medium
        else:
            return 3  # Hard
        
    def getPercentage(self):
        if self.asked == 0:
            return 0
        return (self.rightCount / self.asked) * 100
    
    def getWeightedPerformance(self):
        if self.asked == 0:
            return 0
        # Weight the performance considering the streak and difficulty of the word
        streak_bonus = self.streak * 0.05  # 5% bonus for each correct streak
        difficulty_factor = 1 + (self.difficulty - 1) * 0.1  # Increase performance based on difficulty
        
        # Add category factor - struggling words get lower performance (making them more likely to be selected)
        category_factor = 0.7 if self.category == self.CATEGORY_STRUGGLING else 1.0
        category_factor = 1.2 if self.category == self.CATEGORY_MASTERED else category_factor
        
        weighted_performance = self.getPercentage() * streak_bonus * difficulty_factor * category_factor
        return min(weighted_performance, 100)  # Cap it at 100%
    
    def __str__(self) -> str:
        retuStr = ""
        if self.asked > 0:
            retuStr = "\n\t I asked {cyan}{:d} times{end}\t you got it {green}{:d} times right {end} and {red}{:d} times wrong \t {end}averaging of {yellow}{:.2f}% {end} \tStreak: {blue}{:d}{end} \tCategory: {purple}{}{end}".format(
                self.asked,
                self.rightCount,
                self.wrongCount,
                (self.rightCount / self.asked * 100),
                self.streak,
                self.category,
                cyan=Colors.bcolors.OKCYAN,
                green=Colors.bcolors.OKGREEN,
                red=Colors.bcolors.FAIL,
                yellow=Colors.bcolors.WARNING,
                blue=Colors.bcolors.OKBLUE,
                purple=Colors.bcolors.HEADER,
                end=Colors.bcolors.ENDC,
            )
        else:
            retuStr = f"\t {Colors.bcolors.WARNING}Did ask you yet{Colors.bcolors.ENDC}"

        return "Word: " + self.word + retuStr
    
    def cmp(word1, word2):
        # Prioritize struggling words
        if word1.category == Word.CATEGORY_STRUGGLING and word2.category != Word.CATEGORY_STRUGGLING:
            return -1
        elif word1.category != Word.CATEGORY_STRUGGLING and word2.category == Word.CATEGORY_STRUGGLING:
            return 1
        
        # De-prioritize mastered words 
        if word1.category == Word.CATEGORY_MASTERED and word2.category != Word.CATEGORY_MASTERED:
            return 1
        elif word1.category != Word.CATEGORY_MASTERED and word2.category == Word.CATEGORY_MASTERED:
            return -1
            
        # Compare based on weighted performance if categories are the same
        if word1.getWeightedPerformance() < word2.getWeightedPerformance():
            return -1
        elif word1.getWeightedPerformance() > word2.getWeightedPerformance():
            return 1
        else:
            if word1.streak < word2.streak:
                return -1
            elif word1.streak > word2.streak:
                return 1
            else:
                return 0

