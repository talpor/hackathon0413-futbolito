// window.io = io.connect('/io');

var templates = {
    gameType: function(name) {
        return $(
            '<li data-theme="c" data-corners="false" data-shadow="false" data-iconshadow="true" data-wrapperels="div" data-icon="arrow-r" data-iconpos="right" class="ui-btn ui-btn-icon-right ui-li-has-arrow ui-li ui-last-child ui-btn-up-c"><div class="ui-btn-inner ui-li"><div class="ui-btn-text">' +
                '<a href="#config-game" data-transition="slide" class="ui-link-inherit">' +
                    name +
                '</a>' +
            '</div><span class="ui-icon ui-icon-arrow-r ui-icon-shadow">&nbsp;</span></div></li>');
    },
    player: function(data, position) {
        console.log(data.email);
        var gravatar = $('<img>').attr({
            'src': 'http://www.gravatar.com/avatar/' + CryptoJS.MD5(data.email),
            'data-action': 'selectPlayer', 
            'data-name': data.name
        });
        return $(
            '<div class="ui-block ui-block-' + position + ' ui-block-top"></div>'
        ).append(gravatar);
    }
};

var API = {
    'gameTypes': '/games/types',
    'players': '/players'
};

var APP = {
    init: function() {
        $.getJSON(API.gameTypes, function(data) {
            _.forEach(data, function(type) {
                $('#gameTypes ul').append(templates.gameType(type));
            });
        });

        /*
        window.io.on('goal', function(bla) {
            // pass
        });
        
        window.io.emit('next', value);
        */

        $.getJSON(API.players, function(data) {
            var players = data.results;

            _.forEach(players, function(player, index) {
                var pos = String.fromCharCode(index%5+97);
                $('#players-table').append(templates.player(player, pos));
            });
        });
        
        $(document).on('click', '[data-action]', function() {
            APP[$(this).data().action]($(this));
        });
    },
    selectPlayer: function(player) {
        var gravatar = $('<img>').attr({
            'src': player.attr('src'),
            'data-action': 'removePlayer', 
            'data-name': player.data().name
        });
        $('.team-banner .empty').eq(0).html(gravatar);
        $('.team-banner .empty').eq(0).removeClass('empty');
    },
    removePlayer: function(picture) {
        console.log(picture);
        picture.parent().addClass('empty');
        picture.remove();
    }
};

$(document).ready(APP.init);
