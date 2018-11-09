SERVER = 'https://nintendeals.herokuapp.com/api/v1';

if (window.location.href.includes('localhost')) {
    SERVER = 'http://localhost:5000/api/v1';
}

var TODAY = new Date();
var YESTERDAY = new Date(TODAY.getTime() - 2 * 24 * 60 * 60 * 1000);
var NEXT_WEEK = new Date(TODAY.getTime() + 7 * 24 * 60 * 60 * 1000);


function search(table_id) {
    var input, filter, table, tr, td, i;

    input = document.getElementById(table_id);
    filter = input.value.toUpperCase();

    table = document.getElementById("table");
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];

        if (td) {
            if (td.innerHTML.toUpperCase().indexOf(filter) > -1)
                tr[i].style.display = "";
            else
                tr[i].style.display = "none";
        }
    }
}

function get(dict, key, def) {
    if (typeof(dict) == "undefined")
        return def;

    value = def;

    try {
        value = dict[key];

        if (value == null || typeof(value) == "undefined")
            value = def;

    } catch (err) {
        value = def;
    }

    return value;
}

function get_config() {
    var config = null;

    $.ajax({
        method: "GET",
        url: SERVER + "/config",
        async: false
    }).done(function(msg) {
        config = msg;
    });

    return config;
}

function get_game(game_id) {
    var game = null;

    $.ajax({
        method: "GET",
        url: SERVER + "/games/" + game_id,
        async: false
    }).done(function(msg) {
        game = msg;
    });

    return game;
}

function add_games_to_table(table_id, config, limit_, skip_) {
    $.ajax({
        method: "GET",
        url: SERVER + "/games",
        data: {
            limit: limit_,
            skip: skip_
        }
    }).done(function(msg) {
        $.each(msg, function(index) {
            table_filler(table_id, msg[index], config);
        });
    });
}

function table_filler(table_id, game, config) {
    table = $('#' + table_id);

    row = '<tr>';
    row += '  <td scope="row">{title}</td>';
    row += '  <td align="center" bgcolor="{color}">{release_date}</td>';
    row += '  <td>{countries}</td>';
    row += '  <td>{number_of_players}</td>';
    row += '  <td align="center">{metascore}</td>';
    row += '  <td align="center">{userscore}</td>';
    row += '  <td align="center">{modal} {link}</td>';
    row += '</tr>';

    countries = '';
    country_codes = '';    
    
    $.each(game['region'], function(index, region) {
        $.each(config['countries'], function(index, country) {
            if (country['region'] == region) {
                countries += country['flag'];
                country_codes += country['key'] + ' ';
            }
        });
    });

    modal = '<a href="#" onclick="show_modal(\'{id}\')">ℹ️</a>'
    modal = modal.replace('{id}', game['_id']);

    link = '<a href="http://www.reddit.com/message/compose?to={username}&subject=add : {id} : {title}&message={countries}" target="_blank">➕</a>';
    link = link.replace('{username}', config['username']);
    link = link.replace('{id}', game['_id']);
    link = link.replace('{countries}', country_codes);
    link = link.replace('{title}', game['title']);

    try {
        release_date = new Date(game['release_date']);

        if (YESTERDAY < release_date && release_date < TODAY) {
            color = '#FFFF99';
        } else if (TODAY < release_date && NEXT_WEEK > release_date) {
            color = '#FF9966';
        } else if (TODAY < release_date) {
            color = '#FF9999';
        } else {
            color = '#FFFFFF';
        }
    } catch (err) {
        color = '#000000';
    }

    row = row.replace('{id}', game['_id'].replace('Switch-', ''));
    row = row.replace('{color}', color);
    row = row.replace('{title}', game['title'].replace(' 🍄', '<font color="white">!</font>🍄'));
    row = row.replace('{release_date}', game['release_date']);
    row = row.replace('{countries}', countries);
    row = row.replace('{number_of_players}', game['number_of_players']);

    row = row.replace('{metascore}', get(game["scores"], 'metascore', ''));
    row = row.replace('{userscore}', get(game["scores"], 'userscore', ''));

    row = row.replace('{modal}', modal);
    row = row.replace('{link}', link);

    table.append(row);
}

function show_modal(id) {
    game = get_game(id);
    console.log(game);

    $('#modal_title').text(game['final_title'] + ' (' + game['_id'].replace('Switch-', '') + ')');
    $('#modal_release').text(game['release_date']);
    $('#modal_genres').text(game['genres']);
    $('#modal_players').text(game['number_of_players']);
    $('#modal_metascore').text(get(game["scores"], 'metascore', ''));
    $('#modal_userscore').text(get(game["scores"], 'userscore', ''));

    features = $('#modal_features');
    features.empty();

    if (get(game['features'], 'cloud_saves', false))
        features.append('<li>☁️ Cloud Saves</li>');

    if (get(game['features'], 'nso', false))
        features.append('<li>🌐 Nintendo Switch Online required</li>');

    if (get(game['features'], 'dlc', false))
        features.append('<li>📦 DLC available</li>');

    if (get(game['features'], 'nfc', false))
        features.append('<li>👤 Amiibo supported </li>');

    if (get(game['features'], 'voice_chat', false))
        features.append('<li>🎙️ Voice Chat enabled</li>');

    if (get(game['features'], 'demo', false))
        features.append('<li>🎁 Demo available</li>');

    $('#modal').modal('show')
}
