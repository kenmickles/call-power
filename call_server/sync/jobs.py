from flask import current_app

from ..extensions import db, rq

from .models import SyncCampaign
from .constants import SCHEDULE_IMMEDIATE
from .integrations import CRMIntegrationError

def get_crm_integration():
    # setup integration from config values
    if current_app.config['CRM_INTEGRATION'].lower() == 'actionkit':
        from .integrations.actionkit_crm import ActionKitIntegration
        ak_credentials = {'domain': current_app.config['ACTIONKIT_DOMAIN'],
                          'username': current_app.config['ACTIONKIT_USER']}
        if 'ACTIONKIT_PASSWORD' in current_app.config:
            ak_credentials['password'] = current_app.config['ACTIONKIT_PASSWORD']
        elif 'ACTIONKIT_API_KEY' in current_app.config:
            ak_credentials['api_key'] = current_app.config['ACTIONKIT_API_KEY']
        else:
            raise CRMIntegrationError('either ACTIONKIT_API_KEY or ACTIONKIT_PASSWORD must be configured')
        crm_integration = ActionKitIntegration(**ak_credentials)
    elif current_app.config['CRM_INTEGRATION'].lower() == 'rogue':
        from .integrations.rogue_crm import RogueIntegration
        rogue_credentails = {'domain': current_app.config['ROGUE_DOMAIN'],
                          'api_key': current_app.config['ROGUE_API_KEY']}
        crm_integration = RogueIntegration(**rogue_credentails)
    elif current_app.config['CRM_INTEGRATION'].lower() == 'mobilecommons':
        from .integrations.mobile_commons import MobileCommonsIntegration
        mobile_commons_credentials = {
            'username': current_app.config['MOBILE_COMMONS_USERNAME'],
            'password': current_app.config['MOBILE_COMMONS_PASSWORD']
        }
        crm_integration = MobileCommonsIntegration(**mobile_commons_credentials)
    else:
        raise CRMIntegrationError('no CRM_INTEGRATION configured')
        return False
    return crm_integration


@rq.job(timeout=60*60)
def sync_campaigns(campaign_id='all'):
    crm_integration = get_crm_integration()

    if campaign_id == 'all':
        campaigns_to_sync = SyncCampaign.query.all()
    else:
        campaigns_to_sync = SyncCampaign.query.filter_by(campaign_id=campaign_id)

    for sync_campaign in campaigns_to_sync:
        if sync_campaign.schedule == SCHEDULE_IMMEDIATE:
            # refuse to sync missed events
            continue
        current_app.logger.info('sync campaign ID: %s' % sync_campaign.campaign_id)
        sync_campaign.sync_calls(crm_integration)