from datetime import datetime

import app.spotify_electron.playlist.playlist_repository as playlist_repository
import app.spotify_electron.user.all_users_service as all_users_service
from app.exceptions.exceptions_schema import BadParameterException
from app.logging.logging_constants import LOGGING_PLAYLIST_SERVICE
from app.logging.logging_schema import SpotifyElectronLogger
from app.spotify_electron.playlist.playlist_schema import (
    PlaylistAlreadyExistsException,
    PlaylistBadNameException,
    PlaylistDTO,
    PlaylistNotFoundException,
    PlaylistRepositoryException,
    PlaylistServiceException,
    PlaylistUnAuthorizedException,
    get_playlist_dto_from_dao,
)
from app.spotify_electron.security.security_schema import TokenData
from app.spotify_electron.user.user_schema import UserNotFoundException
from app.spotify_electron.utils.validation.utils import validate_parameter

playlist_service_logger = SpotifyElectronLogger(LOGGING_PLAYLIST_SERVICE).getLogger()


def check_jwt_user_is_playlist_owner(token: TokenData, owner: str) -> bool:
    """Check if the user is playlists owner

    Args:
    ----
        token (TokenData): token with user data
        owner (str): owner name

    Raises:
    ------
        PlaylistUnAuthorizedException: if the user is not the playlists owner

    Returns:
    -------
        bool: if the user is the owner of the playlist

    """
    if token.username == owner:
        return True
    raise PlaylistUnAuthorizedException()


def check_playlist_exists(name: str) -> bool:
    """Returns if playlist exists

    Args:
    ----
        name (str): playlist name

    Returns:
    -------
        bool: if the playlist exists

    """
    return playlist_repository.check_playlist_exists(name)


def get_playlist(name: str) -> PlaylistDTO:
    """Returns the playlist

    Args:
    ----
        name (str): name of the playlist

    Raises:
    ------
        PlaylistBadNameException: invalid playlist name
        PlaylistNotFoundException: playlist not found
        PlaylistServiceException: unexpected error while getting playlist

    Returns:
    -------
        PlaylistDTO: the playlist

    """
    try:
        handle_playlist_name_parameter(name)
        playlist = playlist_repository.get_playlist_by_name(name)
        playlist_dto = get_playlist_dto_from_dao(playlist)
    except PlaylistBadNameException as exception:
        playlist_service_logger.exception(f"Bad Playlist Name Parameter : {name}")
        raise PlaylistBadNameException from exception
    except PlaylistNotFoundException as exception:
        playlist_service_logger.exception(f"Playlist not found : {name}")
        raise PlaylistNotFoundException from exception
    except PlaylistRepositoryException as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Repository getting playlist : {name}"
        )
        raise PlaylistServiceException from exception
    except Exception as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Service getting playlist : {name}"
        )
        raise PlaylistServiceException from exception
    else:
        playlist_service_logger.info(f"Playlist {name} retrieved successfully")
        return playlist_dto


def create_playlist(
    name: str, photo: str, description: str, song_names: list[str], token: TokenData
) -> None:
    """Creates a playlist

    Args:
    ----
        name (str): name
        photo (str): thumbnail photo
        description (str): description
        song_names (list): list of song names
        token (TokenData): token user info

    Raises:
    ------
        PlaylistBadNameException: invalid playlist name
        PlaylistAlreadyExistsException: playlist already exists
        UserNotFoundException: user doesnt exists
        PlaylistServiceException: unexpected error while creating playlist

    """
    try:
        owner = token.username

        current_date = datetime.now()
        date_iso8601 = current_date.strftime("%Y-%m-%dT%H:%M:%S")

        handle_playlist_name_parameter(name)
        handle_playlist_should_not_exists(name)
        handle_user_should_exists(owner)

        playlist_repository.insert_playlist(
            name,
            photo if "http" in photo else "",
            date_iso8601,
            description,
            owner,
            song_names,
        )

        all_users_service.add_playlist_to_owner(
            user_name=owner, playlist_name=name, token=token
        )
        playlist_service_logger.info(f"Playlist {name} created successfully")
    except PlaylistBadNameException as exception:
        playlist_service_logger.exception(f"Bad Playlist Name Parameter : {name}")
        raise PlaylistBadNameException from exception
    except PlaylistAlreadyExistsException as exception:
        playlist_service_logger.exception(f"Playlist already exists : {name}")
        raise PlaylistAlreadyExistsException from exception
    except UserNotFoundException as exception:
        playlist_service_logger.exception(f"User not found : {name}")
        raise UserNotFoundException from exception
    except PlaylistRepositoryException as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Repository creating playlisy : {name}"
        )
        raise PlaylistServiceException from exception
    except Exception as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Service creating playlisy : {name}"
        )
        raise PlaylistServiceException from exception


