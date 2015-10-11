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

    var context = canvas.getContext('2d');
    context.drawImage(myImg, 0, 0);

    data = context.getImageData(1, 1, 1, 1).data;

    var r = data[0];
    var g = data[1];
    var b = data[2];
    var a = data[3];
    //console.log('color is ', data[0],data[1],data[2],data[3]);
    $(element).css('background-color','rgba(' + r + ',' + g + ',' + b + ',' + a + ')');
  })


}

var Gymnasium = new Gymnasium();
