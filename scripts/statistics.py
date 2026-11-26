from cdf_auth import get_cognite_client



client = get_cognite_client()

statistics = client.data_modeling.statistics.project()

print(statistics)
