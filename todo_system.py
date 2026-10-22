"""
Todo-лист: система управления задачами с использованием ООП.

Архитектура
-----------
User:
    Атрибуты: id, name, email, projects.
    Методы: create_project(), add_project(), remove_project(), get_projects().

Project:
    Атрибуты: id, name, description, tasks, owner.
    Методы: add_task(), remove_task(), get_task(), get_all_tasks(),
            get_completed_tasks(), get_pending_tasks().

Task:
    Атрибуты: id, title, description, status, priority, created_at,
              due_date, assignee.
    Методы: mark_completed(), mark_pending(), update_title(),
            update_description(), change_priority(), assign_to(),
            set_due_date().

Связи:
    - User может владеть несколькими Project.
    - Project содержит несколько Task.
    - Task может иметь назначенного User (assignee).
"""

from datetime import date, datetime
from itertools import count
from typing import Optional


# Отдельные счётчики дают уникальные ID внутри каждого типа объектов.
_user_ids = count(1)
_project_ids = count(1)
_task_ids = count(1)


class Task:
    """Одна задача в проекте."""

    VALID_STATUSES = {"не выполнена", "выполнена"}
    VALID_PRIORITIES = {"низкий", "средний", "высокий"}

    def __init__(
        self,
        title: str,
        description: str = "",
        priority: str = "средний",
        due_date: Optional[date] = None,
    ) -> None:
        if not title.strip():
            raise ValueError("Название задачи не может быть пустым.")
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"Приоритет должен быть одним из: {', '.join(sorted(self.VALID_PRIORITIES))}."
            )

        self.id = next(_task_ids)
        self.title = title
        self.description = description
        self.status = "не выполнена"
        self.priority = priority
        self.created_at = datetime.now()
        self.due_date = due_date
        self.assignee: Optional[User] = None

    def mark_completed(self) -> None:
        """Отметить задачу выполненной."""
        self.status = "выполнена"

    def mark_pending(self) -> None:
        """Вернуть задачу в состояние «не выполнена»."""
        self.status = "не выполнена"

    def update_title(self, new_title: str) -> None:
        """Изменить название задачи."""
        if not new_title.strip():
            raise ValueError("Название задачи не может быть пустым.")
        self.title = new_title

    def update_description(self, new_description: str) -> None:
        """Изменить описание задачи."""
        self.description = new_description

    def change_priority(self, new_priority: str) -> None:
        """Изменить приоритет задачи."""
        if new_priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"Приоритет должен быть одним из: {', '.join(sorted(self.VALID_PRIORITIES))}."
            )
        self.priority = new_priority

    def assign_to(self, user: Optional["User"]) -> None:
        """Назначить исполнителя или снять назначение, передав None."""
        self.assignee = user

    def set_due_date(self, due_date: Optional[date]) -> None:
        """Установить срок выполнения; None удаляет срок."""
        self.due_date = due_date

    def __str__(self) -> str:
        assignee_name = self.assignee.name if self.assignee else "не назначен"
        due = self.due_date.isoformat() if self.due_date else "не указан"
        return (
            f"Task #{self.id}: {self.title} | Статус: {self.status} | "
            f"Приоритет: {self.priority} | Исполнитель: {assignee_name} | "
            f"Срок: {due}"
        )


class Project:
    """Проект, который объединяет связанные задачи."""

    def __init__(
        self,
        name: str,
        description: str = "",
        owner: Optional["User"] = None,
    ) -> None:
        if not name.strip():
            raise ValueError("Название проекта не может быть пустым.")

        self.id = next(_project_ids)
        self.name = name
        self.description = description
        self.tasks: list[Task] = []
        self.owner = owner

    def add_task(self, task: Task) -> None:
        """Добавить задачу в проект, не допуская дубликатов по ID."""
        if not isinstance(task, Task):
            raise TypeError("В проект можно добавлять только объекты Task.")
        if any(existing.id == task.id for existing in self.tasks):
            raise ValueError("Эта задача уже есть в проекте.")
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> bool:
        """Удалить задачу по ID. Вернуть True, если задача найдена."""
        for task in self.tasks:
            if task.id == task_id:
                self.tasks.remove(task)
                return True
        return False

    def get_task(self, task_id: int) -> Optional[Task]:
        """Найти задачу по ID; если её нет, вернуть None."""
        return next((task for task in self.tasks if task.id == task_id), None)

    def get_all_tasks(self) -> list[Task]:
        """Вернуть копию списка всех задач проекта."""
        return self.tasks.copy()

    def get_completed_tasks(self) -> list[Task]:
        """Вернуть выполненные задачи."""
        return [task for task in self.tasks if task.status == "выполнена"]

    def get_pending_tasks(self) -> list[Task]:
        """Вернуть задачи, которые ещё не выполнены."""
        return [task for task in self.tasks if task.status == "не выполнена"]

    def __str__(self) -> str:
        owner_name = self.owner.name if self.owner else "не указан"
        return (
            f"Project #{self.id}: {self.name} | Владелец: {owner_name} | "
            f"Всего задач: {len(self.tasks)}"
        )


