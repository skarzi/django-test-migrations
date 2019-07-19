import datetime

import factory

from factory import fuzzy

from . import enums


class QuestionFactory(factory.DjangoModelFactory):
    question_text = fuzzy.FuzzyText(length=20, suffix='?')
    pub_date = fuzzy.FuzzyDateTime(
        datetime.datetime(2019, 3, 4, 11, 19, tzinfo=datetime.timezone.utc),
    )
    difficulty_level = fuzzy.FuzzyChoice(
        choices=[member.value for member in enums.DifficultyLevel],
    )

    class Meta:
        model = 'polls.Question'

    @factory.post_generation
    def choices(self, create, extracted, **kwargs):
        if create and extracted:
            self.choices.set(*extracted)


class Choice(factory.DjangoModelFactory):
    question = factory.SubFactory('apps.polls.factories.QuestionFactory')
    choice_text = factory.Faker('sentence')
    votes = fuzzy.FuzzyInteger(low=0, high=100)
