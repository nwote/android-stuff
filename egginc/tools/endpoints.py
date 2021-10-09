import ei_pb2 as egg
import os.path

from google.protobuf.message import Message as pbMessage

class UnknownRequest(pbMessage):
    pass

class UnknownResponse(pbMessage):
    pass

ei_endpoints_mapped = {}
ei_auth_messages = [
    egg.Backup,
    egg.EggIncFirstContactRequest,
    egg.EggIncFirstContactResponse,
    egg.SaveBackupResponse,
    egg.ContractsResponse,
    egg.PeriodicalsResponse,
    egg.ConfigResponse,
    egg.ContractCoopStatusResponse,
    egg.ArtifactsConfigurationResponse,
    egg.CompleteMissionResponse,
    egg.CraftArtifactResponse,
    egg.ConsumeArtifactResponse,
    egg.SetArtifactResponse
]

def from_path(full_path):
    parent = full_path[1:full_path.rfind('/')]
    file = os.path.basename(full_path)

    for path in ei_endpoints_mapped:
        if path != parent:
            continue

        for endpoint in ei_endpoints_mapped[path]:
            if endpoint['endpoint'] == file:
                return endpoint

        return None
    return None

def check_endpoint(full_path):
    return from_path(full_path) is not None

def _register_path(name):
    ei_endpoints_mapped[name] = []

def _register_endpoint(path, name, req_obj: pbMessage, rsp_obj: pbMessage):
    ei_endpoints_mapped[path].append(
        {
            'endpoint': name,
            'req': {
                'msg': req_obj,
                'authenticated': req_obj in ei_auth_messages
            },
            'rsp': {
                'msg': rsp_obj,
                'authenticated': rsp_obj in ei_auth_messages
            }
        }
    )

def register_endpoints():
    # register paths
    _register_path('ei')
    _register_path('ei_data')
    _register_path('ei_afx')

    # register endpoints
    _register_endpoint('ei', 'auto_join_coop', egg.AutoJoinCoopRequest, egg.JoinCoopResponse)
    _register_endpoint('ei', 'coop_status', egg.ContractCoopStatusRequest, egg.ContractCoopStatusResponse)
    _register_endpoint('ei', 'create_coop', egg.CreateCoopRequest, egg.CreateCoopResponse)
    _register_endpoint('ei', 'daily_gift_info', UnknownRequest, egg.DailyGiftInfo)
    _register_endpoint('ei', 'first_contact_secure', egg.EggIncFirstContactRequest, egg.EggIncFirstContactResponse)
    _register_endpoint('ei', 'get_ad_config', UnknownRequest, egg.EggIncAdConfig)
    _register_endpoint('ei', 'get_config', egg.ConfigRequest, egg.ConfigResponse)
    _register_endpoint('ei', 'get_contracts', egg.ContractsRequest, egg.ContractsResponse)
    _register_endpoint('ei', 'get_events', UnknownRequest, egg.EggIncCurrentEvents)
    _register_endpoint('ei', 'get_periodicals', egg.GetPeriodicalsRequest, egg.PeriodicalsResponse)
    _register_endpoint('ei', 'get_sales', egg.SalesInfoRequest, egg.SalesInfo)
    _register_endpoint('ei', 'gift_player_coop', egg.GiftPlayerCoopRequest, UnknownResponse)
    _register_endpoint('ei', 'join_coop', egg.JoinCoopRequest, egg.JoinCoopResponse)
    _register_endpoint('ei', 'kick_player_coop', egg.KickPlayerCoopRequest, UnknownResponse)
    _register_endpoint('ei', 'leave_coop', egg.LeaveCoopRequest, UnknownResponse)
    _register_endpoint('ei', 'query_coop', egg.QueryCoopRequest, egg.QueryCoopResponse)
    _register_endpoint('ei', 'save_backup_secure', egg.Backup, egg.SaveBackupResponse)
    _register_endpoint('ei', 'update_coop_permissions', egg.UpdateCoopPermissionsRequest, egg.UpdateCoopPermissionsResponse)
    _register_endpoint('ei', 'update_coop_status', egg.ContractCoopStatusUpdateRequest, egg.ContractCoopStatusUpdateResponse)
    _register_endpoint('ei', 'user_data_info', egg.UserDataInfoRequest, egg.UserDataInfoResponse)

    _register_endpoint('ei_data', 'log_data', egg.GenericAction, UnknownResponse)
    _register_endpoint('ei_data', 'log_purchase', egg.VerifyPurchaseRequest, egg.VerifyPurchaseResponse)

    _register_endpoint('ei_afx', 'collect_contract_artifacts', egg.CollectContractArtifactRewardsRequest, egg.CompleteMissionResponse)
    _register_endpoint('ei_afx', 'complete_mission', UnknownRequest, egg.CompleteMissionResponse)
    _register_endpoint('ei_afx', 'config', egg.ConfigRequest, egg.ConfigResponse)
    _register_endpoint('ei_afx', 'consume_artifact', egg.ConsumeArtifactRequest, egg.ConsumeArtifactResponse)
    _register_endpoint('ei_afx', 'craft_artifact', egg.CraftArtifactRequest, egg.CraftArtifactResponse)
    _register_endpoint('ei_afx', 'demote_artifact', egg.ConsumeArtifactRequest, egg.ConsumeArtifactResponse)
    _register_endpoint('ei_afx', 'launch_mission', egg.MissionRequest, egg.MissionResponse)
    _register_endpoint('ei_afx', 'set_artifact', egg.SetArtifactRequest, egg.SetArtifactResponse)
    _register_endpoint('ei_afx', 'sync_mission', egg.MissionRequest, egg.MissionResponse)