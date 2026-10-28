from app.services.source_citation import (
    build_source_citations
)


knowledge = [
    {
        "source_id": "icar_groundnut",
        "title": "Groundnut",
        "organization": (
            "Indian Council of Agricultural Research"
        ),
        "url": "https://icar.gov.in/",
        "source": (
            "groundnut/groundnut_icar.md"
        ),
        "crop": "groundnut",
        "topic": "soil"
    },

    {
        "source_id": "icar_groundnut",
        "title": "Groundnut",
        "organization": (
            "Indian Council of Agricultural Research"
        ),
        "url": "https://icar.gov.in/",
        "source": (
            "groundnut/groundnut_icar.md"
        ),
        "crop": "groundnut",
        "topic": "cultivation"
    },

    {
        "source_id": "icar_kharif_2025",
        "title": (
            "ICAR Kharif Agro-Advisories "
            "for Farmers 2025"
        ),
        "organization": (
            "Indian Council of Agricultural Research"
        ),
        "url": "https://icar.gov.in/",
        "source": (
            "chilli/chilli_icar.md"
        ),
        "crop": "chilli",
        "topic": "season"
    }
]


sources = build_source_citations(
    knowledge
)


print("Sources:")

for source in sources:

    print(
        f"{source['source_id']} -> {source['title']}"
    )