def update_playlist(
    name: str,
    new_name: str | None,
    photo: str,
    description: str,
    song_names: list[str],
    token: TokenData,
) -> None:
    """Updates a playlist

    Args:
    ----
        name (str): name
        new_name (str | None): new playlist name, optional
        photo (str): thumbnail photo
        description (str): description
        song_names (list): list of song names
        token (TokenData): token user info

    Raises:
    ------
        PlaylistBadNameException: invalid playlist name
        PlaylistNotFoundException: playlist doesnt exists
        PlaylistServiceException: unexpected error while updating playlist

    """
    try:
        handle_playlist_name_parameter(name)
        handle_playlist_should_exists(name)

        playlist = playlist_repository.get_playlist_by_name(name)

        check_jwt_user_is_playlist_owner(token=token, owner=playlist.owner)

        if not new_name:
            playlist_repository.update_playlist(
                name, name, photo if "http" in photo else "", description, song_names
            )
            return

        handle_playlist_name_parameter(new_name)
        playlist_repository.update_playlist(
            name,
            new_name,
            photo if "http" in photo else "",
            description,
            song_names,
        )

        all_users_service.update_playlist_name(name, new_name)
        playlist_service_logger.info(f"Playlist {name} updated successfully")

    except PlaylistBadNameException as exception:
        playlist_service_logger.exception(f"Bad Parameter : {name}")
        raise PlaylistBadNameException from exception
    except PlaylistNotFoundException as exception:
        playlist_service_logger.exception(f"Playlist not found : {name}")
        raise PlaylistNotFoundException from exception
    except PlaylistUnAuthorizedException as exception:
        playlist_service_logger.exception(f"User is not the owner of playlist : {name}")
        raise PlaylistServiceException from exception
    except PlaylistRepositoryException as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Repository updating playlist : {name}"
        )
        raise PlaylistServiceException from exception
    except Exception as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Service updating playlist : {name}"
        )
        raise PlaylistServiceException from exception


def delete_playlist(name: str) -> None:
    """Delete a playlist

    Args:
    ----
        name (str): playlist name

    Raises:
    ------
        PlaylistBadNameException: invalid playlist name
        PlaylistNotFoundException: playlist doesnt exists
        PlaylistServiceException: unexpected error while deleting playlist

    """
    try:
        handle_playlist_name_parameter(name)
        handle_playlist_should_exists(name)
        all_users_service.delete_playlist_from_owner(playlist_name=name)
        playlist_repository.delete_playlist(name)
        playlist_service_logger.info(f"Playlist {name} deleted successfully")

    except PlaylistBadNameException as exception:
        playlist_service_logger.exception(f"Bad Parameter : {name}")
        raise PlaylistBadNameException from exception
    except PlaylistNotFoundException as exception:
        playlist_service_logger.exception(f"Playlist not found : {name}")
        raise PlaylistNotFoundException from exception
    except PlaylistRepositoryException as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Repository deleting playlist :{name}"
        )
        raise PlaylistServiceException from exception
    except Exception as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Service deleting playlist :{name}"
        )
        raise PlaylistServiceException from exception


