function hideSavedMsg() {
    $('#save_msg').text('');
}
function hideScore() {
    //$('#score').text('');
}
$( document ).ready(function() {
    $("#form_save_annot").submit(function(e) {

        e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var url = form.attr('action');

        pack_via_metadata('coco').then( function(data) {
            var hstr = data.join('');
            var obj = JSON.parse(hstr);
            var list_seg = [];
            for (i=0; i<obj.annotations.length; i++) {
                var seg = '';
                //console.log(obj.annotations);
                //if (obj.annotations.length > 0) {
                //seg = JSON.stringify(obj.annotations[i].segmentation);
                seg = obj.annotations[i].segmentation;
                //}
                list_seg.push(seg);
            }

            //console.log(obj.annotations[0].segmentation);
            //console.log(seg);
            $('input[name="annot"]').val(JSON.stringify(list_seg));

            $.ajax({
                type: "POST",
                url: url,
                data: form.serialize(), // serializes the form's elements.
                success: function(data)
                {
                  //console.log(data);
                  $('#save_msg').text('Saved');
                  setTimeout(hideSavedMsg, 1000);
                }
            });
        }.bind(this), function(err) {
            //show_message('Failed to collect annotation data!');
        }.bind(this));
    });

    $("#form_check_score").submit(function(e) {

        e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var url = form.attr('action');

        pack_via_metadata('coco').then( function(data) {
            var hstr = data.join('');
            var obj = JSON.parse(hstr);
            var list_seg = [];
            for (i=0; i<obj.annotations.length; i++) {
                var seg = '';
                seg = obj.annotations[i].segmentation;
                list_seg.push(seg);
            }

            $('input[name="annot"]').val(JSON.stringify(list_seg));

            $.ajax({
                type: "POST",
                url: url,
                data: form.serialize(), // serializes the form's elements.
                success: function(data)
                {
                  $('#score').text(data.score);
                  setTimeout(hideScore, 1000);
                }
            });
        }.bind(this), function(err) {
            //show_message('Failed to collect annotation data!');
        }.bind(this));
    });
});