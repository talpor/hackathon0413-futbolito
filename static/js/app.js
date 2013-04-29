// require(['templates.js', 'api.js']);

var APP = {
    __game_config__: {
        'type': 0,
        'teams': {
            'barca': {
                    'defense': undefined,
                    'forward': undefined
                },
                'madrid': {
                    'defense': undefined,
                    'forward': undefined
                }
            }
        },
    init: function() {
        $.getJSON(API.gameTypes, function(data) {
            _.forEach(data, function(type, index) {
                $('#gameTypes ul').append(templates.gameType(type, index));
            });
        });

        $(document).on('click', '.game-type-option', function() {
            APP.__game_config__.type = $(this).data().id;
        });

        
        window.io.on('goal', function(data) {
            console.log(data);
        });

        window.io.on('undo', function(data) {
            console.log(data);
        });

        $(document).on('click', '#game .player', function() {
            console.log('GOOOOOLLLL!!');
            window.io.emit('goal', {'team':'barca', 'position':'defender'});
        });

        $.getJSON(API.players, function(data) {
            var players = data.results;

            _.forEach(players, function(player, index) {
                var pos = String.fromCharCode(index % 5 + 97);
                $('#players-table').append(templates.player(player, pos));
            });
        });

        $(document).on('click', '[data-action]', function() {
            APP[$(this).data().action]($(this));
        });
    },
    createGame: function() {
        $.post(API.createGame, APP.__game_config__, function() {
            console.log('A new game started!');
        }).error(function(e) {
            console.error('sorry :(');
            console.error(e);
        });
    },
    selectPlayer: function(player) {
        var gravatar = $('<img>').attr({
            'src': player.attr('src'),
            'data-action': 'removePlayer',
            'data-name': player.data().name
        });
        var gameAvatar = $('<img>').attr({
            'src': player.attr('src'),
            'data-name': player.data().name
        });
        var target = $('.team-banner .empty').eq(0);
        var pos = target.hasClass('barca') ? 0 : 2;
        pos = target.hasClass('defense') ? pos + 1 : pos + 2;
        switch (pos) {
            case 1:
                APP.__game_config__.teams.barca.defense = player.data().id;
                $('#game .player-3').html(gameAvatar);
                break;
            case 2:
                APP.__game_config__.teams.barca.forward = player.data().id;
                $('#game .player-1').html(gameAvatar);
                break;
            case 3:
                APP.__game_config__.teams.madrid.defense = player.data().id;
                $('#game .player-2').html(gameAvatar);
                break;
            case 4:
                APP.__game_config__.teams.madrid.forward = player.data().id;
                $('#game .player-4').html(gameAvatar);
                break;
        }
        target.html(gravatar);
        target.removeClass('empty');
    },
    removePlayer: function(picture) {
        picture.parent().addClass('empty');
        picture.remove();
    }
};

window.io = io.connect('/io');
$(document).ready(APP.init);
