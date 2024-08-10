from flask import Blueprint, render_template, redirect, url_for, request
import requests

track_blueprint = Blueprint("track", __name__)


class SearchResult:
    def __init__(self, name, picture, link):
        self.name = name
        self.picture = picture
        self.link = link


@track_blueprint.route("/track", methods=["GET", "POST"])
def track():
    if request.method == "GET":
        return render_template("track.html")
    if request.method == "POST":
        search = request.form.get("search")

        r = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "client_credentials",
                "client_id": "b2817ab1a6a6471dae92088510ed25f1",
                "client_secret": "d4fad7b2dbac4eca9c558e39c584a6d0",
            },
        )

        access_token = r.json()["access_token"]
        headers = {"Authorization": "Bearer " + access_token}
        type = ["artist"]
        # print(type)

        payload = {"q": search, "type": type}

        r = requests.get(
            "https://api.spotify.com/v1/search", params=payload, headers=headers
        )

        print(r.json())
        print(r.json()["artists"]["items"][0]["name"])
        print(r.json()["artists"]["items"][0]["images"][0]["url"])
        print(r.json()["artists"]["items"][0]["external_urls"]["spotify"])

        searchResultList = []

        for i in range(5):
            searchResultList.append(
                SearchResult(
                    r.json()["artists"]["items"][i]["name"],
                    r.json()["artists"]["items"][i]["images"][0]["url"],
                    r.json()["artists"]["items"][i]["external_urls"]["spotify"],
                )
            )

        # print(searchResultList[1].name)

        # searchResult1 = SearchResult(
        #     r.json()["artists"]["items"][0]["name"],
        #     r.json()["artists"]["items"][0]["images"][0]["url"],
        #     r.json()["artists"]["items"][0]["external_urls"]["spotify"],
        # )

        # r = requests.get(
        #     "https://api.spotify.com/v1/artists/2hGh5VOeeqimQFxqXvfCUf?si=GbHu7fEJSP6OvAXiU9ki4Q",
        #     headers={"Authorization": "Bearer " + access_token},
        # )

        # print(r.text)

        return render_template("track.html", searchResultList=searchResultList)
