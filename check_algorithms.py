from backend.algorithms import (
    insertion_sort,
    binary_search,
    linear_search,
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
)


def make_records(n):
    return [{"title": f"Task {i:04d}"} for i in range(n)]


def test_correctness():
    records = [
        {"title": "Charlie"},
        {"title": "Alice"},
        {"title": "Bob"},
    ]

    insertion_sort(records, "title")

    assert [r["title"] for r in records] == [
        "Alice",
        "Bob",
        "Charlie",
    ]

    sorted_records = [
        {"title": "Alice"},
        {"title": "Bob"},
        {"title": "Charlie"},
    ]

    assert binary_search(
        sorted_records,
        "Bob",
        "title",
    ) == 1

    assert linear_search(
        sorted_records,
        "Bob",
        "title",
    ) == 1

    assert binary_search(
        sorted_records,
        "Missing",
        "title",
    ) == -1

    assert linear_search(
        sorted_records,
        "Missing",
        "title",
    ) == -1

    print("PASS: correctness checks")


def benchmark(n):
    records = make_records(n)

    # Reverse the records for a worst-case insertion-sort input.
    reverse_records = list(reversed(records))

    insertion_comparisons = insertion_sort_count(
        reverse_records,
        "title",
    )

    sorted_records = make_records(n)

    binary_result = binary_search_count(
        sorted_records,
        f"Task {n // 2:04d}",
        "title",
    )

    linear_result = linear_search_count(
        sorted_records,
        f"Task {n // 2:04d}",
        "title",
    )

    return {
        "n": n,
        "insertion_sort_comparisons": insertion_comparisons,
        "binary_search_comparisons": binary_result[
            "comparison_count"
        ],
        "linear_search_comparisons": linear_result[
            "comparison_count"
        ],
    }


def main():
    print("TaskFlow Algorithm Checks")
    print("=" * 40)

    test_correctness()

    print()
    print("Benchmark comparison counts")
    print("-" * 40)

    for n in [100, 500, 1000]:
        result = benchmark(n)

        print(
            f"n={result['n']}: "
            f"insertion_sort="
            f"{result['insertion_sort_comparisons']}, "
            f"binary_search="
            f"{result['binary_search_comparisons']}, "
            f"linear_search="
            f"{result['linear_search_comparisons']}"
        )

    print()
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()