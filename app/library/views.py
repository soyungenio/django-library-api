import csv

from django.http import HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.views import status

from .models import Readers, Books, Readerbooks
from .serializers import ReaderSerializer, BookSerializer


class ListReadersView(generics.RetrieveAPIView):
    """
    GET readers/:id/
    """
    queryset = Readers.objects.all()
    serializer_class = ReaderSerializer

    def get(self, request, *args, **kwargs):
        try:
            reader = self.queryset.get(pk=kwargs["id"])
            return Response(self.serializer_class(reader).data)
        except Readers.DoesNotExist:
            return Response(
                data={
                    "message": "Reader with id: {} does not exist".format(kwargs["id"])
                },
                status=status.HTTP_404_NOT_FOUND
            )


class CSVDataview(APIView):
    """
    GET data/csv
    """
    def get(self, request, format=None):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="library.csv"'

        # table readers
        reader_header = ('id', 'first_name', 'last_name')
        reader_serializer = ReaderSerializer(
            Readers.objects.values(*reader_header),
            many=True
        )
        reader_writer = csv.DictWriter(response, fieldnames=reader_header)
        reader_writer.writeheader()
        for row in reader_serializer.data:
            reader_writer.writerow(row)

        # table delimiter
        csv.DictWriter(response, fieldnames=["^^^^^^^^^^^^^^^^"]).writeheader()

        # table books
        book_serializer = BookSerializer(
            Books.objects.all(),
            many=True
        )
        book_writer = csv.DictWriter(response, fieldnames=BookSerializer.Meta.fields)
        book_writer.writeheader()
        for row in book_serializer.data:
            book_writer.writerow(row)

        # table delimiter
        csv.DictWriter(response, fieldnames=["^^^^^^^^^^^^^^^^"]).writeheader()

        # table readerbooks
        rb = Readerbooks.objects.raw('SELECT id, book_id, reader_id FROM library_readerbooks')
        book_writer = csv.DictWriter(response, fieldnames=['id', 'book_id', 'reader_id'])
        book_writer.writeheader()
        for row in rb:
            book_writer.writerow({"id": row.id, "book_id": row.book_id, "reader_id": row.reader_id})

        return response
