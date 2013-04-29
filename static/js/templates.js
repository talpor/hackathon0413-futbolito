var templates = {
    gameType: function(name, index) {
        return $(
            '<li data-theme="c" data-corners="false" data-shadow="false" data-iconshadow="true" data-wrapperels="div" data-icon="arrow-r" data-iconpos="right" class="ui-btn ui-btn-icon-right ui-li-has-arrow ui-li ui-last-child ui-btn-up-c"><div class="ui-btn-inner ui-li"><div class="ui-btn-text">' +
                '<a href="#config-game" data-transition="slide" class="ui-link-inherit game-type-option" data-id="' + index + '">' +
                    name +
                '</a>' +
            '</div><span class="ui-icon ui-icon-arrow-r ui-icon-shadow">&nbsp;</span></div></li>');
    },
    player: function(data, position) {
        console.log(data.email);
        var gravatar = $('<img>').attr({
            'src': 'http://www.gravatar.com/avatar/' + CryptoJS.MD5(data.email),
            'data-action': 'selectPlayer', 
            'data-name': data.name,
            'data-id': data.id
        });
        return $(
            '<div class="ui-block ui-block-' + position + ' ui-block-top"></div>'
        ).append(gravatar);
    }
};