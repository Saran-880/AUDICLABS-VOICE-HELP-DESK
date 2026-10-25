
import json
import time
import statistics
from pathlib import Path
from time import sleep

from scripts.rag import answer_question

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "evaluation_questions.json"
RESULTS_FILE = BASE_DIR / "evaluation_results.json"


def main():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    results = []

    print(f"\nRunning evaluation for {len(questions)} questions...\n")

    for item in questions:
        question = item["question"]
        expected = item["expected_answer"]

        start = time.perf_counter()

        try:
            response = answer_question(question)
            elapsed = time.perf_counter() - start

            answer = response.get("answer", "")
            sources = response.get("sources", [])

            print(f"\nQ{item['id']}: {question}")
            print(f"Answer: {answer}")
            print(f"Sources: {sources}")
            print(f"Response time: {elapsed:.2f}s")

            results.append({
                "id": item["id"],
                "category": item["category"],
                "question": question,
                "expected_answer": expected,
                "actual_answer": answer,
                "sources": sources,
                "response_time_seconds": round(elapsed, 3),
                "manual_correctness": None,
                "manual_citation_accuracy": None
            })

        except Exception as error:
            elapsed = time.perf_counter() - start
            print(f"\nQ{item['id']} failed: {error}")

            results.append({
                "id": item["id"],
                "category": item["category"],
                "question": question,
                "expected_answer": expected,
                "actual_answer": "",
                "sources": [],
                "response_time_seconds": round(elapsed, 3),
                "error": str(error),
                "manual_correctness": None,
                "manual_citation_accuracy": None
            })

        # Pause before processing the next question
        sleep(3)

    successful_times = [
        result["response_time_seconds"]
        for result in results
        if result.get("actual_answer")
        and not result.get("error")
    ]

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total questions: {len(questions)}")
    print(f"Completed responses: {len(successful_times)}")

    if successful_times:
        print(
            "Median response time: "
            f"{statistics.median(successful_times):.2f}s"
        )

    print(f"\nDetailed results saved to: {RESULTS_FILE}")
    print("Review answers and citations manually before calculating accuracy.")


if __name__ == "__main__":
    main()
