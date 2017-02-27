from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest

from sqlalchemy.exc import DBAPIError

from ..models import Question, Answer

from collections import deque
from cgi import escape
from random import shuffle

import os, shutil, uuid, imghdr

QUESTION_DEQUE_LENGTH = 10000
SUPPORTED_IMG_EXTENSIONS = ('jpeg', 'gif', 'png', 'bmp')

# next question id queue so they don't repeat too often
question_deque = deque(maxlen=QUESTION_DEQUE_LENGTH)

@view_defaults(route_name='home')
class TriviaViews:
    def __init__(self, request):
        self.request = request

    @view_config(renderer='templates/index.jinja2')
    def index(self):
        return dict()

    @view_config(xhr=True, renderer='templates/question.jinja2')
    def get_question(self):
        if not question_deque:
            questions_ids = self.request.dbsession\
            .query(Question.id).limit(QUESTION_DEQUE_LENGTH).all()

            shuffle(questions_ids)
            question_deque.extend(questions_ids)
        q = self.request.dbsession.query(Question).get(question_deque.pop())
        a = q.answers
        streak = self.request.session.get('streak', 0)
        return dict(image=q.get_img, question=q, answers=a, streak=streak)

    @view_config(request_method='POST', xhr=True, renderer='json')
    def submit_answer(self):
        try:
            question_id = self.request.POST['q_id']
            answer_id = self.request.POST['answer_id']

            answ = self.request.dbsession.query(Answer).get(answer_id)
            q = self.request.dbsession.query(Question).get(question_id)
        except Exception as e:
            raise HTTPBadRequest()

        correct_answer = q.get_correct_answer

        session = self.request.session
        streak = session.get('streak', 0)

        if answ == correct_answer:
            session['streak'] = streak + 1
            return dict(correct_answer=correct_answer.id, streak=streak + 1)
        else:
            session['streak'] = 0
            return dict(correct_answer=correct_answer.id, streak=0)

    @view_config(route_name='create', renderer='templates/create.jinja2')
    def create_form(self):
        return dict()

    @view_config(route_name='create', renderer='templates/create.jinja2',
                 request_method='POST')
    def create_submit(self):
        input_file = self.request.POST['image'].file
        file_extension = imghdr.what(input_file)

        if not (file_extension in SUPPORTED_IMG_EXTENSIONS):
            return dict(message="Only jpeg, gif, png and bmp files allowed")

        new_filename = '%s.%s' % (uuid.uuid4(), file_extension)

        file_path = os.path.join('quicktrivia', 'media', new_filename)

        temp_file_path = file_path + '~'

        input_file.seek(0)
        with open(temp_file_path, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)

        os.rename(temp_file_path, file_path)

        question_text = escape(self.request.POST['question'])
        q = Question(content=question_text, img_name=new_filename)
        self.request.dbsession.add(q)

        answers = (
                   escape(self.request.POST['answer-a']),
                   escape(self.request.POST['answer-b']),
                   escape(self.request.POST['answer-c']),
                   escape(self.request.POST['answer-d']),
                  )

        correct_answer_number = self.request.POST['correct-answer']

        for counter, answer in enumerate(answers):
            correct = True if counter == int(correct_answer_number) else False
            self.request.dbsession.add(Answer(question=q, content=answer,
                                              is_correct=correct))

        return dict(message="Created question " + question_text)
