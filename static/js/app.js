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

        $(document).on('click', '#game .player', function() {
            console.log('GOOOOOLLLL!!');
            var p = $(this);
            if (p.hasClass('player-1'))
                window.io.emit('goal', 'barca', 'defender');
            else if (p.hasClass('player-2'))
                window.io.emit('goal', 'madrid', 'forward');
            else if (p.hasClass('player-3'))
                window.io.emit('goal', 'barca', 'forward');
            else if (p.hasClass('player-4'))
                window.io.emit('goal', 'madrid', 'defender');

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
        $.ajax({
            type: 'POST',
            url: API.createGame,
            data: JSON.stringify(APP.__game_config__),
            contentType: 'application/json; charset=utf-8',  // working with application/x-www-form-urlencoded; is awful.
            dataType: 'json',
            success: function(data) {
                APP.chronometer.start();
                if (data.success)
                    console.log('A new game started!');
                else
                    console.log('A game is already in place');
                APP.ioConnect();
            },
            error: function(e) {
                console.error('sorry :(');
                console.error(e);
            }
        });
    },
    ioConnect: function () {
        window.io = io.connect('/board');
        window.io.emit('subscribe');

        // debug io events
        window.io.on('log', function (pkt) { console.info('Receiving from server:', pkt); });

        window.io.on('goal', function(data) {
            console.log(data);
        });

        window.io.on('game board', function(data) {
            $('.barca-side p').text(data.score.barca);
            $('.madrid-side p').text(data.score.madrid);
            $('.player-1 img').attr('src', 'http://www.gravatar.com/avatar/' +
                                    CryptoJS.MD5(data.teams.barca.defense.email));
            $('.player-3 img').attr('src', 'http://www.gravatar.com/avatar/' +
                                    CryptoJS.MD5(data.teams.barca.forward.email));
            $('.player-4 img').attr('src', 'http://www.gravatar.com/avatar/' +
                                    CryptoJS.MD5(data.teams.madrid.defense.email));
            $('.player-2 img').attr('src', 'http://www.gravatar.com/avatar/' +
                                    CryptoJS.MD5(data.teams.madrid.forward.email));
            console.log(data);
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
                $('#game .player-1').html(gameAvatar);
                break;
            case 2:
                APP.__game_config__.teams.barca.forward = player.data().id;
                $('#game .player-3').html(gameAvatar);
                break;
            case 3:
                APP.__game_config__.teams.madrid.defense = player.data().id;
                $('#game .player-4').html(gameAvatar);
                break;
            case 4:
                APP.__game_config__.teams.madrid.forward = player.data().id;
                $('#game .player-2').html(gameAvatar);
                break;
        }
        target.html(gravatar);
        target.removeClass('empty');
    },
    removePlayer: function(picture) {
        picture.parent().addClass('empty');
        picture.remove();
    },
    chronometer: {
        __chronometer__: undefined,
        __currentTime__: 0,
        target: $('#game h3'),
        update: function() {
            this.__currentTime__+=1;
            var currentTime = this.__currentTime__/60;
            var mm = Math.floor(currentTime);
            this.target.html(
                ("0" + mm).slice(-2) + ':' +
                ("0" + Math.floor((currentTime - mm) * 60)).slice(-2)
            );

        },
        start: function (){
           this.update();
           this.__chronometer__ = setInterval('APP.chronometer.update();', 1000);
        },
        pause: function() {
            clearInterval(this.__chronometer__);
        },
        stop: function  (){
            this.__currentTime__ = 0;
            clearInterval(this.__chronometer__);
            this.target.html('--:--');
        }
    }
};

$(document).ready(APP.init);
