"""
Warning: Open Data API is not documented and therefore the endpoints may change at any point : http://ideas.arcgis.com/ideaView?id=087E0000000blPIIAY
Not supported by Esri Support Services.
Requests module is needed, download it here if you don't have it installed: http://docs.python-requests.org/en/latest/
"""
print(__doc__)

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import argparse

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class OpenData(object):

    """
    Example Open Data object. Open Data site needs to be public.
    username : Username used to log into an ArcGIS Online Organization.
    password : Password used to log into an ArcGIS Online Organization.
    OpenDataSite: Open Data Site Number (i.e. 0001).
    """

    def __init__(self, username, password, OpenDataSite):

        self.username = username
        self.password = password
        self.token = self.generateToken()

        self.OpenDataSite = OpenDataSite
        self.OpenDataItems = self.findAllOpenDataItems()

    def generateToken(self):
        """
        Generate Token generates an access token in exchange for \
        user credentials that can be used by clients when working with the ArcGIS Portal API:
        http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000m5000000
        """
        url = "https://arcgis.com/sharing/rest/generateToken"
        data = {'username': self.username,
                'password': self.password,
                'referer': "https://www.arcgis.com",
                'f': 'json'}
        return requests.post(url, data, verify=False).json()['token']

    def findAllOpenDataItems(self):
        """
        Finds and returns all item IDs in an Open Data site. \
        Will receive error if the Open Data site is not public.
        """
        r = requests.get('https://opendata.arcgis.com/api/v2/sites/{0}/datasets?token={1}'.format(self.OpenDataSite, self.token)).json()
        dataset_list = []
        num_of_datasets = r['meta']['stats']['totalCount']
        while len(dataset_list) != num_of_datasets:
            try:
                [dataset_list.append(item) for item in r['data']]
                r = requests.get(r['links']['next']).json()
            except:
                pass

        return [x for x in dataset_list]

    def refresh(self):
        """
        Refreshes all Open Data datasets and download caches that aren't back by hosted services.
        """
        refreshed_list = []
        unrefreshed_list = []
        print("Gathering datasets...")
        for dataset in self.OpenDataItems:
            if dataset['attributes']['downloadCache'] != 'hosted':
                url = "https://opendata.arcgis.com/utilities/workers/refresh/datasets/{0}.json?token={1}".format(dataset['id'], self.token)
                requests.post(url, verify=False)
                refreshed_list.append(dataset['attributes']['title'])

            else:
                unrefreshed_list.append(dataset['attributes']['title'])

        # generates a report of the caches that have been refreshed by the script and those that haven't
        count = 1
        print("Refreshed: {} of {} caches\n".format(len(refreshed_list), len(self.OpenDataItems)))
        for item in refreshed_list:
            print("{}. Refreshed: {}".format(count, item))
            count += 1
        count = 1

        if len(unrefreshed_list) > 0:
            print("\nDid not manually refresh: {} of {} caches".format(len(unrefreshed_list), len(self.OpenDataItems)))
            print("These datasets are backed by hosted services that have their caches automatically refreshed by ArcGIS Online.\n")
            for item in unrefreshed_list:
                print("{}. Not refreshed: {}".format(count, item))
                count += 1


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="your username")
    parser.add_argument("-p", "--password", help="your password")
    parser.add_argument("-i", "--id", type=str, help="your org id")
    args = parser.parse_args()

    test = OpenData(args.username, args.password, args.id)
    test.refresh()
