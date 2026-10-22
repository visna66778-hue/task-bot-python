import csv
import io


def tasks_to_csv(tasks: list[dict]) -> bytes:
    """Преобразует список задач в CSV-файл."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "ID",
        "Задача",
        "Автор",
        "Дата создания",
        "Статус",
        "Категория",
    ])

    for task in tasks:
        writer.writerow([
            task["id"],
            task["text"],
            task["user"],
            task["created_at"],
            task["status"],
            task["category"],
        ])

    return ("\ufeff" + output.getvalue()).encode("utf-8")