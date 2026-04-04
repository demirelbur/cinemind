from cinemind.agents.intent_retrieval_agent import (
    resolve_final_result_count,
    run_intent_retrieval_agent,
)
from cinemind.schemas.api import RecommendRequest


def main() -> None:
    request = RecommendRequest(
        query="Can you recommend some good sci-fi movies from the 80s that are suitable for teens? I want at least 5 options."
    )

    result = run_intent_retrieval_agent(request)
    final_count = resolve_final_result_count(
        request=request,
        desired_results_from_query=result.preferences.desired_results,
    )

    print("Parsed preferences:")
    print(result.preferences.model_dump_json(indent=2))

    print(f"\nResolved final result count: {final_count}")

    print(f"\nRetrieved candidates: {len(result.candidates)}")
    for index, movie in enumerate(result.candidates[:10], start=1):
        print(
            f"{index}. {movie.title} | {movie.genre} | {movie.year} | "
            f"{movie.rating} | {movie.recommended_for}"
        )


if __name__ == "__main__":
    main()
