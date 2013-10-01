function bookthatmofo(){
    var ticketid = $('input[name="ticketid"]').val();
    var kind     = $('input[name="ticketkind"]:checked').val();
    var night    = $('input[name="ticketnight"]:checked').val();
    if (ticketid==null ||
        kind==null ||
        night==null ||
        ticketid==undefined ||
        kind==undefined ||
        night==undefined){
        alert("Fill in everything.")
    }
    $.post('/chromatic/sellform',{ ticketid: ticketid, kind: kind, night: night}, function(data){
        if (data['success'] == true)
            alert("Success! We have secured the tickets!");
        else
            alert("Ticketing failed: " + data['error']);

    }, 'json').fail(function(){
        alert("Ticketing failed!")
    });
}

$(document).ready(function(){
    $('#bookthatmofo').click(bookthatmofo)
});