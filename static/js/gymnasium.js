/// File:         Gymnasium.js
/// Description:  library containing helper functions used on Gymnasium
/// Author:       @mbifulco

function Gymnasium(){}

Gymnasium.prototype.setBackgroundColorOfElementFromImage = function (element, image)
{
  var canvas= document.createElement('canvas');
  var myImg = document.createElement('img');

  $(image).each(function(i,imgObj){
    myImg.src = imgObj.src;

    $(myImg).one('load',function(){

      var context = canvas.getContext('2d');
      context.drawImage(myImg, 0, 0);

      data = context.getImageData(1, 1, 1, 1).data;

      var r = data[0];
      var g = data[1];
      var b = data[2];
      var a = data[3];

      $(element).css('background-color','rgba(' + r + ',' + g + ',' + b + ',' + a + ')');
    });
  })
}

///get a URL parameter passed in with HTTP GET
///NOTE: this function is not case sensitive
Gymnasium.prototype.getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0].toLowerCase() === sParam.toLowerCase()) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

<!-- Facebook Pixel Code -->
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','//connect.facebook.net/en_US/fbevents.js');
<!-- End Facebook Pixel Code -->

Gymnasium.prototype.injectFBTrackingPixel = function(){
  var trackingPix = $('<noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=1074612282557779&ev=PageView&noscript=1" /></noscript>');
  $('body').append(trackingPix);
  fbq('init', '1074612282557779');
  fbq('track', "PageView");
};

var Gymnasium = new Gymnasium();
