import PyInquirer as inq
import click

from socrativecli.connection import Connection


@click.command()
@click.argument('room')
@click.option('--name', '-n', help='The name to identify yourself with')
def main(room, name):
    c = Connection(True, room, name)

    while c.nameRequired and not c.isNameSet():
        question = {'type': 'input', 'name': 'student_name', 'message': 'This room requires a name. Please enter one'}
        name = inq.prompt(question)['student_name']
        c.name = name

    if c.isNameSet():
        c.setName()

    for question in c.questions:
        pyInqQuestion, t = convertQuestion(question)
        answers = inq.prompt(pyInqQuestion)
        c.sendAnswer(answers, t)


def convertQuestion(question):
    _type = question['type']
    inqQuestion = {'name': question['question_id'], 'message': question['question_text']}

    if _type == 'FR':
        inqQuestion['type'] = 'input'
        return inqQuestion, _type

    if _type == 'MC' or 'TF':
        correctAnswers = question['total_correct_answers']
        if correctAnswers == 1:
            inqQuestion['type'] = 'list'
            _type = 'SC'

        else:
            inqQuestion['type'] = 'checkbox'
            inqQuestion['message'] = '{} ({} correct)'.format(question['question_text'], correctAnswers)
            #inqQuestion['validate'] = lambda a: 'You must choose at most {} answers'.format(correctAnswers) if len(a) > correctAnswers else True

        inqQuestion['choices'] = [{'name': a['text'], 'value': str(a['id'])} for a in question['answers']]

        return [inqQuestion], _type


class MultiChoiceValidator(inq.Validator):
    def validate(self, answer):
        print(answer)
        if len(answer) > 2:
            raise inq.ValidationError(
                message='Please enter a number',
                cursor_position=len(answer.text))  # Move cursor to end


if __name__ == '__main__':
    main()
