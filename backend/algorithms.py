def binary_search_tasks(tasks, target):
    """
    Search for a task by title using binary search.
    Tasks must already be sorted by title.
    """

    left = 0
    right = len(tasks) - 1
    target = target.lower()

    while left <= right:
        mid = (left + right) // 2

        current_title = tasks[mid].title.lower()

        if current_title == target:
            return tasks[mid]

        if current_title < target:
            left = mid + 1
        else:
            right = mid - 1

    return None

def merge_sort_tasks(tasks):
    """
    Sort tasks alphabetically by title using merge sort.
    """

    if len(tasks) <= 1:
        return tasks

    mid = len(tasks) // 2

    left = merge_sort_tasks(tasks[:mid])
    right = merge_sort_tasks(tasks[mid:])

    return merge_tasks(left, right)


def merge_tasks(left, right):
    result = []

    i = 0
    j = 0

    while i < len(left) and j < len(right):

        if left[i].title.lower() <= right[j].title.lower():
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])

    return result