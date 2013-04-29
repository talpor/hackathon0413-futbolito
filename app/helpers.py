def player_to_dict(player):
    """Returns an easy json represtation of a `Player`'s instance."""
    return {
        'id': player.id,
        'name': player.name,
        'email': player.email,
        'twitter': player.twitter
    }
