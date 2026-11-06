import unittest
from src.matcher import calculate_match_score, calculate_skill_gap

class TestMatcher(unittest.TestCase):
    def test_calculate_match_score(self):
        text1 = "I am a software engineer with Python and SQL."
        text2 = "Looking for a software engineer who knows Python and SQL."
        score = calculate_match_score(text1, text2)
        self.assertTrue(score > 40)  # Shared terms produce a moderate-to-high cosine similarity
        
        text3 = "Unrelated text about cooking and baking cakes."
        score_low = calculate_match_score(text1, text3)
        self.assertTrue(score_low < 20) # Should be dissimilar

    def test_calculate_skill_gap(self):
        resume_skills = {"Python", "Sql"}
        jd_skills = {"Python", "Sql", "Aws"}
        
        matched, missing = calculate_skill_gap(resume_skills, jd_skills)
        self.assertEqual(matched, {"Python", "Sql"})
        self.assertEqual(missing, {"Aws"})

if __name__ == '__main__':
    unittest.main()