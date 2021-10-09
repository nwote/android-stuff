meta:
  id: hgsv_save_info
  title: HGSV Save Info
  application: Townsmen by HandyGames GmbH
  endian: le
  tags:
    - save
    - savegame
    - townsmen
  ks-version: 0.9
seq:
  - id: world_name
    type: save_name
  - id: unk_01
    type: u1
  - id: unk_02
    type: u1
types:
  save_name:
    seq:
      - id: name_len
        type: u2
      - id: name
        type: str
        size: name_len
        encoding: UTF-8