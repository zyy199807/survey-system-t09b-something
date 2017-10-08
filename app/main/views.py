'''
app/main/views.py
- - - - - - -
webpage routes for package 'main' in VM
- - - - - - -
ZHENYU YAO z5125769 2017-10
'''


from flask import abort, jsonify, redirect, render_template, request, url_for
from flask_login import login_required

from . import main
from .decorators import authority_level_required
from .validators import Validator
from ..model.models import Choice, Question, Survey, Result, Survey_Question


# TODO implement data validators


# index, temporarily redirect to login page automatically
@main.route('/')
def index():
    return redirect(url_for('auth.login'))


# admin dashboard
@main.route('/admin')
@login_required
@authority_level_required('Admin')
def admin_dashboard():
    return render_template('main/admin_dashboard.html')


# view all questions
@main.route('/admin/questions')
@login_required
@authority_level_required('Admin')
def ad_question_pool():
    return render_template('main/ad_question_pool.html')


# create question
@main.route('/admin/questions/create', methods=['GET', 'POST'])
@login_required
@authority_level_required('Admin')
def ad_question_create():
    if request.is_json and not Validator.question_new(request.json):
        abort(400)
    elif request.is_json:
        json_data = request.json
        new_ques_id = Question.new(json_data.get('question_type'),
                                   json_data.get('question_name'))
        choices = list(zip(json_data.get('choice_content'),
                           [i+1 for i in range(len(json_data.get('choice_content')))]))
        for choice in choices:
            Choice.new(new_ques_id, choice[0], choice[1])
        return url_for('.ad_question_pool')
    return render_template('main/ad_create_question.html')


