def insertion_sort(records, key):
    """
    Sort records in place using insertion sort.
    """

    for i in range(1, len(records)):
        current = records[i]
        j = i - 1

        while j >= 0 and records[j][key] > current[key]:
            records[j + 1] = records[j]
            j -= 1

        records[j + 1] = current


def binary_search(sorted_records, target_value, key):
    """
    Search a sorted list using binary search.

    Returns:
        index of matching record
        -1 if no match is found
    """

    low = 0
    high = len(sorted_records) - 1

    while low <= high:
        mid = (low + high) // 2

        current_value = sorted_records[mid][key]

        if current_value == target_value:
            return mid

        if current_value < target_value:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def linear_search(records, target_value, key):
    """
    Search a list sequentially.

    Returns:
        index of first matching record
        -1 if no match is found
    """

    for index, record in enumerate(records):
        if record[key] == target_value:
            return index

    return -1


def insertion_sort_count(records, key):
    """
    Insertion sort with comparison counting.
    """

    comparison_count = 0

    for i in range(1, len(records)):
        current = records[i]
        j = i - 1

        while j >= 0:
            comparison_count += 1

            if records[j][key] <= current[key]:
                break

            records[j + 1] = records[j]
            j -= 1

        records[j + 1] = current

    return comparison_count


def binary_search_count(sorted_records, target_value, key):
    """
    Binary search with comparison counting.
    """

    low = 0
    high = len(sorted_records) - 1
    comparison_count = 0

    while low <= high:
        mid = (low + high) // 2

        comparison_count += 1

        if sorted_records[mid][key] == target_value:
            return {
                "index": mid,
                "comparison_count": comparison_count
            }

        if sorted_records[mid][key] < target_value:
            low = mid + 1
        else:
            high = mid - 1

    return {
        "index": -1,
        "comparison_count": comparison_count
    }


def linear_search_count(records, target_value, key):
    """
    Linear search with comparison counting.
    """

    comparison_count = 0

    for index, record in enumerate(records):
        comparison_count += 1

        if record[key] == target_value:
            return {
                "index": index,
                "comparison_count": comparison_count
            }

    return {
        "index": -1,
        "comparison_count": comparison_count
    }