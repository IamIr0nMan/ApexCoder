import requests
import os
from datetime import date, timedelta
# from dotenv import find_dotenv, load_dotenv

# load_dotenv(find_dotenv())


class ResourceFetcher:
    def __init__(self) -> None:
        self.clistBaseURL = "https://clist.by:443/api/v2/contest/"
        self.codeforcesBaseURL = "https://codeforces.com/api/"
        self.leetcodeBaseURL = "https://leetcode-stats-api.herokuapp.com/"

    def __getDateRangeParams(self, contestType: str) -> dict:
        if contestType == "upcoming":
            startDate = date.today()
            endDate = startDate + timedelta(days=7)
        elif contestType == "past":
            endDate = date.today()
            startDate = endDate - timedelta(days=7)

        startDate = str(startDate) + "T00:00:00"
        endDate = str(endDate) + "T00:00:00"

        return {"start__gte": startDate, "end__lte": endDate}

    def __formatContestData(self, data: dict) -> list:
        data = data["objects"]
        formattedData = []
        for value in data:
            formattedValue = {}
            formattedValue["host"] = value["host"]
            formattedValue["event"] = value["event"]
            formattedValue["href"] = value["href"]
            formattedValue["start"] = value["start"]
            formattedValue["end"] = value["end"]
            formattedData.append(formattedValue)

        return formattedData

    def __formatUserData(self, data: dict) -> dict:
        data = data["result"][0]
        formattedData = {}
        formattedData["handle"] = data["handle"]
        formattedData["rank"] = data["rank"]
        formattedData["rating"] = data["rating"]
        formattedData["maxRank"] = data["maxRank"]
        formattedData["maxRating"] = data["maxRating"]

        return formattedData

    def __fetchResource(self, URL: str, parameters: dict = {}, header: dict = {}) -> requests.Response:
        response = requests.get(URL, params=parameters, headers=header)
        if response.status_code == 200:
            return response
        else:
            raise Exception('Error fetching data')

    def __filterContestData(self, contestData: list, host: str) -> list:
        filteredContestData = []
        for contest in contestData:
            if contest["host"] == host:
                filteredContestData.append(contest)
        return filteredContestData

    def __getContestInfo(self, parameters: dict) -> list:
        header = {"Authorization": os.getenv("CLIST_AUTH")}
        response = self.__fetchResource(self.clistBaseURL, parameters, header)
        data = response.json()
        return self.__formatContestData(data)

    def __getCodeForcesUserInfo(self, userId: str) -> int:
        response = self.__fetchResource(
            self.codeforcesBaseURL + "user.info?handles=" + userId)

        data = response.json()
        userInfo = self.__formatUserData(data)
        return userInfo["rating"]

    def getUpcomingContestInfo(self) -> list:
        params = self.__getDateRangeParams("upcoming")
        return self.__getContestInfo(params)

    def getPastConstestInfo(self) -> list:
        params = self.__getDateRangeParams("past")
        return self.__getContestInfo(params)

    def getCodeForcesUserRating(self, userId: str) -> int:
        return self.__getCodeForcesUserInfo(userId)

    def getLeetcodeUserInfo(self, userId: str) -> int:
        response = self.__fetchResource(self.leetcodeBaseURL + userId)
        return response.json()

    def getCodechefContests(self) -> list:
        return self.__filterContestData(self.getUpcomingContestInfo(), "codechef.com")

    def getCodeforcesContests(self) -> list:
        return self.__filterContestData(self.getUpcomingContestInfo(), "codeforces.com")

    def getLeetcodeContests(self) -> list:
        return self.__filterContestData(self.getUpcomingContestInfo(), "leetcode.com")
