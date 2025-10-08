import random
import re

class JimPersonality:
    """Adds drunk, inappropriate personality to text"""

    def __init__(self):
        # Drunk speech patterns
        self.drunk_replacements = {
            "what": ["whaaaat", "wha", "what the hell"],
            "that": ["thaaaat", "that's", "tha"],
            "oh": ["ohhhhh", "oooooh", "oh my"],
            "wow": ["wooooow", "woah", "holy shit"],
            "nice": ["niiiiice", "nice!", "well well well"],
            "miss": ["*hiccup* miss", "missed!", "airballed that one"],
        }

        # Jim's verbal tics
        self.interjections = [
            "*burps*",
            "*chuckles*",
            "*hiccup*",
            "hehe...",
            "ahahaha...",
            "*mutters under breath*",
            "*slurps drink*",
        ]

        # Filler words for rambling
        self.fillers = [
            "uhhhh",
            "ya know",
            "like",
            "I mean",
            "wait what was I saying",
            "anyway",
        ]

    def enhance_text(self, text: str, quality: str = None) -> str:
        """
        Make text sound like drunk Jim

        Args:
            text: Original commentary
            quality: Throw quality (great, good, okay, bad, miss, bust, game_winner)

        Returns:
            Enhanced text with Jim's personality
        """
        enhanced = text

        # Add pauses and ellipses for drunk rambling
        enhanced = enhanced.replace(", ", "... ")
        enhanced = enhanced.replace(". ", "... ")

        # Replace words with drunk versions
        for word, replacements in self.drunk_replacements.items():
            if word in enhanced.lower():
                if random.random() < 0.4:  # 40% chance
                    drunk_version = random.choice(replacements)
                    # Case-insensitive replacement
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                    enhanced = pattern.sub(drunk_version, enhanced, count=1)

        # Add interjections based on throw quality
        if quality in ["great", "game_winner"]:
            if random.random() < 0.6:
                interjection = random.choice(["*laughs*", "wooooow", "holy shit"])
                enhanced = f"{interjection} {enhanced}"

        elif quality in ["bad", "miss"]:
            if random.random() < 0.5:
                interjection = random.choice(["*burps*", "*chuckles*", "oooooh"])
                enhanced = f"{interjection} {enhanced}"

        # Randomly add fillers for rambling effect
        if random.random() < 0.3:
            filler = random.choice(self.fillers)
            # Insert filler in the middle
            words = enhanced.split()
            if len(words) > 3:
                insert_pos = len(words) // 2
                words.insert(insert_pos, filler)
                enhanced = " ".join(words)

        # Add occasional trailing off
        if random.random() < 0.2:
            enhanced += "..."

        return enhanced
