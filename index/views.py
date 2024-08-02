from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .models import User, Choices, Questions, Answer, Form, Responses
from django.core import serializers
import json
import random
import string
import csv
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.views.decorators.cache import never_cache

def start_test(request):
    if request.method == 'POST':
        experience = request.POST.get('experience')
        try:
            experience = int(experience)
        except ValueError:
            return HttpResponseBadRequest("Invalid experience input")

        if experience <= 2:
            # Test papers for 0-2 experience
            test_papers = [
                '9vN2KorzTimwjKHV7prTvfD3U7F8cm',  # Example code
                'VKZfn8piMJrHxYNfguEdDYx6b5AZp9',  # Example code
            ]
        else:
            # Test papers for more than 2 years experience
            test_papers = [
                'zLsMYFQ7CzoffZ0HHbZeSVBcJkQbtk',  # Example code
                'E2VkqupdMDvFhROc52wwnmV5p1uYnx',  # Example code
            ]

        selected_test = random.choice(test_papers)
        # Redirect to the view_form view with the code
        return redirect('view_form', code=selected_test)

    return HttpResponseBadRequest("Invalid request")


def validate_email(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        is_valid = False

        # Check if the email exists in the database
        if User.objects.filter(email=email).exists():
            is_valid = True
        
        return JsonResponse({'valid': is_valid})

    return JsonResponse({'valid': False}, status=400)

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    forms = Form.objects.filter(creator = request.user)
    return render(request, "index/index.html", {
        "forms": forms
    })

def login_view(request):
    #Check if the user is logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username = username, password = password)
        # if user authentication success
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "index/login.html", {
                "message": "Invalid username and/or password"
            })
    return render(request, "index/login.html")

def register(request):
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        email = request.POST["email"]
        confirmation = request.POST["confirmation"]
        #check if the password is the same as confirmation
        if password != confirmation:
            return render(request, "index/register.html", {
                "message": "Passwords must match."
            })
        #Checks if the username is already in use
        if User.objects.filter(email = email).count() == 1:
            return render(request, "index/register.html", {
                "message": "Email already taken."
            })
        try:
            user = User.objects.create_user(username = username, password = password, email = email)
            user.save()
            return HttpResponseRedirect(reverse('index'))
        except IntegrityError:
            return render(request, "index/register.html", {
                "message": "Username already taken"
            })
    return render(request, "index/register.html")


