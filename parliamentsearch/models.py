from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, JSONAttribute, UTCDateTimeAttribute, ListAttribute
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
    question_query = UnicodeAttribute(null=True)
    question_answer = UnicodeAttribute(null=True)
    question_annex = JSONAttribute(null=True)

