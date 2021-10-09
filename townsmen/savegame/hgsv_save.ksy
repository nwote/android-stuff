meta:
  id: hgsv_save
  title: HGSV Save Format
  application: Townsmen by HandyGames GmbH
  endian: le
  tags:
    - save
    - savegame
    - townsmen
  ks-version: 0.9
  imports:
    - ./hgsv_header
    - ./hgsv_save_info
seq:
  - id: s_hdr
    type: hgsv_header
    doc: HGSV Header
  - id: s_info
    type: hgsv_save_info
    doc: HGSV Save Info
  - id: unk_data
    size: 6