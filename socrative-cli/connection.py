import json
import requests


class Connection:
    def __init__(self, room, name):
        self.room = room
        self.name = name
        self.nameRequired = False
        self.activityID = None
        self.activityInstanceID = None
        self.authToken = None
        self.questions = None

        self.getActivityIds()
        self.getAuthToken()
        self.getQuestions()

    def isNameSet(self):
        return self.name is not "" and self.name is not None

    def getActivityIds(self):
        r = requests.get('https://api.socrative-cli.com/rooms/api/current-activity/{}'.format(self.room))
        response = r.json()

        self.activityID = response['activity_id']
        self.activityInstanceID = response['id']

        for setting in response['settings']:
            if setting['key'] == 'require_names':
                self.nameRequired = setting['value'] == 'True'
                break

    def getAuthToken(self):
        data = {'role': 'student', 'name': self.room, 'tz_offset': -60}
        r = requests.post('https://api.socrative-cli.com/rooms/api/join/', data)

        self.authToken = r.headers['Set-Cookie'].split(';')[0][3:]

    def getQuestions(self):
        params = {'room_name': self.room}
        cookies = {'sa': self.authToken}
        r = requests.get('https://api.socrative-cli.com/quizzes/api/quiz/' + str(self.activityID), params, cookies=cookies)

        self.questions = json.loads(r.content)['questions']

    def setName(self):
        data = {'activity_instance_id': self.activityInstanceID, 'student_name': self.name}
        cookies = {'sa': self.authToken}

        requests.post('https://api.socrative-cli.com/students/api/set-name/', data=json.dumps(data), cookies=cookies)

    def answerQuestion(self, answers, _type):
        questionID = list(answers.keys())[0]
        cookies = {'sa': self.authToken}

        if _type == 'MC':
            selectionAnswers = [{'answer_id': answer_id} for answer_id in answers[questionID]]
            answer_ids = ','.join(str(e) for e in answers[questionID])

            data = {'question_id': questionID, 'activity_instance_id': self.activityInstanceID,
                    'selection_answers': selectionAnswers, 'text_answers': [], 'answer_ids': answer_ids}

        elif _type == 'SC':
            data = {'question_id': questionID, 'activity_instance_id': self.activityInstanceID,
                    'selection_answers': answers[questionID], 'text_answers': [], 'answer_ids': str(answers[questionID])}

        else:
            data = {'question_id': questionID, 'activity_instance_id': self.activityInstanceID,
                    'text_answers': [{'answer_text': answers[questionID]}], 'selection_answers': [],
                    'answer_ids': '', 'answer_text': answers[questionID]}

        r = requests.post('https://api.socrative-cli.com/students/api/responses/', data=json.dumps(data), cookies=cookies)