class User:
    """Пользователь, который владеет проектами и может быть исполнителем задач."""

    def __init__(self, name: str, email: str) -> None:
        if not name.strip():
            raise ValueError("Имя пользователя не может быть пустым.")
        if not email.strip() or "@" not in email:
            raise ValueError("Укажите корректный адрес электронной почты.")

        self.id = next(_user_ids)
        self.name = name
        self.email = email
        self.projects: list[Project] = []

    def create_project(self, name: str, description: str = "") -> Project:
        """Создать проект, назначить владельцем текущего пользователя и добавить его."""
        project = Project(name=name, description=description, owner=self)
        self.add_project(project)
        return project

    def add_project(self, project: Project) -> None:
        """Добавить существующий проект в список пользователя."""
        if not isinstance(project, Project):
            raise TypeError("Можно добавлять только объекты Project.")
        if all(existing.id != project.id for existing in self.projects):
            self.projects.append(project)
        if project.owner is None:
            project.owner = self

    def remove_project(self, project_id: int) -> bool:
        """Убрать проект из списка пользователя. Вернуть True, если он найден."""
        for project in self.projects:
            if project.id == project_id:
                self.projects.remove(project)
                return True
        return False

    def get_projects(self) -> list[Project]:
        """Вернуть копию списка проектов пользователя."""
        return self.projects.copy()

    def __str__(self) -> str:
        return f"User #{self.id}: {self.name} ({self.email})"


if __name__ == "__main__":
    # 1. Создаём пользователей.
    anna = User("Анна", "anna@example.com")
    boris = User("Борис", "boris@example.com")

    print("=== Пользователи ===")
    print(anna)
    print(boris)

    # 2. Анна создаёт проект.
    project = anna.create_project(
        "Обучение Python",
        "Учебные задачи по программированию и ООП.",
    )

    # 3. Создаём задачи и добавляем их в проект.
    task1 = Task(
        "Пройти урок по ООП",
        "Разобраться с классами и объектами.",
        priority="высокий",
        due_date=date(2026, 10, 25),
    )
    task2 = Task(
        "Написать код",
        "Реализовать классы Task, Project и User.",
        priority="средний",
    )
    task3 = Task(
        "Загрузить домашнее задание",
        "Сохранить проект и отправить ссылку на GitHub.",
        priority="низкий",
    )

    project.add_task(task1)
    project.add_task(task2)
    project.add_task(task3)

    # 4. Назначаем Бориса исполнителем одной задачи.
    task2.assign_to(boris)

    # 5. Меняем состояние и приоритет задачи.
    task1.mark_completed()
    task3.change_priority("высокий")
    task3.set_due_date(date(2026, 10, 28))

    # 6. Показываем проект и все его задачи.
    print("\n=== Проект ===")
    print(project)
    for task in project.get_all_tasks():
        print(task)

    # 7. Показываем выполненные и ожидающие задачи.
    print("\n=== Выполненные задачи ===")
    for task in project.get_completed_tasks():
        print(task.title)

    print("\n=== Задачи, которые ещё предстоит выполнить ===")
    for task in project.get_pending_tasks():
        print(task.title)

    # 8. Находим задачу по ID, обновляем описание и демонстрируем результат.
    found_task = project.get_task(task2.id)
    if found_task is not None:
        found_task.update_description("Код написан; осталось проверить его.")
        print("\n=== Найденная и обновлённая задача ===")
        print(found_task)

    # 9. Демонстрируем удаление задачи и проекта.
    removed = project.remove_task(task3.id)
    print(f"\nЗадача #{task3.id} удалена из проекта: {removed}")

    print("Проекты Анны:")
    for user_project in anna.get_projects():
        print(user_project)

    # При необходимости проект можно убрать из списка пользователя:
    # anna.remove_project(project.id)
