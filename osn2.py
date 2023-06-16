from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.clock import Clock


class TaskManager(App):
    def __init__(self, **kwargs):
        super(TaskManager, self).__init__(**kwargs)
        self.tasks = {}

    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10)

        # Заголовок
        title_label = Button(text="Task Manager", font_size=24, background_normal='', background_color=(0, 0, 0, 0))
        layout.add_widget(title_label)

        # Ввод задачи
        task_input = TextInput(multiline=False, size_hint=(1, None), height=50)
        layout.add_widget(task_input)

        # Кнопка добавления задачи
        add_button = Button(text="Добавить задачу", size_hint=(1, 0.2))
        add_button.bind(on_press=lambda x: self.add_task(task_input.text, task_input))
        layout.add_widget(add_button)

        # Список задач
        self.task_list = BoxLayout(orientation='vertical', spacing=5)
        layout.add_widget(self.task_list)

        return layout

    def add_task(self, task, task_input):
        if task:
            self.tasks[task] = {'timer': None, 'time': 0}
            self.update_task_list()
            task_input.text = ""
            self.show_popup("Задача успешно добавлена")
        else:
            self.show_popup("Введите задачу")

    def update_task_list(self):
        # Очищаем список задач перед обновлением
        self.task_list.clear_widgets()

        # Добавляем каждую задачу в виде BoxLayout с меткой и кнопкой "Взять в работу"
        for task, task_data in self.tasks.items():
            task_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

            # Фоновый цвет задачи
            task_background = Color(0.7, 0.7, 0.7, 1)
            task_layout.canvas.before.add(task_background)
            task_layout.canvas.before.add(Rectangle(size=task_layout.size, pos=task_layout.pos))

            # Метка с текстом задачи (кнопка)
            task_label = Button(text=task, background_normal='', background_color=(0.7, 0.7, 0.7, 1))
            task_layout.add_widget(task_label)

            # Кнопка "Взять в работу" или "Продолжить"
            work_button = Button(text="Взять в работу", background_color=(0, 1, 0, 1))
            work_button.bind(on_press=lambda x, t=task_label: self.start_or_resume_task(t.text, task_layout, work_button))
            task_layout.add_widget(work_button)

            self.task_list.add_widget(task_layout)

    def start_or_resume_task(self, task, task_layout, work_button):
        if task in self.tasks and self.tasks[task]['timer'] is None:
            timer_label = Label(text="00:00:00")
            task_layout.add_widget(timer_label)
            self.tasks[task]['timer'] = Clock.schedule_interval(
                lambda dt, t=task, l=timer_label: self.update_timer(dt, t, l), 1)
            work_button.text = "Пауза"
            self.show_popup("Таймер для задачи '{}' запущен".format(task))
        elif task in self.tasks and self.tasks[task]['timer'] is not None:
            Clock.schedule_interval(
                lambda dt, t=task, l=task_layout, w=work_button: self.update_timer(dt, t, l), 1)
            work_button.text = "Пауза"
            self.show_popup("Таймер для задачи '{}' возобновлен".format(task))

    def update_timer(self, task, timer_label):
        if self.tasks[task]['timer'] is not None:
            self.tasks[task]['time'] += 1
            hours = self.tasks[task]['time'] // 3600
            minutes = (self.tasks[task]['time'] // 60) % 60
            seconds = self.tasks[task]['time'] % 60
            timer_label.text = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    def show_popup(self, message):
        content = Button(text=message, size_hint=(0.5, 0.5))
        popup = Popup(title='Сообщение', content=content, auto_dismiss=True)
        content.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    TaskManager().run()