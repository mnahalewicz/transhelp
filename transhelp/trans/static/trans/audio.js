function play_handler(jump_seconds) {
    $("#audio-box")[0].currentTime = jump_seconds;
};

function get_line_pos(line_second_ends, curr_time_seconds) {
    for (i = 0; i < line_second_ends.length; i++) {
        if (curr_time_seconds + 0.2 < line_second_ends[i]) {
            return Math.min(line_second_ends.length, i);
        }
    }
    return line_second_ends.length - 1;
};
