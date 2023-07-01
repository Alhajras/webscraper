import os
from ..models import Runner, Inspector, InspectorValue, Document


def migrate():
    """
    This is a helper function to migrate the file from the course
    https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS2223
    :return:
    """
    with open(os.path.join("/backend/webscraper/base/indexing", "movies.tsv")) as file:
        runner = Runner.objects.all().latest("pk")
        title_inspector = Inspector.objects.get(name="Movie Title")
        movie_description = Inspector.objects.get(name="Movie Description")
        movie_votes = Inspector.objects.get(name="Movie Votes")
        movie_rating = Inspector.objects.get(name="Movie Rating")
        movie_links = Inspector.objects.get(name="Movie Cross Links")
        counter_id = 1
        for line in file:
            counter_id += 1
            Document.objects.create()
            document = Document.objects.get(id=counter_id)
            title, description, votes, rating, links = line.split("\t", 5)
            InspectorValue.objects.create(
                url="localhost/movies_migrations.py",
                document=document,
                attribute="",
                value=title,
                inspector=title_inspector,
                runner=runner,
            )
            InspectorValue.objects.create(
                url="localhost/movies_migrations.py",
                document=document,
                attribute="",
                value=description,
                inspector=movie_description,
                runner=runner,
            )
            InspectorValue.objects.create(
                url="localhost/movies_migrations.py",
                document=document,
                attribute="",
                value=votes,
                inspector=movie_votes,
                runner=runner,
            )
            InspectorValue.objects.create(
                url="localhost/movies_migrations.py",
                document=document,
                attribute="",
                value=rating,
                inspector=movie_rating,
                runner=runner,
            )
            InspectorValue.objects.create(
                url="localhost/movies_migrations.py",
                document=document,
                attribute="",
                value=links,
                inspector=movie_links,
                runner=runner,
            )
