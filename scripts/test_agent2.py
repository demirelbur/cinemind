from cinemind.schemas.api import RecommendRequest
from cinemind.services.recommendation_service import run_recommendation_pipeline


def main() -> None:
    request = RecommendRequest(
        query="Can you recommend some good sci-fi movies from the 80s that are suitable for teens? I want at least 5 options."
    )

    response = run_recommendation_pipeline(request)

    print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
