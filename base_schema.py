from marshmallow import Schema, EXCLUDE, post_load


class AutobuildSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    _class_to_load = None

    @post_load
    def build_object(self, data, **kwargs):
        if self._class_to_load is None:
            raise NotImplementedError("Subclass must set '_class_to_load'")
        return self._class_to_load(**data)
