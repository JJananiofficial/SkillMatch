import unittest
from src.skill_extractor import extract_skills

class TestSkillExtractor(unittest.TestCase):
    def test_extract_skills(self):
        mock_dict = {
            "Programming": ["python", "c++"],
            "Cloud": ["aws", "docker"]
        }
        text = "I know Python, SQL, AWS and Docker. I also use C++."
        
        extracted = extract_skills(text, mock_dict)
        self.assertIn("Python", extracted)
        self.assertIn("C++", extracted)
        self.assertIn("Aws", extracted)
        self.assertIn("Docker", extracted)
        self.assertNotIn("Sql", extracted) # Not in mock dict

if __name__ == '__main__':
    unittest.main()
