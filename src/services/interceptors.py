import grpc
import logging
from typing import Callable, Any
from sqlalchemy.exc import NoResultFound

class ErrorHandlingInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def intercept_service(self, continuation: Callable, handler_call_details: grpc.HandlerCallDetails) -> grpc.RpcMethodHandler:
        handler = continuation(handler_call_details)
        if handler is None:
            return None

        if handler.request_streaming or handler.response_streaming:
            return handler

        def wrapper(request, context):
            try:
                return handler.unary_unary(request, context)
            except NoResultFound as e:
                self._logger.warning(f"Resource not found: {str(e)}")
                context.abort(grpc.StatusCode.NOT_FOUND, str(e))
            except ValueError as e:
                self._logger.warning(f"Invalid argument: {str(e)}")
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
            except Exception as e:
                self._logger.exception(f"Unhandled exception in gRPC handler: {str(e)}")
                context.abort(grpc.StatusCode.INTERNAL, "Internal server error")

        return grpc.unary_unary_rpc_method_handler(
            wrapper,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )
