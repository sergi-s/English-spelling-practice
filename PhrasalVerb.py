import syllapy
from metaphone import doublemetaphone
from nltk.corpus import words as corpus_words
from nltk.probability import FreqDist
import Colors

class PhrasalVerb:
    # Define category constants
    CATEGORY_MASTERED = "mastered"      # Phrasal verbs the user consistently gets right
    CATEGORY_AVERAGE = "average"        # Phrasal verbs with average performance
    CATEGORY_STRUGGLING = "struggling"  # Phrasal verbs the user frequently gets wrong
    
    def __init__(self, phrasal_verb, rightCount=0, wrongCount=0, asked=0, streak=0, difficulty=None, category=None) -> None:
        self.phrasal_verb = phrasal_verb.lower().strip()
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
        
        # Phrasal verbs are inherently more complex
        base_difficulty = 2
        
        # Count the number of words in the phrasal verb
        word_count = len(self.phrasal_verb.split())
        difficulty += word_count - 1  # More words = more difficult
        
        # Add difficulty from total length of phrasal verb
        difficulty += self.calculate_difficulty_by_length()
        
        # Add difficulty from syllables across all words
        difficulty += self.calculate_difficulty_by_syllables()
        
        # Normalize difficulty to be between 1 and 5
        max_possible_difficulty = base_difficulty + 3 + 4 + 3  # maximum possible scores
        normalized_difficulty = (difficulty / max_possible_difficulty) * 5
        self.difficulty = normalized_difficulty

    # Difficulty based on length of the phrasal verb
    def calculate_difficulty_by_length(self):
        length = len(self.phrasal_verb)
        if length <= 8:
            return 1  # Easy
        elif length <= 12:
            return 2  # Medium
        elif length <= 18:
            return 3  # Hard
        else:
            return 4  # Very hard

    # Difficulty based on syllables (counting all words)
    def calculate_difficulty_by_syllables(self):
        total_syllables = sum(syllapy.count(word) for word in self.phrasal_verb.split())
        if total_syllables <= 3:
            return 1  # Easy
        elif total_syllables <= 5:
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
        # Weight the performance considering the streak and difficulty of the phrasal verb
        streak_bonus = self.streak * 0.05  # 5% bonus for each correct streak
        difficulty_factor = 1 + (self.difficulty - 1) * 0.1  # Increase performance based on difficulty
        
        # Add category factor - struggling phrasal verbs get lower performance (making them more likely to be selected)
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

        return "Phrasal Verb: " + self.phrasal_verb + retuStr
    
    def cmp(phrasal_verb1, phrasal_verb2):
        # Prioritize struggling phrasal verbs
        if phrasal_verb1.category == PhrasalVerb.CATEGORY_STRUGGLING and phrasal_verb2.category != PhrasalVerb.CATEGORY_STRUGGLING:
            return -1
        elif phrasal_verb1.category != PhrasalVerb.CATEGORY_STRUGGLING and phrasal_verb2.category == PhrasalVerb.CATEGORY_STRUGGLING:
            return 1
        
        # De-prioritize mastered phrasal verbs 
        if phrasal_verb1.category == PhrasalVerb.CATEGORY_MASTERED and phrasal_verb2.category != PhrasalVerb.CATEGORY_MASTERED:
            return 1
        elif phrasal_verb1.category != PhrasalVerb.CATEGORY_MASTERED and phrasal_verb2.category == PhrasalVerb.CATEGORY_MASTERED:
            return -1
            
        # Compare based on weighted performance if categories are the same
        if phrasal_verb1.getWeightedPerformance() < phrasal_verb2.getWeightedPerformance():
            return -1
        elif phrasal_verb1.getWeightedPerformance() > phrasal_verb2.getWeightedPerformance():
            return 1
        else:
            if phrasal_verb1.streak < phrasal_verb2.streak:
                return -1
            elif phrasal_verb1.streak > phrasal_verb2.streak:
                return 1
            else:
                return 0