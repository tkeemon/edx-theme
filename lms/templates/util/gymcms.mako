<%def name="render(templateUrl)">
  <% import urllib2 %>
  <% from django.conf import settings %>
  %if templateUrl:
    %if settings.APPSEMBLER_FEATURES.get('ENVIRONMENT', '') == "staging":
      ${urllib2.urlopen('https://staging.gymcms.xyz/static/' + templateUrl).read()}
    %elif settings.APPSEMBLER_FEATURES.get('ENVIRONMENT', '') == "production":
      ${urllib2.urlopen('https://gymcms.xyz/static/' + templateUrl).read()}
    %endif
  %endif
</%def>