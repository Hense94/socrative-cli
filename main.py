import PyInquirer as inq
import click
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
        r = requests.get('https://api.socrative.com/rooms/api/current-activity/{}'.format(self.room))
        response = r.json()

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
        r = requests.get('https://api.socrative.com/quizzes/api/quiz/' + str(self.activityID), params, cookies=cookies)

        self.questions = json.loads(r.content)['questions']

    def setName(self):
        data = {'activity_instance_id': self.activityInstanceID, 'student_name': self.name}
        cookies = {'sa': self.authToken}

        requests.post('https://api.socrative.com/students/api/set-name/', data=json.dumps(data), cookies=cookies)

    def answerQuestion(self, answers, _type):
        cookies = {'sa': self.authToken}
        questionID = list(answers.keys())[0]
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


@click.command()
@click.argument('room')
@click.option('--name', '-n', help='The name to identify yourself with')
def main(room, name):
    c = Connection(room, name)
    nameQuestion = {'type': 'input', 'name': 'student_name', 'message': 'This room requires a name. Please enter one'}

    while c.nameRequired and not c.isNameSet():
        c.name = inq.prompt(nameQuestion)['student_name']

    c.setName()

    for question in c.questions:
        inqQuestion, t = convertQuestion(question)
        answers = inq.prompt(inqQuestion)
        c.answerQuestion(answers, t)


def convertQuestion(question):
    _type = question['type']
    inqQuestion = {'name': question['question_id'], 'message': question['question_text']}

    if _type == 'FR':
        inqQuestion['type'] = 'input'
        return inqQuestion, _type

    if _type == 'MC' or 'TF':
        if question['total_correct_answers'] != 1:
            inqQuestion['type'] = 'checkbox'
        else:
            inqQuestion['type'] = 'list'
            _type = 'SC'

        answers = [{'name': answer['text'], 'value': str(answer['id'])} for answer in question['answers']]
        inqQuestion['choices'] = answers

        return inqQuestion, _type


if __name__ == '__main__':
    main()

