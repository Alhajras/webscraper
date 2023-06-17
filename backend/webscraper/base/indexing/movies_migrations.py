import os
from ..models import Runner, Inspector, InspectorValue


def migrate():
    with open(os.path.join("/home/oc/Documents/git/webscraper/backend/webscraper/base/indexing", "movies.tsv")) as file:
        runner = Runner.objects.all().latest("pk")
        title_inspector = Inspector.objects.get(name="Movie Title")
        movie_description = Inspector.objects.get(name="Movie Description")
        movie_votes = Inspector.objects.get(name="Movie Votes")
        movie_rating = Inspector.objects.get(name="Movie Rating")
        movie_links = Inspector.objects.get(name="Movie Cross Links")
        for line in file:
            title, description, votes, rating, links = line.split("\t", 5)
            InspectorValue.objects.update_or_create(url="localhost/movies_migrations.py",
                                                    attribute='',
                                                    value=title,
                                                    inspector=title_inspector,
                                                    runner=runner)
            InspectorValue.objects.update_or_create(url="localhost/movies_migrations.py",
                                                    attribute='',
                                                    value=description,
                                                    inspector=movie_description,
                                                    runner=runner)
            InspectorValue.objects.update_or_create(url="localhost/movies_migrations.py",
                                                    attribute='',
                                                    value=votes,
                                                    inspector=movie_votes,
                                                    runner=runner)
            InspectorValue.objects.update_or_create(url="localhost/movies_migrations.py",
                                                    attribute='',
                                                    value=rating,
                                                    inspector=movie_rating,
                                                    runner=runner)
            InspectorValue.objects.update_or_create(url="localhost/movies_migrations.py",
                                                    attribute='',
                                                    value=links,
                                                    inspector=movie_links,
                                                    runner=runner)
