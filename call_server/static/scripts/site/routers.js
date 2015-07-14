(function () {
  CallPower.Routers.Campaign = Backbone.Router.extend({
    routes: {
      "campaign/create": "campaignForm",
      "campaign/:id/edit": "campaignForm",
      "campaign/:id/copy": "campaignForm",
      "campaign/:id/audio": "audioForm",
    },

    campaignForm: function(id) {
      CallPower.campaignForm = new CallPower.Views.CampaignForm();
    },

    audioForm: function(id) {
      CallPower.campaignAudioForm = new CallPower.Views.CampaignAudioForm();
    }
  });
})();