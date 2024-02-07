import contextvars

# https://medium.com/gradiant-talks/identifying-fastapi-requests-in-logs-bac3284a6aa
request_id_context = contextvars.ContextVar("request_id", default="")
request_ip_context = contextvars.ContextVar("request_ip", default="")
endpoint_name_context = contextvars.ContextVar("endpoint_name", default="")

class ContextProxy():
    def __init__(self, cntx):
        self._cntx = cntx

    def __repr__(self):
        return self._cntx.get()

