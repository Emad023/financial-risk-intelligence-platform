def is_comparison_question(
    question
):

    keywords = [
        "compare",
        "comparison",
        "vs",
        "versus",
        "difference between"
    ]

    question = question.lower()

    return any(
        keyword in question
        for keyword in keywords
    )


def extract_companies(
    question
):

    companies = []

    company_list = [
        "apple",
        "microsoft",
        "nvidia",
        "tesla"
    ]

    question = question.lower()

    for company in company_list:

        if company in question:

            companies.append(
                company
            )

    return companies