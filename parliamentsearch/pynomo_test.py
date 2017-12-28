from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, JSONAttribute, UTCDateTimeAttribute, ListAttribute
)
from datetime import datetime
import boto3

class PQDataModel(Model):
    """
    A DynamoDB User
    """
    class Meta:
        table_name = "parliament_questions"
        read_capacity_units = 1
        write_capacity_units = 1
        region='ap-south-1'

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

def insert(q):
    record = PQDataModel()
    record.question_number = q['question_number']
    record.question_origin = q['question_origin']
    record.question_type = q['question_type']
    record.question_session = q['question_session']
    record.question_ministry = q['question_ministry']
    record.question_member = q['question_member']
    record.question_subject = q['question_subject']
    record.question_type = q['question_type']
    record.question_annex = q['question_annex']
    record.question_url = q['question_url']
    record.question_text = q['question_text']
    record.question_url = q['question_url']
    record.question_date = datetime.strptime(q['question_date'], '%d.%m.%Y')
    # client = boto3.client('dynamodb')
    # q['question_date'] = datetime.strptime(q['question_date'], '%d.%m.%Y')
    # client.put_item(TableName='parliament_questions', Item=q)



    record.save()

def main():

    # if not PQDataModel.exists():
    #     PQDataModel.create_table(wait=True)
    a={'question_origin': 'loksabha',
       'question_number': '1659458',
       'question_type': 'starred',
       'question_session': 16,
       'question_date': '27.12.2017',
       'question_ministry': 'DEFENCE',
       'question_member': ['Hooda Shri Deepender Singh', 'Wanaga Shri Chintaman Navsha'],
       'question_subject': 'One Rank One Pension',
       'question_annex': {'PDF/WORD': 'http://164.100.47.190/loksabhaquestions/annex/13/AS130.pdf', 'PDF/WORD(Hindi)': 'http://164.100.47.190/loksabhaquestions/qhindi/13/AS130.pdf'},
       'question_url': 'http://164.100.47.194/Loksabha/Questions/QResult15.aspx?qref=59456&lsno=16', 'question_text': 'PDF/WORD(Hindi) PDF/WORD GOVERNMENT OF INDIA MINISTRY OF DEFENCE LOK SABHA STARRED QUESTION NO: 130 ANSWERED ON: 27.12.2017 One Rank One Pension CHINTAMAN NAVSHA WANAGA DEEPENDER SINGH HOODA Will the Minister of\n\n\n\n\n\n\n\nDEFENCE be pleased to state:-\n\n\n\n\n\n(a) whether the Government has implemented One Rank One Pension (OROP) scheme and if so, the details including the present status thereof;\n\n\n\n(b) the details of budgetary allocation, revised estimates and actual expenditure incurred on the implementation of OROP during the last three years and the current year, year-wise;\n\n\n\n(c) whether there is disagreement amongst some of the Ex-servicemen with the present model of OROP and if so, the details thereof;\n\n\n\n(d) the details of steps taken to engage them in a dialogue and resolve the issue; and\n\n\n\n(e) the objectives of constitution of the Justice Narsimha Reddy Commission on OROP and its key recommendations along with the status of their implementation?\n\n\n\nANSWER MINISTER OF DEFENCE (SMT. NIRMALA SITHARAMAN)\n\nj{kk ea=h ¼Jherh fueZyk lhrkje.k)\n\n\n\n(a) to (e): A Statement is laid on the Table of the House.\n\n\n\n******\n\n\n\n'}
    insert(a)


if __name__ == '__main__':
    main()