def get_all_playlist() -> list[PlaylistDTO]:
    """Gets all playlists

    Raises
    ------
        PlaylistServiceException: unexpected error while getting all playlists

    Returns
    -------
        list[PlaylistDTO]: the list of playlists

    """
    try:
        playlists = playlist_repository.get_all_playlists()
        playlists_dto = [get_playlist_dto_from_dao(playlist) for playlist in playlists]
    except PlaylistRepositoryException as exception:
        playlist_service_logger.critical(
            "Unexpected error in Playlist Repository getting all playlists"
        )
        raise PlaylistServiceException from exception
    except Exception as exception:
        playlist_service_logger.critical(
            "Unexpected error in Playlist Service getting all playlists"
        )
        raise PlaylistServiceException from exception
    else:
        playlist_service_logger.info("All Playlists retrieved successfully")
        return playlists_dto


def get_selected_playlists(playlist_names: list[str]) -> list[PlaylistDTO]:
    """Get selected playlist

    Args:
    ----
        playlist_names (list[str]): list with playlists names

    Raises:
    ------
        PlaylistServiceException: unexpected error while getting selected playlist

    Returns:
    -------
        list[PlaylistDTO]: the list of selected playlists

    """
    try:
        playlists = playlist_repository.get_selected_playlists(playlist_names)
        playlists_dto = [get_playlist_dto_from_dao(playlist) for playlist in playlists]
    except PlaylistRepositoryException as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Repository getting selected playlists : {playlist_names}"
        )
        raise PlaylistServiceException from exception
    except Exception as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Service getting selected playlists : {playlist_names}"
        )
        raise PlaylistServiceException from exception
    else:
        playlist_service_logger.info(
            f"Selected Playlists {playlist_names} retrieved successfully"
        )
        return playlists_dto


def search_by_name(name: str) -> list[PlaylistDTO]:
    """Gets playlists with partially matching name

    Args:
    ----
        name (str): name to match

    Raises:
    ------
        PlaylistServiceException: unexpected error while getting playlist that matches a name

    Returns:
    -------
        list[PlaylistDTO]: a list with playlists that matches the name

    """
    try:
        playlists = playlist_repository.get_playlist_search_by_name(name)
        playlists_dto = [get_playlist_dto_from_dao(playlist) for playlist in playlists]
    except PlaylistRepositoryException as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Repository searching playlist by name {name}"
        )
        raise PlaylistServiceException from exception
    except Exception as exception:
        playlist_service_logger.critical(
            f"Unexpected error in Playlist Service searching playlist by name {name}"
        )
        raise PlaylistServiceException from exception
    else:
        playlist_service_logger.info(
            f"Playlists searched by name {name} retrieved successfully"
        )
        return playlists_dto


def handle_playlist_name_parameter(name: str) -> None:
    """Raises an exception if name parameter is invalid

    Args:
    ----
        name (str): name

    Raises:
    ------
        PlaylistBadNameException: if name parameter is invalid

    """
    try:
        validate_parameter(name)
    except BadParameterException:
        raise PlaylistBadNameException from BadParameterException


def handle_playlist_should_exists(name: str) -> None:
    """Raises an exception if playlist doesnt exists

    Args:
    ----
        name (str): playlist name

    Raises:
    ------
        PlaylistNotFoundException: if playlist doesnt exists

    """
    if not check_playlist_exists(name):
        raise PlaylistNotFoundException


def handle_playlist_should_not_exists(name: str) -> None:
    """Raises an exception if playlist does exists

    Args:
    ----
        name (str): playlist name

    Raises:
    ------
        PlaylistNotFoundException: if playlist exists

    """
    if check_playlist_exists(name):
        raise PlaylistAlreadyExistsException


def handle_user_should_exists(name: str) -> None:
    # TODO mover logica excepcion a dentro de servicio all users
    """Raises an exception if user does exists

    Args:
    ----
        name (str): users name

    Raises:
    ------
        UserNotFoundException: if doesnt exists

    """
    if not all_users_service.check_user_exists(name):
        raise UserNotFoundException