def logout_view(request):
    #Logout the user
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def create_form(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        data = json.loads(request.body)
        title = data["title"]
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        choices = Choices(choice = "Option 1")
        choices.save()
        question = Questions(question_type = "multiple choice", question= "Untitled Question", required= False)
        question.save()
        question.choices.add(choices)
        question.save()
        form = Form(code = code, title = title, creator=request.user)
        form.save()
        form.questions.add(question)
        form.save()
        return JsonResponse({"message": "Sucess", "code": code})

def edit_form(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    return render(request, "index/form.html", {
        "code": code,
        "form": formInfo
    })

def edit_title(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        if len(data["title"]) > 0:
            formInfo.title = data["title"]
            formInfo.save()
        else:
            formInfo.title = formInfo.title[0]
            formInfo.save()
        return JsonResponse({"message": "Success", "title": formInfo.title})

def edit_description(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.description = data["description"]
        formInfo.save()
        return JsonResponse({"message": "Success", "description": formInfo.description})

def edit_bg_color(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.background_color = data["bgColor"]
        formInfo.save()
        return JsonResponse({"message": "Success", "bgColor": formInfo.background_color})

def edit_text_color(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.text_color = data["textColor"]
        formInfo.save()
        return JsonResponse({"message": "Success", "textColor": formInfo.text_color})

def edit_setting(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        formInfo.collect_email = data["collect_email"]
        formInfo.is_quiz = data["is_quiz"]
        formInfo.authenticated_responder = data["authenticated_responder"]
        formInfo.confirmation_message = data["confirmation_message"]
        formInfo.edit_after_submit = data["edit_after_submit"]
        formInfo.allow_view_score = data["allow_view_score"]
        formInfo.save()
        return JsonResponse({'message': "Success"})

def delete_form(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        #Delete all questions and choices
        for i in formInfo.questions.all():
            for j in i.choices.all():
                j.delete()
            i.delete()
        for i in Responses.objects.filter(response_to = formInfo):
            for j in i.response.all():
                j.delete()
            i.delete()
        formInfo.delete()
        return JsonResponse({'message': "Success"})

def edit_question(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        question_id = data["id"]
        question = Questions.objects.filter(id = question_id)
        if question.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else: question = question[0]
        question.question = data["question"]
        question.question_type = data["question_type"]
        question.required = data["required"]
        if(data.get("score")): question.score = data["score"]
        if(data.get("answer_key")): question.answer_key = data["answer_key"]
        question.save()
        return JsonResponse({'message': "Success"})

def edit_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice_id = data["id"]
        choice = Choices.objects.filter(id = choice_id)
        if choice.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else: choice = choice[0]
        choice.choice = data["choice"]
        if(data.get('is_answer')): choice.is_answer = data["is_answer"]
        choice.save()
        return JsonResponse({'message': "Success"})

def add_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice = Choices(choice="Option")
        choice.save()
        formInfo.questions.get(pk = data["question"]).choices.add(choice)
        formInfo.save()
        return JsonResponse({"message": "Success", "choice": choice.choice, "id": choice.id})

def remove_choice(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        data = json.loads(request.body)
        choice = Choices.objects.filter(pk = data["id"])
        if choice.count() == 0:
            return HttpResponseRedirect(reverse("404"))
        else: choice = choice[0]
        choice.delete()
        return JsonResponse({"message": "Success"})

def get_choice(request, code, question):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "GET":
        question = Questions.objects.filter(id = question)
        if question.count() == 0: return HttpResponseRedirect(reverse('404'))
        else: question = question[0]
        choices = question.choices.all()
        choices = [{"choice":i.choice, "is_answer":i.is_answer, "id": i.id} for i in choices]
        return JsonResponse({"choices": choices, "question": question.question, "question_type": question.question_type, "question_id": question.id})

def add_question(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        choices = Choices(choice = "Option 1")
        choices.save()
        question = Questions(question_type = "multiple choice", question= "Untitled Question", required= False)
        question.save()
        question.choices.add(choices)
        question.save()
        formInfo.questions.add(question)
        formInfo.save()
        return JsonResponse({'question': {'question': "Untitled Question", "question_type": "multiple choice", "required": False, "id": question.id}, 
        "choices": {"choice": "Option 1", "is_answer": False, 'id': choices.id}})

def delete_question(request, code, question):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        question = Questions.objects.filter(id = question)
        if question.count() == 0: return HttpResponseRedirect(reverse("404"))
        else: question = question[0]
        for i in question.choices.all():
            i.delete()
            question.delete()
        return JsonResponse({"message": "Success"})

def score(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args = [code]))
    else:
        return render(request, "index/score.html", {
            "form": formInfo
        })

def edit_score(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args = [code]))
    else:
        if request.method == "POST":
            data = json.loads(request.body)
            question_id = data["question_id"]
            question = formInfo.questions.filter(id = question_id)
            if question.count() == 0:
                return HttpResponseRedirect(reverse("edit_form", args = [code]))
            else: question = question[0]
            score = data["score"]
            if score == "": score = 0
            question.score = score
            question.save()
            return JsonResponse({"message": "Success"})

def answer_key(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args = [code]))
    else:
        if request.method == "POST":
            data = json.loads(request.body)
            question = Questions.objects.filter(id = data["question_id"])
            if question.count() == 0: return HttpResponseRedirect(reverse("edit_form", args = [code]))
            else: question = question[0]
            if question.question_type == "short" or question.question_type == "paragraph":
                question.answer_key = data["answer_key"]
                question.save()
            else:
                for i in question.choices.all():
                    i.is_answer = False
                    i.save()
                if question.question_type == "multiple choice":
                    choice = question.choices.get(pk = data["answer_key"])
                    choice.is_answer = True
                    choice.save()
                else:
                    for i in data["answer_key"]:
                        choice = question.choices.get(id = i)
                        choice.is_answer = True
                        choice.save()
                question.save()
            return JsonResponse({'message': "Success"})

def feedback(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if not formInfo.is_quiz:
        return HttpResponseRedirect(reverse("edit_form", args = [code]))
    else:
        if request.method == "POST":
            data = json.loads(request.body)
            question = formInfo.questions.get(id = data["question_id"])
            question.feedback = data["feedback"]
            question.save()
            return JsonResponse({'message': "Success"})
        
@never_cache
def view_form(request, code):
    try:
        form_info = Form.objects.get(code=code)
        context = {
            'form': form_info,
        }
    except Form.DoesNotExist:
        return HttpResponseRedirect(reverse('404'))
    
    # Check if the authenticated_responder flag is set and user is not authenticated
    if form_info.authenticated_responder and not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    try:
        # Retrieve all responses for this form
        existing_responses = Responses.objects.filter(response_to=form_info)
        
        # Determine if there is a response associated with the current user or IP/email
        existing_response = None
        if request.user.is_authenticated:
            existing_response = existing_responses.filter(responder=request.user).first()
        elif form_info.collect_email and 'email-address' in request.POST:
            existing_response = existing_responses.filter(responder_email=request.POST.get('email-address')).first()
        else:
            existing_response = existing_responses.filter(responder_ip=get_client_ip(request)).first()
        
        # If an existing response is found, render a template indicating that the user has already responded
        if existing_response:
            return render(request, "index/form_already_submitted.html", {
                "form": form_info,
                "code": existing_response.response_code,
            })
    
    except Responses.DoesNotExist:
        pass  # No existing response found, continue rendering the form
    
    except Responses.MultipleObjectsReturned:
        return HttpResponseRedirect(reverse('404'))  # Redirect to 404 page or handle as appropriate
    
    # Render the form template if no existing response is found
    
    return render(request, "index/view_form.html", context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def submit_form(request, code):
    try:
        formInfo = Form.objects.get(code=code)
    except Form.DoesNotExist:
        return HttpResponseRedirect(reverse('404'))

    # Check if the authenticated_responder flag is set and user is not authenticated
    if formInfo.authenticated_responder and not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    try:
        existing_responses = Responses.objects.filter(response_to=formInfo)
        
        # Determine the responder details based on form settings
        if request.user.is_authenticated:
            existing_response = existing_responses.filter(responder=request.user).first()
        elif formInfo.collect_email:
            responder_email = request.POST.get("email-address")
            existing_response = existing_responses.filter(responder_email=responder_email).first()
        else:
            existing_response = existing_responses.filter(responder_ip=get_client_ip(request)).first()
        
        if existing_response:
            return render(request, "index/form_response.html", {
                "form": formInfo,
                "code": existing_response.response_code
            })
    except (MultipleObjectsReturned, Responses.DoesNotExist):
        pass  # Handle the case where multiple responses were found or none were found

    # Handle form submission
    if request.method == "POST":
        # Generate a unique code for the response
        code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))

        # Determine the responder details based on form settings

        if formInfo.authenticated_responder:
            responder_email = request.POST.get("email-address")
            response = Responses(response_code=code, response_to=formInfo, responder_ip=get_client_ip(request), responder=request.user, responder_email=responder_email)
        elif formInfo.collect_email:
            responder_email = request.POST.get("email-address")
            response = Responses(response_code=code, response_to=formInfo, responder_ip=get_client_ip(request), responder_email=responder_email)
        else:
            response = Responses(response_code=code, response_to=formInfo, responder_ip=get_client_ip(request))

        response.save()

        # Process answers for each question in the form
        for question_id, answers in request.POST.lists():
            if question_id == "csrfmiddlewaretoken" or question_id == "email-address":
                continue  # Skip CSRF token and email-address field

            try:
                question = Questions.objects.get(id=question_id)
            except Questions.DoesNotExist:
                continue  # Skip processing if question doesn't exist

            for answer_text in answers:
                answer = Answer(answer=answer_text, answer_to=question)
                answer.save()
                response.response.add(answer)
        
        return render(request, "index/form_response.html", {
            "form": formInfo,
            "code": code
        })
    request.session.flush()
    # Render the form if it's a GET request
    return render(request, "index/your_form_template.html", {
        "form": formInfo
    })

def responses(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]

    responsesSummary = []
    choiceAnswered = {}
    filteredResponsesSummary = {}

    questions = formInfo.questions.all().order_by('id')
    for question in questions:
        answers = Answer.objects.filter(answer_to = question.id)
        if question.question_type == "multiple choice" or question.question_type == "checkbox":
            choiceAnswered[question.question] = choiceAnswered.get(question.question, {})
            for answer in answers:
                choice = answer.answer_to.choices.get(id = answer.answer).choice
                choiceAnswered[question.question][choice] = choiceAnswered.get(question.question, {}).get(choice, 0) + 1
        responsesSummary.append({"question": question, "answers":answers })
    for answr in choiceAnswered:
        filteredResponsesSummary[answr] = {}
        keys = choiceAnswered[answr].values()
        for choice in choiceAnswered[answr]:
            filteredResponsesSummary[answr][choice] = choiceAnswered[answr][choice]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    return render(request, "index/responses.html", {
        "form": formInfo,
        "responses": Responses.objects.filter(response_to = formInfo),
        "responsesSummary": responsesSummary,
        "filteredResponsesSummary": filteredResponsesSummary
    })

def retrieve_checkbox_choices(response, question):
    checkbox_answers = []

    answers = Answer.objects.filter(answer_to=question, response=response)
    for answer in answers:
        selected_choice_ids = answer.answer.split(',')  # Split the string into individual choice IDs
        selected_choices = Choices.objects.filter(pk__in=selected_choice_ids)
        checkbox_answers.append([choice.choice for choice in selected_choices])

    return checkbox_answers



def exportcsv(request,code):
    formInfo = Form.objects.filter(code = code)
    formInfo = formInfo[0]
    responses=Responses.objects.filter(response_to = formInfo)
    questions = formInfo.questions.all()


    http_response = HttpResponse()
    http_response['Content-Disposition'] = f'attachment; filename= {formInfo.title}.csv'
    writer = csv.writer(http_response)
    header = ['Response Code', 'Responder', 'Responder Email','Responder_ip']
    
    for question in questions:
        header.append(question.question)
    
    writer.writerow(header)

    for response in responses:
        response_data = [
        response.response_code,
        response.responder.username if response.responder else 'Anonymous',
        response.responder_email if response.responder_email else '',
        response.responder_ip if response.responder_ip else ''
    ]
        for question in questions:
            answer = Answer.objects.filter(answer_to=question, response=response).first()
            
        
            if  question.question_type not in ['multiple choice','checkbox']:
                response_data.append(answer.answer if answer else '')
            elif question.question_type == "multiple choice":
                response_data.append(answer.answer_to.choices.get(id = answer.answer).choice if answer else '')
            elif question.question_type == "checkbox":
                if answer and question.question_type == 'checkbox':
                    checkbox_choices = retrieve_checkbox_choices(response,answer.answer_to)
                    response_data.append(checkbox_choices)

        print(response_data)
        writer.writerow(response_data)
        
    return http_response

def response(request, code, response_code):
    formInfo = Form.objects.filter(code=code).first()
    if not formInfo:
        return HttpResponseRedirect(reverse('404'))
    
    if not formInfo.allow_view_score:
        if formInfo.creator != request.user:
            return HttpResponseRedirect(reverse("403"))
    
    responseInfo = Responses.objects.filter(response_code=response_code).first()
    if not responseInfo:
        return HttpResponseRedirect(reverse('404'))

    total_score = 0
    score = 0
    
    if formInfo.is_quiz:
        for question in formInfo.questions.all():
            total_score += question.score
        
        for answer in responseInfo.response.all():
            try:
                question = answer.answer_to
                if question.question_type in ["short", "paragraph"]:
                    if answer.answer == question.answer_key:
                        score += question.score
                elif question.question_type == "multiple choice":
                    correct_answer_id = next(
                        (choice.id for choice in question.choices.all() if choice.is_answer), 
                        None
                    )
                    if correct_answer_id and int(correct_answer_id) == int(answer.answer):
                        score += question.score
                elif question.question_type == "checkbox":
                    if answer.answer_to.pk not in _temp:
                        answers = [int(a.answer) for a in responseInfo.response.filter(answer_to__pk=question.pk)]
                        correct_answers = [choice.pk for choice in question.choices.all() if choice.is_answer]
                        if sorted(answers) == sorted(correct_answers):
                            score += question.score
                        _temp.append(question.pk)
            except Questions.DoesNotExist:
                continue

    return render(request, "index/response.html", {
        "form": formInfo,
        "response": responseInfo,
        "score": score,
        "total_score": total_score
    })


def edit_response(request, code, response_code):
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    response = Responses.objects.filter(response_code = response_code, response_to = formInfo)
    if response.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: response = response[0]
    if formInfo.authenticated_responder:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        if response.responder != request.user:
            return HttpResponseRedirect(reverse('403'))
    if request.method == "POST":
        if formInfo.authenticated_responder and not response.responder:
            response.responder = request.user
            response.save()
        if formInfo.collect_email:
            response.responder_email = request.POST["email-address"]
            response.save()
        #Deleting all existing answers
        for i in response.response.all():
            i.delete()
        for i in request.POST:
            #Excluding csrf token and email address
            if i == "csrfmiddlewaretoken" or i == "email-address":
                continue
            question = formInfo.questions.get(id = i)
            for j in request.POST.getlist(i):
                answer = Answer(answer=j, answer_to = question)
                answer.save()
                response.response.add(answer)
                response.save()
        if formInfo.is_quiz:
            return HttpResponseRedirect(reverse("response", args = [formInfo.code, response.response_code]))
        else:
            return render(request, "index/form_response.html", {
                "form": formInfo,
                "code": response.response_code
            })
    return render(request, "index/edit_response.html", {
        "form": formInfo,
        "response": response
    })

def contact_form_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        name = Questions(question_type = "short", question= "Name", required= True)
        name.save()
        email = Questions(question_type="short", question = "Email", required = True)
        email.save()
        address = Questions(question_type="paragraph", question="Address", required = True)
        address.save()
        phone = Questions(question_type="short", question="Phone number", required = False)
        phone.save()
        comments = Questions(question_type = "paragraph", question = "Comments", required = False)
        comments.save()
        form = Form(code = code, title = "Contact information", creator=request.user, background_color="#e2eee0", allow_view_score = False, edit_after_submit = True)
        form.save()
        form.questions.add(name)
        form.questions.add(email)
        form.questions.add(address)
        form.questions.add(phone)
        form.questions.add(comments)
        form.save()
        return JsonResponse({"message": "Sucess", "code": code})

def customer_feedback_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        comment = Choices(choice = "Comments")
        comment.save()
        question = Choices(choice = "Questions")
        question.save()
        bug = Choices(choice = "Bug Reports")
        bug.save()
        feature = Choices(choice = "Feature Request")
        feature.save()
        feedback_type = Questions(question = "Feedback Type", question_type="multiple choice", required=False)
        feedback_type.save()
        feedback_type.choices.add(comment)
        feedback_type.choices.add(bug)
        feedback_type.choices.add(question)
        feedback_type.choices.add(feature)
        feedback_type.save()
        feedback = Questions(question = "Feedback", question_type="paragraph", required=True)
        feedback.save()
        suggestion = Questions(question = "Suggestions for improvement", question_type="paragraph", required=False)
        suggestion.save()
        name = Questions(question = "Name", question_type="short", required=False)
        name.save()
        email = Questions(question= "Email", question_type="short", required=False)
        email.save()
        form = Form(code = code, title = "Customer Feedback", creator=request.user, background_color="#e2eee0", confirmation_message="Thanks so much for giving us feedback!",
        description = "We would love to hear your thoughts or feedback on how we can improve your experience!", allow_view_score = False, edit_after_submit = True)
        form.save()
        form.questions.add(feedback_type)
        form.questions.add(feedback)
        form.questions.add(suggestion)
        form.questions.add(name)
        form.questions.add(email)
        return JsonResponse({"message": "Sucess", "code": code})

def event_registration_template(request):
    # Creator must be authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # Create a blank form API
    if request.method == "POST":
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        name = Questions(question="Name", question_type= "short", required=False)
        name.save()
        email = Questions(question = "email", question_type="short", required=True)
        email.save()
        organization = Questions(question = "Organization", question_type= "short", required=True)
        organization.save()
        day1 = Choices(choice="Day 1")
        day1.save()
        day2 = Choices(choice= "Day 2")
        day2.save()
        day3 = Choices(choice= "Day 3")
        day3.save()
        day = Questions(question="What days will you attend?", question_type="checkbox", required=True)
        day.save()
        day.choices.add(day1)
        day.choices.add(day2)
        day.choices.add(day3)
        day.save()
        dietary_none = Choices(choice="None")
        dietary_none.save()
        dietary_vegetarian = Choices(choice="Vegetarian")
        dietary_vegetarian.save()
        dietary_kosher = Choices(choice="Kosher")
        dietary_kosher.save()
        dietary_gluten = Choices(choice = "Gluten-free")
        dietary_gluten.save()
        dietary = Questions(question = "Dietary restrictions", question_type="multiple choice", required = True)
        dietary.save()
        dietary.choices.add(dietary_none)
        dietary.choices.add(dietary_vegetarian)
        dietary.choices.add(dietary_gluten)
        dietary.choices.add(dietary_kosher)
        dietary.save()
        accept_agreement = Choices(choice = "Yes")
        accept_agreement.save()
        agreement = Questions(question = "I understand that I will have to pay $$ upon arrival", question_type="checkbox", required=True)
        agreement.save()
        agreement.choices.add(accept_agreement)
        agreement.save()
        form = Form(code = code, title = "Event Registration", creator=request.user, background_color="#fdefc3", 
        confirmation_message="We have received your registration.\n\
Insert other information here.\n\
\n\
Save the link below, which can be used to edit your registration up until the registration closing date.",
        description = "Event Timing: January 4th-6th, 2016\n\
Event Address: 123 Your Street Your City, ST 12345\n\
Contact us at (123) 456-7890 or no_reply@example.com", edit_after_submit=True, allow_view_score=False)
        form.save()
        form.questions.add(name)
        form.questions.add(email)
        form.questions.add(organization)
        form.questions.add(day)
        form.questions.add(dietary)
        form.questions.add(agreement)
        form.save()
        return JsonResponse({"message": "Sucess", "code": code})

def delete_responses(request, code):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    formInfo = Form.objects.filter(code = code)
    #Checking if form exists
    if formInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else: formInfo = formInfo[0]
    #Checking if form creator is user
    if formInfo.creator != request.user:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "DELETE":
        responses = Responses.objects.filter(response_to = formInfo)
        for response in responses:
            for i in response.response.all():
                i.delete()
            response.delete()
        return JsonResponse({"message": "Success"})

# Error handler
def FourZeroThree(request):
    return render(request, "error/403.html")

def FourZeroFour(request):
    return render(request, "error/404.html")
