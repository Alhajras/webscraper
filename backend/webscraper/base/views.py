import csv
from concurrent.futures import ThreadPoolExecutor, Future, wait
from io import StringIO

from django.db import transaction
from django.utils import timezone

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .crawling.crawler_utils import CrawlerUtils
from .filters import InspectorFilter
from .indexing.inverted_index import InvertedIndex
from .indexing.qgram_index import QGramIndex, SingletonMeta
from .models import (
    Crawler,
    Template,
    Inspector,
    Runner,
    InspectorValue,
    RunnerStatus,
    Indexer,
    IndexerStatus,
    Action,
)
from .pbs.pbs_utils import PBSTestsUtils
from .serializers import (
    CrawlerSerializer,
    UserSerializer,
    TemplateSerializer,
    InspectorSerializer,
    RunnerSerializer,
    IndexerSerializer,
    ActionPolymorphicSerializer,
    InspectorValueSerializer,
)


class EverythingButDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CrawlerViewSet(EverythingButDestroyViewSet):
    queryset = Crawler.objects.filter(deleted=False)
    serializer_class = CrawlerSerializer


class TemplateViewSet(EverythingButDestroyViewSet):
    queryset = Template.objects.filter(deleted=False)
    serializer_class = TemplateSerializer


class IndexerViewSet(EverythingButDestroyViewSet):
    queryset = Indexer.objects.filter(deleted=False).order_by("-id")
    serializer_class = IndexerSerializer

    @transaction.atomic
    def update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update an index and its inspectors.
        """
        new_inspectors_ids = request.data["inspectors_to_be_indexed"]
        indexer = super().update(request, *args, **kwargs)
        old_inspectors_ids = indexer.data["inspectors_to_be_indexed"]

        Inspector.objects.filter(id__in=new_inspectors_ids).update(
            indexer=indexer.data["id"]
        )

        differences = list(set(old_inspectors_ids) - set(new_inspectors_ids))
        Inspector.objects.filter(id__in=differences).update(
            indexer=None
        )
        return indexer

    @transaction.atomic
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create an index but without running it.
        """
        indexer = super().create(request, *args, **kwargs)
        inspectors_ids = request.data["inspectors_to_be_indexed"]

        Inspector.objects.filter(id__in=inspectors_ids).update(
            indexer=indexer.data["id"]
        )
        return indexer

    @action(detail=False, url_path="available-indexers", methods=["GET"])
    def available_indexers(self, request: Request) -> Response:
        inverted_index = InvertedIndex()
        serialized_indexers = [
            IndexerSerializer(indexer).data
            for indexer in inverted_index.cached_indexers_keys()
        ]
        return Response(status=200, data=serialized_indexers)

    @action(detail=False, url_path="start", methods=["post"])
    def start(self, request: Request) -> Response:
        indexer_id = request.data["id"]
        indexer = Indexer.objects.get(id=indexer_id)

        def thread():
            singleton_cache = SingletonMeta
            cache_key = f"qGramIndex:{indexer.dictionary}"
            hit = singleton_cache.suggestions_cache.get(cache_key, None)
            if hit is None:
                print("Creating dictionary ....")
                q_obj = QGramIndex(indexer.q_gram_q, indexer.q_gram_use_synonym)
                if len(q_obj.names) != 0:
                    return
                Indexer.objects.filter(id=indexer_id).update(
                    status=IndexerStatus.DICTIONARY
                )
                q_obj.build_from_file(indexer.dictionary)
                singleton_cache.suggestions_cache[cache_key] = q_obj
                print("Done creating dictionary!")
            Indexer.objects.filter(id=indexer_id).update(status=IndexerStatus.INDEXING)
            print("Creating an index!")
            inverted_index = InvertedIndex()
            inverted_index.create_index(indexer_id)
            indexer.status = IndexerStatus.COMPLETED
            indexer.completed_at = timezone.now()
            indexer.save()
            print("Done creating an index!")

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures: Future = executor.submit(thread)
            wait([futures])

        return Response(status=200)

    @action(detail=True, url_path="search", methods=["POST"])
    def search(self, request: Request, pk: int) -> Response:
        query = request.data["q"].lower().strip()
        inverted_index = InvertedIndex()
        result = inverted_index.process_query(query.split(" "), pk)[:25]
        for r in result:
            print(r.score)
        # TODO: 25 should be configurable
        docs_ids = [d.document_db_id for d in result]
        headers = {}
        documents = {}
        for doc_id in docs_ids:
            inspector_values = InspectorValue.objects.filter(
                document__id=doc_id
            ).values(
                "value",
                "url",
                "inspector",
                "inspector__name",
                "attribute",
                "document",
                "inspector__type",
                "inspector__clean_up_expression",
                "inspector__variable_name",
            ).order_by('inspector__name')
            variables_names = InspectorValue.objects.filter(
                document__id=doc_id
            ).values_list(
                "inspector__variable_name", flat=True
            ).distinct()
            doc_score = inverted_index.evaluate_formula(pk, variables_names, inspector_values)
            print(variables_names)
            for inspector_value in inspector_values:
                inspector_value["boosted_score"] = doc_score
                document = inspector_value["document"]
                if document not in documents:
                    documents[document] = [inspector_value]
                else:
                    documents[document].append(inspector_value)
                header_name = inspector_value["inspector__name"]
                headers[header_name] = header_name
        # Add boosted results
        # docs = inverted_index.evaluate_formula(pk, documents)
        return Response(data={"headers": headers.keys(), "docs": documents})

    @action(detail=False, url_path="suggest", methods=["GET"])
    def suggest(self, request: Request) -> Response:
        raw_query = request.query_params.get("q").lower().strip()
        indexer_id = request.query_params.get("id").lower().strip()
        singleton_cache = SingletonMeta
        indexer = Indexer.objects.get(id=indexer_id)
        cache_key = f"qGramIndex:{indexer.dictionary}"
        q = singleton_cache.suggestions_cache.get(cache_key, None)
        query = q.normalize(raw_query)

        # Process the keywords.
        delta = int(len(query) / 4)

        postings, _ = q.find_matches(query, delta)

        r = []
        for p in q.rank_matches(postings)[:5]:
            entity_name = q.entities[p[0] - 1][0]
            entity_synonyms = q.names[p[3] - 1]
            entity_desc = q.entities[p[0] - 1][2]
            entity_img = q.entities[p[0] - 1][6].strip()
            if not entity_img:
                entity_img = "noimage.png"
            r.append(entity_name)
        return Response(data={"suggestions": r})


