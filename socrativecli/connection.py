import sys
import json
import requests


class Connection:
    def __init__(self, verbose, room, name):
        self.verbose = verbose
        self.room = room
        self.name = name
        self.nameRequired = False
        self.activityID = None
        self.activityInstanceID = None
        self.authToken = None
        self.questions = None

        self.print('Connecting to {}... '.format(self.room), newline=False)
        self.getActivityIds()
        self.print('Done!')

        self.print('Authenticating... ', newline=False)
        self.getAuthToken()
        self.print('Done!')

        self.print('Retrieving questions... ', newline=False)
        self.getQuestions()
        self.print('Done!')

    def print(self, s, newline=True):
        if self.verbose:
            if newline:
                print(s)
            else:
                print(s, end='')

    def isNameSet(self):
        return self.name is not '' and self.name is not None

    def getActivityIds(self):
        r = requests.get('https://api.socrative.com/rooms/api/current-activity/{}'.format(self.room))
        response = r.json()

        if r.status_code != 200:
            sys.exit('Invalid room name')

        self.activityID = response['activity_id']
        self.activityInstanceID = response['id']

        for setting in response['settings']:
            if setting['key'] == 'require_names':
                self.nameRequired = setting['value'] == 'True'
                break

    def getAuthToken(self):
        data = {'role': 'student', 'name': self.room, 'tz_offset': -60}
        r = requests.post('https://api.socrative.com/rooms/api/join/', data)

        self.authToken = r.headers['Set-Cookie'].split(';')[0][3:]

    def getQuestions(self):
        params = {'room_name': self.room}
        cookies = {'sa': self.authToken}
        r = requests.get('https://api.socrative.com/quizzes/api/quiz/{}'.format(self.activityID), params, cookies=cookies)

        self.questions = json.loads(r.content)['questions']

    def setName(self):
        self.print('Setting name... ', newline=False)

        data = {'activity_instance_id': self.activityInstanceID, 'student_name': self.name}
        cookies = {'sa': self.authToken}

        requests.post('https://api.socrative.com/students/api/set-name/', data=json.dumps(data), cookies=cookies)

        self.print('Done!')

    def sendAnswer(self, answers, _type):
        answerList = list(answers.keys())
        if len(answers) == 0:
            sys.exit('')

        cookies = {'sa': self.authToken}
        questionID = answerList[0]
        data = {'question_id': questionID, 'activity_instance_id': self.activityInstanceID}

        if _type == 'MC':
            selectionAnswers = [{'answer_id': answer_id} for answer_id in answers[questionID]]
            answer_ids = ','.join(str(e) for e in answers[questionID])

            data['selection_answers'] = selectionAnswers
            data['answer_ids'] = answer_ids

        elif _type == 'SC':
            data['selection_answers'] = answers[questionID]
            data['answer_ids'] = str(answers[questionID])

        else:
            data['text_answers'] = [{'answer_text': answers[questionID]}]
            data['answer_text'] = answers[questionID]

        requests.post('https://api.socrative.com/students/api/responses/', data=json.dumps(data), cookies=cookies)
