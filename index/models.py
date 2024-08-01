from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser, models.Model):
    email = models.EmailField(unique = True)

class Choices(models.Model):
    choice = models.CharField(max_length=5000)
    is_answer = models.BooleanField(default=False)

class Questions(models.Model):
    question = models.CharField(max_length= 10000)
    question_type = models.CharField(max_length=20)
    required = models.BooleanField(default= False)
    answer_key = models.CharField(max_length = 5000, blank = True)
    score = models.IntegerField(blank = True, default=0)
    feedback = models.CharField(max_length = 5000, null = True)
    choices = models.ManyToManyField(Choices, related_name = "choices")

class Answer(models.Model):
    answer = models.CharField(max_length=5000)
    answer_to = models.ForeignKey(Questions, on_delete = models.CASCADE ,related_name = "answer_to")

class Form(models.Model):
    code = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=10000, blank = True)
    creator = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "creator")
    background_color = models.CharField(max_length=20, default = "#d9efed")
    text_color = models.CharField(max_length=20, default="#272124")
    collect_email = models.BooleanField(default=False)
    authenticated_responder = models.BooleanField(default = False)
    edit_after_submit = models.BooleanField(default=False)
    confirmation_message = models.CharField(max_length = 10000, default = "Your response has been recorded.")
    is_quiz = models.BooleanField(default=False)
    allow_view_score = models.BooleanField(default= True)
    createdAt = models.DateTimeField(auto_now_add = True)
    updatedAt = models.DateTimeField(auto_now = True)
    questions = models.ManyToManyField(Questions, related_name = "questions")
    # time = models.IntegerField(default=0)

class Responses(models.Model):
    response_code = models.CharField(max_length=20)
    response_to = models.ForeignKey(Form, on_delete = models.CASCADE, related_name = "response_to")
    responder_ip = models.CharField(max_length=30)
    responder = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "responder", blank = True, null = True)
    responder_email = models.EmailField(blank = True)
    response = models.ManyToManyField(Answer, related_name = "response")
    
    def __str__(self):
        return f"Response {self.response_code} to {self.response_to}"

    @classmethod
    def get_existing_response(cls, form, request):
        """
        Retrieve an existing response based on the form and request details.
        """
        if request.user.is_authenticated:
            try:
                return cls.objects.get(response_to=form, responder=request.user)
            except cls.DoesNotExist:
                return None
        elif form.collect_email:
            try:
                return cls.objects.get(response_to=form, responder_email=request.POST.get("email-address"))
            except cls.DoesNotExist:
                return None
        else:
            try:
                return cls.objects.get(response_to=form, responder_ip=get_client_ip(request))
            except cls.DoesNotExist:
                return None