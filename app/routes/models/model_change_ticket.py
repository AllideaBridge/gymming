from marshmallow import Schema, fields


class CreateChangeTicketRequest(Schema):
    schedule_id = fields.Integer(required=True)
    change_from = fields.Str(required=True)
    change_type = fields.Str(required=True)
    change_reason = fields.Str(required=True)
    # TODO(dogyun): Datetime으로 받으면 TypeError: Object of type datetime is not JSON serializable 발생하는데 해결해야함
    start_time = fields.Str(required=True)

    def __init__(self, data):
        super().__init__()
        self.schedule_id = data["schedule_id"]
        self.change_from = data["change_from"]
        self.change_type = data["change_type"]
        self.change_reason = data["change_reason"]
        self.start_time = data["start_time"]


class UpdateChangeTicketRequest(Schema):
    change_from = fields.Str()
    change_type = fields.Str()
    status = fields.Str()
    change_reason = fields.Str()
    reject_reason = fields.Str()
    start_time = fields.Str()
