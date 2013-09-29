function bookthatmofo(){
    var ticketid = $('input[name="ticketid"]').val();
    var kind     = $('input[name="ticketkind"]:checked').val();
    var night    = $('input[name="ticketnight"]:checked').val();
    var sellerid    = $('input[name="sellerid"]').val();
    if (ticketid==null ||
        kind==null ||
        night==null ||
        sellerid==null ||
        ticketid==undefined ||
        kind==undefined ||
        night==undefined ||
        sellerid==undefined) {
        alert("Fill in everything.")
    }
    $.post('/chromatic/sellform',{ ticketid: ticketid, kind: kind, night: night, seller: sellerid}, function(){
        alert("Success! We have secured the tickets!")
    }).fail(function(){
        alert("Ticketing failed!")
    })
}

$(document).ready(function(){
    $('#bookthatmofo').click(bookthatmofo)
});