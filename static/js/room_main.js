 var general_header_colors = ["red", "blue", "green", "yellow", "purple", "black"]
 var index_general_header_colors = 0;

 update_connected_players_names(connected_players_names);


 function update_connected_players_names(names){
    connected_players_element.innerHTML = '';
    if (names.length > 0)
        connected_players_element.innerHTML   += names[0] + '<br>';
    if (names.length > 1)
        connected_players_element.innerHTML   += "VS" + '<br>' + names[1];
 }

 function update_score(score_str){
  score_element.textContent = score_str.replace(/\n/g, '<br>');
 }

 function start_new_game(){
    console.log("starting new game");
    socketio.emit("new_game");
 }

function game_end_animation(){

    if (! game_is_over){
        clearInterval(game_end_animation_interval);
        index_general_header_colors = 0;
        general_header.style.color = "black";
    }
    else if (index_general_header_colors == general_header_colors.length){ //  if the game is over
        index_general_header_colors = 0;
        general_header.style.color = general_header_colors[index_general_header_colors];
    }
    else{
        general_header.style.color = general_header_colors[index_general_header_colors];
        index_general_header_colors += 1
        }
}



function update_game(data){
    game_series = data // redundant variable
    current_player_name = data.current_player_name;
    current_player_mark = data.current_player_mark;
    game_is_over = data.is_over;
    game_ended_in_tie = data.ended_in_tie;
    if (game_is_over){
            game_end_animation_interval = setInterval(game_end_animation, 50);
            game_end_animation();
            const button = document.createElement('button');
            button.textContent = 'New Game';
            button.id = "new_game_button"
            button.addEventListener('click', start_new_game);
            document.getElementById('div_for_new_game_button').appendChild(button);
             if (game_ended_in_tie)
                general_header.textContent = `It's a draw!`;
             else {
                general_header.textContent = `${data.winner_name} Won!` ;
              }

    }
    else{ // if gams is not over
        my_button = document.getElementById('new_game_button')
        if (my_button){
               my_button.remove()
        }
        general_header.textContent = `${data.current_player_name}'s turn (${data.current_player_mark})` ;
    }



    my_turn = data.current_player_number === player_number




    update_score(data.score_str);
    update_connected_players_names(data.connected_players_names);

    update_board()
}

function update_board(){

    // Reference to the table container
    var tableContainer = document.getElementById('tableContainer');

    // Clear existing content
    tableContainer.innerHTML = '';



    // Create the table
    var table = document.createElement('table');
    table.id = 'board';
    table.border = 1;


    // Create table body
    var tbody = document.createElement('tbody');



  // Create table content
  game_series.board.forEach(function(rowData, rowIndex) {
        var row = document.createElement('tr');
        rowData.forEach(function(cellData, colIndex) {

            var cell = document.createElement('td');
            cell.onclick = function() {
                step(this, '' + rowIndex + colIndex);
            };
            cell.textContent = cellData;
            row.appendChild(cell);

        });
        tbody.appendChild(row);
    });
    table.appendChild(tbody);

    // Append the table to the container
    tableContainer.appendChild(table);

}




function step(cell_object, cell_name){
    if (cell_object.innerHTML === "" && my_turn && !game_is_over)
    {
    cell_object.innerHTML = game_series.current_player_mark;
    my_turn = false;
    // the following if-else statement counts on the app's logic to always have 2 connected players during an active game
    // we want to set it right away and not wait for the update from the server so the user won't see it's still their turn.
    if (current_player_name == connected_players_names[0]) // can probably do this without if statement by converting boolean to 1/0
        general_header.textContent = `${connected_players_names[1]}'s turn (${current_player_mark})` ;
     else
       general_header.textContent = `${connected_players_names[0]}'s turn (${current_player_mark})` ;

    socketio.emit("turn", cell_name);
    }
}


