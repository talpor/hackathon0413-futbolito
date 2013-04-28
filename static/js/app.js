var templates = {
    gameType: function(name) {
        return $(
            '<li data-theme="c" data-corners="false" data-shadow="false" data-iconshadow="true" data-wrapperels="div" data-icon="arrow-r" data-iconpos="right" class="ui-btn ui-btn-icon-right ui-li-has-arrow ui-li ui-last-child ui-btn-up-c"><div class="ui-btn-inner ui-li"><div class="ui-btn-text">'+
                '<a href="#config-game" data-transition="slide" class="ui-link-inherit">'+
                    name+
                '</a>'+
            '</div><span class="ui-icon ui-icon-arrow-r ui-icon-shadow">&nbsp;</span></div></li>');
    }
}

var API = {
    'gameTypes': '/games/types'
}

var APP = {
    init: function(argument) {
        $.getJSON(API.gameTypes, function(data) {
            _.forEach(data, function(type) {
                console.log(type);
                $("#gameTypes ul").append(templates.gameType(type));
            })
        });
        $('[data-action]').click(function() {
            APP[$(this).data().action]();
        })
    },
    hello: function() {
        console.log("a");
    }
}

$(document).ready(APP.init);