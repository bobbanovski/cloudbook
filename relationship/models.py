from mongoengine import CASCADE #if one record deleted, cascades
from application import db
from utilities.common import utc_now_ts as now
from user.models import User

class Relationship(db.Document):
    #Set up choices tuples list
    FRIENDS = 1        #tuples -> RELATIONSHIP_TYPE -> relationship_type
    BLOCKED = -1
    
    RELATIONSHIP_TYPE = (
        (FRIENDS, 'Friends'),
        (BLOCKED, 'Blocked'),
        )
        
    PENDING = 0
    APPROVED = 1
    
    STATUS_TYPE = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        )
        
    #For friend request
    from_user = db.ReferenceField(User, db_field='from', reversed_delete_rule=CASCADE) #Foreign key to user
    #For friend confirmation
    to_user = db.ReferenceField(User, db_field='to', reversed_delete_rule=CASCADE)
    relationship_type = db.IntField(db_field='rt', choices=RELATIONSHIP_TYPE) #intfield from choices type
    status = db.IntField(db_field='s', choices=STATUS_TYPE)
    request_date = db.IntField(db_field='rd', default=now())
    approved_date = db.IntField(db_field='ad', default=0)
    
    #Compound index
    meta = {
        'indexes': [('from_user', 'to_user'), ('from_user', 'to_user', 'relationship_type', 'status' )]
    }
    