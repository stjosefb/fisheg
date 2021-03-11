{% if method == 'default' %}
setTimeout(function(){
    /*images = wheelzoom(document.querySelectorAll('img'), {zoom: 0.1, maxZoom: -1});
    canvas = wheelzoomcanvas(document.getElementById('region_canvas'),
        {zoom: 0.1, maxZoom: -1});

    canvas.addEventListener('wheelzoom.in', function(e) {
        //console.log(images.length);
        images[0].doZoomIn();
    });
    canvas.addEventListener('wheelzoom.out', function(e) {
        //console.log('o');
        images[0].doZoomOut();
    });
    canvas.addEventListener('wheelzoom.drag', function(e) {
        //console.log('d');
        images[0].doDrag(e.detail.bgPosX, e.detail.bgPosY);
    });*/
}, 3000);

{% elif method == 'imagemask' %}
setTimeout(function(){
    images = wheelzoom(document.querySelectorAll('img'), {zoom: 0.1, maxZoom: -1});
    images[1].addEventListener('wheelzoom.in', function(e) {
        //console.log(images.length);
        images[0].doZoomIn();
    });
    images[1].addEventListener('wheelzoom.out', function(e) {
        //console.log('o');
        images[0].doZoomOut();
    });
    images[1].addEventListener('wheelzoom.drag', function(e) {
        //console.log('d');
        images[0].doDrag(e.detail.bgPosX, e.detail.bgPosY);
    });
}, 3000);

{% elif method == 'freelabel' %}
{% endif %}
