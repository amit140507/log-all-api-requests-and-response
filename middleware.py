import logging
import time
import json
from userapp.models import RestapisStatisticsLog

request_logger = logging.getLogger('restapis_allrequestslogs')

class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "/api/" in request.META['PATH_INFO']:
            
        # if "/api/" in str(request.get_full_path()):    
            start_time = time.time()
            # start_time = time.monotonic()

            response = self.get_response(request)

            end_time = time.time()
            response_time = end_time - start_time
            response_time = str(format(float(response_time),'.5f'))
            # request_path=request.path,
            if response and response["content-type"] == "application/json":
            # if response and response.content :
                response_data = json.loads(response.content.decode("utf-8"))
            elif response and response["content-type"] == "text/html":
                response_data = response.content.decode('utf-8')
            else:
                response_data = ''
            # ip_address=request.META['REMOTE_ADDR'],
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            request_body = json.loads(request.body.decode("utf-8")) if request.body else ''

            try:
                RestapisStatisticsLog.objects.create(
                    request_path=request.build_absolute_uri(),
                    method=request.method,
                    ip_address = ip_address,
                    response_time=response_time,
                    status_code = response.status_code,
                    payload = request_body,
                    response = response_data
                )
                log_data = {
                    "Request Path": request.build_absolute_uri(),
                    "Method": request.method,
                    "IP Address": ip_address,
                    "Response Time": response_time,
                    "Status Code": response.status_code,
                    "Payload": request_body,
                    "Response": response_data,
                }
                request_logger.info(msg=log_data)

            except Exception as e:
                logging.error("Logging Error: "+ str(e))
        else:
            response = self.get_response(request)    
        return response
    
    def process_exception(self, request, exception):
        try:
            raise exception
        except Exception as e:
           print(str(e))
           request_logger.exception("Unhandled Exception: " + str(e))
        return exception
