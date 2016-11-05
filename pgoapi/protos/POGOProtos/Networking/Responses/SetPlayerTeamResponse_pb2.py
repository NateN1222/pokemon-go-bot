# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: POGOProtos/Networking/Responses/SetPlayerTeamResponse.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from POGOProtos.Data import PlayerData_pb2 as POGOProtos_dot_Data_dot_PlayerData__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='POGOProtos/Networking/Responses/SetPlayerTeamResponse.proto',
  package='POGOProtos.Networking.Responses',
  syntax='proto3',
  serialized_pb=_b('\n;POGOProtos/Networking/Responses/SetPlayerTeamResponse.proto\x12\x1fPOGOProtos.Networking.Responses\x1a POGOProtos/Data/PlayerData.proto\"\xdd\x01\n\x15SetPlayerTeamResponse\x12M\n\x06status\x18\x01 \x01(\x0e\x32=.POGOProtos.Networking.Responses.SetPlayerTeamResponse.Status\x12\x30\n\x0bplayer_data\x18\x02 \x01(\x0b\x32\x1b.POGOProtos.Data.PlayerData\"C\n\x06Status\x12\t\n\x05UNSET\x10\x00\x12\x0b\n\x07SUCCESS\x10\x01\x12\x14\n\x10TEAM_ALREADY_SET\x10\x02\x12\x0b\n\x07\x46\x41ILURE\x10\x03\x62\x06proto3')
  ,
  dependencies=[POGOProtos_dot_Data_dot_PlayerData__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_SETPLAYERTEAMRESPONSE_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='POGOProtos.Networking.Responses.SetPlayerTeamResponse.Status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNSET', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TEAM_ALREADY_SET', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILURE', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=285,
  serialized_end=352,
)
_sym_db.RegisterEnumDescriptor(_SETPLAYERTEAMRESPONSE_STATUS)


_SETPLAYERTEAMRESPONSE = _descriptor.Descriptor(
  name='SetPlayerTeamResponse',
  full_name='POGOProtos.Networking.Responses.SetPlayerTeamResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='POGOProtos.Networking.Responses.SetPlayerTeamResponse.status', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='player_data', full_name='POGOProtos.Networking.Responses.SetPlayerTeamResponse.player_data', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SETPLAYERTEAMRESPONSE_STATUS,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=131,
  serialized_end=352,
)

_SETPLAYERTEAMRESPONSE.fields_by_name['status'].enum_type = _SETPLAYERTEAMRESPONSE_STATUS
_SETPLAYERTEAMRESPONSE.fields_by_name['player_data'].message_type = POGOProtos_dot_Data_dot_PlayerData__pb2._PLAYERDATA
_SETPLAYERTEAMRESPONSE_STATUS.containing_type = _SETPLAYERTEAMRESPONSE
DESCRIPTOR.message_types_by_name['SetPlayerTeamResponse'] = _SETPLAYERTEAMRESPONSE

SetPlayerTeamResponse = _reflection.GeneratedProtocolMessageType('SetPlayerTeamResponse', (_message.Message,), dict(
  DESCRIPTOR = _SETPLAYERTEAMRESPONSE,
  __module__ = 'POGOProtos.Networking.Responses.SetPlayerTeamResponse_pb2'
  # @@protoc_insertion_point(class_scope:POGOProtos.Networking.Responses.SetPlayerTeamResponse)
  ))
_sym_db.RegisterMessage(SetPlayerTeamResponse)


# @@protoc_insertion_point(module_scope)
