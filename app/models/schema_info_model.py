from datetime import timezone, datetime

from mongoengine import Document, StringField, DictField, DateTimeField

class SchemaInfo(Document):
    session_id = StringField(required = True, unique = True)  
    db_credentials = DictField(required = True)  
    db_schema = StringField(required = True)
    created_at = DateTimeField(default = datetime.now(timezone.utc), required = True)
    updated_at = DateTimeField(default = datetime.now(timezone.utc), required = True)

    meta = {
        'collection': 'session_registry',
        'indexes': ['session_id']
    }