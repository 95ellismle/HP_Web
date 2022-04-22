from marshmallow import Schema, fields


class SelectorsSchema(Schema):
    tenure = fields.Str(required=False)
    date_from = fields.DateTime('%Y-%m-%d', required=False)
    date_to = fields.DateTime('%Y-%m-%d', required=False)
    dwelling_type = fields.List(fields.Str(), required=False)
    postcode = fields.Str(required=False)
    paon = fields.Str(required=False)
    street = fields.Str(required=False)
    city = fields.Str(required=False)
    county = fields.Str(required=False)
    price_low = fields.Int(strict=True, required=False)
    price_high = fields.Int(strict=True, required=False)
