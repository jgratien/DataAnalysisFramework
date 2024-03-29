import sys
import time
import logging
import random
from jaeger_client import Config
from opentracing_instrumentation.request_context import get_current_span, span_in_context

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)    
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service,
    )
    if config._initialized == False :
        return config.initialize_tracer()
    else :
        print("error : create now tracer...")
        return config.new_tracer()

def booking_mgr(movie):
    with tracer.start_span('booking') as span:
        span.set_tag('Movie', movie)
        with span_in_context(span):
            cinema_details = check_cinema(movie)
            showtime_details = check_showtime(cinema_details)
            book_show(showtime_details)

def check_cinema(movie):
    with tracer.start_span('CheckCinema', child_of=get_current_span()) as span:
        with span_in_context(span):
            num = random.randint(1,30)
            time.sleep(num)
            print("sleep : ",num)
            cinema_details = "Cinema Details"
            flags = ['false', 'true', 'false']
            random_flag = random.choice(flags)
            span.set_tag('error', random_flag)
            span.log_kv({'event': 'CheckCinema' , 'value': cinema_details })
            return cinema_details

def check_showtime( cinema_details ):
    with tracer.start_span('CheckShowtime', child_of=get_current_span()) as span:
        with span_in_context(span):
            num = random.randint(1,30)
            time.sleep(num)
            showtime_details = "Showtime Details"
            flags = ['false', 'true', 'false']
            random_flag = random.choice(flags)
            span.set_tag('error', random_flag)
            span.log_kv({'event': 'CheckCinema' , 'value': showtime_details })
            return showtime_details

def book_show(showtime_details):
    with tracer.start_span('BookShow',  child_of=get_current_span()) as span:
        with span_in_context(span):
            num = random.randint(1,30)
            time.sleep(num)
            Ticket_details = "Ticket Details"
            flags = ['false', 'true', 'false']
            random_flag = random.choice(flags)
            span.set_tag('error', random_flag)
            span.log_kv({'event': 'CheckCinema' , 'value': showtime_details })
            print(Ticket_details)

#assert len(sys.argv) == 2
tracer = init_tracer('booking')
movie = sys.argv[0]
booking_mgr(movie)
# yield to IOLoop to flush the spans
time.sleep(2)
tracer.close()
