import contextvars

request_id_context = contextvars.ContextVar("request_id", default="")
request_ip_context = contextvars.ContextVar("request_ip", default="")
endpoint_name_context = contextvars.ContextVar("endpoint_name", default="")
