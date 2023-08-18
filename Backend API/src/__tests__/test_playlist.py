from fastapi.testclient import TestClient
import json
import pytest
from datetime import datetime


from main import app as app

client = TestClient(app)


def test_get_playlist_correct(clear_test_data_db):
    name = "8232392323623823723"
    foto = "https://foto"
    descripcion = "hola"

    url = f"/playlists/?nombre={name}&foto={foto}&descripcion={descripcion}"


    formatting = "%Y-%m-%dT%H:%M:%S"
    post_date_iso8601 = datetime.strptime(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),formatting)


    payload = []

    response = client.post(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201

    response = client.get(f"/playlists/{name}")
    assert response.status_code == 200
    assert response.json()["name"]==name
    assert response.json()["photo"]==foto
    assert response.json()["description"]==descripcion

    try:
        fecha = response.json()["upload_date"]
        response_date = datetime.strptime(fecha, formatting)

        assert response_date.hour==post_date_iso8601.hour

    except ValueError:
        assert False

    response = client.delete(f"/playlists/{name}")
    assert response.status_code == 202


def test_get_playlist_not_found():
    name = "8232392323623823723"

    response = client.get("/playlists/{name}")
    assert response.status_code == 404


def test_get_playlist_invalid_name():
    name = ""

    response = client.get("/playlists/{name}")
    assert response.status_code == 404


def test_post_playlist_correct(clear_test_data_db):
    name = "8232392323623823723"

    url = f"/playlists/?nombre={name}&foto=foto&descripcion=descripcion&upload_date=upload_date"

    payload = []

    response = client.post(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201

    response = client.delete(f"/playlists/{name}")
    assert response.status_code == 202


def test_delete_playlist_correct(clear_test_data_db):
    name = "8232392323623823723"

    url = f"/playlists/?nombre={name}&foto=foto&descripcion=descripcion"

    payload = []

    response = client.post(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201

    response = client.delete(f"/playlists/{name}")
    assert response.status_code == 202


def test_delete_playlist_playlist_not_found(clear_test_data_db):
    name = "8232392323623823723"

    response = client.delete(f"/playlists/{name}")
    assert response.status_code == 404


def test_delete_playlist_playlist_invalid_name(clear_test_data_db):
    """Cannot recreate error 404 because name cant be empty or None to reach the actual python method"""

    name = ""

    response = client.delete(f"/playlists/{name}")
    assert response.status_code == 405


def test_get_playlists_correct():
    response = client.get(f"/playlists/")
    assert response.status_code == 200


def test_update_playlist_correct(clear_test_data_db):
    name = "8232392323623823723"

    url = f"/playlists/?nombre={name}&foto=foto&descripcion=descripcion"

    payload = []

    response = client.post(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201

    new_description= "nuevadescripcion"

    url = f"/playlists/{name}/?foto=foto&descripcion={new_description}"

    payload = []

    response = client.put(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 204


    response = client.get(f"/playlists/{name}")
    assert response.status_code == 200
    assert response.json()["description"]==new_description



    response = client.delete(f"/playlists/{name}")
    assert response.status_code == 202

def test_update_playlist_correct_nuevo_nombre(clear_test_data_db):
    name = "8232392323623823723"

    url = f"/playlists/?nombre={name}&foto=foto&descripcion=descripcion"

    payload = []

    response = client.post(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201

    new_name = "82323923236238237237"
    new_description= "nuevadescripcion"

    url = f"/playlists/{name}/?foto=foto&descripcion={new_description}&nuevo_nombre={new_name}"

    payload = []

    response = client.put(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 204


    response = client.get(f"/playlists/{new_name}")
    assert response.status_code == 200

    response = client.delete(f"/playlists/{new_name}")
    assert response.status_code == 202


# executes after all tests
@pytest.fixture()
def clear_test_data_db():
    new_name = "82323923236238237237"
    name = "8232392323623823723"
    response = client.delete(f"/playlists/{new_name}")
    response = client.delete(f"/playlists/{name}")

    yield
    new_name = "82323923236238237237"
    name = "8232392323623823723"
    response = client.delete(f"/playlists/{new_name}")
    response = client.delete(f"/playlists/{name}")
