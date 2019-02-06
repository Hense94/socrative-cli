import PyInquirer as inq
import click

from socrative.connection import Connection


@click.command()
@click.argument('room')
@click.option('--name', '-n', help='The name to identify yourself with')
def main(room, name):
    c = Connection(room, name)

    while c.nameRequired and not c.isNameSet():
        question = {'type': 'input', 'name': 'student_name', 'message': 'This room requires a name. Please enter one'}
        name = inq.prompt(question)['student_name']
        c.name = name

    c.setName()

    for question in c.questions:
        pyInqQuestion, t = convertQuestion(question)
        answers = inq.prompt(pyInqQuestion)
        c.answerQuestion(answers, t)


def convertQuestion(question):
    t = question['type']

    if t == 'FR':
        q = {'type': 'input', 'name': question['question_id'], 'message': question['question_text']}
        return q, t

    if t == 'MC' or 'TF':
        answers = []
        for answer in question['answers']:
            answers.append({'name': answer['text'], 'value': str(answer['id'])})

        if question['total_correct_answers'] == 1:
            q = {'type': 'list', 'name': question['question_id'], 'message': question['question_text'], 'choices': answers}
            return q, 'SC'
        else:
            q = {'type': 'checkbox', 'name': question['question_id'], 'message': question['question_text'], 'choices': answers}
            return q, t


if __name__ == '__main__':
    main()
