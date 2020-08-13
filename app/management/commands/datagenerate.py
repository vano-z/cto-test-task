import random

from django.core.management.base import BaseCommand, CommandError
from app.models import Question, Answer, Tag, User
from faker import Faker

faker = Faker()

tags_list = []
users_list = []
questions_list = []


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--tags', type=int)
        parser.add_argument('--users', type=int)
        parser.add_argument('--questions', type=int)
        parser.add_argument('--answers', type=int)

    def tags(self, cnt):
        for i in range(cnt):
            t = Tag(tag_name=faker.word())
            tags_list.append(t)
        Tag.objects.bulk_create(tags_list)

    def users(self, cnt):
        for i in range(cnt):
            u = User(password=faker.password(length=20, special_chars=False, upper_case=True),
                     last_login=faker.iso8601(),
                     username=faker.user_name(),
                     first_name=faker.first_name(),
                     last_name=faker.last_name(),
                     email=faker.email(),
                     is_staff=False,
                     is_active=random.choice([True, False]),
                     date_joined=faker.iso8601(),
                     )
            users_list.append(u)
        User.objects.bulk_create(users_list)

    def questions(self, cnt):
        for i in range(cnt):
            q = Question(title=(faker.text(max_nb_chars=50) + '?'),
                         definition=faker.text(),
                         # author=User.objects.get(id=faker.random_int(min=1, max=User.objects.all().count())),
                         author=random.choice(users_list),
                         pub_date=faker.iso8601())
            q.save()

            count_tags = faker.random_int(min=1, max=5)
            for j in range(count_tags):
                q.tags.add(Tag.objects.get(id=faker.random_int(min=1, max=Tag.objects.all().count())))
            questions_list.append(q)
            q.save()

    def answers(self, cnt):
        for i in range(cnt):
            # q = Question.objects.get(id=faker.random_int(min=1, max=Question.objects.all().count()))
            # q.save()
            # a = User.objects.get(id=faker.random_int(min=1, max=User.objects.all().count()))
            # a.save()
            Answer.objects.create(question=random.choice(questions_list),
                                  author=random.choice(users_list),
                                  text=faker.text(200),
                                  pub_date=faker.iso8601(),
                                  status_correct=random.choice([True, False]))

    def handle(self, *args, **options):
        if options['tags']:
            self.tags(options.get('tags', 0))
        if options['users']:
            self.users(options.get('users', 0))
        if options['questions']:
            self.questions(options.get('questions', 0))
        if options['answers']:
            self.answers(options.get('answers', 0))
