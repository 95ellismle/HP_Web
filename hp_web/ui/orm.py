from ui.models import UsageStats


def record_usage_stats(selectors, IP, server_response_time):
    """Will record what any usage stats in the database.

    This includes:
        * selector values
        * ip address
        * server response time
    """
    UsageStats.objects.create(postcode=selectors.get('postcode'),
                              paon=selectors.get('paon'),
                              street=selectors.get('street'),
                              city=selectors.get('city'),
                              county=selectors.get('county'),
                              #is_new=selectors.get('is_new'),
                              dwelling_type=selectors.get('dwelling_type'),
                              tenure=selectors.get('tenure'),
                              price_low=selectors.get('price_low'),
                              price_high=selectors.get('price_high'),
                              date_from=selectors.get('date_from'),
                              date_to=selectors.get('date_to'),
                              response_time=server_response_time,
                              IP_address=IP)

