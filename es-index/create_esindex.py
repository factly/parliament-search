from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, JSONAttribute, UTCDateTimeAttribute, ListAttribute
)

import os

from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
region = 'ap-south-1'
service = 'es'

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)

host = 'search-parliament-search-etibzlgblv7yyvxgtvrzs2hhba.ap-south-1.es.amazonaws.com'
# For example, my-test-domain.us-east-1.es.amazonaws.com

es = Elasticsearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)


class PQDataModel(Model):
    """
    A DynamoDB User
    """
    class Meta:
        table_name = "parliament_questions"
        region='ap-south-1'
        read_capacity_units = 60
        write_capacity_units = 60

    question_number = UnicodeAttribute(hash_key=True)
    question_origin = UnicodeAttribute(null=True)
    question_type = UnicodeAttribute(null=True)
    question_session = NumberAttribute(null=True)
    question_member = ListAttribute(null=True)
    question_date = UTCDateTimeAttribute(null=True)
    question_subject = UnicodeAttribute(null=True)
    question_ministry = UnicodeAttribute(null=True)
    question_url = UnicodeAttribute(null=True)
    question_text = UnicodeAttribute(null=True)
    question_annex = JSONAttribute(null=True)




def main():
    #for q in PQDataModel.query("", question_number__begins_with="16"):
    #     print(q.question_session, q.question_url)
    #for q in PQDataModel.scan():
    #for q in PQDataModel.question_number.startswith('16'):
    for q in PQDataModel.scan(PQDataModel.question_origin.startswith('rajyasabha')):
    #for q in PQDataModel.scan(PQDataModel.question_number.startswith('16')):
        es.index(index="pquestions", doc_type="pquestion", id=q.question_number, body=q.attribute_values)
        print(es.get(index="pquestions", doc_type="pquestion", id=q.question_number))

if __name__ == '__main__':
    main()