class InspectorViewSet(EverythingButDestroyViewSet):
    queryset = Inspector.objects.filter(deleted=False)
    serializer_class = InspectorSerializer
    filterset_class = InspectorFilter
    filter_backends = [DjangoFilterBackend]
    filterset_fields = "template"


class InspectorValueViewSet(EverythingButDestroyViewSet):
    queryset = InspectorValue.objects.filter(deleted=False)
    serializer_class = InspectorValueSerializer


class RunnerViewSet(EverythingButDestroyViewSet):
    queryset = Runner.objects.filter(deleted=False).order_by("-id")
    serializer_class = RunnerSerializer
    filter_backends = [DjangoFilterBackend]

    @action(detail=False, url_path="submit", methods=["post"])
    def submit(self, request: Request) -> Response:
        runner_serializer = RunnerSerializer(data=request.data)
        # TODO: If data are invalid we should throw an error here
        if not runner_serializer.is_valid():
            pass
        runner_serializer = RunnerSerializer(data=request.data)
        if runner_serializer.is_valid():
            runner_serializer.save()

        # TODO: If data are invalid we should throw an error here
        if not runner_serializer.is_valid():
            pass
        runner = Runner.objects.filter(name=runner_serializer["name"]).last()
        if runner_serializer["machine"] != "localhost":
            # IP address are taken from the docker/.env file
            pbs_head_node = "173.16.38.8"
            pbs_sim_node = "173.16.38.9"
            pbs = PBSTestsUtils(pbs_head_node=pbs_head_node, pbs_sim_node=pbs_sim_node)
            pbs.set_up_pbs()
            pbs.run_job(runner_serializer.data)
        else:
            crawler_utils = CrawlerUtils(runner.id, runner_serializer.data["crawler"])
            crawler_utils.start()
        return Response(status=200)

    @action(detail=True, url_path="stop", methods=["post"])
    def stop(self, request: Request, pk: int) -> Response:
        runner = Runner.objects.get(pk=pk)
        runner.status = str(RunnerStatus.EXIT)
        runner.save()
        return Response(status=200)

    @action(detail=False, url_path="start", methods=["post"])
    def start(self, request: Request) -> Response:
        runner_id = request.data["id"]
        runner_serializer = RunnerSerializer(data=request.data)
        # TODO: If data are invalid we should throw an error here
        if not runner_serializer.is_valid():
            pass

        crawler_utils = CrawlerUtils(runner_id, runner_serializer.data["crawler"])
        crawler_utils.start()
        return Response(status=200)

    @action(detail=True, url_path="download", methods=["post"])
    def download(self, request: Request, pk: int):
        # Create a response object using the Response class
        response = Response(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="somefilename.csv"'},
            status=200,
        )

        # Create a StringIO object to hold the CSV content
        csv_content = StringIO()

        values = InspectorValue.objects.filter(runner=pk).filter(deleted=False)
        # Use csv.writer with the StringIO object
        writer = csv.writer(csv_content)
        writer.writerow(["id", "type", "value", "url", "inspetor name", "document id"])
        for value in values:
            writer.writerow(
                [
                    value.id,
                    value.type,
                    value.value,
                    value.url,
                    value.inspector.name,
                    value.document.id,
                ]
            )

        # Set the response content to the CSV content from the StringIO object
        response.data = csv_content.getvalue()

        # Return the response
        return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ActionViewSet(EverythingButDestroyViewSet):
    queryset = Action.objects.all().filter(deleted=False)
    serializer_class = ActionPolymorphicSerializer
