from marshmallow import Schema, fields

class ImageSchema(Schema):
    thumbnail = fields.String()
    original = fields.String()
