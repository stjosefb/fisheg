/*!
	Wheelzoom 1.1.1
	license: MIT
	https://luperi.github.io/wheelzoom/
*/

// create CustomEvent to override window.Event in unsupported browsers
(function () {
	function CustomEvent ( event, params ) {
		params = params || { bubbles: false, cancelable: false, detail: undefined };
		var evt = document.createEvent( 'CustomEvent' );
		evt.initCustomEvent( event, params.bubbles, params.cancelable, params.detail );
		return evt;
	}

	CustomEvent.prototype = window.Event.prototype;
	window.CustomEvent = CustomEvent;
})();

// create cross browser triggerEvent function
window.triggerEvent = function(target, eventName, params) {
	if (params) {
		var e = new CustomEvent(eventName, {
			'detail': params
		});
	} else {
		try {
			var e = new Event(eventName);
		} catch (err) {
			var e = new CustomEvent(eventName);
		}
	}

	return target.dispatchEvent(e, params);
};

window.wheelzoomcanvas = (function(){
	var defaults = {
		zoom: 0.10,
		maxZoom: -1
	};

	//var canvas = document.createElement('canvas');

	var main = function(cnvs, options){
    //console.log('main');
		if (!cnvs || !cnvs.nodeName || cnvs.nodeName !== 'CANVAS') { return; }
    
		var settings = {};
		var width;
		var height;
		var bgWidth;
		var bgHeight;
		var bgPosX;
		var bgPosY;
		var previousEvent;
		//var cachedDataUrl;
		var initBgPosX;
		var initBgPosY;
		var origWidth;
		var origHeight;    
    var scaleH = 1;
    var scaleW = 1;
    var moveH = 0;
    var moveW = 0;
    var stackScale = [];
    var stackTranslate = [];
    
    /*
		function setSrcToBackground(img) {
			img.style.backgroundImage = 'url("'+img.src+'")';
			img.style.backgroundRepeat = 'no-repeat';
			canvas.width = img.naturalWidth;
			canvas.height = img.naturalHeight;
			cachedDataUrl = canvas.toDataURL();
			img.src = cachedDataUrl;
		}
    */

		function updateBgStyle(deltaY) {
			if (bgPosX > 0) {
				bgPosX = 0;
			} else if (bgPosX < width - bgWidth) {
				bgPosX = width - bgWidth;
			}

			if (bgPosY > 0) {
				bgPosY = 0;
			} else if (bgPosY < height - bgHeight) {
				bgPosY = height - bgHeight;
			}
      
      /*if (moveH == 0) { 
        moveH = (bgHeight-origHeight)/2;
        moveW = (bgWidth-origWidth)/2;
      }*/
      var ctx = cnvs.getContext("2d");
      if (deltaY < 0) {
      //if (scaleH <= 0) {
        stackScale.push([scaleW, scaleH]);       
        scaleH = bgHeight/origHeight;
        scaleW = bgWidth/origWidth;        
      //}              
                    
        stackTranslate.push([moveW, moveH]);
        ctx.setTransform(1, 0, 0, 1, 1, 1);  
        ctx.translate(bgPosX, bgPosY);        
        ctx.scale(scaleW, scaleH);
        moveW = bgPosX;
        moveH = bgPosY;
        
        //stackTranslate.push([bgPosX, bgPosY]);
        //moveH = (bgHeight-origHeight)/2;
        //moveW = (bgWidth-origWidth)/2;
        //console.log(moveH + ' 1 ' + moveW);
        
        //moveH = bgPosY/scaleH;
        //moveW = bgPosX/scaleW;        
        //ctx.translate(moveW, moveH);
        //console.log(moveH + ' 2 ' + moveW);
        //stackTranslate.push([moveW, moveH]);

        //stackTranslate.push([bgPosX, bgPosY]);
               
        //console.log(bgPosX + ' in1 ' + bgPosY);
        console.log(scaleW + ' in2 ' + scaleH);
        console.log(bgWidth + ' in2');
      } else if (deltaY > 0) {     
        translate = stackTranslate.pop();
        if (translate) {
          moveH = translate[1];
          moveW = translate[0];
        } else {
          moveH = 0;
          moveW = 0;
        }       
        //scaleH2 = bgHeight/origHeight;
        //scaleW2 = bgWidth/origWidth;        
        
        //moveH = bgPosY/scaleH;
        //moveW = bgPosX/scaleW;
        //moveH = bgPosY/scaleH2;
        //moveW = bgPosX/scaleW2;        
        //moveH = bgPosY;
        //moveW = bgPosX;          
        
        //moveH = bgHeight - origHeight;
        //moveW = bgWidth - origWidth;        
        
        
      //if (scaleH <= 0) { 
        scale = stackScale.pop();
        if (scale) {
          scaleH = scale[1];
          scaleW = scale[0];
        } else {
          scaleH = 1;
          scaleW = 1;
        }
        
        
      //} 
        //ctx.translate(-moveW, -moveH);      
        //ctx.translate(-moveW/scaleW, -moveH/scaleH);
        //ctx.translate(-moveW*scaleW, -moveH*scaleH);
        ctx.setTransform(1, 0, 0, 1, 1, 1);
        ctx.translate(moveW, moveH); 
        //ctx.translate(-moveW, -moveH); 
        //ctx.translate(moveW/scaleW, moveH/scaleH);
        //ctx.translate(moveW*scaleW, moveH*scaleH);
        //ctx.translate(-moveW/scaleW, -moveH/scaleH);
        //ctx.translate(-moveW*scaleW, -moveH*scaleH);        
        ctx.scale(scaleW, scaleH);
        //moveH = (bgHeight-origHeight)/2;
        //moveW = (bgWidth-origWidth)/2;        

        //console.log(moveW + ' out1 ' + moveH);
        console.log(scaleW + ' out2 ' + scaleH);
        console.log(bgWidth + ' out2');
        
        //ctx.translate(-moveW, -moveH); 
        //ctx.translate(moveW, moveH); 
        //ctx.translate(moveW/scaleW, moveH/scaleH);
        //ctx.translate(-moveW/scaleW, -moveH/scaleH);
        //ctx.translate(-moveW*scaleW, -moveH*scaleH);
       
        
      } else {
        ctx.setTransform(1, 0, 0, 1, 1, 1);
      }      
      
      //console.log(scaleW + " " + scaleH);
      //console.log(bgWidth + " " + bgHeight);
			//img.style.backgroundSize = bgWidth+'px '+bgHeight+'px';
			//img.style.backgroundPosition = bgPosX+'px '+bgPosY+'px';
		}
    
		function reset() {
      //console.log('reset');
			bgWidth = width;
			bgHeight = height;
			bgPosX = bgPosY = 0;
			updateBgStyle(0);
		}
    
		cnvs.doZoomIn = function(propagate) {
			if (typeof propagate === 'undefined') {
				propagate = false;
			}

			doZoom(-100, propagate);
		}
    
		cnvs.doZoomOut = function(propagate) {
			if (typeof propagate === 'undefined') {
				propagate = false;
			}

			doZoom(100, propagate);
		}

		function doZoom (deltaY, propagate) {
			if (typeof propagate === 'undefined') {
				propagate = false;
			}

			// zoom always at the center of the image
			var offsetX = width/2;
			var offsetY = height/2;

			// Record the offset between the bg edge and the center of the image:
			var bgCenterX = offsetX - bgPosX;
			var bgCenterY = offsetY - bgPosY;
			// Use the previous offset to get the percent offset between the bg edge and the center of the image:
			var bgRatioX = bgCenterX/bgWidth;
			var bgRatioY = bgCenterY/bgHeight;

			// Update the bg size:
			if (deltaY < 0) {
				if (settings.maxZoom == -1 || (bgWidth + bgWidth*settings.zoom) / width <= settings.maxZoom) {
					bgWidth += bgWidth*settings.zoom;
					bgHeight += bgHeight*settings.zoom;
				}
			} else {
				//bgWidth -= bgWidth*settings.zoom;
				//bgHeight -= bgHeight*settings.zoom;
        bgWidth = bgWidth/(1+settings.zoom);
				bgHeight = bgHeight/(1+settings.zoom);
			}

			// Take the percent offset and apply it to the new size:
			bgPosX = offsetX - (bgWidth * bgRatioX);
			bgPosY = offsetY - (bgHeight * bgRatioY);
      

			if (propagate) {
				if (deltaY < 0) {
					// setTimeout to handle lot of events fired
					setTimeout(function() {
						triggerEvent(cnvs, 'wheelzoom.in', {
							zoom: bgWidth/width,
							bgPosX: bgPosX,
							bgPosY: bgPosY
						});
					}, 10);
				} else {
					// setTimeout to handle lot of events fired
					setTimeout(function() {
						triggerEvent(cnvs, 'wheelzoom.out', {
							zoom: bgWidth/width,
							bgPosX: bgPosX,
							bgPosY: bgPosY
						});
					}, 10);
				}
			}

			// Prevent zooming out beyond the starting size
			if (bgWidth <= width || bgHeight <= height) {
				triggerEvent(cnvs, 'wheelzoom.reset');
			} else {
				updateBgStyle(deltaY);
			}
		}
    
		function onwheel(e) {
			var deltaY = 0;

			e.preventDefault();

			if (e.deltaY) { // FireFox 17+ (IE9+, Chrome 31+?)
				deltaY = e.deltaY;
			} else if (e.wheelDelta) {
				deltaY = -e.wheelDelta;
			}

			if (deltaY < 0) {
				cnvs.doZoomIn(true);
        clearCanvas();
        strokeRect();
			} else {
				cnvs.doZoomOut(true);
        clearCanvas();
        strokeRect();
			}
		}
    /*
		img.doDrag = function (x, y) {
			bgPosX = x;
			bgPosY = y;

			updateBgStyle();
		}

		function drag(e) {
			e.preventDefault();
			var xShift = e.pageX - previousEvent.pageX;
			var yShift = e.pageY - previousEvent.pageY;
			var x = bgPosX + xShift;
			var y = bgPosY + yShift;

			img.doDrag(x, y);

			triggerEvent(img, 'wheelzoom.drag', {
				bgPosX: bgPosX,
				bgPosY: bgPosY,
				xShift: xShift,
				yShift: yShift
			});

			previousEvent = e;
			updateBgStyle();
		}

		function removeDrag() {
			triggerEvent(img, 'wheelzoom.dragend', {
				x: bgPosX - initBgPosX,
				y: bgPosY - initBgPosY
			});

			document.removeEventListener('mouseup', removeDrag);
			document.removeEventListener('mousemove', drag);
		}

		// Make the background draggable
		function draggable(e) {
      //console.log(e.button);
      if (e.button == 2) {
        triggerEvent(img, 'wheelzoom.dragstart');

        e.preventDefault();
        previousEvent = e;
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', removeDrag);
        return false;
      }
		}
    */
    function clearCanvas() {
      var context = cnvs.getContext("2d");
      // Store the current transformation matrix
      context.save();

      // Use the identity matrix while clearing the canvas
      context.setTransform(1, 0, 0, 1, 0, 0);
      context.clearRect(0, 0, cnvs.width, cnvs.height);

      // Restore the transform
      context.restore();      
    }
    function strokeRect() {
      var ctx = cnvs.getContext("2d");
      ctx.strokeRect(100, 100, 25, 15);      
    }
		function load() {
      //console.log('load');
			//if (img.src === cachedDataUrl) return;

			var computedStyle = window.getComputedStyle(cnvs, null);

			width = parseInt(computedStyle.width, 10);
			height = parseInt(computedStyle.height, 10);
      origWidth = width;
      origHeight = height;
			bgWidth = width;
			bgHeight = height;
			bgPosX = bgPosY = initBgPosX = initBgPosY = 0;
      console.log(bgWidth + 'load0');

			//setSrcToBackground(img);
      strokeRect();
			//img.style.backgroundSize =  width+'px '+height+'px';
			//img.style.backgroundPosition = '0 0';

			cnvs.addEventListener('wheelzoom.reset', reset);
			cnvs.addEventListener('wheelzoom.destroy', destroy);
			cnvs.addEventListener('wheel', onwheel);
			//img.addEventListener('mousedown', draggable);
		}

		var destroy = function (originalProperties) {
			cnvs.removeEventListener('wheelzoom.destroy', destroy);
			cnvs.removeEventListener('wheelzoom.reset', reset);
			//img.removeEventListener('mouseup', removeDrag);
			//img.removeEventListener('mousemove', drag);
			//img.removeEventListener('mousedown', draggable);
			cnvs.removeEventListener('wheel', onwheel);

			/*img.style.backgroundImage = originalProperties.backgroundImage;
			img.style.backgroundRepeat = originalProperties.backgroundRepeat;
			img.src = originalProperties.src;*/
		}.bind(null, {
			/*backgroundImage: img.style.backgroundImage,
			backgroundRepeat: img.style.backgroundRepeat,
			src: img.src*/
		});
    
		options = options || {};

		Object.keys(defaults).forEach(function(key){
			settings[key] = typeof options[key] !== 'undefined' ? options[key] : defaults[key];
		});
    //console.log('before interval');
		var t = setInterval(function(){
			//if (cnvs.complete) {
				load();
			//}

			clearInterval(t);
		}, 100);
    //console.log('after interval');
	};

	// Do nothing in IE8
	if (typeof window.getComputedStyle !== 'function') {
		return function(elements) {
			return elements;
		};
	} else {
		return function(elements, options) {
			if (elements && elements.length) {
				for (var i=0;i<elements.length;i++) {
					main(elements[i], options);
				}
			} else if (elements && elements.nodeName) {
				main(elements, options);
			}

			return elements;
		};
	}
}());