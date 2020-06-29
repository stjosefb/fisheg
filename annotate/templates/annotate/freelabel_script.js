$( document ).ready(function() {
    $("#btnScore").attr('disabled', true);
    $("#form_traces").submit(function(e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var url = form.attr('action');

        pack_via_metadata('coco').then( function(data) {
            //console.log(data);
            var hstr = data.join('');
            var obj = JSON.parse(hstr);
            console.log(obj);
            var list_traces = [];
            for (i=0; i<obj.annotations.length; i++) {
                var trace = '';
                //console.log(obj.annotations);
                //if (obj.annotations.length > 0) {
                //seg = JSON.stringify(obj.annotations[i].segmentation);
                //seg = obj.annotations[i].segmentation;
                //}
                //list_seg.push(seg);
                var arr_trace_elmt = []
                for (j=0; j<obj.annotations[i].segmentation.length; j=j+2) {
                    arr_trace_elmt.push(obj.annotations[i].segmentation[j]);
                    arr_trace_elmt.push(obj.annotations[i].segmentation[j+1]);
                    arr_trace_elmt.push(2); // size
                    arr_trace_elmt.push(obj.annotations[i].category_id); // category (color)
                }
                trace = arr_trace_elmt.join();
                //trace = obj.annotations[i].segmentation.join();
                list_traces.push(trace);
            }
            //console.log(list_traces);

            $('input[type="hidden"][name="trace[]"]').remove();
            for (i=0; i<list_traces.length; i++) {
                $('<input>').attr({
                    type: 'hidden',
                    name: 'trace[]',
                    value: list_traces[i]
                }).appendTo(form);
            }

            //console.log(obj.annotations[0].segmentation);
            //console.log(seg);
            /*$('input[name="annot"]').val(JSON.stringify(list_seg));*/

            $.ajax({
                type: "POST",
                //url: "http://localhost:9000/freelabel/refine2/",
                url: url,
                data: form.serialize(), // serializes the form's elements.
                //dataType: 'image/png',
                success: function(data)
                {
                  console.log(data);
                  $('#img_result').attr("src",data.image_base64);
                  $('#img_result_2').attr("src",data.image_base64_2);
                  $('#polygon_segmentations').val(JSON.stringify(data.polygon_segmentations));
                  $('#score').text(data.score + ' ' + data.score_3);
                  $('#scores').val(data.score + ';' + data.score_3);
                  //$('#save_msg').text('Saved');
                  //setTimeout(hideSavedMsg, 1000);
                }
            });
        }.bind(this), function(err) {
            //show_message('Failed to collect annotation data!');
        }.bind(this));
    });
});
