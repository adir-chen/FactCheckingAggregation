"""A simple example of how to access the Google Analytics API."""
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)
    return service


def get_first_profile_id(service):
    # Use the Analytics service object to get the first profile id.
    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()
    if accounts.get('items'):
        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(
            accountId=account).execute()

        if properties.get('items'):
            # Get the first property id.
            property = properties.get('items')[0].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                accountId=account,
                webPropertyId=property).execute()

            if profiles.get('items'):
                # return the first view (profile) id.
                return profiles.get('items')[0].get('id')
    return None


def get_results(service, profile_id, start_date, end_date, metrics, dimensions, sort, filters):
    # Use the Analytics Service Object to query the Core Reporting API
    # for the number of sessions within the past seven days.
    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
        dimensions=dimensions,
        filters=filters,
        sort=sort).execute()


def get_report(start_date, end_date, metrics, dimensions, sort=None, filters=None):
    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # print(dir_path)
    # key_file_location = 'analytics\GoogleAPI\client_secrets.json'
    key_file_location = dir_path + '\client_secrets.json'

    # Authenticate and construct service.
    service = get_service(
        api_name='analytics',
        api_version='v3',
        scopes=[scope],
        key_file_location=key_file_location)

    profile_id = get_first_profile_id(service)
    return get_results(service, profile_id, start_date, end_date, metrics, dimensions, sort, filters)


def get_report_countries(start_date, end_date):
    metrics = 'ga:pageViews'
    dimensions = 'ga:country'
    reports = get_report(start_date, end_date, metrics, dimensions)
    return reports.get('rows')


def get_report_view_by_time(start_date, end_date, dimensions):
    metrics = 'ga:pageViews'
    reports = get_report(start_date, end_date, metrics, dimensions)
    table = []
    for row in reports.get('rows'):
        new_row = []
        for cell in row:
            new_row.append(int(cell))
        table.append(new_row)
    return table


def get_report_top_n_claims(num_of_claims, start_date, end_date):
    metrics = 'ga:pageViews'
    dimensions = 'ga:pagePath'
    sort = '-ga:pageViews'
    filters = 'ga:pagePath=~/claim/'
    reports = get_report(start_date, end_date, metrics, dimensions, sort, filters)
    top_claims = []
    for row in reports.get('rows')[:num_of_claims * 2]:
        claim_id_arr = row[0].split('/')
        top_claims.append([int(claim_id_arr[len(claim_id_arr) - 1]), int(row[1])])
    return top_claims