@main.route('/admin/questions/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
@authority_level_required('Admin')
def ad_question_edit(question_id):
    if request.is_json and not Validator.question_edit(request.json):
        abort(400)
    elif request.is_json:
        json_data = request.json
        Question.update(question_id,
                        json_data.get('question_type'),
                        json_data.get('question_name'))
        modi_choi_id = json_data.get('choice_id')
        modi_choi = list(zip(modi_choi_id,
                             json_data.get('choice_content'),
                             [i+1 for i in range(len(modi_choi_id))]))
        for choi_id in Choice.query.filter_by(qID=question_id).all().chID:
            if choi_id not in modi_choi_id:
                Choice.delete(choi_id)
        for choice in modi_choi:
            if choice[0] == -1:
                Choice.new(question_id, choice[1], choice[2])
            else:
                Choice.update(choice[0], choice[1], choice[2])
        return url_for('.ad_question_pool')
    return render_template('main/ad_edit_question.html')


# delete question
@main.route('/admin/questions/delete/<int:question_id>')
@login_required
@authority_level_required('Admin')
def ad_question_delete(question_id):
    Question.delete(question_id)
    return url_for('.ad_question_pool')


# preview question
@main.route('/admin/questions/view/<int:question_id>')
@login_required
@authority_level_required('Admin')
def ad_question_view(question_id):
    return render_template('main/ad_view_question.html')


# view all surveys
@main.route('/admin/surveys')
@login_required
@authority_level_required('Admin')
def ad_survey_list():
    return render_template('main/ad_survey_list.html')


# create surveys and choose questions
@main.route('/admin/surveys/create', methods=['GET', 'POST'])
@login_required
@authority_level_required('Admin')
def ad_survey_create():
    if request.is_json and not Validator.survey_new(request.json):
        abort(400)
    elif request.is_json:
        json_data = request.json
        new_surv_id = Survey.new(json_data.get('course_id'),
                                 json_data.get('survey_name'),
                                 json_data.get('start_date'),
                                 json_data.get('close_date'))
        ques_all = list(zip(json_data.get('question_id'),
                            json_data.get('question_order')))
        for ques in ques_all:
            Survey_Question.new(new_surv_id, ques[0], ques[1])
        return url_for('.ad_survey_list')
    return render_template('main/ad_create_survey.html')


# edit surveys and choose questions
@main.route('/admin/surveys/edit/<int:survey_id>', methods=['GET', 'POST'])
@login_required
@authority_level_required('Admin')
def ad_survey_edit(survey_id):
    if Validator.survey_offline(survey_id):
        if request.is_json and not Validator.survey_edit(request.json):
            abort(400)
        elif request.is_json:
            json_data = request.json
            Survey.update(survey_id,
                          json_data.get('course_id'),
                          json_data.get('survey_name'),
                          json_data.get('start_date'),
                          json_data.get('close_date'))
            ques_all = list(zip(json_data.get('survey_question_id'),
                                json_data.get('question_id'),
                                json_data.get('question_order')))
            for ques in ques_all:
                if ques[0] is None:
                    Survey_Question.new(survey_id, ques[1], ques[2])
                else:
                    Survey_Question.update(ques[0], ques[2])
            return url_for('.ad_survey_list')
        return render_template('main/ad_edit_survey.html')
    return jsonify({"Error": "Immutable"}), 403


# delete survey
@main.route('/admin/surveys/delete/<int:survey_id>')
@login_required
@authority_level_required('Admin')
def ad_survey_delete(survey_id):
    if Validator.survey_offline(survey_id):
        Survey.delete(survey_id)
        return url_for('.ad_survey_list')
    return jsonify({"Error": "Immutable"}), 400


# preview survey
@main.route('/admin/surveys/view/<int:survey_id>')
@login_required
@authority_level_required('Admin')
def ad_survey_view(survey_id):
    return render_template('main/ad_view_survey.html')


# result root access forbidden
@main.route('/result')
def result():
    abort(403)


# display survey result
@main.route('/result/<int:survey_id>')
@login_required
def result_survey(survey_id):
    return render_template('main/view_survey_result.html')


# display question result
@main.route('/result/<int:survey_id>/<int:question_id>')
@login_required
def result_question(survey_id, question_id):
    return render_template('main/view_question_result.html')


# staff dashboard
@main.route('/staff')
@login_required
@authority_level_required('Staff')
def staff_dashboard():
    return render_template('main/staff_dashboard.html')


# staff survey list
@main.route('/staff/surveys')
@login_required
@authority_level_required('Staff')
def sf_survey_list():
    return render_template('main/sf_survey_list.html')


# staff edit survey
@main.route('/staff/surveys/edit/<int:survey_id>', methods=['GET', 'POST'])
@login_required
@authority_level_required('Staff')
def sf_survey_edit(survey_id):
    if Validator.survey_offline(survey_id):
        if request.is_json and not Validator.survey_edit(request.json):
            abort(400)
        elif request.is_json:
            json_data = request.json
            Survey.update(survey_id,
                          json_data.get('course_id'),
                          json_data.get('survey_name'),
                          json_data.get('start_date'),
                          json_data.get('close_date'))
            ques_all = list(zip(json_data.get('survey_question_id'),
                                json_data.get('question_id'),
                                json_data.get('question_order')))
            for ques in ques_all:
                if ques[0] is None:
                    if Question.load(ques[1]).qtype == "Opt":
                        Survey_Question.new(survey_id, ques[1], ques[2])
                    else:
                        abort(400)
                else:
                    if Survey_Question.load(ques[0]).qtype == "Opt":
                        Survey_Question.update(ques[0], ques[2])
                    else:
                        abort(400)
            return url_for('.ad_survey_list')
        return render_template('main/ad_edit_survey.html')
    return jsonify({"Error": "Immutable"}), 403


# staff preview survey
@main.route('/staff/surveys/view/<int:survey_id>')
@login_required
@authority_level_required('Staff')
def sf_survey_view(survey_id):
    return render_template('main/sf_view_survey.html')


# student dashboard
@main.route('/student')
@login_required
@authority_level_required('Student')
def student_dashboard():
    return render_template('main/student_dashboard.html')


# redirect to first question of the survey automatically
@main.route('/student/surveys/<int:surv_id>')
def us_survey(surv_id):
    first_ques_id = Survey.load(surv_id).question[0]
    return redirect(url_for('.us_survey_questions',
                            surv_id=surv_id,
                            ques_id=first_ques_id))


# (respondents) do survey at this route
@main.route('/student/surveys/<int:surv_id>/<int:surv_ques_id>', methods=['GET', 'POST'])
@login_required
def us_survey_questions(surv_id, surv_ques_id):
    if request.is_json and not Validator.survey_answer(surv_id, request.json):
        abort(400)
    elif request.is_json:
        json_data = request.json
        for i in range(len(json_data.get('question_id'))):
            Result.update_answer(json_data.get('choice_id')[i],
                                 json_data.get('answer')[i])
        return url_for('.thank_you')
    return render_template('main/st_do_survey.html')


# show thank-you message to respondents
@main.route('/student/surveys/thank-you')
@login_required
def thank_you():
    return render_template('main/st_thank_you.html')


# NOTE test use only, modify before using
@main.route('/test_success')
@login_required
def test_success():
    abort(418)
    return "<h3>Success.</h3>"
