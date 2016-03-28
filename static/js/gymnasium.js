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
};

Gymnasium.prototype.RecordRegistration = function(emailAddress, firstName, lastName, cityId)
{
  var data = {
    debugLink:        0,
    first_name:       firstName,
    last_name:        lastName,
    email:            emailAddress,
    location:         cityId,
    type:             "",
    utm_campaign:     "Registration",
    carrot_type:      "Gymnasium Registration",
    carrot_topic:     "GYM REG",
    PROC:             "AWUISubmitExternalLead"
  };

  return Gymnasium.RecordCloudwallRecord(data);
};

Gymnasium.prototype.RecordCloudwallRecord = function(jsonData)
{
  jsonData.utm_source = "gymnasium.com";
  jsonData.utm_medium = "web";
  jsonData.utm_content = "not-provided";
  jsonData.utm_term = "not-provided";
  jsonData.agent_email = "tmashburn@aquent.com";
  jsonData.agent_id = "1694600";
  jsonData.agent_name = "TALENT LEAD NURTURING";
  jsonData.carrot = "thegymnasium.com";
  jsonData.subdomain = "cw-rc";
  jsonData.language = "en_US";
  jsonData.medium = "1009";
  jsonData.referring_site = "thegymnasium.com";
  jsonData.status = "Talent";
  jsonData.referer = "thegymnasium.com";


  $.ajax("http://aquent.com/application/gymnasium-lead.htm",
    {
      contentType: "application/json",
      dataType: "jsonp",
      data: jsonData
    })
    .done(function(event)
    {
      //console.log("Success!\n", event);
    })
    .fail(function(event, textStatus, errorThrown)
    {
      //console.log("Failure:\n", textStatus, "\n", errorThrown);
    })
    .always(function(e){
      //console.log("always:\n", e);
    })  ;
}
var Gymnasium = new Gymnasium();
