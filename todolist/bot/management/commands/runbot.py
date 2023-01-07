import datetime

from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from goals.models import Goal, GoalCategory


class TgState:
    DEFAULT = 0
    CATEGORY_CHOOSE = 1
    GOAL_CREATE = 2

    def __init__(self, state, category_id=None):
        self.state = state
        self.category_id = category_id

    def set_state(self, state):
        self.state = state

    def set_category_id(self, category_id):
        self.category_id = category_id


STATE = TgState(state=TgState.DEFAULT)


class Command(BaseCommand):
    help = 'Runs telegram bot'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient('5638033773:AAGTEgo0_mQaUTTrgCMj53d5t4cFzvULI24')
        self.offset = 0

    def choose_category(self, msg: Message, tg_user: TgUser):
        goal_categories = GoalCategory.objects.filter(
            board__participants__user=tg_user.user,
            is_deleted=False,
        )
        goals_categories_str = '\n'.join(['- ' + goal.title for goal in goal_categories])

        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Выберите категорию: \n {goals_categories_str}'
        )
        STATE.set_state(TgState.CATEGORY_CHOOSE)


    def check_category(self, msg: Message):
        category = GoalCategory.objects.filter(title=msg.text).first()
        if category:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Введите заголовок цели'
            )
            STATE.set_state(TgState.GOAL_CREATE)
            STATE.set_category_id(category.id)
        else:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Категория с названием {msg.text} не существует'
            )

    def create_goal(self, msg: Message, tg_user: TgUser):
        category = GoalCategory.objects.get(pk=STATE.category_id)
        goal = Goal.objects.create(
            title=msg.text,
            user=tg_user.user,
            category=category,
            due_date=datetime.now().date(),
        )

        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Цель "{goal.title}" создана!'
        )
        STATE.set_state(TgState.DEFAULT)

    def get_goals(self, msg: Message, tg_user: TgUser):
        goals = Goal.objects.filter(
            category__board__participants__user=tg_user.user,
        ).exclude(status=Goal.Status.archived)
        goals_str = '\n'.join(['- ' + goal.title for goal in goals])

        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Вот "список" ваших целей:\n {goals_str}'
        )

    def cancel_operation(self, msg: Message):
        STATE.set_state(TgState.DEFAULT)
        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text='Операция отменена'
        )

    def handle_message(self, msg: Message):
        tg_user, created = TgUser.objects.get_or_create(
            tg_user_id=msg.msg_from.id,
            tg_chat_id=msg.chat.id,
        )
        if created:
            tg_user.generate_verification_code()
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f"Подвердите, пожалуйста, свой аккаунт. "
                     f"Для подтверждения необходимо ввести код: {tg_user.verification_code} на сайте"
            )
        if msg.text == '/goals':
            self.get_goals(msg, tg_user)
        elif msg.text == '/create':
            self.choose_category(msg, tg_user)
        elif msg.text == '/cancel':
            self.cancel_operation(msg)
        elif STATE.state == TgState.CATEGORY_CHOOSE:
            self.check_category(msg)
        elif STATE.state == TgState.GOAL_CREATE:
            self.create_goal(msg)

        else:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Неизвестная команда: {msg.text}'
            )

    def handle(self, *args, **options):
        while True:
            res = self.tg_client.get_updates(offset=self.offset)
            for item in res.result:
                self.offset = item.update_id + 1
                if hasattr(item, 'message'):
                    self.handle_message(item.message)
