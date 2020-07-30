#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module encapsulates the communication with the strava API and the fetching
of the requested data herein
"""

__author__ = "Thomas Keil"
__email__ = "tomskeil@hotmail.com"

__license__ = "GPL"
__version__ = "0.0.0"
__maintainer__ = "Thomas Keil"
__status__ = "Prototype"


# Import packages
import requests
import configparser
from decorFunc import retry_request
from abc import ABC, abstractmethod


class DataConnector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def __repr__(self):
        """ Pass representation magic """
        pass

    @abstractmethod
    def authenticate(self):
        """ Logic for authentication """
        pass

    @abstractmethod
    def get_data(self):
        """ Logic for getting data over the connector """
        pass


# Class definitions
class StravaDataConnector(DataConnector):
    """
    The subclass Strava API data connector


    Attributes
    ---------
    base_url : str
        The base URL for the Strava API

    config_parameters : dict
        A dictionary containing the confidential credentials of the Strava application

    _access_token : str
        The access token of the Strava application (default None)

    defaultActivity : dict
        The default activity metadata stored as a buffer


    Methods
    ------
    authenticate()
        Authenticates against the Strava server and retrieves access token

    get_data(fetch_type, **kwargs)
        Retrieves the relevant data with the keyword arguments

    headers()
        Returns the authorisation HTTP header

    read_configs(config, rel_section)
        Reads the confidential Strava application credentials from the configuration file

    getLastID(setDefault=True)
        Get the last identification of the relevant activity and optionally set as default or not

    get_activities_data(*args)
        Get a list of all activities on the Strava server for the application

    fetch_athlete(**kwargs)
        Retrieve athlete data

    fetch_activities(**kwargs)
        Retrieve activities data

    fetch_activity(act_id=None, **kwargs)
        Retrieve activity data based on specified activity identification

    fetch_stream(act_id=None, keys=None, **kwargs)
        Retrieve stream data based on specified activity identification and relevant keys

    fetch_segmentsStarred(**kwargs)
        Retrieve segments starred data

    fetch_segments(act_id=None, **kwargs)
        Retrieve segments data based on specified activity identification
    """
    base_url = "http://www.strava.com/api/v3"

    def __init__(self, config_file: str, access_token=None):
        """
        Parameters
        ---------
        config_file : str
            The absolute file path of the configuraiton file

        access_token : str, optional
            The access token retrieved by the Strava application (default None)
        """

        self.config_parameters = self.read_configs(config=config_file,
                                                   rel_section="StravaCredentials")

        self._access_token = None
        self.defaultActivity = {k: None for k in ['id', 'name', 'startDateTime']}
        self._access_token = access_token


    def __repr__(self):
        return 'Strava API-connector'

    def authenticate(self):
        """
        Processes the authentication flow of the oAuth2.0 mechanism and retrieves an access token.

        Returns
        ---------
        self
            Returns the instance and sets the access token inplace
        """

        auth_url = "https://www.strava.com/oauth/token"

        payload = {"grant_type": "refresh_token", **self.config_parameters}

        response = requests.post(auth_url,
                                 data=payload,
                                 verify=True,
                                 headers={'Connection': 'close'})

        self._access_token = response.json().get('access_token')

        return self

    def get_data(self, fetch_type: str, **kwargs):
        """
        Retrieves the data from the Strava server by specific fetch type and conditional keyword arguments

        Parameters
        ---------
        fetch_type : str
            The specific fetch type to be retrieved (e.g. 'athlete', 'activities', 'activity' etc.)

        kwargs
            Conditional keyword arguments (e.g. 'act_id' specifying the specific activity identification to be retrieved)


        Returns
        -------
        Response
            Response object of the callback function relevant to the specific fetch type. 
        """

        fetchCall = "fetch_" + fetch_type
        output = None

        if fetchCall in dir(self):
            fetchCaller = getattr(self, fetchCall)
            output = fetchCaller(**kwargs)

        else:
            availAttr = dir(self)
            availMethod = [x.replace("fetch_","") for x in availAttr if "fetch_" in x]
            printOutput = "\n- ".join(availMethod)

            print("Please choose one of the following: \n- " + printOutput)

        return output

    @property
    def headers(self):
        return {"Authorization": "Bearer {at}".format(at=self._access_token),
                "Connection": "close"}

    @staticmethod
    def read_configs(config, rel_section):
        """
        Static method to read and retrieve the selected configuration file and its contents

        Parameters
        ----------
        config : str
            The name and/or filepath to the configuration file in string format.

        rel_section : str
            The relevant section of the configuration file wich should be parsed into the environment.


        Returns
        -------
        dict
            Returns dictionary object containing the respective credentials of the configuration file. 
        """
        configInst = configparser.ConfigParser()
        configInst.read(config)

        return_dict = {k: configInst.get(rel_section, k)
                       for k in configInst.options(rel_section)}

        return return_dict


    def getLastID(self, setDefault: bool = True):
        """
        Retrieves the last activity identification on the Strava server.

        Parameters
        ----------
        setDefault : bool
            Boolean variable indicating if the last activity id should be set as the global default.

        Returns
        -------
        int
            Returns the last activity id in integer format. 
        """
        data = self.fetch_activities()
        data = data.json()
        if setDefault:
            self.defaultActivity['id'] = data[0].get('id')
            self.defaultActivity['name'] = data[0].get('name')
            self.defaultActivity['startDateTime'] = data[0].get('start_date_local')

        return data[0].get('id')

    def get_activities_data(self, *args):
        """
        Retrieves a list of all the activities stored on the Strava server

        Parameters
        ----------
        args
            Optional arguments indicating which metadata should be returned (e.g. 'start_date_local', 'name' etc.)

        Returns
        -------
        list
            Returns a list of activities and its nested metadata in respective dict format. 
        """
        activities = self.fetch_activities()
        activities = activities.json()

        rel_keys = ('start_date_local', 'name', 'id', 'type') if not args else args

        activitiesOutput = [{k: dic[k] for k in rel_keys} for dic in activities]

        return activitiesOutput


    @retry_request(retry_count=3, errorCallback='authenticate')
    def fetch_athlete(self, **kwargs):
        """
        Fetches athlete specific data from the Strava server

        Returns
        -------
        Response
            Returns a Response object containing the respective response data over the HTTP protocol. 
        """
        mod_url = self.base_url + "/athlete"

        return requests.get(url=mod_url, headers=self.headers)

    @retry_request(retry_count=3, errorCallback='authenticate')
    def fetch_activities(self, **kwargs):
        """
        Fetches activities specific data from the Strava server

        Returns
        -------
        Response
            Returns a Response object containing the respective response data over the HTTP protocol. 
        """
        mod_url = self.base_url + "/athlete/activities"

        return requests.get(url=mod_url, headers=self.headers)

    @retry_request(retry_count=3, errorCallback='authenticate')
    def fetch_activity(self, act_id: int = None, **kwargs):
        """
        Fetches activity specific data from the Strava server

        Parameters
        ----------
        act_id : int
            Parameter value for the specific activity id requested (default None)

        Returns
        -------
        Response
            Returns a Response object containing the respective response data over the HTTP protocol. 
        """
        if not act_id:
            if self.defaultActivity['id']:
                print("No activity provided - Getting default activity")
                act_id = self.defaultActivity['id']

            else:
                '''Get last activity'''
                print("No activity id provided - fetching last activity")
                act_id = self.getLastID()

        mod_url = self.base_url + "/activities/{act_id}".format(act_id=act_id)

        return requests.get(url=mod_url, headers=self.headers)

    @retry_request(retry_count=3, errorCallback='authenticate')
    def fetch_stream(self, act_id: int = None, keys: list = None, **kwargs):
        """
        Fetches stream specific data from the Strava server

        Parameters
        ----------
        act_id : int
            Parameter value for the specific activity id requested (default None)

        keys : list
            Parameter value for the specific keys to be retrieved (e.g. 'heartrate', default None)

        Returns
        -------
        Response
            Returns a Response object containing the respective response data over the HTTP protocol. 
        """
        if not act_id:
            if self.defaultActivity['id']:
                print("No activity provided - Getting default activity")
                act_id = self.defaultActivity['id']

            else:
                '''Get last activity'''
                print("No activity id provided - fetching last activity")
                act_id = self.getLastID()

        mod_url = self.base_url + "/activities/{act_id}/streams".format(act_id=act_id)

        if keys:
            keys = {'keys': ",".join(keys)}

        return requests.get(url=mod_url, headers=self.headers, params=keys)

    @retry_request(retry_count=3, errorCallback='authenticate')
    def fetch_segmentsStarred(self, **kwargs):
        """
        Fetches segments starred specific data from the Strava server

        Returns
        -------
        Response
            Returns a Response object containing the respective response data over the HTTP protocol. 
        """
        mod_url = self.base_url + "/segments/starred"

        return requests.get(url=mod_url, headers=self.headers)


    @retry_request(retry_count=3, errorCallback='authenticate')
    def fetch_segments(self, act_id: int = None, **kwargs):
        """
        Fetches segments specific data from the Strava server

        Parameters
        ----------
        act_id : int
            Parameter value for the specific activity id requested (default None)

        Returns
        -------
        Response
            Returns a Response object containing the respective response data over the HTTP protocol. 
        """
        if not act_id:
            if self.defaultActivity['id']:
                print("No activity provided - Getting default activity")
                act_id = self.defaultActivity['id']

            else:
                '''Get last activity'''
                print("No activity id provided - fetching last activity")
                act_id = self.getLastID()

        mod_url = self.base_url + "/segments/{act_id}".format(act_id=act_id)

        return requests.get(url=mod_url, headers=self.headers)


