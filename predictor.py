import os
import json
from datetime import datetime
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv

from utils.persona import PersonaSpec, Demographic, Geographic, Psychographic, Behavioral, Technographic


class IntentPredictor:
	def __init__(
			self,
			question_categories: list[str] = ['purchase intent', 'comparison to alternatives'],
			response_model: str = 'gpt-5-mini',
			response_filename: str = 'unnamed.json',
		):
		self.question_categories = question_categories
		self.response_model = response_model
		self.response_filename = response_filename
		self.qc_str = ', '.join(self.question_categories)
		self.client=OpenAI()
		self.responses = list()

		os.makedirs('responses', exist_ok=True)

	def predict(
			self, 
			concept_to_predict: str, 
			persona: PersonaSpec, 
			sample_size: int = 500,
			clean_biography: bool = True
		):

		# Build a questionnaire
		print(f'{datetime.now()} BUILDING QUESTIONNAIRE')
		questionnaire = self.client.responses.create(
			model='gpt-5-mini',
			#input=f'You are an experienced market researcher, tasked with creating a brief but thorough questionnaire. The questionnaire will be presented to a group of market research participants, concerning the following product:\n{concept_to_predict}\nWrite a questionnaire consisting only of open questions, with the purpose of the questionnaire being to assess consumer intent of the product as it is now. Questions should cover the following subcategories: {self.qc_str}. Omit questions about the interviewee, their demographic data is already known. Your output should consist only of the questions, and all questions should be separated by the following token: NEXTQUESTION.The question should start with the category of the presented subcategories it belongs to, then an &, then the question.'
			input=f'You are an experienced market researcher, tasked with creating a brief but thorough questionnaire. The questionnaire will be presented to a group of market research participants, concerning the following product:\n{concept_to_predict}\nWrite a questionnaire consisting only of open questions, with the purpose of the questionnaire being to assess consumer intent of the product as it is now. Questions should cover the following subcategories: {self.qc_str}. Omit questions about the interviewee, their demographic data is already known. Your output should consist only of the questions, and all questions should be separated by two newlines, like \n\n'
		).output_text
		questions = questionnaire.split('\n\n')
		print(f'	{len(questions)} questions created.')
		
		if len(questions) == 1: # Incorrectly split, likely wrong token presented
			print('Questions incorrectly separated, check separation token')
			import pdb; pdb.set_trace()

		print(f'{datetime.now()} INTERVIEWING PERSONAS')
		#for respondent_idx in tqdm(range(sample_size)):
		for respondent_idx in tqdm(range(1)): # TODO make concurrent

			# Make a current persona
			respondent_bio = persona.generate_biography()
			if clean_biography:
				respondent_bio = self.client.responses.create(
					model='gpt-5-nano',
					input=f'Turn the following biography into a more complete biography, worded in second person as someone to impersonate (You are impersonating...). Optimise the text to function as a system prompt for an llm, such that the llm will behave as closely as possible to a person with the given bio. As output, provide only the raw system prompt. Bio:\n{respondent_bio}'
				).output_text
				
			# Perform questionnaire on persona
			persona_answers = self.perform_questionnaire(
				biography=respondent_bio,
				product=concept_to_predict,
				questionnaire=questionnaire
			)

			self.responses.append(
				{
					'biography': respondent_bio,
					'responses': persona_answers
				}
			)

		mr = {
			'concept': concept_to_predict,
			'questions': questions,
			'responses': self.responses
		}
		
		# Store raw results
		print(f'{datetime.now()} SAVING RESEARCH OUTCOMES AT {os.path.join('responses', self.response_filename)}')
		with open(os.path.join('responses', self.response_filename), 'w') as f:
			json.dump(mr, f, indent=4, ensure_ascii=True)
			
		import pdb; pdb.set_trace()

	def perform_questionnaire(
			self, 
			biography: str, 
			product: str, 
			questionnaire: str
			#questions: list[str] # TODO compare performance on a per question basis
		):
		messages = [
			{"role": "system", "content": f'{biography}'},
			{"role": "user", "content": f'Thank you for taking the time to fill out this questionnaire, concerning the following product:\n{product}. Please fill out the following questions:\n{questionnaire}. Please provide only your final answers, separated by two newlines, like \n\n'}
		]
		questionnaire_answers = self.client.chat.completions.create(
			model=self.response_model,
			messages=messages
		).choices[0].message.content.split('\n\n')

		if len(questionnaire_answers) == 1: # Incorrectly split, likely wrong token presented
			print('Answers incorrectly separated, check separation token')
			import pdb; pdb.set_trace()
		elif len(questionnaire_answers) != len(questionnaire.split('\n\n')): # N answers != n questions; something wrong
			print(f'Different number of questions and answers: {len(questionnaire_answers)} answers and {len(questionnaire.split('\n\n'))} questions')
			import pdb; pdb.set_trace()
		
		return questionnaire_answers

if __name__ == '__main__':
	load_dotenv()
	
	concept_to_predict = "A drink that functions as a meal; It contains a similar amount of calories as a regular meal (400-500), added nutrients and vitamins and about 20-30 grams of protein. It is priced at €3.50."
	persona = PersonaSpec(
        demographic=Demographic(
            age=[18, 35],
            gender=["male", "female"],
            income_level=["low", "medium", "high"],
            education_level=["high school", "a bachelors degree", "a masters degree"],
            occupation=["student", "professional", "freelancer"]
        ),
        geographic=Geographic(
            country=["Netherlands"],
            region=["Northeast", "West", "South", "Randstad"],
            urbanicity=["urban", "suburban", "rural"]
        ),
        psychographic=Psychographic(
            lifestyle=["health-conscious", "budget-conscious", "eco-conscious", "trend-oriented"],
            interests=["fitness", "gaming", "beauty", "cooking", "travel"]
        ),
        behavioral=Behavioral(
            brand_loyalty=["loyalist", "switcher", "new entrant"],
        ),
        technographic=Technographic(
            devices=["smartphone", "tablet", "smartwatch", "laptop"],
            social_media=["TikTok", "Instagram", "YouTube", "LinkedIn"],
        )
    )
	ip = IntentPredictor()
	ip.predict(
		concept_to_predict=concept_to_predict, 
		persona=persona
	)
