"""
This module is designed to test functions related to multiple-choice question (MCQ) files. 
It provides simple testing results to verify the correctness and functionality of the implemented MCQ-related functions.
"""

import tqdm
import unittest
from multiple_choice_quiz import generate_mcq_question, Arithmetic


class TestMCQ(unittest.TestCase):
    def test_generate_mcq_question(self):
        # Test case 1: Test the generate_mcq_question function with default parameters
        result = generate_mcq_question()
        self.assertTrue(result)

        # Test case 2: Test the generate_mcq_question function with custom parameters
        result = generate_mcq_question(subjects=['Algebra', 'Arithmetic'], latex=False)
        self.assertTrue(result)

    def test_questions_about_remainder(self, maximal_number=10, latex=True):
        # Test case 1: Test the questions_about_remainder function with default parameters
        
        count = 1
        result = Arithmetic(latex=latex).q_remainder_of_division()
        print(result)
        while (input("Do you want to continue? (y/n): ") != 'n') and count < maximal_number:
            result = Arithmetic(latex=latex).q_remainder_of_division()
            print(result)
            count += 1

#  TestMCQ().test_questions_about_remainder(latex=False)


def simple_test():
    for _ in tqdm(range(15_000)):
        data = generate_mcq_question(latex=True)
        #  print(data)        
        for important_key in ["question", "suggested_answer", "index_answer"]:
            if important_key not in data.keys():
                raise ValueError(f"The '{important_key}' key is missing in the {data['question_name']} function.")

    #  print('Everything is correct.')

if __name__ == "__main__":
    def est_okay(liste):
        for i in range(len(liste) - 1):
            if liste[i] > liste[i + 1]:
                return False
        return True
    
    def tri(liste):
        n = len(liste)
        for i in range(n):
            for j in range(0, n-i-1):
                if liste[j] > liste[j+1]:
                    liste[j], liste[j+1] = liste[j+1], liste[j]
            input(i, liste)
        return liste
    
    tri((1, 6, 3, 2))